import os
import re
import time
import pathlib
import subprocess
import tempfile

from flask import Flask, request, jsonify

app = Flask(__name__)

ROOT = pathlib.Path(__file__).resolve().parent
RUN_SCRIPT = ROOT / "run.sh"
TIMEOUT = 120

TIME_RE = re.compile(r"Finished processing in ([\d.]+) seconds", re.I)


def run_lute_dump(source_code: str) -> dict:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = pathlib.Path(tmpdir)
        in_file = tmp / "input.lua"
        out_file = tmp / "out.lua"

        in_file.write_text(source_code, encoding="utf-8", errors="ignore")

        started = time.perf_counter()
        proc = subprocess.Popen(
            ["bash", str(RUN_SCRIPT), str(in_file), str(out_file)],
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
            return {"success": False, "error": "timeout", "took": TIMEOUT}

        took = time.perf_counter() - started
        m = TIME_RE.search(log or "")
        if m:
            took = float(m.group(1))

        if proc.returncode != 0 or not out_file.exists():
            tail = (log or "").strip().splitlines()[-1:] or ["unknown error"]
            return {"success": False, "error": tail[-1][:500], "took": took}

        head = out_file.read_text(errors="ignore")[:6]
        if head.startswith("--err"):
            reason = out_file.read_text(errors="ignore")[5:].strip()
            return {"success": False, "error": reason[:500] or "engine error", "took": took}

        result = out_file.read_text(errors="ignore")
        return {"success": True, "result": result, "took": took}


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
