import glob
import os
import shutil
import sys
import threading
import time
from datetime import datetime

import serial

PORT = os.getenv("DEVICE_PORT", "rfc2217://localhost:4000")
HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.join(os.path.dirname(HERE), "Wokwi_I2C_BUGGY")
OUT = os.path.join(HERE, "logs")

NORMAL_S = 6      # робота до FAULT ON
FAULT_S = 4       # FAULT увімкнено
AFTER_S = 10      # спостереження після FAULT OFF


def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def connect():
    while True:
        try:
            return serial.serial_for_url(PORT, baudrate=115200, timeout=0.05)
        except Exception:
            time.sleep(0.5)


def reader(ser, log, stop):
    buf = b""
    while not stop.is_set():
        try:
            data = ser.read(512)
        except Exception:
            break
        if not data:
            continue
        buf += data
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            text = line.decode(errors="replace").rstrip("\r")
            if text.strip():
                log.write(f"{ts()} < {text}\n")
                log.flush()


def check_vcd(path):
    """Return (ok, message): FAULT must start OFF, go ON, then back OFF,
    and the capture must continue >= 5 s after FAULT OFF."""
    ids, t, fault, end = {}, 0, [], 0
    for line in open(path):
        l = line.strip()
        if l.startswith("$var"):
            p = l.split(); ids[p[3]] = p[4]
        elif l.startswith("#"):
            t = int(l[1:]); end = t
        elif l and l[0] in "01" and ids.get(l[1:]) == "FAULT":
            fault.append((t / 1e9, int(l[0])))
    if not fault or fault[0][1] != 0:
        return False, "на старті FAULT був ON — перед запуском переведи перемикач в OFF"
    on = next((x for x in fault if x[1] == 1), None)
    if not on:
        return False, "FAULT так і не перемкнувся в ON"
    off = next((x for x in fault if x[0] > on[0] + 0.2 and x[1] == 0), None)
    if not off:
        return False, "FAULT не повернувся в OFF"
    if end / 1e9 - off[0] < 5:
        return False, "після FAULT OFF записано менше 5 с — зупиняй симуляцію пізніше"
    return True, f"FAULT ON {on[0]:.3f} s, OFF {off[0]:.3f} s, запис до {end / 1e9:.3f} s"


def countdown(msg, seconds):
    for s in range(seconds, 0, -1):
        print(f"\r{msg} через {s} с ...   ", end="", flush=True)
        time.sleep(1)
    print(f"\r{msg} — ЗАРАЗ!                ", flush=True)
    print("\a", end="", flush=True)


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    os.makedirs(OUT, exist_ok=True)
    i = 1
    while i <= runs:
        print(f"\n=== Прогін {i} з {runs} ===")
        print("Перевір: перемикач FAULT у положенні OFF (у попередньому прогоні ти повертав його в OFF).")
        print("Запусти симуляцію: F1 → Wokwi: Start Simulator (FAULT має бути OFF).")
        before = {p: os.path.getmtime(p) for p in glob.glob(os.path.join(BENCH, "*.vcd"))}
        ser = connect()
        print("Підключено до Serial.")
        stop = threading.Event()
        with open(os.path.join(OUT, f"run{i}_serial.log"), "w", encoding="utf-8") as log:
            th = threading.Thread(target=reader, args=(ser, log, stop), daemon=True)
            th.start()
            countdown("Перемкни FAULT у ON", NORMAL_S)
            countdown("Перемкни FAULT у OFF", FAULT_S)
            countdown("Зупини симуляцію (F1 → Wokwi: Stop Simulator)", AFTER_S)
            input("Коли симуляцію зупинено, натисни Enter ...")
            stop.set()
            th.join(timeout=2)
        try:
            ser.close()
        except Exception:
            pass
        time.sleep(1)
        vcds = [p for p in glob.glob(os.path.join(BENCH, "*.vcd")) if os.path.getmtime(p) != before.get(p)]
        if vcds:
            newest = max(vcds, key=os.path.getmtime)
            shutil.copy2(newest, os.path.join(OUT, f"run{i}_i2c_fault.vcd"))
            ok, msg = check_vcd(os.path.join(OUT, f"run{i}_i2c_fault.vcd"))
            print(("OK: " if ok else "ПРОГІН НЕВДАЛИЙ: ") + msg)
            if ok:
                i += 1
            else:
                print("Повторюємо цей прогін.")
        else:
            print("УВАГА: новий VCD не знайдено — повторюємо цей прогін.")
    print("DONE")


if __name__ == "__main__":
    main()
