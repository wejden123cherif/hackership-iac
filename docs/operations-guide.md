# Operations Guide

Common day-2 tasks for the Hackership infrastructure.

## Scaling: add an application node

1. Add a new VM resource in `infra/compute.py` (same image/flavor as `app-vm-1`/`app-vm-2`), attached to `app-security-group`.
2. Export its ID/IP in `infra/main.py`.
3. Add it as an LB pool member in `infra/loadbalancer.py`.
4. Apply:
   ```bash
   pulumi up
   ```
5. Add the new node to the Ansible inventory and run:
   ```bash
   ansible-playbook -i inventory/ site.yml --limit new_node_hostname
   ```
6. Confirm it joins the pool as healthy:
   ```bash
   openstack loadbalancer member list <pool_id>
   ```

Scaling down is the reverse: remove the pool member first, then the Ansible host, then the Pulumi resource.

## Checking load balancer / pool health

```bash
openstack loadbalancer list
openstack loadbalancer pool list
openstack loadbalancer member list <pool_id>
openstack loadbalancer healthmonitor show <monitor_id>
```
A member showing `operating_status: ERROR` or `OFFLINE` means the health monitor is failing checks against that node — check the app's `/health` endpoint directly on that node first.

## Deploying an application update

```bash
cd ansible
ansible-playbook -i inventory/ site.yml --tags app
```
Since both app nodes are behind the LB, update one node at a time if you want zero-downtime rollout:
```bash
ansible-playbook -i inventory/ site.yml --limit app-vm-1
# wait for it to pass health checks, then:
ansible-playbook -i inventory/ site.yml --limit app-vm-2
```

## Rotating OpenStack application credentials

```bash
openstack application credential create hackership-iac-new --unrestricted
```
Update `felcloud-env.sh` with the new ID/secret, verify with `openstack server list`, then revoke the old one:
```bash
openstack application credential delete <old_credential_id>
```

## Database backups

**Logical backup (pg_dump), scheduled on `db-vm`:**
```bash
pg_dump -U <db_user> <db_name> > /backups/hackership_$(date +%F).sql
```
Ship this off-instance (object storage or a separate volume) — it protects against logical/accidental data loss.

**Volume snapshot (protects against volume-level failure):**
```bash
openstack volume snapshot create --volume <db_volume_id> hackership-db-snapshot-$(date +%F)
```

**Restoring from a volume snapshot:**
```bash
openstack volume create --snapshot <snapshot_id> hackership-db-restored
# then attach the new volume to a (new or existing) db VM
```

## Rollback

**Infrastructure rollback (Pulumi):**
```bash
pulumi stack history
pulumi stack export --version <n> > previous-state.json
pulumi stack import < previous-state.json
pulumi up
```

**Application rollback (Ansible):**
Tag releases in git; to roll back, deploy a previous tag:
```bash
git checkout <previous_tag>
ansible-playbook -i inventory/ site.yml --tags app
```

## Simulating a node failure (HA validation)

```bash
# Option 1: stop the service
ssh app-vm-1 "sudo systemctl stop hackership"

# Option 2: stop the VM entirely
openstack server stop app-vm-1
```
Then watch the pool:
```bash
watch openstack loadbalancer member list <pool_id>
```
`app-vm-1` should flip to unhealthy and be removed from active rotation within roughly 30 seconds (based on the health monitor's 10s interval × 3 retries), while traffic continues on `app-vm-2` uninterrupted. Restart the service or the VM to confirm it rejoins automatically once healthy.
