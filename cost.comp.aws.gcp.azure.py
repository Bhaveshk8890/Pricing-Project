import json
import requests
import pandas as pd  # type: ignore

# Azure → AWS mapping
instance_map = {
    "Standard_A1_v2": "a1.medium",        # 1 vCPU, 2 GB
    "Standard_A2_v2": "a1.large",         # 2 vCPU, 4 GB
    "Standard_A2m_v2": "a1.xlarge",       # 2 vCPU, 16 GB
    "Standard_A4_v2": "a1.xlarge",        # 4 vCPU, 8 GB
    "Standard_A4m_v2": "a1.2xlarge",      # 4 vCPU, 32 GB
    "Standard_B2ms": "t3.medium",         # 2 vCPU, 8 GB
    "Standard_B4ms": "t3.large",          # 4 vCPU, 16 GB
    "Standard_B8ms": "t3.xlarge",         # 8 vCPU, 32 GB
    "Standard_F4s_v2": "c5.xlarge",       # 4 vCPU, 8 GB
    "Standard_F8s_v2": "c5.2xlarge",      # 8 vCPU, 16 GB
    "Standard_D2_v3": "m5.large",         # 2 vCPU, 8 GB
    "Standard_D4_v3": "m5.xlarge",        # 4 vCPU, 16 GB
    "Standard_D8_v3": "m5.2xlarge",       # 8 vCPU, 32 GB
    "Standard_D16_v3": "m5.4xlarge",      # 16 vCPU, 64 GB
    "Standard_D32_v3": "m5.8xlarge",      # 32 vCPU, 128 GB
    "Standard_D64_v3": "m5.16xlarge",     # 64 vCPU, 256 GB
    "Standard_NV6": "g4dn.xlarge",        # 6 vCPU, 56 GB, GPU
    "Standard_H8": "hpc6id.8xlarge",      # 8 vCPU, high mem/disk
    "Standard_E2s_v3": "r5.large",        # 2 vCPU, 16 GB
    "Standard_E4s_v3": "r5.xlarge",       # 4 vCPU, 32 GB
    "Standard_E8s_v3": "r5.2xlarge",      # 8 vCPU, 64 GB
    "Standard_B1s": "t3.nano",         # 1 vCPU
    "Standard_E4s_v5": "r5.xlarge",       # 4 vCPU, 32 GB
    "Standard_F8s": "c5.2xlarge",       # 8 vCPU, 16 GB

    "Standard_B1ms": "t3.micro",       # 1 vCPU
    "Standard_B2s": "t3.small",        # 2 vCPU
    "Standard_B2ms": "t3.medium",      # 2 vCPU
    "Standard_B4ms": "t3.large",       # 2 vCPU
    "Standard_B8ms": "t3.xlarge",      # 4 vCPU
    "Standard_B16ms": "t3.2xlarge",    # 8 vCPU
    "Standard_B32ms": "t3.4xlarge",    # 16 vCPU
    "Standard_E8s_v4": "r5.2xlarge",       # 8 vCPU, 64 GB
    "Standard_D2s_v3": "m5.large",         # 2 vCPU
    "Standard_D4s_v3": "m5.xlarge",        # 4 vCPU
    "Standard_D8s_v3": "m5.2xlarge",       # 8 vCPU
    "Standard_D16s_v3": "m5.4xlarge",      # 16 vCPU
    "Standard_D32s_v3": "m5.8xlarge",      # 32 vCPU
    "Standard_D48s_v3": "m5.12xlarge",     # 48 vCPU
    "Standard_D64s_v3": "m5.16xlarge",     # 64 vCPU
    "Standard_DS13_v2": "m5.4xlarge",      # 16 vCPU, 64 GB
    "Standard_H16mr": "u-3tb1.56xlarge",  # 16 vCPU, 224 GB
    "Standard_E2s_v3": "r5.large",         # 2 vCPU
    "Standard_E4s_v3": "r5.xlarge",        # 4 vCPU
    "Standard_E8s_v3": "r5.2xlarge",       # 8 vCPU
    "Standard_E16s_v3": "r5.4xlarge",      # 16 vCPU
    "Standard_E32s_v3": "r5.8xlarge",      # 32 vCPU
    "Standard_E48s_v3": "r5.12xlarge",     # 48 vCPU
    "Standard_E64s_v3": "r5.16xlarge",     # 64 vCPU

    "Standard_F2s_v2": "c5.large",         # 2 vCPU
    "Standard_F4s_v2": "c5.xlarge",        # 4 vCPU
    "Standard_F8s_v2": "c5.2xlarge",       # 8 vCPU
    "Standard_F16s_v2": "c5.4xlarge",      # 16 vCPU
    "Standard_F32s_v2": "c5.8xlarge",      # 32 vCPU
    "Standard_F48s_v2": "c5.12xlarge",     # 48 vCPU

    "Standard_L8s_v2": "i3.2xlarge",       # 8 vCPU
    "Standard_L16s_v2": "i3.4xlarge",      # 16 vCPU
    "Standard_L32s_v2": "i3.8xlarge",      # 32 vCPU

    "Standard_H8": "h1.2xlarge",           # 8 vCPU
    "Standard_H16": "h1.4xlarge",          # 16 vCPU

    "Standard_M64ms": "u-6tb1.metal",      # 64 vCPU
    "Standard_M64ls": "u-9tb1.metal",      # 64 vCPU
    "Standard_M128ms": "u-9tb1.metal",     # 128 vCPU

    "Standard_NC6": "p3.2xlarge",          # 6 vCPU
    "Standard_NC12": "p3.8xlarge",         # 12 vCPU
    "Standard_NC24": "p3.16xlarge",        # 24 vCPU

    "Standard_NV6": "g4dn.xlarge",         # 6 vCPU
    "Standard_NV12": "g4dn.2xlarge",       # 12 vCPU
    "Standard_NV24": "g4dn.4xlarge",       # 24 vCPU

#GCP to AWS instance mapping
    "e2-micro": "t3.nano",
    "e2-small": "t3.micro",
    "e2-medium": "t3.small",
    "e2-standard-2": "t3.medium",
    "e2-standard-4": "t3.xlarge",
    "e2-standard-8": "t3.2xlarge",
    "e2-highmem-2": "r5.large",
    "e2-highmem-4": "r5.xlarge",
    "n1-standard-1": "m4.large",
    "n1-standard-2": "m4.xlarge",
    "n1-standard-4": "m4.2xlarge",
    "n1-standard-8": "m4.4xlarge",
    "n1-standard-16": "m4.10xlarge",
    "n1-standard-32": "m4.16xlarge",
    "n2-standard-2": "m5.large",
    "n2-standard-4": "m5.xlarge",
    "n2-standard-8": "m5.2xlarge",
    "n2-standard-16": "m5.4xlarge",
    "n2-standard-32": "m5.8xlarge",
    "n2-standard-64": "m5.16xlarge",
    "c2-standard-4": "c5.xlarge",
    "c2-standard-8": "c5.2xlarge",
    "c2-standard-16": "c5.4xlarge",
    "c2d-standard-4": "c6a.xlarge",
    "c2d-standard-8": "c6a.2xlarge",
    "c2d-standard-16": "c6a.4xlarge",
    "c2d-standard-32": "c6a.8xlarge",
    "n2-highmem-8": "r5.2xlarge",
    "n2-highmem-16": "r5.4xlarge",
    "n2-highmem-32": "r5.8xlarge",
    "m1-megamem-96": "x1.32xlarge",
    "m2-ultramem-208": "x1e.16xlarge",
    "m2-ultramem-416": "x1e.32xlarge",
    "a2-highgpu-1g": "g4dn.xlarge",
    "a2-highgpu-2g": "g4dn.2xlarge",
    "a2-highgpu-4g": "g4dn.4xlarge",
    "a2-highgpu-8g": "g4dn.8xlarge",
    "a2-megagpu-16g": "p4d.24xlarge",
    "l2-standard-4": "i3.xlarge",
    "l2-standard-8": "i3.2xlarge",
    "l2-standard-16": "i3.4xlarge",
    "l2-standard-32": "i3.8xlarge",
    "t2d-standard-1": "t4g.small",
    "t2d-standard-2": "t4g.medium",
    "t2d-standard-4": "t4g.large",
    "t2d-standard-8": "t4g.xlarge",
    "t2d-standard-16": "t4g.2xlarge"   
}

