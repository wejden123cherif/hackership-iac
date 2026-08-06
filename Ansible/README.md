# hackership-ansible (Person 3 scope)

Ansible roles/playbooks for deploying the Hackership app. 
This repo does **not** provision infrastructure.

## Structure

```
inventory/hosts.ini.example   documents the shape of the generated inventory
scripts/generate_inventory.sh builds inventory/hosts.ini from live Pulumi outputs
requirements.yml               collections needed by roles/security and roles/db
group_vars/
  all/vars.yml                 non-secret config, aligned with the app's .env.example
  all/vault.yml.example        secrets template (copy -> vault.yml -> ansible-vault encrypt)
  app.yml / db.yml              per-host-group firewall port lists
site.yml                       main playbook: base -> security -> [reverse_proxy, hackership_app] | db
playbooks/deploy.yml           app-only rolling redeploy (no full re-provisioning)
roles/
  base/            OS packages, Podman, NTP, monitoring agent hook
  security/        SSH hardening, ufw, fail2ban
  db/              PostgreSQL 16 + Redis 7 on the data-tier host
  reverse_proxy/   Nginx config (adapted from the app repo's real nginx.conf)
  hackership_app/  clone app repo, build image, env file, migrations, systemd unit
docs/
  known-limitations.md   gaps in the real app code, explicitly accepted for the pilot
  secrets.md              vault usage, GitLab deploy token setup
  troubleshooting-guide.md  issues actually hit during first deployment + fixes
```

## Topology

- `app-vm-1` / `app-vm-2`: Nginx + the Flask app (Podman), no floating IP
- `db-vm`: PostgreSQL + Redis (Podman), no floating IP
- `bastion-vm`: the only host with a public floating IP; all SSH access to
  the other nodes goes through it via `ProxyCommand`

## Usage

Install the required collections:
```bash
ansible-galaxy collection install -r requirements.yml
```

Generate the inventory from the live Pulumi stack (never hand-edit
`inventory/hosts.ini` — regenerate it instead):
```bash
SSH_KEY=/path/to/your/key.pem scripts/generate_inventory.sh
```

Set up secrets:
```bash
cp group_vars/all/vault.yml.example group_vars/all/vault.yml
# edit group_vars/all/vault.yml — see docs/secrets.md for the GitLab
# deploy token setup specifically
ansible-vault encrypt group_vars/all/vault.yml
```

Deploy:
```bash
ansible-playbook site.yml --ask-vault-pass
```

Subsequent app-code-only updates (rolling, one node at a time):
```bash
ansible-playbook playbooks/deploy.yml --ask-vault-pass
```

Hit an error partway through? Check `docs/troubleshooting-guide.md` first —
it covers vault password issues, GitLab token mixups, the removed
`community.general.yaml` callback plugin, missing Cinder volumes on the db
host, and a routing issue that can block image pulls on a specific node.

## Known limitations (accepted for the pilot)

Found while reading the real app code (`app/__init__.py`) — not fixable from
Ansible alone, need app-side changes eventually. See `docs/known-limitations.md`:

1. APScheduler runs unguarded on every node (duplicate scheduled jobs)
2. Flask-SocketIO's `message_queue` is not yet configured — real-time events
   don't cross nodes (Redis is deployed and available for this; wiring it up
   is an app-side change)
3. Avatar/CV uploads are per-node local volumes (not shared) — accepted for
   the pilot; object storage migration planned later
4. No dedicated `/health` route — the load balancer's health monitor and
   this repo's own readiness check both target `/` instead
