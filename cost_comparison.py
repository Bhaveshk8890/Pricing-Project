from azure_inventory import get_azure_vms
from resource_mapper import map_azure_to_aws
from aws_pricing import get_ec2_price
import pandas as pd

def generate_cost_report(subscription_id):
    azure_resources = get_azure_vms(subscription_id)
    aws_mapped = map_azure_to_aws(azure_resources)

    results = []
    for res in aws_mapped:
        aws_cost = get_ec2_price(res["aws_instance"])
        results.append({
            "Azure VM": res["azure_name"],
            "Azure VM Type": res["azure_type"],
            "AWS Equivalent": res["aws_instance"],
            "AWS Hourly Cost (USD)": aws_cost
        })

    df = pd.DataFrame(results)
    df.to_csv("output/cost_report.csv", index=False)
    print("✅ Cost report generated: output/cost_report.csv")

# Example Run
if __name__ == "__main__":
    subscription_id = "84f7ce89-8e23-4da8-ae8b-c8c99d5eba51"
    generate_cost_report(subscription_id)
