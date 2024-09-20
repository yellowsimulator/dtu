
"""
A code to provision the VM.
The base code was taken from the Azure documentation page:
https://learn.microsoft.com/en-us/azure/developer/python/sdk/examples/azure-sdk-example-virtual-machines?tabs=cmd
"""

# Import the needed credential and management objects from the libraries.
import os

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient

# Read parameters and credentials
RESOURCE_GROUP_NAME = os.environ["RESOURCE_GROUP_NAME"]
LOCATION = os.environ["LOCATION"]
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
VNET_NAME = os.environ["VNET_NAME"]
SUBNET_NAME = os.environ["SUBNET_NAME"]
IP_NAME = os.environ["IP_NAME"]
IP_CONFIG_NAME = os.environ["IP_CONFIG_NAME"]
NIC_NAME = os.environ["NIC_NAME"]
VM_NAME = os.environ["VM_NAME"]
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]

print(
    "Provisioning a virtual machine...some operations might take a \
minute or two."
)

# Acquire a credential object.
credential = DefaultAzureCredential()

# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]


# Step 1: Provision a resource group

# Obtain the management object for resources.
resource_client = ResourceManagementClient(credential, subscription_id)


# Obtain the management object for networks
network_client = NetworkManagementClient(credential, subscription_id)

# Provision the virtual network and wait for completion
poller = network_client.virtual_networks.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
        "location": LOCATION,
        "address_space": {"address_prefixes": ["10.0.0.0/16"]},
    },
)

vnet_result = poller.result()

print(
    f"Provisioned virtual network {vnet_result.name} with address \
prefixes {vnet_result.address_space.address_prefixes}"
)

#--------------------------------------------------------------------------
# Step 3: Provision the subnet and wait for completion
# Step 3.1: Provision a Network Security Group
NSG_NAME = "nsg-Yapi-Donatien-Achou"
poller = network_client.network_security_groups.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    NSG_NAME,
    {
        "location": LOCATION,
        "security_rules": [
            {
                "name": "AllowSSH",
                "properties": {
                    "protocol": "Tcp",
                    "SourcePortRange": "*",
                    "DestinationPortRange": "22",
                    "SourceAddressPrefix": "*",
                    "DestinationAddressPrefix": "*",
                    "Access": "Allow",
                    "Priority": 3400,
                    "Direction": "Inbound",
                },
            }
        ],
    },
)

nsg_result = poller.result()
print(f"Provisioned Network Security Group {nsg_result.name}")

poller = network_client.subnets.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    SUBNET_NAME,
    {"address_prefix": "10.0.0.0/24",
     "network_security_group": {
            "id": nsg_result.id 
        }

     
     },
)
subnet_result = poller.result()

print(
    f"Provisioned virtual subnet {subnet_result.name} with address \
prefix {subnet_result.address_prefix}"
)

#---------------------------------------------------------------------
# Step 4: Provision an IP address and wait for completion
poller = network_client.public_ip_addresses.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    IP_NAME,
    {
        "location": LOCATION,
        "sku": {"name": "Standard"},
        "public_ip_allocation_method": "Static",
        "public_ip_address_version": "IPV4",
    },
)

ip_address_result = poller.result()

print(
    f"Provisioned public IP address {ip_address_result.name} \
with address {ip_address_result.ip_address}"
)

#-----------------------------------------------------------------
# Step 5: Provision the network interface client
poller = network_client.network_interfaces.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    NIC_NAME,
    {
        "location": LOCATION,
        "ip_configurations": [
            {
                "name": IP_CONFIG_NAME,
                "subnet": {"id": subnet_result.id},
                "public_ip_address": {"id": ip_address_result.id},
            }
        ],
    },
)

nic_result = poller.result()

print(f"Provisioned network interface client {nic_result.name}")

#--------------------------------------------------------------------------------
# Step 6: Provision the virtual machine
# Obtain the management object for virtual machines
compute_client = ComputeManagementClient(credential, subscription_id)


print(
    f"Provisioning virtual machine {VM_NAME}; this operation might \
take a few minutes."
)

# Provision the VM specifying only minimal arguments, which defaults
# to an Ubuntu 18.04 VM on a Standard DS1 v2 plan with a public IP address
# and a default virtual network/subnet.

poller = compute_client.virtual_machines.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VM_NAME,
    {
        "location": LOCATION,
        "storage_profile": {
            "image_reference": {
                "publisher": "Canonical",
                "offer": "UbuntuServer",
                "sku": "16.04.0-LTS",
                "version": "latest",
            }
        },
        "hardware_profile": {"vm_size": "Standard_DS1_v2"},
        "os_profile": {
            "computer_name": VM_NAME,
            "admin_username": USERNAME,
            "admin_password": PASSWORD,
        },
        "network_profile": {
            "network_interfaces": [
                {
                    "id": nic_result.id,
                }
            ]
        },
    },
)

vm_result = poller.result()

print(f"Provisioned virtual machine {vm_result.name}")