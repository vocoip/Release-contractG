#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")"
chmod +x contractG/run.command
exec contractG/run.command
