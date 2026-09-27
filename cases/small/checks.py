import json
import sys
import time
import urllib.error
import urllib.request

TIMEOUT = 5


def call(base, method, path, body=None, headers=None, raw=None):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(base + path, data=data, method=method, headers=headers or {})
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            status, payload = resp.status, resp.read()
    except urllib.error.HTTPError as err:
        status, payload = err.code, err.read()
    return status, json.loads(payload) if payload else None


def expect(cond, message):
    if not cond:
        raise AssertionError(message)


def expect_error(status, body, want_status, want_code):
    expect(status == want_status, f"status {status}, want {want_status}")
    err = (body or {}).get("error") or {}
    expect(err.get("code") == want_code, f"error code {err.get('code')!r}, want {want_code!r}")
    expect(isinstance(err.get("message"), str) and err["message"], "error.message missing")


def create(base, title, body="", key=None):
    headers = {"Idempotency-Key": key} if key else {}
    return call(base, "POST", "/notes", {"title": title, "body": body}, headers)


def check_health(base):
    status, body = call(base, "GET", "/health")
    expect(status == 200 and body == {"status": "ok"}, f"got {status} {body}")


def check_reset(base):
    create(base, "to be wiped")
    status, body = call(base, "POST", "/_test/reset")
    expect(status == 204 and body is None, f"got {status} {body}")
    expect(call(base, "GET", "/notes") == (200, {"notes": []}), "notes not empty after reset")


def check_create(base):
    status, note = create(base, "  first  ", "hello")
    expect(status == 201, f"status {status}")
    expect(note["title"] == "first" and note["body"] == "hello", f"fields {note}")
    expect(isinstance(note["id"], str) and note["id"], "id missing")
    expect(note["created_at"].endswith(("Z", "+00:00")), f"created_at not UTC: {note['created_at']}")
    status, default = call(base, "POST", "/notes", {"title": "no body"})
    expect(status == 201 and default["body"] == "", f"default body {status} {default}")


def check_get_and_list_order(base):
    _, a = create(base, "a")
    _, b = create(base, "b")
    expect(call(base, "GET", f"/notes/{a['id']}") == (200, a), "get returned a different note")
    status, body = call(base, "GET", "/notes")
    ids = [n["id"] for n in body["notes"]]
    expect(status == 200 and ids == [a["id"], b["id"]], f"list order {ids}")


def check_idempotent_replay(base):
    first = create(base, "once", key="k-1")
    again = create(base, "once", key="k-1")
    expect(first[0] == 201 and again == first, f"replay {again} != {first}")
    _, body = call(base, "GET", "/notes")
    expect(len(body["notes"]) == 1, f"{len(body['notes'])} notes after replay")


def check_idempotent_conflict(base):
    create(base, "original", key="k-2")
    status, body = create(base, "changed", key="k-2")
    expect_error(status, body, 409, "idempotency_conflict")
    _, listed = call(base, "GET", "/notes")
    expect(len(listed["notes"]) == 1, "conflict created a note")


def check_validation(base):
    for payload in ({"title": ""}, {"title": "   "}, {"title": "x" * 201}, {}, {"title": 7},
                    {"title": "ok", "body": "x" * 10001}):
        status, body = call(base, "POST", "/notes", payload)
        expect_error(status, body, 422, "validation_error")
    status, body = call(base, "POST", "/notes", raw=b"{not json")
    expect_error(status, body, 400, "bad_request")
    status, body = call(base, "POST", "/notes", [1, 2])
    expect_error(status, body, 400, "bad_request")
    expect(call(base, "GET", "/notes") == (200, {"notes": []}), "invalid request created a note")


def check_not_found(base):
    status, body = call(base, "GET", "/notes/does-not-exist")
    expect_error(status, body, 404, "not_found")
    status, body = call(base, "GET", "/nowhere")
    expect_error(status, body, 404, "not_found")


def check_delete(base):
    _, note = create(base, "short lived")
    status, body = call(base, "DELETE", f"/notes/{note['id']}")
    expect(status == 204 and body is None, f"delete {status} {body}")
    status, body = call(base, "GET", f"/notes/{note['id']}")
    expect_error(status, body, 404, "not_found")
    status, body = call(base, "DELETE", f"/notes/{note['id']}")
    expect_error(status, body, 404, "not_found")
    _, again = create(base, "after delete")
    expect(again["id"] != note["id"], "id reused after delete")


CHECKS = [check_health, check_reset, check_create, check_get_and_list_order,
          check_idempotent_replay, check_idempotent_conflict, check_validation,
          check_not_found, check_delete]


def main():
    if len(sys.argv) != 2:
        print("usage: python3 checks.py <base-url>", file=sys.stderr)
        return 2
    base = sys.argv[1].rstrip("/")
    started = time.monotonic()
    results = []
    for check in CHECKS:
        try:
            call(base, "POST", "/_test/reset")
            check(base)
            results.append((check.__name__, None))
        except Exception as exc:
            results.append((check.__name__, f"{type(exc).__name__}: {exc}"))
    failed = [r for r in results if r[1]]
    print(f"checks: {len(results) - len(failed)} passed, {len(failed)} failed, "
          f"{time.monotonic() - started:.1f}s, {base}")
    for name, error in results:
        print(f"{'FAIL' if error else 'ok  '} {name}" + (f" — {error}" if error else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
