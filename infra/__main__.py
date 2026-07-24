import pulumi

from network import private_network, private_subnet

from security import (
    app_security_group,
    db_security_group,
    lb_security_group,
    bastion_security_group
)

from compute import (
    app_vm_1,
    app_vm_2,
    db_vm,
    app_port_1,
    app_port_2,
    db_port
)

from bastion import (
    bastion,
    bastion_port,
    bastion_fip,
    bastion_fip_association,
    bastion_floating_ip
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

pulumi.export(
    "bastion_security_group_id",
    bastion_security_group.id
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
    "app_port_1_id",
    app_port_1.id
)

pulumi.export(
    "app_port_2_id",
    app_port_2.id
)

pulumi.export(
    "db_port_id",
    db_port.id
)

pulumi.export(
    "bastion_vm_id",
    bastion.id
)

pulumi.export(
    "bastion_port_id",
    bastion_port.id
)

pulumi.export(
    "bastion_floating_ip_id",
    bastion_fip.id if bastion_fip else None
)

pulumi.export(
    "bastion_floating_ip_association_id",
    bastion_fip_association.id if bastion_fip_association else None
)

pulumi.export(
    "bastion_floating_ip",
    bastion_floating_ip
)


# ==========================
# Storage exports
# ==========================

pulumi.export(
    "db_volume_id",
    db_volume.id
)
