#!/bin/bash
for manifest in "${1:-.}"/*/__manifest__.py; do
    [ -f "$manifest" ] || continue
    if grep -Eq "^\s*['\"]installable['\"]\s*:\s*False" "$manifest"; then
        continue
    fi
    dirname "$manifest"
done
