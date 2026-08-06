# Gestion des secrets
Aucun secret en clair dans ce dépôt.

## Secrets applicatifs

Vivent dans `group_vars/all/vault.yml`, chiffré avec `ansible-vault`.

**Important** : ce fichier doit être dans le sous-dossier `group_vars/all/`, pas
directement dans `group_vars/`. Ansible ne charge automatiquement que
`group_vars/all.yml` et le contenu de `group_vars/all/` — un fichier nommé
`group_vars/vault.yml` à plat n'est jamais chargé et ses variables restent
`undefined`, même si le fichier existe et est correctement chiffré.

```bash
cp group_vars/all/vault.yml.example group_vars/all/vault.yml
# éditer : vault_secret_key, vault_postgres_password, vault_groq_api_key,
#          vault_smtp_password, vault_gitlab_deploy_token
ansible-vault encrypt group_vars/all/vault.yml
```

Le mot de passe du vault ne doit jamais être committé :
- fichier local `.vault_pass` (déjà dans `.gitignore`), référencé par `ansible.cfg`
- ou en CI : passé via le coffre-fort du système CI, jamais en clair dans les logs

Édition : `ansible-vault edit group_vars/all/vault.yml`

## Token de déploiement GitLab

Le clone du dépôt applicatif (`hackership_repo_url` dans
`group_vars/all/vars.yml`) utilise un **deploy token** GitLab plutôt qu'un
token personnel :

1. Sur le dépôt GitLab → Settings → Repository → Deploy tokens
2. Créer un token avec le scope `read_repository` uniquement (pas d'écriture)
3. Copier la valeur générée dans `vault_gitlab_deploy_token`

Un deploy token scopé à ce seul dépôt est préférable à un token personnel :
il peut être révoqué/régénéré indépendamment d'un compte utilisateur, et
n'expose aucun autre accès.

## Ce qui n'est PAS dans ce dépôt

Les credentials OpenStack (pour Pulumi) et la config du load balancer
relèvent de Person 1/2, pas de ce dépôt Ansible.
