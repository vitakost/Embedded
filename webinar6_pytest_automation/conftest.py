import os
import time
from datetime import datetime

import pytest

from device import Device

LOG_PATH = os.getenv("SERIAL_LOG")


class LoggedDevice(Device):
    """Device with raw TX/RX logging and buffer draining after timeouts."""

    def __init__(self, port, timeout=1.0, log=None):
        super().__init__(port, timeout=timeout)
        self.log = log

    def _w(self, text):
        if self.log:
            self.log.write(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {text}\n")
            self.log.flush()

    def command_raw(self, command):
        self._w(f">> {command}")
        t0 = time.monotonic()
        try:
            line = super().command_raw(command)
        except TimeoutError:
            self._w(f"-- timeout after {(time.monotonic() - t0) * 1000:.0f} ms (timeout={self.ser.timeout}s)")
            raise
        self._w(f"<< {line}  (+{(time.monotonic() - t0) * 1000:.0f} ms)")
        return line

    def drain(self, idle=0.25, max_wait=2.5):
        """Read and log everything the device still sends (e.g. late replies)."""
        old = self.ser.timeout
        self.ser.timeout = idle
        t0 = time.monotonic()
        try:
            while time.monotonic() - t0 < max_wait:
                line = self.ser.readline()
                if not line:
                    break
                self._w(f"<< {line.decode(errors='replace').strip()}  (late)")
        finally:
            self.ser.timeout = old
            self.ser.reset_input_buffer()

    def safe_reset(self, max_wait=4.0):
        """RESET and wait for *its* reply, logging anything stale before it.

        Used as precondition and cleanup, so every test starts in sync
        with the device and in the requested safe state.
        """
        self.ser.reset_input_buffer()
        self._w(">> RESET")
        t0 = time.monotonic()
        self.ser.write(b"RESET\n")
        self.ser.flush()
        old = self.ser.timeout
        self.ser.timeout = 0.2
        try:
            while time.monotonic() - t0 < max_wait:
                line = self.ser.readline().decode(errors="replace").strip()
                if not line:
                    continue
                if '"reset"' in line:
                    self._w(f"<< {line}  (+{(time.monotonic() - t0) * 1000:.0f} ms)")
                    break
                self._w(f"<< {line}  (late)")
            else:
                self._w(f"-- no RESET reply in {max_wait * 1000:.0f} ms")
        finally:
            self.ser.timeout = old
        self.drain(idle=0.2, max_wait=1.0)


@pytest.fixture(scope="session")
def serial_log():
    if not LOG_PATH:
        yield None
        return
    os.makedirs(os.path.dirname(LOG_PATH) or ".", exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write(f"# started {datetime.now().isoformat(timespec='seconds')}\n")
        yield f


@pytest.fixture
def device(request, serial_log):
    port = os.getenv("DEVICE_PORT")
    if not port:
        pytest.skip("Set DEVICE_PORT, e.g. COM5, /dev/ttyUSB0 or rfc2217://localhost:4000 (Wokwi)")
    timeout = float(os.getenv("DEVICE_TIMEOUT", "1.0"))
    dev = LoggedDevice(port, timeout=timeout, log=serial_log)
    dev._w(f"=== {request.node.nodeid}")
    # Precondition: known safe state before every test (LED OFF / PWM 0).
    dev.safe_reset()
    yield dev
    # Cleanup: drain late replies (e.g. after a timeout) and return to safe state.
    try:
        dev.ser.timeout = timeout
        dev.safe_reset()
    finally:
        dev.close()
