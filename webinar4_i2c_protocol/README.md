# Тиждень 4 — I2C protocol analysis (MPU6050, ESP32, Wokwi)

Стенд: ESP32 DevKit + MPU6050 (0x68), SDA GPIO21 / SCL GPIO22, build BUGGY. Перемикач FAULT на GPIO27 імітує втрату датчика.
Трафік записує Wokwi Logic Analyzer (VCD), декодування — PulseView (I2C decoder) і скрипт `scripts/i2c_decode.py`.

## Що в папці

| Файл / папка | Що це |
|---|---|
| `Protocol_Analysis_Sheet_Test_Log_Webinar_4_FAIL.docx` | Протокол: Environment, Transaction Log, Fault Timeline з FAULT ON/OFF, Bug Report, таблиця повторних прогонів, відповіді на питання |
| `logs/first_run_14-10_i2c.vcd` | Первинний ручний прогін 14.10.2026 (D0=SDA, D1=SCL), по ньому зроблені скріни PulseView |
| `logs/run1..5_i2c_fault.vcd`, `logs/run1..5_serial.log` | 5 повторних прогонів 13.11.2026 через Wokwi CLI; FAULT записаний на D2 |
| `logs_failed_attempts/` | Перша серія запусків: перемикач FAULT лишався в ON з попереднього запуску, один VCD не записався. У підрахунок 5/5 не входить |
| `pulseview/` | Скріни PulseView: весь запис, останній ACK, перший NACK |
| `scripts/i2c_rerun.py` | Запуск серії: старт симуляції, FAULT ON → OFF, запис UART і VCD, перевірка, що FAULT у VCD почався з OFF і після OFF є ≥ 5 s запису |
| `scripts/i2c_decode.py` | Декодер VCD: START / Sr / STOP, адреса, дані, ACK/NACK, фронти FAULT |
| `bench/` | `diagram.json` (FAULT додано на канал D2 аналізатора), `wokwi.toml`, код прошивки BUGGY |

## Результат

| Прогін | FAULT ON | Останній ACK | Перший NACK | Повтори | FAULT OFF | Після OFF |
|---|---|---|---|---|---|---|
| run1 | 4.054 s | 3.517791 s | 4.518565 s | 0 | 6.840 s | 7.0 s тиші |
| run2 | 4.703 s | 4.518791 s | 5.519565 s | 0 | 7.408 s | 5.4 s тиші |
| run3 | 5.653 s | 5.519791 s | 6.520565 s | 0 | 7.908 s | 6.6 s тиші |
| run4 | 6.171 s | 5.519791 s | 6.520565 s | 0 | 8.143 s | 6.3 s тиші |
| run5 | 9.124 s | 8.522791 s | 9.523565 s | 0 | 11.412 s | 5.5 s тиші |

На найближчому циклі опитування після FAULT ON йде одна транзакція 0x69 W з NACK, в UART — рядок `[E] requestFrom(): ... Error -1`.
Далі на шині нічого немає (SDA=SCL=1, лінію ніхто не тримає), `[DATA]` і `[SYSTEM] Main loop alive` більше не з'являються, і після FAULT OFF система не відновлюється. Повторного boot немає.

**Bug:** прошивка зависає після першого NACK, Critical, 5/5. У фінальному кейсі — DEF-05 (evidence E04, E05, E19).

## Як повторити

1. Відкрити `Завдання 4/Wokwi_I2C_BUGGY` у VS Code, зібрати PlatformIO (Build).
2. `python scripts/i2c_rerun.py` — 5 прогонів, результати в `logs/` (скрипт шукає папку `Wokwi_I2C_BUGGY` поруч зі своєю папкою, як у робочій структурі `Завдання 4/rerun`).
3. `python scripts/i2c_decode.py logs/run1_i2c_fault.vcd` — список транзакцій і фронти FAULT.
