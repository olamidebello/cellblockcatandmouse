#!/usr/bin/env bash
set -euo pipefail
if [[ $EUID -ne 0 ]]; then echo 'Run this deployment script as root.' >&2; exit 1; fi
apt-get update
apt-get install -y curl ca-certificates
repair_launcher=$(mktemp /tmp/cellblock-repair-XXXXXX.sh)
store_playbook=$(mktemp /tmp/cellblock-store-XXXXXX.yml)
trap 'rm -f "$repair_launcher" "$store_playbook"' EXIT
curl --fail --show-error --location --retry 3 https://raw.githubusercontent.com/olamidebello/cellblockcatandmouse/main/scripts/hard-fix-server.sh -o "$repair_launcher"
bash "$repair_launcher" "$@"
curl --fail --show-error --location --retry 3 https://raw.githubusercontent.com/olamidebello/africanappsstore/main/ansible/deploy-cellblock-mobile.yml -o "$store_playbook"
ansible-playbook -i localhost, -c local "$store_playbook" 2>&1 | tee /var/log/cellblock-store-publish.log
