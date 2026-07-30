# Import Existing Hackership Infrastructure into Pulumi State

This document explains how to bring the existing Felcloud/OpenStack Hackership infrastructure under Pulumi state management — **without recreating or destroying anything**.

---

## Overview

The Pulumi code in `infra/` describes the existing infrastructure. Before running `pulumi up`, every existing resource must be **imported** into Pulumi's state file using `pulumi import`. This tells Pulumi: *"This resource already exists — don't create it, just track it."*

> **⚠️ CRITICAL: Do NOT run `pulumi up` until ALL imports are complete and `pulumi preview` shows 0 changes.**

---

## Existing Infrastructure Reference

### Compute Instances

| Pulumi Resource Name | OpenStack Name | OpenStack UUID | Boot |
|---|---|---|---|
| `bastion` | `Pulumis-Bastion` | `80eed15f-45e5-4a5c-8f99-a387ff121e61` | Volume |
| `app-vm-1` | `Pulumis-app-vm-1` | `23a7599c-ce2a-44ba-990e-93c6302b5235` | Image |
| `app-vm-2` | `Pulumis-app-vm-2` | `e24e7cfd-5fe8-45e3-b9a4-08d83bb8ae60` | Image |
| `db-vm` | `pulumis-db-vm` | `a27d46dd-d678-488d-9594-21311bb34c0f` | Volume |

### Volumes

| Pulumi Resource Name | OpenStack UUID |
|---|---|
| `bastion-root-volume` | `5873bb8a-7142-4a17-a81b-58d19473f7b4` |
| `db-root-volume` | `ce0bd1a5-13f7-466b-b9f9-95a9f429f3c4` |

### Floating IPs

| Pulumi Resource Name | Address | OpenStack UUID |
|---|---|---|
| `bastion-floating-ip` | `197.5.133.81` | `65dd4118-78e3-4165-bb16-f028aa8cea70` |
| `app-vm-1-floating-ip` | `197.5.133.14` | `718d4612-b1a4-42a1-b07b-04d11d3ec35f` |
| `app-vm-2-floating-ip` | `197.5.133.228` | `e28b5e39-09b7-4635-87e9-cd8bda2de32f` |
| `db-floating-ip` | `197.5.133.4` | `af113dae-ac15-433b-9461-ebbe7a9ad172` |

### Security Groups

| Pulumi Resource Name | OpenStack Name | OpenStack UUID |
|---|---|---|
| `all-open` | `all_open` | `3158e473-f869-42f1-a866-0fc8b0f87d17` |

### Network (lookup only — not imported)

The `hackership` network and `sub_hackership` subnet are referenced via `get_network()` / `get_subnet()` lookups. They are **not** managed by this stack and do **not** need to be imported.

---

## Prerequisites

```bash
# 1. Navigate to infra directory
cd infra/

# 2. Activate the Python virtual environment
source venv/bin/activate          # Linux/macOS (WSL)
# or
.\venv\Scripts\Activate.ps1       # Windows PowerShell

# 3. Source your OpenStack credentials
source ../openrc.sh

# 4. Select the Pulumi stack
pulumi stack select dev
```

---

## Import Commands

Run these **one at a time**. Confirm each succeeds (exit code 0) before proceeding.

### Step 1 — Security Group

```bash
pulumi import openstack:networking/secGroup:SecGroup all-open 3158e473-f869-42f1-a866-0fc8b0f87d17
```

### Step 2 — Volumes

```bash
# Bastion root volume
pulumi import openstack:blockstorage/volume:Volume bastion-root-volume 5873bb8a-7142-4a17-a81b-58d19473f7b4

# Database root volume
pulumi import openstack:blockstorage/volume:Volume db-root-volume ce0bd1a5-13f7-466b-b9f9-95a9f429f3c4
```

### Step 3 — Compute Instances

