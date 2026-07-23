# Hackership — OpenStack Foundation Infrastructure Report

**Scope:** Network, security groups, compute, and storage layers, provisioned via Pulumi (Python).
**Status:** Complete, validated with `pulumi up` (0 errors).

## 1. What was built

A 3-tier architecture on OpenStack:

```
                          Internet
                             │
                             ▼
                     ┌───────────────┐
                     │ Load Balancer │
                     │(lb-security-  │
                     │    group)     │
                     └───────┬───────┘
                             │
                     HTTP/HTTPS traffic
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
    ┌───────────────────┐        ┌───────────────────┐
    │ Application VM 1   │        │ Application VM 2   │
    │ (app-security-     │        │ (app-security-     │
    │      group)        │        │      group)        │
    └──────────┬─────────┘        └──────────┬─────────┘
               │                             │
               └──────────────┬──────────────┘
                               │
                       PostgreSQL 5432
                               │
                               ▼
                     ┌───────────────┐
                     │  Database VM  │
                     │ (db-security- │
                     │    group)     │
                     └───────────────┘
```

## 2. Network

| Resource | ID |
|---|---|
| Private network | `3064b1da-3e73-4454-978a-05dd1734a95f` |
| Private subnet | `369dce09-2947-4af6-8f5f-f15345bd701d` |

Used for all internal communication between app servers, DB server, and LB components.

## 3. Security groups

Three groups, least-privilege by design:

| Group | ID | Purpose |
|---|---|---|
| `lb-security-group` | `6e0472d2-40ec-4d53-8e30-e96085ab8eb3` | Public HTTP/HTTPS entry point |
| `app-security-group` | `3f35056a-c8a5-473f-931c-67d24f28fb58` | Application servers |
| `db-security-group` | `5a0feb1c-32f3-4102-8ffe-67907d9ede45` | Database server |

**Rules:**
- `lb-security-group`: ingress 80/443 from `0.0.0.0/0`.
- `app-security-group`: ingress 80/443 restricted to `lb-security-group` only (tightened from an initial `192.168.88.0/24`-wide rule); SSH (22) open for dev/testing only.
- `db-security-group`: ingress 5432 restricted to `app-security-group` only; SSH (22) open for admin, to be locked down later.

Net effect: app servers are reachable only through the LB; the database is reachable only from the app tier — no direct public path to either.

## 4. Compute

| VM | ID | Flavor | Specs | Security group |
|---|---|---|---|---|
| `app-vm-1` | `54f60358-d24a-491c-9e26-54d5af04e4e3` | 1004 | 2 vCPU / 4GB | `app-security-group` |
| `app-vm-2` | `c901a386-eec9-4c4a-afb0-f8a036b013b8` | 1004 | 2 vCPU / 4GB | `app-security-group` |
| `db-vm` | `30ce391b-d91d-4fc9-bcc7-c1d0378b6f49` | 1005 | 2 vCPU / 8GB | `db-security-group` |

App VMs are identical, ready to be added as LB pool members. All on Ubuntu 24.04 LTS.

## 5. Storage

Persistent volume `8c0ed5e6-017f-4ad2-8345-50d949082feb` attached to `db-vm` for PostgreSQL data.

## 6. Stack outputs (exported for the team)

`network_id`, `subnet_id`, `app_security_group_id`, `db_security_group_id`, `lb_security_group_id`, `app_vm_1_id`, `app_vm_2_id`, `db_vm_id`, `db_volume_id`

These feed directly into the load-balancer teammate's work (pool members, health checks).

## 7. Validation

- `pulumi preview` → no planning errors.
- `pulumi up` → successful deployment (3 created, 6 replaced, 0 errors).

## 8. Remaining (next phase, owned by LB teammate)

- Load balancer creation, listener, pool/members, health checks
- Floating IP for LB VIP
- Application deployment (Ansible)
- End-to-end HA test (simulated node failure)
