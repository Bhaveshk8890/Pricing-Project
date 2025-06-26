import requests
import pandas as pd

# Mapping Azure VM sizes to AWS EC2 instances
instance_map = {
    "Standard_B1ms": "t3.micro",
    "Standard_B2ms": "t3.medium",
    "Standard_B4ms": "t3.large",
    "Standard_B8ms": "t3.xlarge"
}

def get_azure_price(instance_type, region):
    url = f"https://prices.azure.com/api/retail/prices?$filter=armRegionName eq '{region}' and skuName eq '{instance_type}' and priceType eq 'Consumption'"
    try:
        response = requests.get(url).json()
        if "Items" in response and response["Items"]:
            return float(response["Items"][0]["unitPrice"])
    except Exception as e:
        print("Azure pricing error:", e)
    return None

def get_aws_price(instance_type, region="us-east-1"):
    pricing_url = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json"
    try:
        data = requests.get(pricing_url).json()
        for sku, product in data["products"].items():
            attr = product["attributes"]
            if (
                attr.get("instanceType") == instance_type and
                attr.get("location") == "US East (N. Virginia)" and
                attr.get("operatingSystem") == "Linux" and
                attr.get("tenancy") == "Shared" and
                attr.get("preInstalledSw") == "NA"
            ):
                sku_terms = data["terms"]["OnDemand"].get(sku)
                if sku_terms:
                    for term_id, term_data in sku_terms.items():
                        for price_id, price_data in term_data["priceDimensions"].items():
                            return float(price_data["pricePerUnit"]["USD"])
    except Exception as e:
        print("AWS pricing error:", e)
    return None

# Load input
df = pd.read_csv("input_vms.csv")

# Fetch prices
df["Mapped AWS Instance"] = df["azure_instance_type"].map(instance_map)
df["Azure Price ($/hr)"] = df.apply(lambda x: get_azure_price(x["azure_instance_type"], x["azure_region"]), axis=1)
df["AWS Price ($/hr)"] = df["Mapped AWS Instance"].apply(lambda x: get_aws_price(x))

# Save output
df.to_csv("price_comparison_report.csv", index=False)
print("✅ price_comparison_report.csv generated")
