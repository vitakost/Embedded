import os
import sys
import threading
import time
from datetime import datetime

import serial

PORT = os.getenv("DEVICE_PORT", "rfc2217://localhost:4000")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

SUITE = [
    ("TC-01", ["help"]),
    ("TC-02", ["status"]),
    ("TC-03", ["led on", "status"]),
    ("TC-04", ["led off", "status"]),
    ("TC-05", ["set speed -1", "status"]),
    ("TC-06", ["set speed 0", "status"]),
    ("TC-07", ["set speed 1", "status"]),
    ("TC-08", ["set speed 127", "status"]),
    ("TC-09", ["set speed 254", "status"]),
    ("TC-10", ["set speed 255", "status"]),
    ("TC-11", ["set speed 256", "status"]),
    ("TC-12", ["set speed", "status"]),
    ("TC-13", ["set speed abc", "status"]),
    ("TC-14", ["set speed *", "status"]),
    ("TC-15", ["set speed 10 20", "status"]),
    ("TC-16", ["set speed 39***", "status"]),
    ("TC-17", ["set speed 9999999999", "status"]),
    ("TC-18", ["set speed 2147483648", "status"]),
    ("TC-19", ["set speed 99999999999999999999", "status"]),
    ("TC-20", ["set timeout 0", "status"]),
    ("TC-21", ["set timeout 1", "status"]),
    ("TC-22", ["set timeout 2", "status"]),
    ("TC-23", ["set timeout 59", "status"]),
    ("TC-24", ["set timeout 60", "status"]),
    ("TC-25", ["set timeout 61", "status"]),
    ("TC-26", ["0", "status"]),
    ("TC-27", ["", "status"]),
    ("TC-28", ["   ", "status"]),
    ("TC-29", ["set  speed 10", "status"]),
    ("TC-30", ["set\tspeed\t10", "status"]),
    ("TC-31", ["!@#$%^&*()", "status"]),
    ("TC-32", ["STATUS"]),
    ("TC-33", ["Help"]),
]

LENGTHS = [30, 38, 39, 40, 41, 42, 45, 60, 100]

BUGS = [
    ("BUG-speed256", ["reset", "set speed 256", "status"]),
    ("BUG-timeout0", ["reset", "set timeout 0", "status"]),
    ("BUG-uppercase", ["reset", "STATUS"]),
    ("BUG-specialchars", ["reset", "!@#$%^&*()", "status"]),
    ("BUG-len40", ["reset", "A" * 40, "status"]),
    ("BUG-len41", ["reset", "A" * 41, "status"]),
    ("BUG-dirty-set", ["reset", "set speed 40", "status", "set", "status"]),
    ("CMP-saved-set", ["reset", "set speed 40", "save", "status", "set", "status"]),
]


def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


class Monitor:
    def __init__(self, port):
        self.ser = serial.serial_for_url(port, baudrate=115200, timeout=0.05)
        self.lock = threading.Lock()
        self.log = None
        self.stop = False
        self.buf = b""
        self.last_rx = time.monotonic()
        self.t = threading.Thread(target=self._reader, daemon=True)
        self.t.start()

    def _write(self, line):
        with self.lock:
            if self.log:
                self.log.write(line + "\n")
                self.log.flush()

    def _reader(self):
        while not self.stop:
            data = self.ser.read(512)
            if not data:
                continue
            self.last_rx = time.monotonic()
            self.buf += data
            while b"\n" in self.buf:
                line, self.buf = self.buf.split(b"\n", 1)
                text = line.decode(errors="replace").rstrip("\r")
                if text.strip():
                    self._write(f"{ts()} < {text}")

    def open(self, name):
        with self.lock:
            if self.log:
                self.log.close()
            self.log = open(os.path.join(OUT, name + ".log"), "w", encoding="utf-8")

    def mark(self, text):
        self._write(f"{ts()} # {text}")

    def cmd(self, command, settle=0.8, max_wait=6.0):
        shown = command.replace("\t", "<TAB>") if command.strip() else f"<{len(command)} spaces>" if command else "<empty line>"
        self._write(f"{ts()} > {shown}")
        self.ser.write((command + "\n").encode())
        self.ser.flush()
        t0 = time.monotonic()
        time.sleep(0.3)
        while time.monotonic() - t0 < max_wait and time.monotonic() - self.last_rx < settle:
            time.sleep(0.1)

    def close(self):
        time.sleep(0.5)
        self.stop = True
        self.t.join()
        with self.lock:
            if self.log:
                self.log.close()
        self.ser.close()


def main():
    os.makedirs(OUT, exist_ok=True)
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    m = Monitor(PORT)
    time.sleep(0.5)
    try:
        print("suite ...", flush=True)
        m.open("suite_run1")
        m.cmd("reset", settle=1.5)
        for tc, cmds in SUITE:
            m.mark(tc)
            for c in cmds:
                m.cmd(c)
        print("length boundary ...", flush=True)
        m.open("length_boundary")
        m.cmd("reset", settle=1.5)
        for n in LENGTHS:
            m.mark(f"length {n}")
            m.cmd("A" * n, settle=1.5)
            m.cmd("status")
        m.mark("two lines 32 + 33")
        m.cmd("A" * 32, settle=1.5)
        m.cmd("A" * 33, settle=1.5)
        m.cmd("status")
        m.mark("valid command padded to 41: 'set speed 10' + spaces")
        m.cmd("set speed 10" + " " * 29, settle=1.5)
        m.cmd("status")
        for i in range(1, runs + 1):
            print(f"bug repro run {i} of {runs} ...", flush=True)
            m.open(f"bugs_run{i}")
            for name, cmds in BUGS:
                m.mark(name)
                for c in cmds:
                    m.cmd(c, settle=1.5 if c == "reset" or len(c) > 40 or c == "set" else 0.8)
    finally:
        m.close()
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
