# Limitations connues (acceptées pour le pilote)

Ces points ont été identifiés en analysant le code applicatif réel
(`app/__init__.py`, `docker-compose.yml`, `.env.example`) et discutés avec
l'équipe. Ils sont **acceptés comme limitations connues pour le pilote**,
pas des bugs de l'infra Ansible — ils nécessitent un changement côté code
applicatif pour être résolus, pas côté configuration/déploiement.

## 1. APScheduler s'exécute sur chaque nœud sans coordination

`register_scheduler()` dans `app/__init__.py` démarre APScheduler
inconditionnellement à chaque `create_app()` (seule exception : `TESTING`).
Sur un déploiement multi-nœud, **chaque nœud applicatif exécute son propre
scheduler** :

- `check_inactivity` toutes les 30 min
- `run_badge_check` toutes les heures

→ Avec N nœuds actifs, ces tâches s'exécutent N fois en parallèle
(notifications dupliquées, badges potentiellement attribués plusieurs fois
selon l'idempotence du code métier).

**Statut** : accepté pour le pilote, documenté ici. Pas de contournement côté
Ansible/infra (le scheduler tourne dans le même process que le serveur web,
il n'y a pas de variable d'environnement pour le désactiver côté app
actuellement).

**Piste de résolution future** (côté code applicatif, hors scope Person 3) :
ajouter une variable d'env (ex: `ENABLE_SCHEDULER`) lue dans
`register_scheduler()`, et ne l'activer que sur un nœud désigné.

## 2. Flask-SocketIO sans `message_queue` partagée

`socketio.init_app(app, cors_allowed_origins="*")` n'a pas de
`message_queue=` configuré. Le projet a pourtant déjà Redis disponible
(sessions, cache).

→ Sur un déploiement multi-nœud, un événement Socket.IO émis pour un client
connecté à `app1` (notification, message de chat, mise à jour du feed en
temps réel) **n'atteint pas** un client connecté à `app2`. Les fonctionnalités
temps réel ne sont donc fiables qu'en usage mono-nœud, ou par chance si un
client reste connecté au même nœud pendant toute sa session (pas garanti sans
persistence LB, elle-même dépendante du design de Person 1/2).

**Statut** : accepté pour le pilote, documenté ici.

**Piste de résolution future** (côté code applicatif, hors scope Person 3) :
`socketio.init_app(app, cors_allowed_origins="*", message_queue=app.config["REDIS_URL"])`.
`REDIS_URL` est déjà disponible dans la config, donc le changement côté code
est minime une fois décidé.

## 3. Uploads (avatars, CVs) non partagés entre nœuds

Confirmé par `docker-compose.yml` (`avatars`/`cvs` en volumes nommés locaux)
et `.env.example` (`UPLOAD_FOLDER`/`CV_UPLOAD_FOLDER` en chemins disque
locaux). Un fichier uploadé via `app1` n'est pas visible par `app2`.

**Statut** : accepté explicitement (trafic faible en phase pilote). Migration
vers de l'object storage (Swift ou S3-compatible) prévue plus tard — hors
scope de ce rôle Ansible tant que ce n'est pas décidé/implémenté côté app.

## 4. Pas de route `/health` dédiée

Le healthcheck (dans `docker-compose.yml` et dans le rôle `hackership_app`)
cible `/` (l'index), faute de mieux. C'est fonctionnel (route publique,
pas de requête DB pour un visiteur anonyme) mais pas idéal : rend un template
HTML complet plutôt qu'une réponse minimale, et ne vérifie pas explicitement
la connectivité DB/Redis.

**Piste de résolution future** : ajouter une route `/health` légère côté app
(ex: `return {"status": "ok"}, 200`, avec éventuellement un ping DB/Redis).
