import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location("small_checks", Path(__file__).parent.parent / "small" / "checks.py")
small = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(small)
call, expect, expect_error = small.call, small.expect, small.expect_error
check_health = small.check_health


def create(base, title):
    return call(base, "POST", "/notes", {"title": title})


def check_reset(base):
    _, note = create(base, "to be wiped")
    status, body = call(base, "POST", "/_test/reset")
    expect(status == 204 and body is None, f"got {status} {body}")
    status, body = call(base, "GET", f"/notes/{note['id']}")
    expect_error(status, body, 404, "not_found")


def check_create_and_get(base):
    status, note = create(base, "first")
    expect(status == 201, f"status {status}")
    expect(note.get("title") == "first", f"title {note}")
    expect(isinstance(note.get("id"), str) and note["id"], "id missing")
    _, other = create(base, "second")
    expect(other["id"] != note["id"], "ids not unique")
    expect(call(base, "GET", f"/notes/{note['id']}") == (200, note), "get does not return the note")


def check_not_found(base):
    status, body = call(base, "GET", "/notes/does-not-exist")
    expect_error(status, body, 404, "not_found")
    status, body = call(base, "GET", "/nowhere")
    expect_error(status, body, 404, "not_found")
    status, body = call(base, "DELETE", "/notes/x")
    expect_error(status, body, 404, "not_found")


def check_validation(base):
    status, body = call(base, "POST", "/notes", raw=b"[1]")
    expect_error(status, body, 400, "bad_request")
    status, body = call(base, "POST", "/notes", raw=b"{not json")
    expect_error(status, body, 400, "bad_request")
    for bad in ({}, {"title": ""}, {"title": 7}, {"title": "x" * 101}):
        status, body = call(base, "POST", "/notes", bad)
        expect_error(status, body, 422, "validation_error")
    status, _ = create(base, "x" * 100)
    expect(status == 201, f"100-character title rejected: {status}")


CHECKS = [check_health, check_reset, check_create_and_get, check_not_found, check_validation]


if __name__ == "__main__":
    sys.exit(small.main(CHECKS))
