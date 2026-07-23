import pulumi_openstack as openstack


# ==========================
# Load Balancer Security Group
# ==========================

lb_security_group = openstack.networking.SecGroup(
    "lb-security-group",
    name="lb-security-group",
    description="Security group for load balancer"
)


# HTTP from Internet
lb_http_rule = openstack.networking.SecGroupRule(
    "lb-http-rule",
    security_group_id=lb_security_group.id,
    direction="ingress",
    ethertype="IPv4",
    protocol="tcp",
    port_range_min=80,
    port_range_max=80,
    remote_ip_prefix="0.0.0.0/0"
)


# HTTPS from Internet
lb_https_rule = openstack.networking.SecGroupRule(
    "lb-https-rule",
    security_group_id=lb_security_group.id,
    direction="ingress",
    ethertype="IPv4",
    protocol="tcp",
    port_range_min=443,
    port_range_max=443,
    remote_ip_prefix="0.0.0.0/0"
)



# ==========================
# Application Security Group
# ==========================

app_security_group = openstack.networking.SecGroup(
    "app-security-group",
    name="app-security-group",
    description="Security group for application servers"
)


# SSH access (temporary for development)
app_ssh_rule = openstack.networking.SecGroupRule(
    "app-ssh-rule",
    security_group_id=app_security_group.id,
    direction="ingress",
    ethertype="IPv4",
    protocol="tcp",
    port_range_min=22,
    port_range_max=22,
    remote_ip_prefix="0.0.0.0/0"
)


# HTTP ONLY from Load Balancer
app_http_rule = openstack.networking.SecGroupRule(
    "app-http-rule",
    security_group_id=app_security_group.id,
    direction="ingress",
    ethertype="IPv4",
    protocol="tcp",
    port_range_min=80,
    port_range_max=80,
    remote_group_id=lb_security_group.id
)


# HTTPS ONLY from Load Balancer
app_https_rule = openstack.networking.SecGroupRule(
    "app-https-rule",
    security_group_id=app_security_group.id,
    direction="ingress",
    ethertype="IPv4",
    protocol="tcp",
    port_range_min=443,
    port_range_max=443,
    remote_group_id=lb_security_group.id
)



# ==========================
# Database Security Group
# ==========================

db_security_group = openstack.networking.SecGroup(
    "db-security-group",
    name="db-security-group",
    description="Security group for database server"
)


# SSH administration (temporary)
db_ssh_rule = openstack.networking.SecGroupRule(
    "db-ssh-rule",
    security_group_id=db_security_group.id,
    direction="ingress",
    ethertype="IPv4",
    protocol="tcp",
    port_range_min=22,
    port_range_max=22,
    remote_ip_prefix="0.0.0.0/0"
)


# PostgreSQL ONLY from application servers
db_postgres_rule = openstack.networking.SecGroupRule(
    "db-postgres-rule",
    security_group_id=db_security_group.id,
    direction="ingress",
    ethertype="IPv4",
    protocol="tcp",
    port_range_min=5432,
    port_range_max=5432,
    remote_group_id=app_security_group.id
)