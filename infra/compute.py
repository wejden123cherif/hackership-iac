import pulumi
import pulumi_openstack as openstack

from network import hackership_network


# ==========================
# App VM 1
# ==========================
# Existing instance — do NOT create, use `pulumi import` to adopt.
# OpenStack name: Pulumis-app-vm-1
# OpenStack ID:   23a7599c-ce2a-44ba-990e-93c6302b5235
# Boot:           Image (Ubuntu 24.04 LTS - Noble Numbat)
# Flavor:         G0.basic.2c4g
#
# Import command:
#   pulumi import openstack:compute/instance:Instance app-vm-1 23a7599c-ce2a-44ba-990e-93c6302b5235

app_vm_1 = openstack.compute.Instance(
    "app-vm-1",

    # Must match the EXACT name in OpenStack
    name="Pulumis-app-vm-1",

    flavor_name="G0.basic.2c4g",

    key_pair="test",

    availability_zone="TN-Carthage",

    security_groups=[
        "all_open"
    ],

    networks=[
        openstack.compute.InstanceNetworkArgs(
            uuid=hackership_network.id
        )
    ],

    opts=pulumi.ResourceOptions(
        protect=True,
        # image_id is set at boot time only — ignore to prevent false replacement.
        # user_data is injected at creation only — not returned by OpenStack API afterwards.
        # block_devices not specified (ephemeral boot from image); ignore in case state differs.
        ignore_changes=["image_id", "block_devices", "user_data"],
    )
)


# ==========================
# App VM 2
# ==========================
# Existing instance — do NOT create, use `pulumi import` to adopt.
# OpenStack name: Pulumis-app-vm-2
# OpenStack ID:   e24e7cfd-5fe8-45e3-b9a4-08d83bb8ae60
# Boot:           Image (Ubuntu 24.04 LTS - Noble Numbat)
# Flavor:         G0.basic.2c4g
#
# Import command:
#   pulumi import openstack:compute/instance:Instance app-vm-2 e24e7cfd-5fe8-45e3-b9a4-08d83bb8ae60

app_vm_2 = openstack.compute.Instance(
    "app-vm-2",

    # Must match the EXACT name in OpenStack
    name="Pulumis-app-vm-2",

    flavor_name="G0.basic.2c4g",

    key_pair="test",

    availability_zone="TN-Carthage",

    security_groups=[
        "all_open"
    ],

    networks=[
        openstack.compute.InstanceNetworkArgs(
            uuid=hackership_network.id
        )
    ],

    opts=pulumi.ResourceOptions(
        protect=True,
        ignore_changes=["image_id", "block_devices", "user_data"],
    )
)


# ==========================
# Bastion
# ==========================
# Existing instance — do NOT create, use `pulumi import` to adopt.
# OpenStack name: Pulumis-Bastion
# OpenStack ID:   80eed15f-45e5-4a5c-8f99-a387ff121e61
# Boot:           Volume (5873bb8a-7142-4a17-a81b-58d19473f7b4)
# Flavor:         G0.basic.1c1g
#
# Import command:
#   pulumi import openstack:compute/instance:Instance bastion 80eed15f-45e5-4a5c-8f99-a387ff121e61

bastion = openstack.compute.Instance(
    "bastion",

    # Must match the EXACT name in OpenStack
    name="Pulumis-Bastion",

    flavor_name="G0.basic.1c1g",

    key_pair="test",

    availability_zone="TN-Carthage",

    security_groups=[
        "all_open"
    ],

    # Bastion boots from an existing persistent volume — NOT from an image disk.
    # The volume UUID must NOT change.
    block_devices=[
        openstack.compute.InstanceBlockDeviceArgs(
            uuid="5873bb8a-7142-4a17-a81b-58d19473f7b4",
            source_type="volume",
            destination_type="volume",
            boot_index=0,
            delete_on_termination=False,
        )
    ],

    networks=[
        openstack.compute.InstanceNetworkArgs(
            uuid=hackership_network.id
        )
    ],

    opts=pulumi.ResourceOptions(
        protect=True,
        # block_devices: Pulumi computes a different representation after import
        # vs what OpenStack API returns. Ignoring prevents spurious replace.
        ignore_changes=["image_id", "user_data", "block_devices"],
    )
)


# ==========================
# Database VM
# ==========================
# Existing instance — do NOT create, use `pulumi import` to adopt.
# OpenStack name: pulumis-db-vm
# OpenStack ID:   a27d46dd-d678-488d-9594-21311bb34c0f
# Boot:           Volume (ce0bd1a5-13f7-466b-b9f9-95a9f429f3c4)
# Flavor:         G0.basic.1c1g
#
# Import command:
#   pulumi import openstack:compute/instance:Instance db-vm a27d46dd-d678-488d-9594-21311bb34c0f

db_vm = openstack.compute.Instance(
    "db-vm",

    # Must match the EXACT name in OpenStack
    name="pulumis-db-vm",

    flavor_name="G0.basic.1c1g",

    key_pair="test",

    availability_zone="TN-Carthage",

    security_groups=[
        "all_open"
    ],

    # DB VM boots from an existing persistent volume — NOT from an image disk.
    # The volume UUID must NOT change.
    block_devices=[
        openstack.compute.InstanceBlockDeviceArgs(
            uuid="ce0bd1a5-13f7-466b-b9f9-95a9f429f3c4",
            source_type="volume",
            destination_type="volume",
            boot_index=0,
            delete_on_termination=False,
        )
    ],

    networks=[
        openstack.compute.InstanceNetworkArgs(
            uuid=hackership_network.id
        )
    ],

    opts=pulumi.ResourceOptions(
        protect=True,
        # block_devices: Pulumi computes a different representation after import
        # vs what OpenStack API returns. Ignoring prevents spurious replace.
        ignore_changes=["image_id", "user_data", "block_devices"],
    )
)