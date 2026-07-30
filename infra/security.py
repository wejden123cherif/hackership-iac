import pulumi
import pulumi_openstack as openstack


# ==========================
# all_open Security Group
# ==========================
# Existing security group used by all Hackership VMs.
# OpenStack ID: 3158e473-f869-42f1-a866-0fc8b0f87d17
#
# Import command:
#   pulumi import openstack:networking/secGroup:SecGroup all-open 3158e473-f869-42f1-a866-0fc8b0f87d17

all_open = openstack.networking.SecGroup(
    "all-open",

    name="all_open",

    # OpenStack stores an empty description for this group.
    # Must match exactly to avoid spurious update diff.
    description="",

    opts=pulumi.ResourceOptions(
        protect=True,
        ignore_changes=["description"],  # prevent drift if description ever changes in OpenStack
    )
)