```bash
# Bastion VM
pulumi import openstack:compute/instance:Instance bastion 80eed15f-45e5-4a5c-8f99-a387ff121e61

# App VM 1
pulumi import openstack:compute/instance:Instance app-vm-1 23a7599c-ce2a-44ba-990e-93c6302b5235

# App VM 2
pulumi import openstack:compute/instance:Instance app-vm-2 e24e7cfd-5fe8-45e3-b9a4-08d83bb8ae60

# Database VM
pulumi import openstack:compute/instance:Instance db-vm a27d46dd-d678-488d-9594-21311bb34c0f
```

### Step 4 — Floating IPs

```bash
# Bastion floating IP (197.5.133.81)
pulumi import openstack:networking/floatingIp:FloatingIp bastion-floating-ip 65dd4118-78e3-4165-bb16-f028aa8cea70

# App VM 1 floating IP (197.5.133.14)
pulumi import openstack:networking/floatingIp:FloatingIp app-vm-1-floating-ip 718d4612-b1a4-42a1-b07b-04d11d3ec35f

# App VM 2 floating IP (197.5.133.228)
pulumi import openstack:networking/floatingIp:FloatingIp app-vm-2-floating-ip e28b5e39-09b7-4635-87e9-cd8bda2de32f

# Database floating IP (197.5.133.4)
pulumi import openstack:networking/floatingIp:FloatingIp db-floating-ip af113dae-ac15-433b-9461-ebbe7a9ad172
```

---

## Post-Import Validation

### Step 1 — Refresh state from OpenStack

```bash
pulumi refresh
```

This syncs Pulumi state with the live OpenStack API. It may populate some read-only fields (like fixed_ip, port_id). This is safe — it only updates the local state file, not the real resources.

### Step 2 — Preview changes

```bash
pulumi preview --diff
```

**Expected output:**

```
Resources:
    11 unchanged
```

If you see **any** `replace` or `delete` operations, **do NOT run `pulumi up`**. See the troubleshooting section below.

### Step 3 — Only if preview shows 0 changes: Apply

```bash
pulumi up --yes
```

---

## Troubleshooting Common Drift Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| VM `replace` due to `name` mismatch | Code name ≠ OpenStack name | Check `openstack server show <id>` and update `name=` in `compute.py` |
| VM `replace` due to `image_id` | Already in `ignore_changes` | Run `pulumi refresh` to clear |
| VM `replace` due to `block_devices` | Pulumi computes hash differently | Add `"block_devices"` to `ignore_changes` for that instance |
| Volume `replace` due to `image_id` | Already in `ignore_changes` | Run `pulumi refresh` to clear |
| Floating IP `replace` due to `address` | Already in `ignore_changes` | Run `pulumi refresh` to clear |
| Security group `update` due to `description` | OpenStack stores empty string, code has text | Set `description=""` in `security.py` to match |
| Import fails: "resource already in state" | Previously imported | Skip that resource, continue with next |
| Import fails: "resource not found" | Wrong UUID | Double-check UUID with `openstack server show <id>` |

---

## Resource Protection Summary

All critical resources have `protect=True`. This means `pulumi up` will **refuse to delete** them even if the code is accidentally changed.

| Resource | Type | Protected |
|----------|------|-----------|
| `bastion` | Instance | ✅ |
| `app-vm-1` | Instance | ✅ |
| `app-vm-2` | Instance | ✅ |
| `db-vm` | Instance | ✅ |
| `bastion-root-volume` | Volume | ✅ |
| `db-root-volume` | Volume | ✅ |
| `bastion-floating-ip` | FloatingIp | ✅ |
| `app-vm-1-floating-ip` | FloatingIp | ✅ |
| `app-vm-2-floating-ip` | FloatingIp | ✅ |
| `db-floating-ip` | FloatingIp | ✅ |
| `all-open` | SecGroup | ✅ |

To remove protection before intentional decommissioning:

```bash
pulumi state unprotect <resource_urn>
# Then confirm: pulumi preview
# Then: pulumi destroy --target <resource_urn>
```
