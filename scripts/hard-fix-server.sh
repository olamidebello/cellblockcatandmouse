#!/usr/bin/env bash
set -euo pipefail
if [[ $EUID -ne 0 ]]; then
  echo 'Run as root: sudo bash /root/cellblock-hard-fix.sh' >&2
  exit 1
fi
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ansible curl ca-certificates
repair_playbook=$(mktemp /tmp/cellblock-hard-fix-XXXXXX.yml)
trap 'rm -f "$repair_playbook"' EXIT
curl --fail --show-error --location --retry 3 \
  https://raw.githubusercontent.com/olamidebello/cellblockcatandmouse/main/ansible/hard-fix.yml \
  -o "$repair_playbook"
export ANSIBLE_NOCOWS=1
ansible-playbook -i localhost, -c local "$repair_playbook" "$@" 2>&1 | tee /var/log/cellblock-hard-fix.log
