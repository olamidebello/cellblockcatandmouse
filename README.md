# Cellblock Cat & Mouse

A fictional, nonviolent multiplayer strategy game. Choose inmate or correctional officer. Built with Python 3.12 standard library, SQLite, and a responsive canvas client. No npm packages or paid services required.

## Play locally

```sh
python3 server.py
```

Open http://127.0.0.1:18842. Register a player, create a room, choose your side, and add a bot or invite another player with the room code. The host starts each round. WASD/arrows or touch controls move; Space collects, delivers, or searches.

Inmates deliver six fictional tokens to the yard within 180 seconds. Bags hold three tokens. Officers search adjacent inmates and stashes, with a three-second search cooldown. An inmate carrying tokens is detained for the round. Empty searches cost points. Officers win on timeout, all inmates detained, or insufficient remaining tokens. All game actions, movement pacing, proximity, inventory, scoring, and win conditions are validated on the server. Inventories are redacted from other players. Accounts use scrypt password hashes and expiring bearer sessions; leaderboards persist in SQLite.

## Deploy to your server

Target domain: **cellblockcatandmouse.africandroid.world** (current domain). Create its DNS A record pointing to your server and remove any conflicting AAAA record. Copy `ansible/inventory.example.ini` to an inventory and replace the host. Then run:

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

Before running, point `cellblockcatandmouse.africandroid.world` to this server and allow inbound TCP 80/443. Replace `YOUR_EMAIL` with your actual email address. Existing conflicting Nginx entries for this exact hostname must be reconciled first. The playbook preserves HTTPS configuration on subsequent updates and enables certificate renewal.

For updates:

```sh
cd /opt/cellblock-deploy
sudo git pull --ff-only
sudo env LETSENCRYPT_EMAIL=YOUR_EMAIL bash scripts/deploy-olamidepanel.sh
```

For deployment from a control machine, use `ansible/inventory.example.ini` with your actual Olamidepanel host and SSH user, then invoke `ansible/olamidepanel.yml` with that inventory. No credentials are stored in the repository. Verify with `systemctl status cellblock` and `curl -fsS https://cellblockcatandmouse.africandroid.world/health`.

## Facility selection and dignity-first game policy

Room creators choose one of three fictional facilities or enter a custom prison name, address, city, state/region, and country. Details are validated on the server and displayed to room members. Do not enter private residential addresses. Facility metadata does not select or claim to reproduce an actual institution's rules. The host API can change the facility between rounds.

An inmate can switch between pocket and abstract underwear concealment. This is a fictional game state, not realistic concealment advice or a statement about real search effectiveness. Routine search actions are resolved by qualified NPC staff; concealed tokens require a fictional token scan followed by supervisor-approved private review. Signals expire after 20 seconds; scans recharge for eight seconds. A review takes four seconds, freezes the target, and happens entirely off-screen with qualified NPC staff and privacy. No anatomy, undressing, invasive examinations, sexual abuse, or searches to determine gender/sex are implemented. NPC staffing abstracts individual search assignments; the system does not collect players' gender, transgender status, or medical details.

Search approval, denial, completion, and evidence receipts appear in a round audit, filtered to the actor and target. Voluntary surrender seizes tokens without detention. Policy concerns can be recorded even by detained players without score penalties; this is an in-game record, not a real PREA report or external complaint. Round audits expire on restart/new rounds; they are not a permanent evidence-management system.

