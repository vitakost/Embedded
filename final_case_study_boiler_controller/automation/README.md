# Automation

| Папка | Що перевіряє | Ризики |
|---|---|---|
| `pytest_cli/` | UART CLI контролера: PING, STATUS, GET TEMP, SET LED, SET PWM 0..100, RESET, невідомі команди, timeout | R02, R03, R05, R12 |
| `network_scenarios/` | NET DOWN / UP, retry, офлайн-буфер 5 / 8 / 9 / 12, 20× reconnect, STRESS і heap | R08, R09, R10 |
| `button_scenario/` | 6 сценаріїв: натиск, утримання 3 s, 5 натискань, шум 5 ms, шум під час критичної операції, heavy bounce 2 ms | R01 |

## pytest_cli
Штатні тести курсу (`test_status.py`, `test_relay.py`, `test_sensor.py`, `test_boundaries.py`, `test_timeout.py`) і власні тести `test_firmware_cli.py` — 53 тест-кейси, разом 67.
`conftest.py` робить RESET до і після кожного тесту, перевіряє STATUS і, якщо виходи лишились увімкненими, вимикає їх явно (SET LED OFF + SET PWM 0); пише сирий UART-лог. `ping_latency.py` міряє час відповіді на PING у 4 ситуаціях.

```powershell
cd automation\pytest_cli
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# у VS Code: PlatformIO Build → Wokwi: Start Simulator (Serial Monitor закритий)
$env:DEVICE_PORT="rfc2217://localhost:4000"
python -m pytest -v
.\run_all.bat        # перевірка .venv + probe + ping_latency + 1 baseline (1.0 s) + 5 регресій (3.0 s), результати в evidence\
```
`DEVICE_TIMEOUT` — таймаут клієнта в секундах (за замовчуванням 1.0), `SERIAL_LOG` — файл для сирого UART-логу.

## network_scenarios
```powershell
cd automation\network_scenarios
python -m pip install pyserial
python run_scenarios.py 1          # усі сценарії, логи в evidence\run1_*.log
python run_scenarios.py 2 A C12    # лише вибрані сценарії
```

## button_scenario
```powershell
wokwi-cli --scenario s2_noise_5ms.yaml --timeout 30000 <папка проєкту кнопки>
```
Кожен сценарій перевіряє одну річ і не чекає на номер події (`wait-serial`), тому завершується сам. Запускається для проєкту кнопки (потрібні Wokwi CLI і токен).
