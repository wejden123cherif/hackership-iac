# Gestion des secrets (scope Ansible / Person 3)

Aucun secret en clair dans ce dépôt.

## Secrets applicatifs

Vivent dans `group_vars/vault.yml`, chiffré avec `ansible-vault` :

```bash
cp group_vars/vault.yml.example group_vars/vault.yml
# éditer : vault_secret_key, vault_postgres_password, vault_groq_api_key, vault_smtp_password
ansible-vault encrypt group_vars/vault.yml
```

Le mot de passe du vault ne doit jamais être committé :
- fichier local `.vault_pass` (déjà dans `.gitignore`), référencé par `ansible.cfg`
- ou en CI : passé via le coffre-fort du système CI, jamais en clair dans les logs

Édition : `ansible-vault edit group_vars/vault.yml`

## Secrets provenant de Person 1/2 (infra)

Les credentials DB/Redis eux-mêmes (mots de passe) sont définis côté Ansible
(`vault_postgres_password`), mais l'**emplacement** (host/IP) de PostgreSQL et
Redis dépend du design infra de Person 1 — pas encore confirmé au moment de la
rédaction. Une fois confirmé, mettre à jour `postgres_host`/`redis_host` dans
`group_vars/all.yml` (ou dans l'inventaire, par groupe).

## Ce qui n'est PAS dans ce dépôt

Les credentials OpenStack (pour Pulumi) et la config du load balancer
relèvent de Person 1/2, pas de ce dépôt Ansible.
