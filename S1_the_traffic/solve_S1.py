#!/usr/bin/env python3
# =====================================================================
#  RAVEN//TRACE — S1 "The Traffic"  :  AUTHOR SOLVE SCRIPT (canary)
# ---------------------------------------------------------------------
#  මේ script එක player කෙනෙක් Wireshark එකෙන් අතින් කරන වැඩේම
#  programmatically කරනවා — flag එක සහ RAVEN-17 identifier එක
#  pcap එකෙන් හරියට ලබාගන්න පුළුවන්ද කියලා ඔප්පු කරන්න.
#
#  Testing & Validation Plan එකේ "Tier 2 — Solvability" එකට මේක
#  ඔයාගේ evidence එක විදිහට පාවිච්චි කරන්න පුළුවන්.
#
#  පාවිච්චිය:  python3 solve_S1.py incident_traffic.pcap
# =====================================================================
import sys, re, base64
from scapy.all import rdpcap, TCP, Raw

EXPECTED_FLAG = "RAVEN{traffic_never_lies}"

def main(path):
    pkts = rdpcap(path)

    # 1) RAVEN-17 identifier එක carry කරන stream එක හොයනවා
    raven_ports = set()
    for p in pkts:
        if TCP in p and Raw in p:
            data = bytes(p[Raw].load)
            if b"X-Raven-ID: RAVEN-17" in data:
                # මේ packet එකේ C2 කතාව තියෙන්නේ. server port එක අල්ලගන්නවා.
                raven_ports.add(p[TCP].dport)   # client->server dport = C2 port
    print(f"[1] RAVEN-17 identifier found on C2 port(s): {sorted(raven_ports)}")

    # 2) ඒ stream එකේ client->server bytes ඔක්කොම එකතු කරනවා
    c2_port = sorted(raven_ports)[0]
    cli = b""
    for p in pkts:
        if TCP in p and Raw in p and p[TCP].dport == c2_port:
            cli += bytes(p[Raw].load)

    # 3) POST body (base64 "layer") එක decode කරනවා
    body = cli.split(b"\r\n\r\n")[-1].strip()
    decoded = base64.b64decode(body).decode(errors="replace")
    print("[2] decoded C2 exfil blob:")
    for line in decoded.strip().splitlines():
        print("      " + line)

    # 4) flag එක extract කරනවා
    m = re.search(r"RAVEN\{[a-z0-9_]+\}", decoded)
    flag = m.group(0) if m else None
    print(f"[3] recovered flag: {flag}")

    ok = (flag == EXPECTED_FLAG)
    print("[RESULT] PASS ✔" if ok else "[RESULT] FAIL ✘")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "incident_traffic.pcap"
    main(path)
