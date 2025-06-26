import boto3
import pandas as pd

# Constants
HOURS_PER_MONTH = 730
MONTHS_PER_YEAR = 12

# Mapping dictionaries
instance_map = {
    "Standard_F4s_v2": "c5.xlarge",
    "Standard_F8s_v2": "c5.2xlarge",
    "Standard_D4s_v3": "t3.xlarge",
    "Standard_D8s_v3": "t3.2xlarge",
    "Standard_F2s_v2": "c5.large",
    "Standard_B2ms": "t3.medium",
    "Standard_D2s_v3": "t3.large",
    "Standard_E4s_v3": "m5.xlarge",
    "Standard_E8s_v3": "m5.2xlarge",
    "Standard_F16s_v2": "c5.4xlarge",
    "Standard_F32s_v2": "c5.9xlarge",
    "Standard_F48s_v2": "c5.12xlarge",
}

azure_region_map = {
    "eastus": "US East (N. Virginia)",
    "westeurope": "EU (Ireland)",
    "southeastasia": "Asia Pacific (Singapore)",
    "centralus": "US West (Oregon)",
    "uksouth": "EU (London)",
    "japaneast": "Asia Pacific (Tokyo)",
}

# Read input CSV
df = pd.read_csv("input_vms.csv")

# Apply mappings
df["Mapped AWS Instance"] = df["azure_instance_type"].map(instance_map)
df["Mapped AWS Region"] = df["azure_region"].map(azure_region_map)

# Check for unmapped entries
invalid_mappings = df[df["Mapped AWS Instance"].isna() | df["Mapped AWS Region"].isna()]
if not invalid_mappings.empty:
    print("⚠️ Unmapped instances or regions:\n", invalid_mappings[["name", "azure_instance_type", "azure_region"]])

# Boto3 pricing call
def is_valid_string(val):
    return isinstance(val, str) and val.lower() != "nan"

def get_savings_plan_price(instance_type, region):
    if not is_valid_string(instance_type) or not is_valid_string(region):
        return None

    client = boto3.client("pricing", region_name="us-east-1")
    try:
        response = client.get_products(
            ServiceCode="AmazonEC2",
            Filters=[
                {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
                {"Type": "TERM_MATCH", "Field": "location", "Value": region},
                {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
                {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
                {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
                {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
            ],
            MaxResults=1,
        )
        for price_item in response["PriceList"]:
            item = eval(price_item)
            terms = item["terms"]["OnDemand"]
            for sku in terms:
                for dim in terms[sku]["priceDimensions"]:
                    return float(terms[sku]["priceDimensions"][dim]["pricePerUnit"]["USD"])
    except Exception as e:
        print(f"[❌] Failed to get Savings Plan price for {instance_type} in {region}: {e}")
    return None

# Get prices
df["AWS Price ($/hr)"] = df.apply(
    lambda row: get_savings_plan_price(row["Mapped AWS Instance"], row["Mapped AWS Region"]), axis=1
)

# Monthly & Yearly calculations
df["AWS Monthly ($)"] = df["AWS Price ($/hr)"] * HOURS_PER_MONTH
df["AWS Yearly ($)"] = df["AWS Monthly ($)"] * MONTHS_PER_YEAR

# Print comparison
for _, row in df.iterrows():
    print(f"\n🔹 VM: {row['name']}")
    print(f"   Azure Instance: {row['azure_instance_type']} in {row['azure_region']}")
    print(f"   Mapped to AWS: {row['Mapped AWS Instance']} in {row['Mapped AWS Region']}")
    print(f"   → AWS Hourly: ${row['AWS Price ($/hr)']:.4f}, Monthly: ${row['AWS Monthly ($)']:.2f}, Yearly: ${row['AWS Yearly ($)']:.2f}")

# Save report
df.to_csv("compute_savings_plan_report.csv", index=False)
print("✅ Report saved as compute_savings_plan_report.csv")
