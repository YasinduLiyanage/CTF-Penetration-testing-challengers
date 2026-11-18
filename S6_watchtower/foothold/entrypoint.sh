#!/bin/sh
# =====================================================================
#  SSH host entrypoint  —  foothold / watchtower-gw දෙකටම පොදුයි
# ---------------------------------------------------------------------
#  env වලින් එන SSH_USER / SSH_PASS එකෙන් user කෙනෙක් හදනවා,
#  host keys generate කරලා, sshd එක foreground එකේ run කරනවා.
# =====================================================================
set -e

: "${SSH_USER:=player}"
: "${SSH_PASS:=player}"

# user එක නැත්නම් හදනවා (shell = /bin/sh)
if ! id "$SSH_USER" >/dev/null 2>&1; then
    adduser -D -s /bin/sh "$SSH_USER"
fi
# password එක set කරනවා (මේකෙන් account එක unlock වෙනවා)
echo "${SSH_USER}:${SSH_PASS}" | chpasswd

# host keys (නැත්නම් හදනවා)
ssh-keygen -A

echo "[entrypoint] sshd starting — user='${SSH_USER}'"
# -D = foreground, -e = log to stderr
exec /usr/sbin/sshd -D -e
