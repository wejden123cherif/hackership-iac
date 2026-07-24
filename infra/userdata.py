# userdata.py

app_user_data = """#cloud-config

package_update: true

packages:
  - openssh-server

ssh_pwauth: false

runcmd:
  - systemctl enable ssh
  - systemctl start ssh
"""