The main reference is [28 CFR 115.15](https://www.ecfr.gov/current/title-28/chapter-I/part-115/subpart-A/subject-group-ECFR4b237dabeebeb07/section-115.15), checked October 26, 2026. PREA imposes specific cross-gender search/viewing limits, documentation requirements, protections for transgender/intersex inmates, and staff training requirements. Our blanket private NPC review workflow is a deliberately stricter fictional abstraction, not all of PREA, a compliance certification, or legal/training advice. Other institutional policies vary. Unmodeled systems include real disciplinary hearings, visitation, medical care, actual reporting investigations, staffing demographics, and emergency exceptions.

## Brand assets

Original artwork generated with the built-in image generator is integrated as `public/assets/cover.webp` and `public/assets/logo.webp` (optimized web derivatives). Cover brief: fully clothed adult inmate and officer, amber/blue graphic-novel cellblock rivalry, cat-and-mouse maze emblem, no violence or intimate imagery. Logo brief: amber cat and blue mouse in a maze-and-bars shield, isolated on transparency, no agency insignia. The complete prompts are in `ART_PROMPTS.md`.

## Standalone first-install and update playbook (154.16.170.86)

`ansible/bootstrap.yml` solves the missing `/opt/cellblock-deploy` directory: it installs Git and Ansible, clones the checkout if absent, pulls updates if present, and runs the full service/Nginx/SSL deployment. Modified tracked files are not forcibly overwritten. Its remote inventory is `ansible/olamidepanel-server.ini`.

On the Olamidepanel server, logged in as root:

```sh
apt-get update
apt-get install -y ansible curl ca-certificates
read -rp 'SSL certificate email: ' LETSENCRYPT_EMAIL
export LETSENCRYPT_EMAIL
BOOTSTRAP_PLAYBOOK=$(mktemp /tmp/cellblock-bootstrap-XXXXXX.yml)
curl --fail --show-error --location https://raw.githubusercontent.com/olamidebello/cellblockcatandmouse/main/ansible/bootstrap.yml -o "$BOOTSTRAP_PLAYBOOK"
ansible-playbook -i localhost, -c local "$BOOTSTRAP_PLAYBOOK"
rm -f "$BOOTSTRAP_PLAYBOOK"
```

Run the same block for updates. The bootstrap file is downloaded before execution; no existing repository or working directory is required. DNS must first resolve `cellblockcatandmouse.africandroid.world` to `154.16.170.86`, with ports 80/443 reachable. HTTPS issuance failure is reported as a deployment failure; fix DNS/reachability before rerunning.

Alternatively, from a control machine with this repository and Ansible installed:

```sh
export LETSENCRYPT_EMAIL=your-real-email@example.com
ansible-playbook -i ansible/olamidepanel-server.ini ansible/bootstrap.yml
```

Use `--ask-pass` if SSH password authentication is needed and available; keep passwords out of inventory files. For a temporary HTTP-only install before DNS is ready, pass `-e enable_tls=false`; enable HTTPS before signing in or using accounts publicly.

### Domain displays Africa Media Hub or another site

Deployment now inspects active Nginx configuration, backs up conflicting files, and removes only the exact game hostname from other `server_name` declarations before installing the game's dedicated virtual host. Other hostnames are preserved. A host-only conflicting declaration receives a unique `.invalid` name. The repair validates Nginx and restores edited contents if validation fails. It does not change wildcard declarations, delete other sites, or reload an invalid configuration. Backups are adjacent to the changed files with `.cellblock-backup-<timestamp>` suffixes. Deployment checks the game's page marker through the virtual host and, with TLS enabled, the public HTTPS URL. A public check failure may also indicate wrong DNS, an upstream proxy, or caching that must be corrected separately.

Rerun the standalone bootstrap commands above to apply this fix. Verify the browser shows the Cellblock brand and a valid certificate; never bypass a certificate warning to sign in.

## Automatic hard repair (missing service, wrong site, incorrect certificate)

The standalone `ansible/hard-fix.yml` installs the application even when neither deployment directory exists. It backs up Nginx and existing source, preserves and backs up the external SQLite database, restores source from GitHub, repairs database permissions, reinstalls/enables systemd, removes exact-hostname routing conflicts, configures the dedicated game virtual host, requests the domain certificate, enables renewal, and checks backend and public HTTPS game content. Source modifications in `/opt/cellblock` are replaced after archival; the database remains in `/var/lib/cellblock`.

Run as root from **any directory** on `154.16.170.86`:

```sh
apt-get update
apt-get install -y curl ca-certificates
curl -fL https://raw.githubusercontent.com/olamidebello/cellblockcatandmouse/main/scripts/hard-fix-server.sh -o /root/cellblock-hard-fix.sh
bash /root/cellblock-hard-fix.sh
```

Optional certificate contact: set `export LETSENCRYPT_EMAIL=your-real-email@example.com` before running. With no email, Certbot registers without one, so certificate account notifications are unavailable. No placeholder email or interactive prompt is required.

Logs: `/var/log/cellblock-hard-fix.log`. Recovery archives: `/var/backups/cellblock` (root-only). Failure output includes the failing task and the game journal. DNS must resolve exclusively to `154.16.170.86` for this default single-server repair; an unexpected A/AAAA record stops issuance with a diagnostic. This script does not edit registrar DNS, bypass certificate validation, repeatedly force renewals, remove unrelated virtual hosts, or promise to fix external firewalls/CA rate limits. Unrelated invalid Nginx configuration is reported for repair rather than deleted. A failure does not mean the site is fixed; retain the log and correct the reported blocker. Run with `-e game_expected_ipv4=NEW_IP` when intentionally moving servers.

## Owner notices and legal requests

Footer and signup links expose `/terms`, `/privacy`, `/copyright`, and `/contact`. The operator/owner notice names **Olamide Olatayo Bello**. Notices describe actual data handling, third-party licenses, and limits on claims involving AI-generated artwork. Effective date: October 26, 2026.

The contact form stores a general/privacy/copyright request in the private SQLite `legal_requests` table, with optional reply email and optional current account association. It sends no email and does not automatically fulfill requests. The owner must review and respond through a verified channel, including requests from people without an account. On the server:

```sh
sudo python3 /opt/cellblock/scripts/legal-requests.py
sudo python3 /opt/cellblock/scripts/legal-requests.py --resolve REQUEST_ID
```

Review output contains personal information; keep it private. Resolution only updates the status and does not erase request data, delete accounts, or send a response. No automatic account/contact/log/backup deletion schedule is configured. Operators must manage retention, applicable rights, and responses. These pages are tailored initial notices, not a claim that all jurisdiction-specific requirements have been implemented. No mandatory arbitration or venue was added.

## Pull and deploy latest updates

Ansible entry point: `ansible/pull-and-deploy.yml`. It imports the standalone bootstrap playbook to clone/pull the latest code, deploy it, and verify all four legal pages. From a control machine:

```sh
export LETSENCRYPT_EMAIL=your-real-email@example.com
ansible-playbook -i ansible/olamidepanel-server.ini ansible/pull-and-deploy.yml
```

On the server, `bash /opt/cellblock/scripts/pull-and-deploy.sh` invokes the existing self-contained hard-repair updater (certificate email optional), which archives existing source before pulling it. If the game is not installed, download and run `scripts/hard-fix-server.sh` using the instructions above.
