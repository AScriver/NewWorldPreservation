"""Behavioral checks preventing a falsely green offline verification receipt."""
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("validation", Path(__file__).parents[1] / "scripts/validate_first_light.py")
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


def test_reports_failures_errors_and_unexpected_skips(tmp_path):
    junit = tmp_path / "result.xml"
    junit.write_text('<testsuites><testsuite><testcase classname="a" name="pass"/>'
                     '<testcase classname="a" name="fail"><failure>private body</failure></testcase>'
                     '<testcase classname="a" name="error"><error/></testcase>'
                     '<testcase classname="a" name="skip"><skipped message="missing fixture"/></testcase>'
                     '</testsuite></testsuites>')
    result = validation.parse_junit(junit)
    assert result == {"total": 4, "passed": 1, "failed": 1, "errors": 1,
                      "skipped": 1, "unexpectedSkips": ["a::skip"]}
    assert "private body" not in str(result)
    assert not validation.validation_passed(result, 0)


@pytest.mark.parametrize("exit_code,total,failed,errors,skips", [
    (1, 456, 0, 0, []), (0, 0, 0, 0, []), (0, 456, 1, 0, []),
    (0, 456, 0, 1, []), (0, 456, 0, 0, ["missing fixture"]),
])
def test_rejects_false_green_results(exit_code, total, failed, errors, skips):
    assert not validation.validation_passed({"total": total, "failed": failed,
                                           "errors": errors, "unexpectedSkips": skips}, exit_code)


def test_accepts_pinned_complete_profile():
    assert validation.validation_passed({"total": 456, "failed": 0,
                                        "errors": 0, "unexpectedSkips": []}, 0)


def test_unidentified_skip_without_message_is_not_approved(tmp_path):
    junit = tmp_path / "result.xml"
    junit.write_text('<testsuite><testcase classname="a" name="skipped"><skipped/></testcase></testsuite>')
    assert validation.parse_junit(junit)["unexpectedSkips"] == ["a::skipped"]


def test_approved_skip_requires_exact_identity_and_reason(tmp_path):
    case_id, reason = next(iter(validation.EXPECTED_SKIPS.items()))
    classname, name = case_id.split("::")
    junit = tmp_path / "result.xml"
    junit.write_text(f'<testsuite><testcase classname="{classname}" name="{name}">'
                     f'<skipped message="{reason}"/></testcase></testsuite>')
    assert validation.parse_junit(junit)["unexpectedSkips"] == []
    junit.write_text(f'<testsuite><testcase classname="{classname}" name="{name}">'
                     '<skipped message="missing fixture"/></testcase></testsuite>')
    assert validation.parse_junit(junit)["unexpectedSkips"] == [case_id]
