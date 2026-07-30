import pulumi
import pulumi_openstack as openstack


# ==========================
# Bastion Root Volume
# ==========================
# Existing volume — do NOT create, use `pulumi import` to adopt.
# OpenStack ID:   5873bb8a-7142-4a17-a81b-58d19473f7b4
# OpenStack Name: (empty — no name assigned in OpenStack)
# Size:           20 GB
# Attached to:    Pulumis-Bastion on /dev/vda
#
# Import command:
#   pulumi import openstack:blockstorage/volume:Volume bastion-root-volume 5873bb8a-7142-4a17-a81b-58d19473f7b4

bastion_root_volume = openstack.blockstorage.Volume(
    "bastion-root-volume",

    # Volume has no name in OpenStack — do not set a name to avoid drift.
    # name is also in ignore_changes as a safety net.

    size=20,

    volume_type="HDD",

    availability_zone="TN-Carthage",

    # Volume has no description in OpenStack.
    description="",

    opts=pulumi.ResourceOptions(
        protect=True,
        ignore_changes=[
            "image_id",     # set at creation only; not returned consistently
            "snapshot_id",  # not applicable
            "description",  # stored as empty in OpenStack
            "name",         # volume has no name in OpenStack
        ],
    )
)


# ==========================
# Database Root Volume
# ==========================
# Existing volume — do NOT create, use `pulumi import` to adopt.
# OpenStack ID:   ce0bd1a5-13f7-466b-b9f9-95a9f429f3c4
# OpenStack Name: (empty — no name assigned in OpenStack)
# Size:           20 GB
# Attached to:    pulumis-db-vm on /dev/vda
#
# Import command:
#   pulumi import openstack:blockstorage/volume:Volume db-root-volume ce0bd1a5-13f7-466b-b9f9-95a9f429f3c4

db_root_volume = openstack.blockstorage.Volume(
    "db-root-volume",

    # Volume has no name in OpenStack — do not set a name to avoid drift.

    size=20,

    volume_type="HDD",

    availability_zone="TN-Carthage",

    # Volume has no description in OpenStack.
    description="",

    opts=pulumi.ResourceOptions(
        protect=True,
        ignore_changes=[
            "image_id",
            "snapshot_id",
            "description",
            "name",
        ],
    )
)