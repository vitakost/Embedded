"""Own tests for the ESP32 JSON CLI (Webinar 6 homework).

Expected results follow requirements/device_requirements.md (R1..R10).
The `device` fixture sends RESET before and after every test.
"""
import time

import pytest


def ok(r, cmd):
    assert r.get("status") == "OK", f"{cmd}: expected status=OK, got {r}"
    return r


def status(device):
    return ok(device.command("STATUS"), "STATUS")


# ---------- R5: every integer 0..100 is accepted (boundary + full range) ----------

@pytest.mark.parametrize("value", [0, 1, 2, 49, 50, 51, 98, 99, 100])
def test_pwm_boundary_values_accepted(device, value):
    r = device.command(f"SET PWM {value}")
    ok(r, f"SET PWM {value}")
    assert r.get("pwm") == value, f"SET PWM {value}: echoed pwm={r.get('pwm')}"


def test_pwm_full_range_sweep_0_to_100(device):
    rejected = []
    for value in range(0, 101):
        r = device.command(f"SET PWM {value}")
        if r.get("status") != "OK" or r.get("pwm") != value:
            rejected.append((value, r))
    assert not rejected, f"values in 0..100 not accepted: {rejected}"


@pytest.mark.parametrize("value", [0, 1, 49, 50, 51, 99, 100])
def test_pwm_value_is_applied_in_status(device, value):
    device.command(f"SET PWM {value}")
    s = status(device)
    assert s.get("pwm") == value, f"after SET PWM {value}: STATUS pwm={s.get('pwm')}"


# ---------- R6: out-of-range PWM -> INVALID_VALUE (negative + boundary) ----------

@pytest.mark.parametrize("value", ["-1", "-100", "101", "102", "255", "1000"])
def test_pwm_out_of_range_is_rejected(device, value):
    r = device.command(f"SET PWM {value}")
    assert r.get("status") == "ERROR", f"SET PWM {value}: {r}"
    assert r.get("code") == "INVALID_VALUE", f"SET PWM {value}: {r}"


@pytest.mark.parametrize("value", ["abc", "50.5", "50abc", "", "0x10"])
def test_pwm_non_integer_is_rejected(device, value):
    r = device.command(f"SET PWM {value}".rstrip())
    assert r.get("status") == "ERROR", f"SET PWM {value!r}: accepted -> {r}"


@pytest.mark.parametrize("bad", ["-1", "101", "abc"])
def test_rejected_pwm_does_not_change_state(device, bad):
    device.command("SET PWM 30")
    device.command(f"SET PWM {bad}")
    assert status(device).get("pwm") == 30


# ---------- R8: unknown commands -> structured UNKNOWN_COMMAND (negative) ----------

@pytest.mark.parametrize("cmd", ["FOO", "GET HUMIDITY", "PINGX", "SET", "SET RELAY ON"])
def test_unknown_command_is_structured_error(device, cmd):
    r = device.command(cmd)
    assert r.get("status") == "ERROR", f"{cmd}: {r}"
    assert r.get("code") == "UNKNOWN_COMMAND", f"{cmd}: {r}"


def test_device_still_works_after_unknown_command(device):
    device.command("FOO")
    assert device.command("STATUS").get("status") == "OK"


# ---------- R4 / R2: LED state and STATUS ----------

@pytest.mark.parametrize("state, expected", [("ON", True), ("OFF", False)])
def test_led_state_reflected_in_status(device, state, expected):
    r = ok(device.command(f"SET LED {state}"), f"SET LED {state}")
    assert r.get("led") is expected, f"SET LED {state} reply: {r}"
    assert status(device).get("led") is expected


def test_status_fields_types(device):
    s = status(device)
    assert isinstance(s.get("heap"), int) and s["heap"] > 0, s
    assert isinstance(s.get("led"), bool), s
    assert isinstance(s.get("pwm"), int), s


# ---------- R7: RESET restores safe state for different start states ----------

@pytest.mark.parametrize("led, pwm", [("OFF", 100), ("ON", 0), ("ON", 50), ("ON", 1)])
def test_reset_from_state(device, led, pwm):
    device.command(f"SET LED {led}")
    device.command(f"SET PWM {pwm}")
    device.command("RESET")
    s = status(device)
    assert (s.get("led"), s.get("pwm")) == (False, 0), f"after LED {led}/PWM {pwm} + RESET: {s}"


# ---------- R3: temperature or explicit sensor error ----------

@pytest.mark.parametrize("attempt", range(5))
def test_get_temp_repeated(device, attempt):
    r = device.command("GET TEMP")
    assert r.get("status") in {"OK", "ERROR"}, r
    if r["status"] == "OK":
        t = r.get("temperature")
        assert isinstance(t, (int, float)) and -40 <= t <= 80, r
    else:
        assert r.get("code"), f"sensor error without code: {r}"


# ---------- R9: finite timeout, latency, recovery after timeout ----------

def test_no_response_times_out_in_bounded_time(device):
    t0 = time.monotonic()
    with pytest.raises(TimeoutError):
        device.command("NO_RESPONSE")
    assert time.monotonic() - t0 < device.ser.timeout + 0.5


@pytest.mark.parametrize("timeout, expect_reply", [(1.0, False), (3.0, True)])
def test_ping_vs_client_timeout(device, timeout, expect_reply):
    device.ser.timeout = timeout
    if expect_reply:
        r = device.command("PING")
        assert r.get("status") == "OK" and r.get("command") == "PING", r
    else:
        with pytest.raises(TimeoutError):
            device.command("PING")


def test_late_reply_after_timeout_is_not_taken_as_next_reply(device):
    """Without draining, the late PING reply would be read as the STATUS reply."""
    normal = device.ser.timeout
    device.ser.timeout = 1.0
    with pytest.raises(TimeoutError):
        device.command("PING")
    device.drain(idle=1.5, max_wait=3.0)
    device.ser.timeout = normal
    r = device.command("STATUS")
    assert r.get("status") == "OK" and "heap" in r, f"stale/foreign reply after timeout: {r}"
