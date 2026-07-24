import pulumi
import pulumi_openstack as openstack

from pathlib import Path
from network import private_network
from security import bastion_security_group


# ==========================
# Configuration
# ==========================

ubuntu_image = "a049a501-f812-4e6c-9c07-61aa3b08bb50"
bastion_flavor = "1004"

config = pulumi.Config()
keypair = config.require("keypair")
create_bastion_fip = config.get_bool("createBastionFloatingIp") or False
bastion_floating_ip_address = config.get("bastionFloatingIpAddress")


# ==========================
# Cloud-init
# ==========================

bastion_userdata = Path(
    "cloud_init/bastion.yaml"
).read_text()


# ==========================
# Create a port for the bastion
# ==========================
bastion_port = openstack.networking.Port(
    "bastion-port",

    network_id=private_network.id,

    security_group_ids=[
        bastion_security_group.id
    ]
)
# attach the port 
bastion = openstack.compute.Instance(
    "bastion-vm",

    name="bastion-vm",

    image_id=ubuntu_image,

    flavor_id=bastion_flavor,

    key_pair=keypair,

    config_drive=True,

    user_data=bastion_userdata,

    networks=[
        {
            "port": bastion_port.id
        }
    ]
)

bastion_fip = None
bastion_fip_association = None
bastion_floating_ip = bastion_floating_ip_address

if bastion_floating_ip_address:
    bastion_fip_association = openstack.networking.FloatingIpAssociate(
        "bastion-fip-associate",
        floating_ip=bastion_floating_ip_address,
        port_id=bastion_port.id
    )
elif create_bastion_fip:
    bastion_fip = openstack.networking.FloatingIp(
        "bastion-floating-ip",
        pool="INTERNET"
    )

    bastion_fip_association = openstack.networking.FloatingIpAssociate(
        "bastion-fip-associate",
        floating_ip=bastion_fip.address,
        port_id=bastion_port.id
    )

    bastion_floating_ip = bastion_fip.address
