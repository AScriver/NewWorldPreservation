"""Original synthetic private identity and isolated loopback consistency checks."""

from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import threading
import uuid

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import private_trial_character as trial  # noqa: E402
import queue_contract_probe as queue  # noqa: E402
import session_handoff_probe as selection  # noqa: E402
from current_player_creation_candidate import (  # noqa: E402
    OWNED_PLAYER_ASSET, compose_player_creation_candidate,
)
from current_creation_member_body import MEMBER_UUID as CREATION_UUID  # noqa: E402
from current_player_identity_body import MEMBER_UUID as IDENTITY_UUID  # noqa: E402
from test_token_contract_probe import exchange  # noqa: E402


UUIDS = (
    "11000000-0000-4000-8000-000000000001",
    "22000000-0000-4000-8000-000000000002",
    "33000000-0000-4000-8000-000000000003",
    "44000000-0000-4000-8000-000000000004",
)
GDE_REF = bytes.fromhex("0200000001000000aabbccddeeff1122")


def record():
    return trial.PrivateTrialCharacter(*UUIDS, "Preservation One",
                                       "2026-10-06T22:00:00Z", GDE_REF)


@pytest.fixture
def private_path(tmp_path):
    # tmp_path is external; the persistence API requires this project's ignored area.
    target = ROOT / ".scratch" / "identity253-implementer" / tmp_path.name / "character.json"
    try:
        yield target
    finally:
        if target.exists():
            target.unlink()
        if target.parent.exists():
            target.parent.rmdir()


def test_fresh_independent_domains_and_once_assigned_ref(monkeypatch):
    draws = iter(uuid.UUID(value) for value in UUIDS)
    monkeypatch.setattr(trial.uuid, "uuid4", lambda: next(draws))
    monkeypatch.setattr(trial, "new_trial_ref", lambda *, occupied_keys: GDE_REF)
    result = trial.new_trial_character(occupied_keys=frozenset(), name="Preservation One")
    assert tuple(getattr(result, key) for key in ("session_id", "character_id",
        "persona_id", "ticket_id")) == UUIDS
    assert len(set(UUIDS)) == 4
    assert not set(UUIDS) & trial.FIXTURE_IDS
    assert result.gde_ref is GDE_REF
    assert result.created_at.endswith("Z")
    assert result.character_id != "00000000-0000-4000-8000-000000000020"
    assert result.identity_body().character_id == result.character_id.encode("utf-8")
    assert result.identity_body().character_name == result.name.encode("utf-8")
    with pytest.raises(FrozenInstanceError):
        result.name = "changed"


@pytest.mark.parametrize("change", [
    dict(session_id="00000000-0000-0000-0000-000000000000"),
    dict(character_id="00000000-0000-4000-8000-000000000020"),
    dict(persona_id="00000000-0000-4000-8000-000000000002"),
    dict(ticket_id="00000000-0000-4000-8000-000000000030"),
    dict(character_id="aa000000-0000-4000-8000-000000000002".upper()),
    dict(persona_id=UUIDS[1]), dict(ticket_id="not-a-uuid"),
    dict(name=""), dict(name="Trailing "), dict(name="Other\x00Name"),
    dict(name="é"), dict(name="A" * 33),
    dict(created_at="2026-10-06T22:00:00+00:00"),
    dict(created_at="2026-02-30T22:00:00Z"),
    dict(gde_ref=bytes(16)),
])
def test_record_requires_exact_original_domains_and_fields(change):
    with pytest.raises(ValueError):
        replace(record(), **change)


def test_exclusive_private_roundtrip_and_occupancy(private_path):
    path = private_path
    source = record()
    assert trial.write_trial_character(path, source) == path.resolve()
    assert trial.read_trial_character(path, occupied_keys=frozenset()) == source
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert trial.read_trial_character(path, occupied_keys=frozenset(),
                                      expected_sha256=digest) == source
    with pytest.raises(ValueError, match="SHA256"):
        trial.read_trial_character(path, occupied_keys=frozenset(),
                                   expected_sha256="0" * 64)
    assert json.loads(path.read_text())["gde_ref"] == GDE_REF.hex()
    with pytest.raises(FileExistsError):
        trial.write_trial_character(path, source)
    with pytest.raises(ValueError, match="occupied"):
        trial.read_trial_character(path, occupied_keys=frozenset({0x100000002}))
    with pytest.raises(ValueError):
        trial.new_trial_character(occupied_keys=frozenset({0x100000002}), name="Bad\x00Name")


