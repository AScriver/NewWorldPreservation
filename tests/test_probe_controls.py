"""Added control paths: same-CA negative SAN and opt-in socket attribution."""
import importlib.util
import json
import socket
import ssl
import threading
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

spec = importlib.util.spec_from_file_location("probe_controls", Path(__file__).parents[1] / "scripts/connectivity_probe.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def test_negative_name_leaf_has_same_ca_key_but_distinct_identity(tmp_path):
    certificates = tmp_path / "certificates"
    manifest = probe.generate_certificates(certificates, ["localhost"], hostname_negative_control=True)
    ca = x509.load_pem_x509_certificate((certificates / "ca.pem").read_bytes())
    correct = x509.load_pem_x509_certificate((certificates / "server.pem").read_bytes())
    wrong = x509.load_pem_x509_certificate((certificates / "hostname-negative.pem").read_bytes())
    for leaf in [correct, wrong]:
        ca.public_key().verify(leaf.signature, leaf.tbs_certificate_bytes, padding.PKCS1v15(), leaf.signature_hash_algorithm)
    assert correct.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo) == wrong.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    assert correct.serial_number != wrong.serial_number
    assert wrong.fingerprint(hashes.SHA256()).hex() == manifest["hostname_negative_control"]["leaf_sha256"]
    assert "localhost" not in wrong.extensions.get_extension_for_class(x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName)
    assert not (certificates / "ca.key").exists()


@pytest.mark.parametrize("negative_name", [False, True])
def test_same_ca_validation_and_exact_client_side_owner_tuple(tmp_path, negative_name):
    certificates = tmp_path / "certificates"
    probe.generate_certificates(certificates, ["localhost"], hostname_negative_control=True)
    log_path = tmp_path / "events.jsonl"
    log = probe.EventLog(log_path)
    server = probe.make_server("127.0.0.1", 0, certificates, log, hostname_negative_control=negative_name)
    looked_up = []
    server.socket_owner_lookup = lambda *address: looked_up.append(address) or 4242
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
    thread.start()
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile=str(certificates / "ca.pem"))
    try:
        with socket.create_connection(server.server_address) as raw:
            client_address = raw.getsockname()
            if negative_name:
                with pytest.raises(ssl.SSLCertVerificationError) as rejected:
                    context.wrap_socket(raw, server_hostname="localhost")
                assert rejected.value.verify_code == 62 # OpenSSL hostname mismatch, not CA failure.
            else:
                with context.wrap_socket(raw, server_hostname="localhost") as trusted:
                    trusted.sendall(b"GET /__probe/health HTTP/1.1\r\nHost: localhost\r\n\r\n")
                    while trusted.recv(4096):
                        pass
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        log.close()
    assert looked_up == [(*client_address, *server.server_address)]
    events = [json.loads(line) for line in log_path.read_text().splitlines()]
    attribution = next(item for item in events if item["state"] == "CONNECTION_OWNER_OBSERVED")
    assert attribution["process_id"] == 4242
    assert attribution["client_identity"] == "unattributed"
    requests = [item for item in events if item["state"] == "HTTP_REQUEST"]
    assert len(requests) == (0 if negative_name else 1)
    if requests:
        assert requests[0]["http_version"] == "HTTP/1.1"
