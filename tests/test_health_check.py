"""Tests for the tiny health-check HTTP server bot.py runs for Render/UptimeRobot.
UptimeRobot's default 'HTTP(s)' monitor type sends HEAD requests, not GET —
this used to only have a do_GET handler, which would have made UptimeRobot's
checks fail (BaseHTTPRequestHandler returns 501 Unsupported Method for any
verb without a matching do_* method)."""
import io

import bot


def _run_request(method):
    handler = bot._HealthCheckHandler.__new__(bot._HealthCheckHandler)
    handler.wfile = io.BytesIO()
    handler.rfile = io.BytesIO(b"")
    handler.requestline = f"{method} / HTTP/1.1"
    handler.request_version = "HTTP/1.1"
    handler.command = method
    handler.headers = {}
    handler.client_address = ("127.0.0.1", 12345)

    sent = {"status": None}
    handler.send_response = lambda code, message=None: sent.__setitem__("status", code)
    handler.send_header = lambda *a, **kw: None
    handler.end_headers = lambda: None

    getattr(handler, f"do_{method}")()
    return sent["status"], handler.wfile.getvalue()


def test_get_returns_200_with_a_body():
    status, body = _run_request("GET")
    assert status == 200
    assert body == b"Study Buddy bot is alive!"


def test_head_returns_200_with_no_body():
    """This is the exact case UptimeRobot needs — without do_HEAD, this would
    404/501 and UptimeRobot would report the bot as down even while it's fine."""
    status, body = _run_request("HEAD")
    assert status == 200
    assert body == b""