def test_queue_cli_digest_and_file_must_cooccur_before_certificate_access(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("certificate path or listener reached")
    monkeypatch.setattr(queue.selection.credentials.token.bootstrap.probe,
                        "private_directory", forbidden)
    base = ["queue_contract_probe.py", "--certificates", "unread",
            "--descriptor", "unread", "--log", "unread", "--case", "token-loopback"]
    for ancillary in (
        ["--trial-character", "unread", "--trial-known-empty-occupancy"],
        ["--trial-character-sha256", "0" * 64],
        ["--trial-character-sha256", "0" * 64, "--trial-known-empty-occupancy"],
    ):
        monkeypatch.setattr(sys, "argv", base + ancillary)
        with pytest.raises(SystemExit) as raised:
            queue.main()
        assert raised.value.code == 2


def test_path_schema_duplicate_and_extent_guards(private_path):
    # pytest's basetemp may be inside project .scratch; own an external directory.
    with TemporaryDirectory(prefix="nwp-trial-path-", dir=ROOT.parent) as external_dir:
        outside = Path(external_dir) / "external.json"
        with pytest.raises(ValueError, match=".scratch"):
            trial.write_trial_character(outside, record())
        with pytest.raises(ValueError, match=".scratch"):
            trial.read_trial_character(outside, occupied_keys=frozenset())
    path = private_path
    path.parent.mkdir(parents=True, exist_ok=True)
    base = json.loads(json.dumps({
        "classification": trial.CLASSIFICATION,
        "session_id": UUIDS[0], "character_id": UUIDS[1],
        "persona_id": UUIDS[2], "ticket_id": UUIDS[3],
        "name": "Preservation One", "created_at": "2026-10-06T22:00:00Z",
        "gde_ref": GDE_REF.hex(),
    }))
    invalid = [
        {**base, "classification": "official"}, {**base, "unknown": 1},
        {key: value for key, value in base.items() if key != "ticket_id"},
        {**base, "gde_ref": GDE_REF.hex().upper()},
        [base],
    ]
    for value in invalid:
        path.write_text(json.dumps(value), encoding="utf-8")
        with pytest.raises(ValueError):
            trial.read_trial_character(path, occupied_keys=frozenset())
    raw = json.dumps(base)
    path.write_text(raw[:-1] + ',"name":"duplicate"}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        trial.read_trial_character(path, occupied_keys=frozenset())
    path.write_bytes(b" " * (trial.MAX_FILE_BYTES + 1))
    with pytest.raises(ValueError, match="bound"):
        trial.read_trial_character(path, occupied_keys=frozenset())


def test_admin_cli_creates_verifies_and_refuses_overwrite(private_path, monkeypatch, capsys):
    command = ["private_trial_character.py", "create", "--path", str(private_path),
               "--known-empty-occupancy", "--name", "Preservation One"]
    monkeypatch.setattr(sys, "argv", command)
    assert trial.main() == 0
    first = private_path.read_bytes()
    created = trial.read_trial_character(private_path, occupied_keys=frozenset())
    assert created.identity_body().character_id == created.character_id.encode()
    monkeypatch.setattr(sys, "argv", ["private_trial_character.py", "verify",
        "--path", str(private_path), "--known-empty-occupancy"])
    assert trial.main() == 0
    assert private_path.read_bytes() == first
    monkeypatch.setattr(sys, "argv", command)
    with pytest.raises(SystemExit) as raised:
        trial.main()
    assert raised.value.code == 2
    assert private_path.read_bytes() == first
    output = capsys.readouterr()
    assert created.character_id not in output.out + output.err
    assert created.gde_ref.hex() not in output.out + output.err


def test_default_responses_still_match_fixed_fixture_bytes():
    for case in selection.CASES:
        model = json.loads((ROOT / "tests/fixtures/connectivity/current-login-info-candidate.json").read_text())
        if case == "empty-characters":
            model["LoginInfoList"]["Characters"] = []
        assert selection.response_case(case) == json.dumps(model, sort_keys=True,
            separators=(",", ":")).encode("utf-8")
    for case in queue.CASES:
        model = json.loads((ROOT / "tests/fixtures/connectivity/current-queue-parser-candidate.json").read_text())
        if case == "token-empty":
            model["LoginQueueResponse"]["Token"] = {}
        assert queue.response_case(case) == json.dumps(model, sort_keys=True,
            separators=(",", ":")).encode()


def test_early_case_and_type_failures_before_certificates_or_bind(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("certificate material or bind reached")
    monkeypatch.setattr(selection.credentials, "make_server", forbidden)
    for bad_case, value in (("empty-characters", record()), ("seed-character", object())):
        with pytest.raises(ValueError):
            selection.make_server("127.0.0.1", 0, Path("unread"), None, {},
                                  case=bad_case, trial_character=value)
    for bad_case, value in (("token-empty", record()), ("token-loopback", object())):
        with pytest.raises(ValueError):
            queue.make_server("127.0.0.1", 0, Path("unread"), None, {},
                              case=bad_case, trial_character=value)


def test_isolated_https_selection_queue_identity_and_candidate(tmp_path):
    bootstrap = selection.credentials.token.bootstrap
    certificates = tmp_path / "certificates"
    bootstrap.probe.generate_certificates(certificates, [bootstrap.BOOTSTRAP_HOST,
        selection.credentials.token.TOKEN_HOST, "prod.newworld.com"])
    event_log = bootstrap.probe.EventLog(tmp_path / "events.jsonl")
    descriptor = bootstrap.load_local_descriptor(
        ROOT / "tests/fixtures/connectivity/local-channel-token-hostnames.json",
        token_routing="original-hostnames")
    source = record()
    server = None
    thread = None
    try:
        server = queue.make_server("127.0.0.1", 0, certificates, event_log,
                                   descriptor, case="token-loopback", trial_character=source)
        assert server.trial_character is source
        thread = threading.Thread(target=server.serve_forever,
                                  kwargs={"poll_interval": 0.05})
        thread.start()
        endpoint = (server, certificates, tmp_path / "events.jsonl")
        selection_raw = exchange(endpoint, method="GET", host=bootstrap.BOOTSTRAP_HOST,
            path="/prod/game/getlogininfo/PRIVATE/omni", authorization="synthetic")
        queue_raw = exchange(endpoint, method="POST", host=bootstrap.BOOTSTRAP_HOST,
            path="/prod/game/login/queue/v2/PRIVATE/omni", authorization="synthetic",
            body=b"synthetic-private-request")
        assert selection_raw.startswith(b"HTTP/1.1 200")
        assert queue_raw.startswith(b"HTTP/1.1 200")
        selected = json.loads(selection_raw.split(b"\r\n\r\n", 1)[1])["LoginInfoList"]["Characters"][0]
        response = json.loads(queue_raw.split(b"\r\n\r\n", 1)[1])["LoginQueueResponse"]
        token = response["Token"]
        assert selected["CharacterId"] == token["CharacterId"] == source.character_id
        assert selected["PersonaId"] == token["PersonaId"] == source.persona_id
        assert selected["Name"] == source.name
        assert selected["CreatedDate"] == selected["ModifiedDate"] == source.created_at
        assert response["TicketId"] == token["TicketId"] == source.ticket_id
        assert selected["WorldId"] == token["WorldId"] == "pdx-nwp-local-1"
        assert token["LocationId"] == "pdx-nwp-local-1"
        assert source.identity_body().character_id == selected["CharacterId"].encode("utf-8")
        assert source.identity_body().character_name == selected["Name"].encode("utf-8")
        candidate = compose_player_creation_candidate(
            slot=0, creation_key=0, identity_key=9,
            creation_class_index=0, identity_class_index=0,
            class_table=(bytes(16), CREATION_UUID, IDENTITY_UUID),
            asset_id=OWNED_PLAYER_ASSET, assigned_gde_ref=source.gde_ref,
            occupied_keys=frozenset(),
            character_id=source.identity_body().character_id,
            character_name=source.identity_body().character_name,
            delivery_mode="resource-index")
        assert candidate.record.members[1].body == source.identity_body()
        assert candidate.record.members[0].body.gde_ref == source.gde_ref
        assert source.character_id.encode() in candidate.typed_bytes
    finally:
        if server is not None:
            if thread is not None and thread.is_alive():
                server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout=3)
            assert not thread.is_alive()
        event_log.close()
    log_text = (tmp_path / "events.jsonl").read_text(encoding="utf-8")
    assert source.character_id not in log_text
    assert source.ticket_id not in log_text
    assert source.gde_ref.hex() not in log_text
    assert "synthetic-private-request" not in log_text
