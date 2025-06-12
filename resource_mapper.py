import json

def map_azure_to_aws(azure_resources, mapping_file='config/mapping_rules.json'):
    with open(mapping_file) as f:
        mappings = json.load(f)

    aws_equivalents = []
    for resource in azure_resources:
        azure_type = resource["vm_size"]
        aws_type = mappings.get(azure_type)
        if aws_type:
            aws_equivalents.append({
                "azure_name": resource["name"],
                "azure_type": azure_type,
                "aws_instance": aws_type
            })
    return aws_equivalents
