import pulumi_openstack as openstack

# ==========================
# Network (lookup only)
# ==========================
# The hackership network already exists in OpenStack.
# We use get_* lookups here because the network is NOT managed
# by this Pulumi stack — it is only referenced by compute resources.
# Do NOT import or recreate the network through this stack.

hackership_network = openstack.networking.get_network(
    name="hackership"
)

hackership_subnet = openstack.networking.get_subnet(
    name="sub_hackership"
)