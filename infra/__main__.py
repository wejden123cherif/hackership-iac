import pulumi


# ==========================
# Network
# ==========================

from network import (
    hackership_network,
    hackership_subnet
)


# ==========================
# Security Groups
# ==========================

from security import (
    all_open
)


# ==========================
# Compute
# ==========================

from compute import (
    app_vm_1,
    app_vm_2,
    db_vm,
    bastion
)


# ==========================
# Storage
# ==========================

from storage import (
    db_root_volume,
    bastion_root_volume
)


# ==========================
# Floating IPs
# ==========================

from floating_ips import (
    bastion_floating_ip,
    app_vm_1_floating_ip,
    app_vm_2_floating_ip,
    db_floating_ip
)


# ==========================
# Network exports
# ==========================

pulumi.export(
    "network_id",
    hackership_network.id
)

pulumi.export(
    "subnet_id",
    hackership_subnet.id
)


# ==========================
# Security exports
# ==========================

pulumi.export(
    "security_group_id",
    all_open.id
)


# ==========================
# Compute exports
# ==========================

pulumi.export(
    "app_vm_1_id",
    app_vm_1.id
)

pulumi.export(
    "app_vm_2_id",
    app_vm_2.id
)

pulumi.export(
    "db_vm_id",
    db_vm.id
)

pulumi.export(
    "bastion_vm_id",
    bastion.id
)


# ==========================
# Storage exports
# ==========================

pulumi.export(
    "db_root_volume_id",
    db_root_volume.id
)

pulumi.export(
    "bastion_root_volume_id",
    bastion_root_volume.id
)


# ==========================
# Floating IP exports
# ==========================

pulumi.export(
    "bastion_floating_ip",
    bastion_floating_ip.address
)

pulumi.export(
    "app_vm_1_floating_ip",
    app_vm_1_floating_ip.address
)

pulumi.export(
    "app_vm_2_floating_ip",
    app_vm_2_floating_ip.address
)

pulumi.export(
    "db_floating_ip",
    db_floating_ip.address
)