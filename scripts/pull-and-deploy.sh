#!/usr/bin/env bash
set -euo pipefail
# Use from any directory; the hard-fix entry point pulls current server source.
exec bash "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/hard-fix-server.sh" "$@"
