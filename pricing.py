import boto3
import pandas as pd
import requests

# Map Azure instances to AWS equivalents
instance_map = {
    "Standard_B2ms": "t3.medium",
    "Standard_B4ms": "t3.large",
    "Standard_B8ms": "t3.xlarge",
    "Standard_D2s_v3": "m5.large",
    "Standard_D4s_v3": "m5.xlarge",
    "Standard_D8s_v3": "m5.2xlarge",
    "Standard_E2s_v3": "r5.large",
    "Standard_E4s_v3": "r5.xlarge",
    "Standard_E8s_v3": "r5.2xlarge",
    "Standard_E16as_v4": "r5.4xlarge",
    "Standard_E64is_v4": "r5.16xlarge",
    "Standard_F4s_v2": "c5.xlarge",
    "Standard_F8s_v2": "c5.2xlarge",
    "Standard_F32s_v2": "c5.9xlarge",
    "Standard_F48s_v2": "c5.12xlarge",
    # Add more as needed
}

# Azure → AWS region mapping
azure_region_map = {
    "eastus": "US East (N. Virginia)",
    "eastus2": "US East (N. Virginia)",
    "centralus": "US East (Ohio)",
    "southcentralus": "US West (Oregon)",
    "westus": "US West (N. California)",
    "westus2": "US West (Oregon)",
    "westeurope": "EU (Ireland)",
    "northeurope": "EU (Ireland)",
    "francecentral": "EU (Paris)",
    "germanywestcentral": "EU (Frankfurt)",
    "uksouth": "EU (London)",
    "brazilsouth": "South America (São Paulo)",
    "japaneast": "Asia Pacific (Tokyo)",
    "japanwest": "Asia Pacific (Osaka)",
    "australiaeast": "Asia Pacific (Sydney)",
    "southindia": "Asia Pacific (Mumbai)",
    "centralindia": "Asia Pacific (Mumbai)",
    "westindia": "Asia Pacific (Mumbai)",
}

# Initialize boto3 pricing client
pricing_client = boto3.client("pricing", region_name="us-east-1")


def get_aws_price(instance_type, aws_region):
    try:
        response = pricing_client.get_products(
            ServiceCode="AmazonEC2",
            Filters=[
                {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
                {"Type": "TERM_MATCH", "Field": "location", "Value": aws_region},
                {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
                {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
                {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
                {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
            ],
            MaxResults=1
        )

        price_list = response["PriceList"]
        if price_list:
            price_item = eval(price_list[0])
            terms = price_item["terms"]["OnDemand"]
            for term_key in terms:
                price_dimensions = terms[term_key]["priceDimensions"]
                for dim in price_dimensions:
                    price_per_hr = float(price_dimensions[dim]["pricePerUnit"]["USD"])
                    return price_per_hr
    except Exception as e:
        print(f"Error fetching AWS price: {e}")
    return None


def get_azure_price(instance_type, region):
    try:
        url = (
            f"https://prices.azure.com/api/retail/prices?"
            f"$filter=armRegionName eq '{region}' and "
            f"skuName eq '{instance_type}' and priceType eq 'Consumption'"
        )
        response = requests.get(url)
        if response.status_code == 200:
            items = response.json().get("Items", [])
            for item in items:
                if item.get("unitPrice") and item["unitPrice"] > 0:
                    return float(item["unitPrice"])
    except Exception as e:
        print(f"Azure price fetch error: {e}")
    return None


# Load VM input CSV
df = pd.read_csv("input_vms.csv")

# Mapping
df["Mapped AWS Instance"] = df["azure_instance_type"].map(instance_map)
df["Mapped AWS Region"] = df["azure_region"].map(azure_region_map)

# Pricing
df["Azure Price ($/hr)"] = df.apply(lambda x: get_azure_price(x["azure_instance_type"], x["azure_region"]), axis=1)
df["AWS Price ($/hr)"] = df.apply(lambda x: get_aws_price(x["Mapped AWS Instance"], x["Mapped AWS Region"]), axis=1)

# Monthly/Yearly calculations
HOURS_PER_MONTH = 730
df["Azure Monthly ($)"] = df["Azure Price ($/hr)"] * HOURS_PER_MONTH
df["Azure Yearly ($)"] = df["Azure Monthly ($)"] * 12
df["AWS Monthly ($)"] = df["AWS Price ($/hr)"] * HOURS_PER_MONTH
df["AWS Yearly ($)"] = df["AWS Monthly ($)"] * 12

# Output
df.to_csv("price_comparison_report_boto3.csv", index=False)
print("\n✅ price_comparison_report_boto3.csv generated successfully!")

# Display results
print("\n📌 Comparison Report Summary:")
for _, row in df.iterrows():
    print(f"\n🔹 VM: {row['name']}")
    print(f"   Azure: {row['azure_instance_type']} in {row['azure_region']} @ ${row['Azure Price ($/hr)']:.4f}/hr")
    print(f"   AWS  : {row['Mapped AWS Instance']} in {row['Mapped AWS Region']} @ ${row['AWS Price ($/hr)']:.4f}/hr")
    print(f"   Azure Monthly: ${row['Azure Monthly ($)']:.2f}, Yearly: ${row['Azure Yearly ($)']:.2f}")
    print(f"   AWS Monthly  : ${row['AWS Monthly ($)']:.2f}, Yearly: ${row['AWS Yearly ($)']:.2f}")
