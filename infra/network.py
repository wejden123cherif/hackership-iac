import pulumi
import pulumi_openstack as openstack

# Lookup existing network
private_network = openstack.networking.get_network(
    name="private_network"
)

# Lookup existing subnet
private_subnet = openstack.networking.get_subnet(
    name="private_subnet"
)