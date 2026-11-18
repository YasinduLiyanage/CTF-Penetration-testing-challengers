#!/usr/bin/env python3
# =====================================================================
#  WATCHTOWER  —  monitoring / telemetry service  (S6 final target)
# ---------------------------------------------------------------------
#  මේ service එක තියෙන්නේ "monitoring segment" (net_mon) එකේ විතරයි.
#  player කෙනෙකුට මේකට කෙලින්ම access කරන්න බෑ — watchtower-gw
#  (pivot host) එක හරහා විතරයි reach කරන්න පුළුවන්.
#
#  හැම endpoint එකක්ම header   X-WT-Key: <WATCHTOWER_API_KEY>   ඉල්ලනවා.
#  ඒ key එක player ට හම්බවෙන්නේ S5 (web exploit) එකෙන්.
#
#  Flag: evidence package එක ඇතුළේ -> RAVEN{you_were_the_attacker}
# =====================================================================
import os, json, functools
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

API_KEY = os.environ.get("WATCHTOWER_API_KEY", "changeme")
SEED = os.path.join(os.path.dirname(__file__), "seed")

def load(name):
    with open(os.path.join(SEED, name), "r", encoding="utf-8") as f:
        return f.read()

def require_key(fn):
    """හැම protected endpoint එකකටම X-WT-Key header එක check කරනවා."""
    @functools.wraps(fn)
    def wrapper(*a, **kw):
        key = request.headers.get("X-WT-Key", "")
        if key != API_KEY:
            return jsonify({
                "error": "WATCHTOWER access denied",
                "reason": "missing or invalid X-WT-Key",
                "hint": "This key is an S5 artifact (recovered from the portal)."
            }), 403
        return fn(*a, **kw)
    return wrapper

@app.route("/")
def banner():
    return jsonify({
        "service": "WATCHTOWER",
        "segment": "monitoring (not externally exposed)",
        "auth": "all data endpoints require header  X-WT-Key",
        "endpoints": ["/telemetry", "/operations/nightfall", "/evidence"]
    })

@app.route("/healthz")
def healthz():
    return "ok", 200

@app.route("/telemetry")
@require_key
def telemetry():
    return Response(load("telemetry.json"), mimetype="application/json")

@app.route("/operations/nightfall")
@require_key
def nightfall():
    return Response(load("nightfall_oplog.json"), mimetype="application/json")

@app.route("/evidence")
@require_key
def evidence():
    return Response(load("evidence_package.txt"), mimetype="text/plain")

if __name__ == "__main__":
    # 0.0.0.0 — container network එක ඇතුළේ විතරයි access වෙන්නේ
    app.run(host="0.0.0.0", port=9000)