# Azure region mapping to AWS regions
azure_region_map = {
    "eastus": "us-east-1",              # Azure East US → AWS US East (N. Virginia)
    "eastus2": "us-east-1",            # Azure East US 2 → AWS US East (N. Virginia)
    "centralus": "us-east-2",         # Azure Central US → AWS US East (Ohio)
    "northcentralus": "us-east-2",    # Azure North Central US → AWS US East (Ohio)
    "southcentralus": "us-west-2",    # Azure South Central US → AWS US West (Oregon)
    "westus": "us-west-1",            # Azure West US → AWS US West (N. California)
    "westus2": "us-west-2",           # Azure West US 2 → AWS US West (Oregon)
    "canadacentral": "ca-central-1",  # Azure Canada Central → AWS Canada (Central)
    "canadaeast": "ca-central-1",     # Azure Canada East → AWS Canada (Central)
    "brazilsouth": "sa-east-1",       # Azure Brazil South → AWS South America (São Paulo)

    "northeurope": "eu-west-1",       # Azure North Europe (Ireland) → AWS EU (Ireland)
    "westeurope": "eu-west-2",        # Azure West Europe (Netherlands) → AWS EU (London)
    "francecentral": "eu-west-3",     # Azure France Central → AWS EU (Paris)
    "germanywestcentral": "eu-central-1", # Azure Germany West Central → AWS EU (Frankfurt)
    "norwayeast": "eu-north-1",       # Azure Norway East → AWS EU (Stockholm)

    "uksouth": "eu-west-2",           # Azure UK South → AWS EU (London)
    "ukwest": "eu-west-2",            # Azure UK West → AWS EU (London)

    "switzerlandnorth": "eu-central-1", # Azure Switzerland North → AWS EU (Frankfurt)
    "switzerlandwest": "eu-central-1",  # Azure Switzerland West → AWS EU (Frankfurt)
    "eastasia": "ap-east-1",          # Azure East Asia (Hong Kong) → AWS Asia Pacific (Hong Kong)
    "southeastasia": "ap-southeast-1",# Azure Southeast Asia (Singapore) → AWS Asia Pacific (Singapore)

    "japaneast": "ap-northeast-1",    # Azure Japan East → AWS Asia Pacific (Tokyo)
    "japanwest": "ap-northeast-3",    # Azure Japan West → AWS Asia Pacific (Osaka)

    "koreacentral": "ap-northeast-2", # Azure Korea Central → AWS Asia Pacific (Seoul)
    "koreasouth": "ap-northeast-2",   # Azure Korea South → AWS Asia Pacific (Seoul)

    "australiaeast": "ap-southeast-2",# Azure Australia East → AWS Asia Pacific (Sydney)
    "australiasoutheast": "ap-southeast-2", # Azure Australia Southeast → AWS Asia Pacific (Sydney)

    "indiawest": "ap-south-1",        # Azure West India → AWS Asia Pacific (Mumbai)
    "indiasouth": "ap-south-1",       # Azure South India → AWS Asia Pacific (Mumbai)
    "indiaeast": "ap-south-1",        # Azure East India → AWS Asia Pacific (Mumbai)

    "uaenorth": "me-central-1",       # Azure UAE North → AWS Middle East (UAE)
    "uaecentral": "me-central-1",     # Azure UAE Central → AWS Middle East (UAE)

    "southafricanorth": "af-south-1", # Azure South Africa North → AWS Africa (Cape Town)
    "southafricawest": "af-south-1",  # Azure South Africa West → AWS Africa (Cape Town)

#GCP to AWS region mapping
    "asia-east1": "ap-east-1",
    "asia-east2": "ap-northeast-1",
    "asia-northeast1": "ap-northeast-1",
    "asia-northeast2": "ap-northeast-2",
    "asia-northeast3": "ap-northeast-3",
    "asia-south1": "ap-south-1",
    "asia-south2": "ap-south-2",
    "asia-southeast1": "ap-southeast-1",
    "asia-southeast2": "ap-southeast-2",
    "australia-southeast1": "ap-southeast-2",
    "australia-southeast2": "ap-southeast-4",
    "europe-central2": "eu-central-1",
    "europe-north1": "eu-north-1",
    "europe-west1": "eu-west-1",
    "europe-west2": "eu-west-2",
    "europe-west3": "eu-central-1",
    "europe-west4": "eu-west-1",
    "europe-west6": "eu-central-1",
    "europe-southwest1": "eu-south-2",
    "me-central1": "me-central-1",
    "me-west1": "me-south-1",
    "northamerica-northeast1": "ca-central-1",
    "northamerica-northeast2": "ca-central-1",
    "southamerica-east1": "sa-east-1",
    "southamerica-west1": "sa-east-1",
    "us-central1": "us-east-1",
    "us-east1": "us-east-1",
    "us-east4": "us-east-2",
    "us-west1": "us-west-1",
    "us-west2": "us-west-2",
    "us-west3": "us-west-1",
    "us-west4": "us-west-2",
    "uaenorth": "me-central-1"

}

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
            print(f"❗ No valid Azure pricing for {instance_type} in {region}")
        else:
            print(f"❌ Azure pricing API error {response.status_code} for {instance_type}")
    except Exception as e:
        print(f"❌ Azure price fetch error: {e}")
    return None

