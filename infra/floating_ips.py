import pulumi
import pulumi_openstack as openstack


# External network pool name on Felcloud (used for floating IP allocation)
INTERNET_POOL = "INTERNET"


# ==========================
# Bastion Floating IP
# ==========================
# Address:      197.5.133.81
# Fixed IP:     192.168.100.90
# OpenStack ID: 65dd4118-78e3-4165-bb16-f028aa8cea70
#
# Import command:
#   pulumi import openstack:networking/floatingIp:FloatingIp bastion-floating-ip 65dd4118-78e3-4165-bb16-f028aa8cea70

bastion_floating_ip = openstack.networking.FloatingIp(
    "bastion-floating-ip",

    pool=INTERNET_POOL,

    address="197.5.133.81",

    opts=pulumi.ResourceOptions(
        protect=True,
        # pool and address are set at allocation time; ignore to prevent drift
        ignore_changes=["pool", "address"],
    )
)


# ==========================
# App VM 1 Floating IP
# ==========================
# Address:      197.5.133.14
# Fixed IP:     192.168.100.202
# OpenStack ID: 718d4612-b1a4-42a1-b07b-04d11d3ec35f
#
# Import command:
#   pulumi import openstack:networking/floatingIp:FloatingIp app-vm-1-floating-ip 718d4612-b1a4-42a1-b07b-04d11d3ec35f

app_vm_1_floating_ip = openstack.networking.FloatingIp(
    "app-vm-1-floating-ip",

    pool=INTERNET_POOL,

    address="197.5.133.14",

    opts=pulumi.ResourceOptions(
        protect=True,
        ignore_changes=["pool", "address"],
    )
)


# ==========================
# App VM 2 Floating IP
# ==========================
# Address:      197.5.133.228
# Fixed IP:     192.168.100.161
# OpenStack ID: e28b5e39-09b7-4635-87e9-cd8bda2de32f
#
# Import command:
#   pulumi import openstack:networking/floatingIp:FloatingIp app-vm-2-floating-ip e28b5e39-09b7-4635-87e9-cd8bda2de32f

app_vm_2_floating_ip = openstack.networking.FloatingIp(
    "app-vm-2-floating-ip",

    pool=INTERNET_POOL,

    address="197.5.133.228",

    opts=pulumi.ResourceOptions(
        protect=True,
        ignore_changes=["pool", "address"],
    )
)


# ==========================
# Database Floating IP
# ==========================
# Address:      197.5.133.4
# Fixed IP:     192.168.100.25
# OpenStack ID: af113dae-ac15-433b-9461-ebbe7a9ad172
#
# Import command:
#   pulumi import openstack:networking/floatingIp:FloatingIp db-floating-ip af113dae-ac15-433b-9461-ebbe7a9ad172

db_floating_ip = openstack.networking.FloatingIp(
    "db-floating-ip",

    pool=INTERNET_POOL,

    address="197.5.133.4",

    opts=pulumi.ResourceOptions(
        protect=True,
        ignore_changes=["pool", "address"],
    )
)