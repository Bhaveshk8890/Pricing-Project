import boto3
import json

def get_ec2_price(instance_type, region="US East (N. Virginia)"):
    client = boto3.client("pricing", region_name="us-east-1")
    response = client.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
            {"Type": "TERM_MATCH", "Field": "location", "Value": region},
            {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
            {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
            {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
            {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"}
        ],
        FormatVersion='aws_v1',
        MaxResults=1
    )

    if response["PriceList"]:
        price_item = json.loads(response["PriceList"][0])
        ondemand_price = list(price_item["terms"]["OnDemand"].values())[0]
        price_dimensions = list(ondemand_price["priceDimensions"].values())[0]
        return float(price_dimensions["pricePerUnit"]["USD"])
    return None