# ✅ Get AWS price
def get_aws_price(instance_type, aws_region_code):
    try:
        if pd.isna(instance_type) or pd.isna(aws_region_code):
            return None

        region_index_url = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/region_index.json"
        region_data = requests.get(region_index_url).json()

        if aws_region_code not in region_data["regions"]:
            print(f"❌ AWS region '{aws_region_code}' not found.")
            return None

        region_url = region_data["regions"][aws_region_code]["currentVersionUrl"]
        full_url = f"https://pricing.us-east-1.amazonaws.com{region_url}"
        pricing_data = requests.get(full_url).json()

        for sku, product in pricing_data["products"].items():
            attr = product.get("attributes", {})
            if (
                attr.get("instanceType") == instance_type and
                attr.get("operatingSystem") == "Linux" and
                attr.get("tenancy") == "Shared" and
                attr.get("preInstalledSw", "NA") in ["NA", ""]
            ):
                term = pricing_data["terms"]["OnDemand"].get(sku)
                if term:
                    for offer in term.values():
                        for price_dim in offer["priceDimensions"].values():
                            return float(price_dim["pricePerUnit"]["USD"])
        print(f"❗ No valid AWS pricing found for {instance_type} in {aws_region_code}")
    except Exception as e:
        print(f"❌ AWS price fetch error: {e}")
    return None

