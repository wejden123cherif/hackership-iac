# Troubleshooting guide

Issues actually hit during the first end-to-end deployment, in the order they tend to appear.

---

## 1. `ansible-vault` errors

### "The vault password file ... was not found"
`ansible.cfg` points `vault_password_file` at `.vault_pass`, which is
git-ignored on purpose (it's a secret). Create it locally:
```bash
touch .vault_pass && chmod 600 .vault_pass
```
An **empty** file satisfies "file exists" for commands that don't actually
need to decrypt anything (e.g. `ansible -m ping`), but will fail as soon as
a real vaulted variable needs to be read.


If you're encrypting `vault.yml` for the first time, set the password in
`.vault_pass` **before** running `ansible-vault encrypt` so it picks it up
non-interactively — otherwise `encrypt` and the file you already pointed
`ansible.cfg` at can disagree.



---

## 2. `stdout_callback = yaml` crashes on Python 3.12

```
[ERROR]: The 'community.general.yaml' callback plugin has been removed...
```
or, on an even older `community.general`, a raw Python traceback
(`TypeError: function() argument 'code' must be code, not str`) instead of
a clean error. Either way, the fix is the same — the plugin was folded into
core:
```bash
ansible-galaxy collection install community.general --upgrade
```
and `ansible.cfg` already uses the replacement (`stdout_callback = default`,
`result_format = yaml`) as of this repo version.

---

## 3. Podman image pulls hang then time out on the db host only

```
Error: initializing source docker://postgres:16-alpine: ... dial tcp ...: i/o timeout
```
— while the same pull works fine from an app host. This is an outbound
routing problem specific to that instance, not a Podman/registry issue.
Compare `ip route` between a working host and the failing one:

```bash
ip route
```
Look for **two `default via ...` routes at the same metric**. If one of
them points somewhere that isn't a real internet gateway (e.g. the bastion's
private IP), the kernel can pick either route non-deterministically, and
traffic routed through a non-gateway host just times out.

Remove the bad route immediately (until reboot):
```bash
sudo ip route del default via <bad-gateway-ip>
```
Then check whether it's baked into netplan so it doesn't come back on
reboot:
```bash
ls -la /etc/netplan/
sudo cat /etc/netplan/*.yaml
```
If a file (commonly a lower-numbered one like `01-netcfg.yaml`, applied
before cloud-init's `50-cloud-init.yaml`) has a `routes:` block causing
this, remove just that block and re-apply:
```bash
sudo nano /etc/netplan/<the-file>.yaml   # delete the routes: section
sudo netplan apply
```
This is an OpenStack/instance-provisioning issue (Person 1's Pulumi/network
scope), not something this Ansible repo causes or can prevent — but it's
worth flagging to whoever owns instance provisioning so it isn't
reintroduced on rebuild.