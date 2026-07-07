import os
import re
import time
import pathlib
import subprocess

from flask import Flask, request, jsonify

app = Flask(__name__)

ROOT = pathlib.Path(__file__).resolve().parent
RUN_SCRIPT = ROOT / "runner.sh"
TIMEOUT = 120

TIME_RE = re.compile(r"Finished processing in ([\d.]+) seconds", re.I)


def run_lute_dump(source_code: str) -> dict:
    stamp = f"{int(time.time()*1000)}_{os.getpid()}"
    in_name = f"in_{stamp}.lua"
    out_name = f"out_{stamp}.lua"
    in_path = ROOT / in_name
    out_path = ROOT / out_name

    in_path.write_text(source_code, encoding="utf-8", errors="ignore")

    started = time.perf_counter()
    proc = subprocess.Popen(
        ["bash", str(RUN_SCRIPT), in_name, out_name],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        log, _ = proc.communicate(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.communicate(timeout=5)
        except Exception:
            pass
        _cleanup(in_path, out_path)
        return {"success": False, "error": "timeout", "took": TIMEOUT}

    took = time.perf_counter() - started
    m = TIME_RE.search(log or "")
    if m:
        took = float(m.group(1))

    try:
        if proc.returncode != 0 or not out_path.exists():
            tail = (log or "").strip().splitlines()[-1:] or ["unknown error"]
            return {"success": False, "error": tail[-1][:500], "took": took}

        head = out_path.read_text(errors="ignore")[:6]
        if head.startswith("--err"):
            reason = out_path.read_text(errors="ignore")[5:].strip()
            return {"success": False, "error": reason[:500] or "engine error", "took": took}

        result = out_path.read_text(errors="ignore")
        return {"success": True, "result": result, "took": took}
    finally:
        _cleanup(in_path, out_path)


def _cleanup(*paths):
    for p in paths:
        try:
            p.unlink()
        except OSError:
            pass


@app.route("/deobfuscate", methods=["POST"])
def deobfuscate():
    data = request.get_json()
    if not data or "code" not in data:
        return jsonify({"success": False, "error": "Missing 'code' field"}), 400

    result = run_lute_dump(data["code"])
    status = 200 if result["success"] else 500
    return jsonify(result), status


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
