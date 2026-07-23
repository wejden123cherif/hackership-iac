# Troubleshooting Guide

Issues encountered while building this project, and how to resolve them.

## `externally-managed-environment` / broken pip inside a venv

**Symptom:**
```
error: externally-managed-environment
```
or, after `python -m pip install --upgrade pip`:
```
ModuleNotFoundError: No module named 'pip._vendor.packaging'
```

**Cause:** the venv was created on a Windows-mounted path (`/mnt/c/...` under WSL). DrvFs doesn't support Linux-style symlinks properly, which corrupts the venv's internal pip installation.

**Fix:** create the venv on the native Linux filesystem instead:
```bash
cd ~
mkdir -p hackership-iac && cd hackership-iac
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```
Keep project files wherever convenient, but venvs and tool installs must live under `~/...`, not `/mnt/c/...`.

## `Application credentials cannot request a scope` (HTTP 401)

**Symptom:**
```
Error authenticating with application credential: Application credentials cannot request a scope.
```

**Cause:** application credentials are already scoped to a project at creation time. Having `OS_PROJECT_ID`, `OS_PROJECT_NAME`, `OS_USER_DOMAIN_NAME`, or `OS_PROJECT_DOMAIN_NAME` set alongside `OS_APPLICATION_CREDENTIAL_ID`/`SECRET` causes a conflicting second scope request. This usually happens because leftover variables from an earlier password-based `source` are still in the shell session.

**Fix:**
```bash
unset OS_USERNAME OS_PASSWORD OS_PROJECT_ID OS_PROJECT_NAME OS_USER_DOMAIN_NAME OS_PROJECT_DOMAIN_NAME
env | grep OS_   # should print nothing at this point
source felcloud-env.sh
openstack server list
```
Going forward, open a fresh terminal tab when switching between password auth and application-credential auth, rather than re-sourcing different env files in the same session.

## `ImportError: cannot import name 'X' from 'module'` where X clearly exists in the file

**Symptom:** Pulumi fails with an `ImportError` for a name that is visibly defined in the source file.

**Diagnosis, in order:**
1. Confirm which file is actually being loaded:
   ```bash
   python -c "import security; print(security.__file__)"
   ```
   If this points outside your project (e.g. into `venv/lib/.../site-packages/`), an installed package is shadowing your local module — rename your file (e.g. `security_groups.py`) and update the import, or uninstall the conflicting package.
2. If the path is correct, check what's actually defined:
   ```bash
   python -c "import security; print(dir(security))"
   ```
   An empty result (no custom names at all) means the file on disk is empty or doesn't match what you intended to save — re-check your editor tab/save, or recreate the file from your source of truth.
3. Clear stale bytecode cache (more relevant on `/mnt/c/...` paths, where file-timestamp granularity can prevent cache invalidation):
   ```bash
   find . -name "__pycache__" -type d -exec rm -rf {} +
   ```

## Invalid `protocol="any"` on `openstack.networking.SecGroupRule`

**Symptom:** security group rule creation fails or behaves unexpectedly when `protocol="any"` is used.

**Cause:** the Neutron API doesn't accept the string `"any"` as a protocol value. Valid values are `tcp`, `udp`, `icmp`, or omitting the field entirely (`null`) for all protocols.

**Fix:** either specify a real protocol with a port range:
```python
protocol="tcp",
port_range_min=1,
port_range_max=65535,
```
or omit `protocol`, `port_range_min`, and `port_range_max` entirely if you genuinely want all protocols/ports allowed.

## Load balancer member shows unhealthy but the app is running

**Checklist, in order:**
1. Does the app actually expose the health monitor's configured path (e.g. `/health`) and return the expected status code (200)? Test directly:
   ```bash
   curl -i http://<app_node_ip>/health
   ```
2. Is the app's security group allowing the health check port from the LB (`sg-app` ingress from `lb-security-group`, not just from the internet)?
2. Check the monitor's own config matches expectations:
   ```bash
   openstack loadbalancer healthmonitor show <monitor_id>
   ```
3. If the app has no `/health` endpoint yet, either add one (preferred) or temporarily switch the monitor `type` to `TCP` (checks port connectivity only, not app-level health) until the endpoint exists.

## Where to look first, generally

Most issues in this stack fall into one of three buckets — check in this order:
1. **Auth/credentials** (`openstack server list` should work before anything else is debugged)
2. **Which file/module Python is actually loading** (especially on `/mnt/c/...` paths)
3. **OpenStack API field validation** (protocol values, CIDR formats, required vs optional fields)