# ✅ Load input CSV
df = pd.read_csv("input_vms.csv")

# ✅ Map Azure to AWS
df["Mapped AWS Instance"] = df["azure_instance_type"].map(instance_map)
df["Mapped AWS Region"] = df["azure_region"].map(azure_region_map)

print("\n📌 Instance & Region Mapping (Azure → AWS):")
print(df[["azure_instance_type", "Mapped AWS Instance", "azure_region", "Mapped AWS Region"]])

# ✅ Get Prices
df["Azure Price ($/hr)"] = df.apply(
    lambda x: get_azure_price(x["azure_instance_type"], x["azure_region"]), axis=1
)
df["AWS Price ($/hr)"] = df.apply(
    lambda x: get_aws_price(x["Mapped AWS Instance"], x["Mapped AWS Region"]), axis=1
)

# ✅ Calculate Monthly and Yearly Costs
HOURS_PER_MONTH = 730
df["Azure Monthly ($)"] = df["Azure Price ($/hr)"] * HOURS_PER_MONTH
df["Azure Yearly ($)"] = df["Azure Monthly ($)"] * 12
df["AWS Monthly ($)"] = df["AWS Price ($/hr)"] * HOURS_PER_MONTH
df["AWS Yearly ($)"] = df["AWS Monthly ($)"] * 12


# ✅ Print Comparison
print("\n💰 Detailed Cost Comparison:")
for _, row in df.iterrows():
    print(f"\n🔹 VM: {row['name']}")
    print(f"   Azure: {row['azure_instance_type']} in {row['azure_region']}")
    if row['Azure Price ($/hr)'] is not None:
        print(f"   → Azure Hourly: ${row['Azure Price ($/hr)']:.4f}, Monthly: ${row['Azure Monthly ($)']:.2f}, Yearly: ${row['Azure Yearly ($)']:.2f}")
    else:
        print("   → Azure pricing not available.")

    print(f"   AWS: {row['Mapped AWS Instance']} in {row['Mapped AWS Region']}")
    if row['AWS Price ($/hr)'] is not None:
        print(f"   → AWS Hourly: ${row['AWS Price ($/hr)']:.4f}, Monthly: ${row['AWS Monthly ($)']:.2f}, Yearly: ${row['AWS Yearly ($)']:.2f}")
    else:
        print("   → AWS pricing not available.")

# ✅ Final report on missing prices
missing_azure = df[df["Azure Price ($/hr)"].isna()]
missing_aws = df[df["AWS Price ($/hr)"].isna()]

if not missing_azure.empty:
    print("\n⚠️ Missing Azure Prices:")
    print(missing_azure[["name", "azure_instance_type", "azure_region"]])

if not missing_aws.empty:
    print("\n⚠️ Missing AWS Prices:")
    print(missing_aws[["name", "Mapped AWS Instance", "Mapped AWS Region"]])

# ✅ Export final CSV
df.to_csv("price_comparison_report.csv", index=False)
print("\n✅ Report saved to 'price_comparison_report.csv'")