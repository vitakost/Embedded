import os
import sys
import time
from datetime import datetime

import serial

PORT = os.getenv("DEVICE_PORT", "rfc2217://127.0.0.1:4000")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join("evidence", "raw_probe.log")

COMMANDS = [
    "PING", "STATUS", "GET TEMP", "GET TEMP", "GET TEMP",
    "SET LED ON", "STATUS", "SET LED OFF", "STATUS",
    "SET PWM 0", "SET PWM 1", "SET PWM 49", "SET PWM 50", "STATUS", "SET PWM 51",
    "SET PWM 99", "SET PWM 100", "STATUS",
    "SET PWM -1", "SET PWM 101", "SET PWM 999", "SET PWM abc", "SET PWM 50.5",
    "SET PWM 50abc", "SET PWM", "STATUS",
    "SET LED ON", "SET PWM 75", "RESET", "STATUS",
    "FOO", "SET LED MAYBE", "GET HUMIDITY", "ping", "NO_RESPONSE", "STATUS",
]


def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def main():
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    ser = serial.serial_for_url(PORT, baudrate=115200, timeout=0.05)
    time.sleep(0.3)
    ser.reset_input_buffer()
    with open(OUT, "w", encoding="utf-8") as log:
        log.write(f"# port={PORT} started={datetime.now().isoformat(timespec='seconds')}\n")
        for cmd in COMMANDS:
            ser.reset_input_buffer()
            t0 = time.monotonic()
            log.write(f"[{ts()}] >> {cmd}\n")
            ser.write((cmd + "\n").encode())
            ser.flush()
            buf = b""
            last_rx = None
            while True:
                now = time.monotonic()
                if now - t0 > 3.0:
                    break
                if last_rx is not None and now - last_rx > 0.4:
                    break
                chunk = ser.read(256)
                if chunk:
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        dt = (time.monotonic() - t0) * 1000
                        log.write(f"[{ts()}] << {line.decode(errors='replace').rstrip()}  (+{dt:.0f} ms)\n")
                        last_rx = time.monotonic()
            if buf:
                log.write(f"[{ts()}] << {buf!r}  (partial)\n")
            if last_rx is None:
                log.write(f"[{ts()}] -- no response in 3000 ms\n")
            log.flush()
    ser.close()
    print("probe saved to", OUT)


if __name__ == "__main__":
    main()
