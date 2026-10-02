"""Validate the observed metadata fixture without pretending it is raw wire."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fixture_probe', ROOT / 'scripts/connectivity_probe.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def test_observed_bootstrap_fixture_preserves_route_and_acceptance_boundary():
    fixture = json.loads((ROOT / 'tests/fixtures/connectivity/current-client-bootstrap.json').read_text())
    request = fixture['request']
    assert fixture['kind'] == 'observed-current-client-metadata-not-raw-wire-or-server-schema'
    assert probe.route_id(request['path'])[0] == 'channel_discovery'
    assert request['method'] == 'GET' and request['httpVersion'] == 'HTTP/1.1'
    assert request['tlsVersion'] == 'TLSv1.2' and request['responseStatus'] == 501
    assert request['authorizationPresent'] is False and request['cookiePresent'] is False
    assert request['declaredBodyBytes'] == 0
    assert fixture['authenticationSucceeded'] is False and fixture['worldEntered'] is False
    assert fixture['differentialControls'] == {
        'untrusted_ca_http_requests': 0, 'trusted_correct_name_http_requests': 3,
        'trusted_wrong_name_http_requests': 0, 'correct_name_restored_http_requests': 3}
    assert 'CONNECTION_OWNER_OBSERVED' in fixture['observedSequence']


def test_fixture_provenance_and_real_game_result_remain_separate_from_controls():
    fixture = json.loads((ROOT / 'tests/fixtures/connectivity/current-client-bootstrap.json').read_text())
    receipt = json.loads((ROOT / fixture['provenance']['receipt']).read_text())
    assert fixture['provenance']['steamBuildId'] == receipt['client']['steamBuildId']
    assert fixture['request'] == receipt['bootstrap']
    assert fixture['provenance']['requestSourceSha256'] in [item['sha256'] for item in receipt['sources']]
    assert receipt['authenticationSucceeded'] is False and receipt['milestone1Achieved'] is False
    assert [phase['httpRequests'] for phase in receipt['phases']] == [0,3,0,3,0,3]
    for phase in receipt['phases'][3:]:
        assert phase['exactSocketOwnerPids'] == [phase['launchCorrelation']['process_id']]
        assert phase['launchCorrelation']['live_executable_path_verified'] is False
