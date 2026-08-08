#!/bin/bash
set -e

CPT_DIR="$HOME/.cpt"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$CPT_DIR"
cp -r "$SCRIPT_DIR"/* "$CPT_DIR/"
mv "$CPT_DIR/main.py" "$CPT_DIR/cpt"

chmod a+x "$CPT_DIR/cpt" "$CPT_DIR"/judgers/*.py
if [ ! -f "$HOME/.bashrc" ] || ! grep -q 'export PATH=.*\$HOME/.cpt' "$HOME/.bashrc"; then
    cat >>"$HOME/.bashrc" <<-EOF
export PATH="\$PATH:\$HOME/.cpt"
EOF
fi
