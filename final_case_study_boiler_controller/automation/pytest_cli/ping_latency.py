"""PING latency in different client conditions (to check whether the spread
comes from the device or from the test fixture)."""
import os
import statistics
import sys
import time
from datetime import datetime

import serial

PORT = os.getenv("DEVICE_PORT", "rfc2217://localhost:4000")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join("evidence", "ping_latency.log")
N = 5


def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def main():
    ser = serial.serial_for_url(PORT, baudrate=115200, timeout=0.05)
    time.sleep(0.5)
    ser.reset_input_buffer()
    log = open(OUT, "w", encoding="utf-8")

    def send(cmd):
        log.write(f"[{ts()}] >> {cmd}\n")
        ser.write((cmd + "\n").encode())
        ser.flush()

    def wait_for(token, limit=12.0):
        t0 = time.monotonic()
        buf = b""
        while time.monotonic() - t0 < limit:
            buf += ser.read(256)
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                text = line.decode(errors="replace").strip()
                if text:
                    log.write(f"[{ts()}] << {text}  (+{(time.monotonic() - t0) * 1000:.0f} ms)\n")
                if token in text:
                    return (time.monotonic() - t0) * 1000
        log.write(f"[{ts()}] -- no {token} in {limit * 1000:.0f} ms\n")
        return None

    def ping():
        ser.reset_input_buffer()
        send("PING")
        return wait_for('"PING"')

    results = {}

    def run(name, before):
        vals = []
        for _ in range(N):
            before()
            vals.append(ping())
        results[name] = vals

    run("A_idle_2s", lambda: time.sleep(2.0))

    def after_reset():
        send("RESET")
        wait_for('"reset"')
        time.sleep(0.2)
    run("B_after_RESET", after_reset)

    def after_timeout_change():
        time.sleep(1.0)
        ser.timeout = 1.0
        ser.timeout = 0.05
    run("C_after_timeout_change", after_timeout_change)

    def after_status():
        time.sleep(1.0)
        send("STATUS")
        wait_for('"heap"')
    run("D_after_STATUS", after_status)

    log.write("\n")
    for name, vals in results.items():
        ok = [v for v in vals if v is not None]
        line = f"{name}: " + ", ".join(f"{v:.0f}" if v is not None else "none" for v in vals)
        if ok:
            line += f"  | min {min(ok):.0f} / median {statistics.median(ok):.0f} / max {max(ok):.0f} ms"
        log.write(line + "\n")
        print(line)
    log.close()
    ser.close()


if __name__ == "__main__":
    main()
