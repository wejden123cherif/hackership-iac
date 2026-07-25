# hackership-ansible (Person 3 scope)

Ansible roles/playbooks for deploying the Hackership app on OpenStack VMs
provisioned by Person 1 (network/compute) and fronted by Person 2's load
balancer. This repo does **not** provision infrastructure — see Person 1/2's
Pulumi repo for that.

## Structure

```
inventory/hosts.ini.example   placeholder — replace with real IPs from Person 1/2's Pulumi outputs
group_vars/all.yml            non-secret config, aligned with the app's real .env.example
group_vars/vault.yml.example  secrets template (copy -> vault.yml -> ansible-vault encrypt)
site.yml                      main playbook: base -> security -> reverse_proxy -> hackership_app
playbooks/deploy.yml          app-only rolling redeploy (no full re-provisioning)
roles/
  base/            OS packages, Podman, NTP, monitoring agent hook
  security/        SSH hardening, ufw, fail2ban
  reverse_proxy/   Nginx config (adapted from the app repo's real nginx.conf)
  hackership_app/  clone app repo, build image, env file, migrations, systemd unit
docs/
  known-limitations.md   3 gaps found in the real app code, explicitly accepted for the pilot
  secrets.md              vault usage
```

## What this assumes (and doesn't yet know)

- **Inventory**: placeholder IPs in `inventory/hosts.ini.example`. Replace once
  Person 1/2 share real Pulumi stack outputs (app instance floating/private IPs).
- **DB/Redis location**: not yet decided with Person 1. `postgres_host` /
  `redis_host` in `group_vars/all.yml` default to `127.0.0.1` (matches the
  current single-node `docker-compose.yml` behavior). Update once confirmed —
  no role changes needed, just the variable.
- **TLS termination point**: not decided with Person 2 (at the LB, or here via
  Nginx+certbot). Currently plain HTTP on port 80 per node, matching the app
  repo's existing `nginx.conf`.

## Known limitations (accepted for the pilot)

Found while reading the real app code (`app/__init__.py`) — not fixable from
Ansible alone, need app-side changes eventually. See `docs/known-limitations.md`:

1. APScheduler runs unguarded on every node (duplicate scheduled jobs)
2. Flask-SocketIO has no `message_queue` (real-time events don't cross nodes)
3. Avatar/CV uploads are per-node local volumes (not shared) — already
   accepted, object storage migration planned later
4. No dedicated `/health` route (healthcheck currently targets `/`)

## Usage

```bash
cp inventory/hosts.ini.example inventory/hosts.ini   # fill in real IPs
cp group_vars/vault.yml.example group_vars/vault.yml
# edit vault.yml with real secrets
ansible-vault encrypt group_vars/vault.yml

ansible-playbook site.yml --ask-vault-pass
```

Subsequent app-code-only updates:

```bash
ansible-playbook playbooks/deploy.yml --ask-vault-pass
```
