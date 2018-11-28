#!/bin/sh

set -e

tmpfile=$(mktemp)

cat >"$tmpfile" <<EOF
     Key-Type: default
     Key-Length: 4096
     Subkey-Type: default
     Subkey-Length: 4096
     Name-Real: $1
     Name-Email: $2
     Expire-Date: 0
     Passphrase: $3
     %commit
EOF

gpg --batch --generate-key ${tmpfile}

rm ${tmpfile}

gpg --export -a "$1"

echo "$3\n" | gpg --batch --export-secret-key -a --pinentry-mode loopback --passphrase-fd 0 "$1"