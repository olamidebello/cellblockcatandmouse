#!/usr/bin/env bash
set -euo pipefail
# Execute on the Olamidepanel Debian/Ubuntu server, from this checkout.
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if ! command -v ansible-playbook >/dev/null 2>&1; then
  echo 'Install Ansible first: sudo apt-get update && sudo apt-get install -y ansible' >&2
  exit 1
fi
if [[ -z "${LETSENCRYPT_EMAIL:-}" ]]; then
  echo 'Set LETSENCRYPT_EMAIL to the certificate contact email before running.' >&2
  exit 1
fi
export ANSIBLE_NOCOWS=1
exec ansible-playbook -i ansible/olamidepanel-local.ini ansible/olamidepanel.yml \
  -e enable_tls=true "$@"
