# Smart Boiler Safety Controller — Embedded QA Case Study

## What this repository demonstrates
Як risk-based тестування IoT-контролера електричного котла для опалення на ESP32 привело до обґрунтованого рішення NO-GO: пристрій працює в happy path, але після збоїв (зависання, втрата живлення, відмова датчика, шум на вході) може залишити нагрів увімкненим або працювати на хибній температурі.

## System
ESP32 DevKit V1 · DHT22 (кімната) · I2C-датчик теплоносія · реле ТЕН · PWM (потужність / циркуляційний насос) · привод змішувального клапана з кінцевиками · кнопка BOOST · UART CLI · NVS · Task WDT / deep sleep · Wi-Fi / MQTT з офлайн-буфером.
Перевірено black-box на Wokwi-стендах підсистем. Схема — [CASE_STUDY.md §3](CASE_STUDY.md).

## Main quality risks
- **R05** — нагрів ON після reset / power loss / RESET (safety).
- **R03 / R04** — відмова датчика маскується як 0.0 °C або заморожує контролер.
- **R01** — шум на кнопці створює хибну дію.
- **R07** — привод клапана не зупиняється на кінцевику, немає таймауту руху.
- **R09 / R10** — втрата і дублювання телеметрії, витік пам'яті.

## Test strategy
- [MASTER_TEST_PLAN.md](MASTER_TEST_PLAN.md) — scope, 12 ризиків, рівні, середовища, entry / exit, регресія, evidence strategy.
- [FINAL_TEST_MATRIX.md](FINAL_TEST_MATRIX.md) — 26 тестів, кожен ризик → метод → evidence → статус.

## Key evidence
- I2C-трейс з PulseView: last ACK → first NACK → 6.7 s тиші ([evidence/hw4_i2c_sensor](evidence/hw4_i2c_sensor/)).
- Boot / reset log: relay=true після WDT reset і power loss ([evidence/hw5_recovery_persistence](evidence/hw5_recovery_persistence/)).
- Вивід pytest і сирі UART-логи 6 прогонів ([evidence/hw6_pytest_cli](evidence/hw6_pytest_cli/)).
- Message ID до / після flush і heap trend, 3 прогони ([evidence/hw7_network_memory](evidence/hw7_network_memory/)).
- Повний індекс — [EVIDENCE_INDEX.md](EVIDENCE_INDEX.md).

## Key findings
25 дефектів (Critical 12, Major 10) — [BUG_REPORTS.md](BUG_REPORTS.md):
- нагрів відновлюється у стані ON після аварійного reset; RESET не вимикає виходи;
- після першого I2C NACK контролер зависає без retry і без WDT;
- відключений датчик → `0.0C / 0.0%` без помилки — термостат гріє без обмеження;
- імпульс шуму 5 ms на кнопці → хибна дія (5/5);
- overflow буфера: 12 повідомлень → 24 publish, 4 втрачено при `dropped=0`; витік 80 B на повідомлення.

## Automation
| Що | Де | Запуск |
|---|---|---|
| pytest CLI (67 тест-кейсів, RESET-фікстура, UART-лог) | [automation/pytest_cli](automation/pytest_cli/) | `python -m pytest -v` (DEVICE_PORT=rfc2217://localhost:4000) |
| Мережеві сценарії A–F, 20× reconnect, stress | [automation/network_scenarios](automation/network_scenarios/) | `python run_scenarios.py 1` |
| Шум / дребезг кнопки | [automation/button_scenario](automation/button_scenario/) | `wokwi-cli --scenario scenario.yaml` |

Опис і запуск — [automation/README.md](automation/README.md).

## Limitations
Wokwi не підтверджує електричну поведінку (brown-out, NVS при фізичній втраті живлення, реальний дребезг), реальні Wi-Fi / MQTT і таймінги; підсистеми не тестувались в одній збірці. План перевірки на залізі — [CASE_STUDY.md §12](CASE_STUDY.md).

## Conclusion
**NO-GO** — відкриті Critical-дефекти у safety-функціях. Умови повторної оцінки — [RELEASE_DECISION.md](RELEASE_DECISION.md).
