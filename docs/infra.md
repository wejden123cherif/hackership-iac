# Hackership - OpenStack Infrastructure Report

**Scope:** Network, security groups, compute, storage, bastion access, and public entry points provisioned via Pulumi (Python).

## 1. Current architecture

The infrastructure now uses two public entry points:

- **Bastion host:** public SSH entry point for administration.
- **HAProxy VM / load balancer:** public HTTP/HTTPS entry point for application traffic.

Application and database VMs stay private. Admin SSH to those nodes goes through the bastion over the private network.

```text
                              Internet
                                  |
                           Floating IPs
                                  |
               +------------------+------------------+
               |                                     |
       +-------v--------+                    +-------v--------+
       | Bastion Host   |                    | HAProxy VM      |
       | Ubuntu         |                    | Ubuntu          |
       | Public FIP     |                    | Public FIP      |
       | Private IP     |                    | Private IP      |
       +-------+--------+                    +-------+--------+
               |                                     |
               | SSH                                 | HTTP/HTTPS
               |                                     |
---------------+-------------------------------------+---------------
                         Private Network
                         192.168.88.0/24
               |                                     |
       +-------+--------+                    +-------+--------+
       |                |                    |                |
+------v------+  +------v------+      +------v------+
| App VM 1    |  | App VM 2    |      | DB VM       |
| Ubuntu      |  | Ubuntu      |      | PostgreSQL  |
| Private IP  |  | Private IP  |      | Private IP  |
+-------------+  +-------------+      +-------------+
```

## 2. Network

| Resource | Purpose |
|---|---|
| `private_network` | Internal network shared by bastion, HAProxy, app VMs, and DB VM |
| `private_subnet` | Private subnet for internal addresses, currently `192.168.88.0/24` |
| Floating IP for bastion | Public SSH entry point |
| Floating IP for HAProxy/LB | Public HTTP/HTTPS entry point |

The app and database VMs do not need floating IPs.

## 3. Security groups

| Group | Purpose |
|---|---|
| `bastion-security-group` | Allows SSH from the internet to the bastion |
| `lb-security-group` | Allows public HTTP/HTTPS to HAProxy/LB and SSH only from bastion |
| `app-security-group` | Allows app traffic from LB and SSH only from bastion |
| `db-security-group` | Allows PostgreSQL from app servers and SSH only from bastion |

**Rules:**

- `bastion-security-group`: ingress TCP/22 from `0.0.0.0/0` for initial access.
- `lb-security-group`: ingress TCP/80 and TCP/443 from `0.0.0.0/0`; TCP/22 from `bastion-security-group`.
- `app-security-group`: ingress TCP/80 and TCP/443 from `lb-security-group`; TCP/22 from `bastion-security-group`.
- `db-security-group`: ingress TCP/5432 from `app-security-group`; TCP/22 from `bastion-security-group`.

Recommended hardening: once the admin public IP is known, restrict bastion SSH from `0.0.0.0/0` to that CIDR.

## 4. Compute

| VM | Role | Network exposure | Security group |
|---|---|---|---|
| `bastion-vm` | SSH jump host | Floating IP + private IP | `bastion-security-group` |
| HAProxy VM | Public application entry point | Floating IP + private IP | `lb-security-group` |
| `app-vm-1` | Application node | Private IP only | `app-security-group` |
| `app-vm-2` | Application node | Private IP only | `app-security-group` |
| `db-vm` | PostgreSQL database | Private IP only | `db-security-group` |

## 5. Storage

The database VM uses a persistent block volume for PostgreSQL data.

## 6. Access paths

Admin SSH:

```bash
ssh -i key.pem ubuntu@<bastion_floating_ip>
ssh ubuntu@<private_vm_ip>
```

Or from the local machine with ProxyJump:

```bash
ssh -i key.pem -J ubuntu@<bastion_floating_ip> ubuntu@<private_vm_ip>
```

Application traffic:

```text
Internet -> HAProxy floating IP -> app-vm-1/app-vm-2 -> db-vm
```

## 7. Stack outputs

Expected Pulumi outputs include:

`network_id`, `subnet_id`, `bastion_security_group_id`, `lb_security_group_id`, `app_security_group_id`, `db_security_group_id`, `bastion_vm_id`, `bastion_port_id`, `bastion_floating_ip`, `app_vm_1_id`, `app_vm_2_id`, `db_vm_id`, `app_port_1_id`, `app_port_2_id`, `db_port_id`, `db_volume_id`.

## 8. Validation checklist

- `pulumi up` completes successfully.
- `openstack server list` shows bastion, HAProxy/LB, app, and DB VMs as `ACTIVE`.
- Bastion port has non-empty `binding_host_id` and `binding_vif_type`.
- Bastion floating IP is associated to the bastion port.
- App and DB VMs have private IPs only.
- SSH to private VMs works through the bastion.
- HTTP/HTTPS reaches HAProxy via its floating IP.
