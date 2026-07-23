# Deployment Guide

Step-by-step procedure to deploy the Hackership infrastructure from zero.

## 1. Prerequisites

- An OpenStack (FelCloud) account and project
- `python3` (3.10+) and `pip`
- Pulumi CLI installed (`curl -fsSL https://get.pulumi.com | sh`)
- Ansible installed (`pip install ansible`, or via your distro's package manager)
- SSH key pair generated and imported into OpenStack (`openstack keypair create`)

**Important — filesystem location (WSL users):** create your virtual environment and clone this repo on the **Linux filesystem** (e.g. `~/hackership-iac`), not under `/mnt/c/...`. Windows-mounted paths (DrvFs) don't support Python venvs and symlinks reliably, and can also cause stale-bytecode issues where edited files don't get picked up. Working under `/mnt/c/` is a common source of hard-to-diagnose errors — avoid it entirely for this project.

## 2. Get OpenStack credentials

Two ways FelCloud can authenticate you; prefer Application Credentials for anything automated (this repo, Pulumi, CI):

**Option A — Application Credentials (recommended)**
1. Authenticate once with your username/password (see Option B) to get a working session.
2. Generate a scoped credential:
   ```bash
   openstack application credential create hackership-iac \
     --description "Pulumi IaC deploy" \
     --unrestricted
   ```
3. Export the result:
   ```bash
   export OS_AUTH_URL=https://identity.api.felcloud.io/v3
   export OS_IDENTITY_API_VERSION=3
   export OS_AUTH_TYPE=v3applicationcredential
   export OS_APPLICATION_CREDENTIAL_ID="<id_from_step_2>"
   export OS_APPLICATION_CREDENTIAL_SECRET="<secret_from_step_2>"
   ```
   Do **not** also set `OS_USERNAME`, `OS_PASSWORD`, `OS_PROJECT_ID`/`OS_PROJECT_NAME`, or domain variables alongside these — application credentials are already scoped, and mixing in project/domain vars causes:
   ```
   Error authenticating with application credential: Application credentials cannot request a scope.
   ```

**Option B — Username/password (only for generating the app credential above, or quick local testing)**
```bash
export OS_AUTH_URL=https://identity.api.felcloud.io/v3
export OS_IDENTITY_API_VERSION=3
export OS_USERNAME="your_username"
export OS_PASSWORD="your_password"
export OS_PROJECT_ID="your_project_id"
export OS_USER_DOMAIN_NAME="Default"
export OS_PROJECT_DOMAIN_NAME="Default"
```

Whichever set you use, put it in a `felcloud-env.sh` file **excluded from git** (`.gitignore` already covers this — see below), and `source` it before running Pulumi or `openstack` CLI commands.

**Verify before touching Pulumi:**
```bash
openstack server list
```
Empty list or real output = auth works. An auth error here means Pulumi will fail the same way — fix it at this step first.

**Note on switching auth methods:** if you switch between password and application-credential auth in the same terminal session, `unset` the previous set of `OS_*` variables first — leftover exports from an earlier `source` don't get cleared automatically and will conflict with the new method.

## 3. Set up the Python environment

```bash
cd ~/hackership-iac/infra
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install pulumi pulumi-openstack
```

## 4. Initialize / verify the Pulumi stack

If the stack already exists (cloned repo):
```bash
pulumi stack select dev
```

If starting fresh:
```bash
pulumi new python
```
(project name `hackership-infra`, stack `dev`; Pulumi's entry point is always `__main__.py`, not `main.py`.)

Set non-secret config:
```bash
pulumi config set openstack:region RegionOne
```

## 5. Deploy the infrastructure

```bash
source ../felcloud-env.sh   # your OS_* credentials
pulumi preview              # review planned resources — should show no errors
pulumi up                   # apply
```

Expected result: network, subnets, 3 security groups, 3 VMs (`app-vm-1`, `app-vm-2`, `db-vm`), and the DB's Cinder volume created with no errors. See `architecture.md` for what each resource represents.

## 6. Configure the load balancer

Once the app VMs exist, the LB/listener/pool/health monitor are provisioned (see `loadbalancer.py` in `infra/`). Recommended health monitor settings:

| Parameter | Value |
|---|---|
| Type | HTTP |
| URL path | `/health` |
| Expected codes | 200 |
| Delay | 10s |
| Timeout | 5s |
| Max retries (down) | 3 |
| Max retries (up) | 2 |

## 7. Run the Ansible playbooks

Generate the inventory from Pulumi outputs, then run:
```bash
cd ../ansible
ansible-playbook -i inventory/ site.yml
```
This applies the `common`, `hackership_app`, and `reverse_proxy` roles to both app nodes.

## 8. Validate the deployment

```bash
curl http://<lb_floating_ip>/
```
Should return the app's response. Then confirm both nodes are in the LB pool:
```bash
openstack loadbalancer member list <pool_id>
```

## 9. Reproducibility test (required by the mission's acceptance criteria)

```bash
pulumi destroy
pulumi up
ansible-playbook -i inventory/ site.yml
```
This full cycle should complete without manual intervention. Note any friction encountered in `troubleshooting-guide.md`.
