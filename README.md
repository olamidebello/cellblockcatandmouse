# Cellblock Cat & Mouse

A fictional, nonviolent multiplayer strategy game. Choose inmate or correctional officer. Built with Python 3.12 standard library, SQLite, and a responsive canvas client. No npm packages or paid services required.

## Play locally

```sh
python3 server.py
```

Open http://127.0.0.1:18842. Register a player, create a room, choose your side, and add a bot or invite another player with the room code. The host starts each round. WASD/arrows or touch controls move; Space collects, delivers, or searches.

Inmates deliver six fictional tokens to the yard within 180 seconds. Bags hold three tokens. Officers search adjacent inmates and stashes, with a three-second search cooldown. An inmate carrying tokens is detained for the round. Empty searches cost points. Officers win on timeout, all inmates detained, or insufficient remaining tokens. All game actions, movement pacing, proximity, inventory, scoring, and win conditions are validated on the server. Inventories are redacted from other players. Accounts use scrypt password hashes and expiring bearer sessions; leaderboards persist in SQLite.

## Deploy to your server

Target domain: **cellblockcatandmouse.africandroid.com** (as supplied, `.com`, not `.world`). Create its DNS A record pointing to your server and remove any conflicting AAAA record. Copy `ansible/inventory.example.ini` to an inventory and replace the host. Then run:

```sh
ansible-playbook -i ansible/inventory.ini ansible/deploy.yml -e enable_tls=true -e letsencrypt_email=YOUR_EMAIL
```

The playbook pulls this repository, installs Python/Nginx/Certbot, creates a restricted systemd service, configures the domain, checks health, and requests HTTPS. Rerun it for updates. A private repository needs server-side Git access. Certificate renewal uses the distribution's Certbot timer. Back up `/var/lib/cellblock/game.db`; stop the service or use SQLite's online backup API when copying a live database.

## Verification

```sh
python3 -m unittest discover -s tests -v
```

## Current operating limits

This is a playable first release, not an exhaustive game or a load-tested production platform. One Python process owns in-memory rooms; do not run multiple workers behind a load balancer. Restarting loses active rounds, but preserves accounts and scores. Rooms support up to 12 players and expire after two idle hours. Leaving a round forfeits it. Disconnected clients can return with the same session while their room exists. The map shows player positions; concealed inventories are the strategy mechanic. Bot officers chase players using map pathfinding. No chat, payments, password recovery, moderation console, email, ranked matchmaking, or anti-collusion system is included. Use HTTPS in production. Session tokens are stored in browser local storage; do not add untrusted scripts. Fonts optionally load from Google Fonts with system fallbacks.

## Deploy on Olamidepanel

Run these commands **on your Olamidepanel server** (Debian/Ubuntu with Nginx). This creates a dedicated service and domain virtual host alongside existing sites. It does not require a guessed panel API or change the panel service.

```sh
sudo apt-get update
sudo apt-get install -y git ansible
sudo git clone https://github.com/olamidebello/cellblockcatandmouse.git /opt/cellblock-deploy
cd /opt/cellblock-deploy
sudo env LETSENCRYPT_EMAIL=YOUR_EMAIL bash scripts/deploy-olamidepanel.sh
```

Before running, point `cellblockcatandmouse.africandroid.com` to this server and allow inbound TCP 80/443. Replace `YOUR_EMAIL` with your actual email address. Existing conflicting Nginx entries for this exact hostname must be reconciled first. The playbook preserves HTTPS configuration on subsequent updates and enables certificate renewal.

For updates:

```sh
cd /opt/cellblock-deploy
sudo git pull --ff-only
sudo env LETSENCRYPT_EMAIL=YOUR_EMAIL bash scripts/deploy-olamidepanel.sh
```

For deployment from a control machine, use `ansible/inventory.example.ini` with your actual Olamidepanel host and SSH user, then invoke `ansible/olamidepanel.yml` with that inventory. No credentials are stored in the repository. Verify with `systemctl status cellblock` and `curl -fsS https://cellblockcatandmouse.africandroid.com/health`.
