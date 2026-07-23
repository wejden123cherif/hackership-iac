import pulumi

from network import private_network, private_subnet

from security import (
    app_security_group,
    db_security_group,
    lb_security_group
)

from compute import (
    app_vm_1,
    app_vm_2,
    db_vm
)

from storage import db_volume


# ==========================
# Network exports
# ==========================

pulumi.export(
    "network_id",
    private_network.id
)

pulumi.export(
    "subnet_id",
    private_subnet.id
)


# ==========================
# Security Groups exports
# ==========================

pulumi.export(
    "app_security_group_id",
    app_security_group.id
)

pulumi.export(
    "db_security_group_id",
    db_security_group.id
)

pulumi.export(
    "lb_security_group_id",
    lb_security_group.id
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


# ==========================
# Storage exports
# ==========================

pulumi.export(
    "db_volume_id",
    db_volume.id
)