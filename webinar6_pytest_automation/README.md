# Webinar 6 — Python/pytest automation для ESP32 CLI

Автотести для навчальної прошивки ESP32 (`homework_buggy`, Wokwi). Пристрій приймає текстові команди по UART 115200 і відповідає одним рядком JSON:
`PING`, `STATUS`, `GET TEMP`, `SET LED ON/OFF`, `SET PWM N`, `RESET`.
Очікувані результати — за вимогами R1–R10 з `device_requirements.md` курсу.

## Структура

| Файл | Призначення |
|---|---|
| `tests/test_firmware_cli.py` | **Власні тести** — 53 тест-кейси, 15 функцій з `@pytest.mark.parametrize` |
| `tests/test_boundaries.py`, `test_relay.py`, `test_sensor.py`, `test_status.py`, `test_timeout.py` | Штатні тести курсу |
| `device.py` | Штатний клієнт пристрою |
| `conftest.py` | Фікстура `device`: RESET до і після кожного тесту + сирий UART-лог |
| `probe_raw.py` | Один прохід по всіх командах з таймаутом 3 с — сирі відповіді пристрою |
| `run_all.bat` | env → probe → 1 baseline (timeout 1.0 s) → 5 регресій (timeout 3.0 s) |
| `evidence/` | Вивід pytest і UART-логи кожного прогону; `evidence/bugs/` — evidence по кожному дефекту |

## Що покривають власні тести

- **Boundary:** PWM 0, 1, 2, 49, 50, 51, 98, 99, 100 і повний перебір 0..100; значення в STATUS.
- **Negative:** PWM −1, −100, 101, 102, 255, 1000, `abc`, `50.5`, `50abc`, порожнє, `0x10`; невідомі команди; відхилене значення не змінює стан; пристрій працює після помилкової команди.
- **RESET:** повернення в безпечний стан із 4 різних станів.
- **Sensor:** 5 повторних `GET TEMP`.
- **Timeout:** скінченний таймаут, PING при таймауті 1.0 і 3.0 s, запізніла відповідь після таймауту.

## Запуск

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# у VS Code: PlatformIO Build → Wokwi: Start Simulator (Serial Monitor закритий)
$env:DEVICE_PORT="rfc2217://localhost:4000"
python -m pytest -v            # один прогін
.\run_all.bat                  # baseline + 5 регресій з evidence
```

Змінна `DEVICE_TIMEOUT` (секунди, за замовчуванням 1.0) задає таймаут клієнта; `SERIAL_LOG` — файл для сирого UART-логу.

## Результати (01.11.2026, BUGGY build)

Baseline (1.0 s): 42 PASS / 25 FAIL. Регресія ×5 (3.0 s): 44 PASS / 23 FAIL, набір FAIL однаковий у 5/5.

| ID | Дефект прошивки | Вимога | Severity | Repro |
|---|---|---|---|---|
| BUG-01 | `SET PWM 100` → `INVALID_VALUE` (off-by-one на верхній межі) | R5 | Major | 6/6 |
| BUG-02 | `GET TEMP` → `{"status":"OK","temperature":24.5` — невалідний JSON | R3 | Major | 6/6 |
| BUG-03 | `RESET` → `reset:true`, але STATUS `led:true, pwm:255` — безпечний стан не відновлено | R7 | Critical | 6/6 |
| BUG-04 | STATUS pwm у шкалі 0..255 (SET 50 → STATUS 127) | R2 | Major | 6/6 |

Інші знахідки (не прошивка):
- **Communication:** PING відповідає за 1.5–5.6 s при таймауті 1.0 s; клієнт не корелює відповідь з командою, тож запізніла відповідь читається як відповідь на наступну.
- **Environment:** латентність Wokwi до 1.8 s; DeprecationWarning pyserial 3.5 на Python 3.14.
- **Test:** у штатній фікстурі немає RESET-передумови; `test_timeout` спирається на недокументовану тишу на `NO_RESPONSE`; 2 хибні PASS і 1 тест із замалим вікном очікування у власному наборі.
- **Requirement:** `NO_RESPONSE` суперечить R8; немає вимоги до часу відповіді; не описано зв'язок LED↔PWM і коди помилок для некоректних аргументів.
