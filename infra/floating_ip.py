import pulumi_openstack as openstack

from compute import app_port_1


# ==========================
# Create Floating IP
# ==========================

app_fip = openstack.networking.FloatingIp(
    "app-floating-ip",
    pool="INTERNET"
)


# ==========================
# Associate Floating IP
# ==========================

app_fip_association = openstack.networking.FloatingIpAssociate(
    "app-fip-association",
    floating_ip=app_fip.address,
    port_id=app_port_1.id
)


# Export value for main.py
floating_ip = app_fip.address