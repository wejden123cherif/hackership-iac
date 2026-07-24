import pulumi
import pulumi_openstack as openstack

from pathlib import Path
from network import private_network
from security import app_security_group, db_security_group
from storage import db_volume


# ==========================
# Cloud-init
# ==========================

common_userdata = Path(
    "cloud_init/common.yaml"
).read_text()


# ==========================
# Configuration
# ==========================

ubuntu_image = "a049a501-f812-4e6c-9c07-61aa3b08bb50"

app_flavor = "1004"   # 2 vCPU / 4GB RAM
db_flavor = "1005"    # 2 vCPU / 8GB RAM


config = pulumi.Config()
keypair = config.require("keypair")


# ==========================
# Application VM Ports
# ==========================

app_port_1 = openstack.networking.Port(
    "app-vm-1-port",
    network_id=private_network.id,
    security_group_ids=[
        app_security_group.id
    ]
)


app_port_2 = openstack.networking.Port(
    "app-vm-2-port",
    network_id=private_network.id,
    security_group_ids=[
        app_security_group.id
    ]
)


# ==========================
# Database VM Port
# ==========================

db_port = openstack.networking.Port(
    "db-vm-port",
    network_id=private_network.id,
    security_group_ids=[
        db_security_group.id
    ]
)


# ==========================
# Application VM 1
# ==========================

app_vm_1 = openstack.compute.Instance(
    "app-vm-1",

    name="app-vm-1",

    image_id=ubuntu_image,
    flavor_id=app_flavor,

    key_pair=keypair,

    # Enable config drive for cloud-init metadata
    config_drive=True,

    # Cloud-init script
    user_data=common_userdata,

    networks=[
        {
            "port": app_port_1.id
        }
    ]
)


# ==========================
# Application VM 2
# ==========================

app_vm_2 = openstack.compute.Instance(
    "app-vm-2",

    name="app-vm-2",

    image_id=ubuntu_image,
    flavor_id=app_flavor,

    key_pair=keypair,

    config_drive=True,

    user_data=common_userdata,

    networks=[
        {
            "port": app_port_2.id
        }
    ]
)


# ==========================
# Database VM
# ==========================

db_vm = openstack.compute.Instance(
    "db-vm",

    name="db-vm",

    image_id=ubuntu_image,
    flavor_id=db_flavor,

    key_pair=keypair,

    config_drive=True,

    user_data=common_userdata,

    networks=[
        {
            "port": db_port.id
        }
    ]
)


# ==========================
# Attach DB Persistent Volume
# ==========================

db_volume_attachment = openstack.compute.VolumeAttach(
    "db-volume-attachment",

    instance_id=db_vm.id,
    volume_id=db_volume.id
)


# ==========================
# Exports
# ==========================

pulumi.export("app_vm_1_id", app_vm_1.id)
pulumi.export("app_vm_2_id", app_vm_2.id)
pulumi.export("db_vm_id", db_vm.id)

pulumi.export("app_port_1_id", app_port_1.id)
pulumi.export("app_port_2_id", app_port_2.id)
pulumi.export("db_port_id", db_port.id)
