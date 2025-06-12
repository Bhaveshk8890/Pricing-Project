from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

def get_azure_vms(subscription_id):
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)
    vms = []

    for vm in compute_client.virtual_machines.list_all():
        vms.append({
            "name": vm.name,
            "location": vm.location,
            "vm_size": vm.hardware_profile.vm_size
        })

    return vms
