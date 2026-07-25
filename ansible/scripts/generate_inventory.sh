#!/usr/bin/env bash
set -euo pipefail

INFRA_DIR="../infra"
OUT="inventory/hosts.ini"

cd "$(dirname "$0")/.."

app1_ip=$(pulumi -C "$INFRA_DIR" stack output app_vm_1_ip)
app2_ip=$(pulumi -C "$INFRA_DIR" stack output app_vm_2_ip)
db_ip=$(pulumi -C "$INFRA_DIR" stack output db_vm_ip)
bastion_ip=$(pulumi -C "$INFRA_DIR" stack output bastion_floating_ip)
bastion_private=$(pulumi -C "$INFRA_DIR" stack output bastion_private_ip)

cat > "$OUT" << EOF
# Auto-generated from Pulumi stack outputs — do not hand-edit.
# Regenerate with: scripts/generate_inventory.sh

[app]
app1 ansible_host=${app1_ip}
app2 ansible_host=${app2_ip}

[db]
db1 ansible_host=${db_ip}

[hackership:children]
app

[all:vars]
ansible_user=ubuntu
bastion_private_ip=${bastion_private}
ansible_ssh_common_args='-o ProxyCommand="ssh -i key.pem -W %h:%p -q ubuntu@${bastion_ip}"'
EOF

echo "Wrote ${OUT}"
