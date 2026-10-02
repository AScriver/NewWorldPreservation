"""CLI acceptance control, not a New World client test."""
import hashlib
import json
import os
import platform
import socket
import ssl
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
(root / ".scratch").mkdir(exist_ok=True)
run = Path(tempfile.mkdtemp(prefix="cli-", dir=root / ".scratch"))
probe_script = root / "scripts/connectivity_probe.py"
certificates = run / "certificates"
environment = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
with (run / "certificate-output.json").open("w", encoding="utf-8") as output:
    subprocess.run([sys.executable, str(probe_script), "certificates", "--directory", str(certificates)],
                   cwd=root, env=environment, stdout=output, stderr=subprocess.STDOUT, check=True, timeout=10)
with (run / "stderr.txt").open("w", encoding="utf-8") as errors:
    process = subprocess.Popen([sys.executable, str(probe_script), "serve", "--certificates", str(certificates),
                                "--log", str(run / "events.jsonl"), "--port", "0", "--duration", "2"],
                               cwd=root, env=environment, stdout=subprocess.PIPE, stderr=errors,
                               text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        ready = json.loads(process.stdout.readline())
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(cafile=str(certificates / "ca.pem"))
        with socket.create_connection((ready["bind"], ready["port"]), timeout=3) as raw:
            with context.wrap_socket(raw, server_hostname="localhost") as connection:
                connection.sendall(b"GET /__probe/health HTTP/1.1\r\nHost: localhost\r\n\r\n")
                response = bytearray()
                while chunk := connection.recv(4096):
                    response.extend(chunk)
        assert response.startswith(b"HTTP/1.1 200"), "Probe health control failed"
        assert process.wait(timeout=8) == 0
    finally:
        if process.poll() is None:
            process.terminate()  # Only the child this harness created.
            process.wait(timeout=5)
        process.stdout.close()
events = [json.loads(line) for line in (run / "events.jsonl").read_text().splitlines()]
assert events[-1]["state"] == "PROBE_STOPPED"
assert (run / "stderr.txt").read_text() == ""
with socket.socket() as closed_check:
    closed_check.settimeout(1)
    assert closed_check.connect_ex((ready["bind"], ready["port"])) != 0, "Probe listener was not closed"
certificate_identity = json.loads((certificates / "certificate-manifest.json").read_text())
receipt = {"observedAtUtc": datetime.now(timezone.utc).isoformat(), "mode": "python-cli-loopback-control",
           "status": "passed", "newWorldClientTested": False, "python": platform.python_version(),
           "probeSha256": hashlib.sha256(probe_script.read_bytes()).hexdigest(),
           "certificateLeafSha256": certificate_identity["leaf_sha256"],
           "trustedCA": "explicit Python SSL context only, no Windows trust-store edit",
           "request": "GET /__probe/health", "httpStatus": 200,
           "states": [event["state"] for event in events], "childExitCode": process.returncode,
           "listenerClosed": True, "stderrEmpty": True, "runDirectory": str(run.relative_to(root))}
(root / "research/evidence/connectivity-cli-control.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt))
