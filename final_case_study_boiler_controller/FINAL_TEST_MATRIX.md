# Final Test Matrix — Smart Boiler Safety Controller

Статус — за фактичними прогонами на Wokwi-стендах. Evidence ID — див. [EVIDENCE_INDEX.md](EVIDENCE_INDEX.md), дефекти — [BUG_REPORTS.md](BUG_REPORTS.md).

| ID | Quality Risk | Pri | Level | Test / Method | Environment | Expected | Actual (коротко) | Evidence | Regression? | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| T01 | R01 Шум / дребезг створює хибну дію | P1 | Component | Звичайний натиск 300 ms ×5 (s1_normal_press) | Wokwi CLI + Serial | 1 подія / 1 дія | 1 / 1 у 5 з 5 | E01 | Yes | PASS |
| T02 | R01 | P1 | Component | Один імпульс шуму 5 ms ×5 (s2_noise_5ms) | Wokwi CLI | 0 подій | Подія і дія від одного RAW-переривання, 5/5 | E01, E02 | Yes | **FAIL** (DEF-01) |
| T03 | R01 | P1 | Component | Heavy bounce: 7 перемикань по 2 ms, потім стабільно ×5 (s3_heavy_bounce) | Wokwi CLI | 1 подія після стабілізації | 1 подія, але прийнята на першому перемиканні, 5/5 | E01 | Yes | **FAIL** (DEF-28) |
| T04 | R01 | P1 | System | 1 / 10 / 20 натисків кнопки на стенді котла | Wokwi | N подій | 1 → 2; 10 → 12–16; 20 → 21 | E10 | Yes | **FAIL** (DEF-02) |
| T05 | R02 CLI приймає некоректне / падає | P2 | Interface | Boundary speed −1…256, timeout 0…61 | Wokwi Serial | Помилка поза діапазоном | timeout 0 прийнято; speed 256 → 255 (5/5) | E03 | Yes | **FAIL** |
| T06 | R02 | P2 | Interface | Рядок 41+ символів; послідовність 1) set speed 40 2) status 3) set у стані DIRTY | Wokwi Serial | Контрольована помилка | SYSTEM FAULT + SW_CPU_RESET (5/5); у стані SAVED той самий set — звичайна ERROR | E03 | Yes | **FAIL** (DEF-03) |
| T07 | R02 | P2 | Interface | pytest: 67 тестів CLI (PWM 0–100, negative, unknown, timeout) | Python / pytest, RFC2217 | Усі PASS | 44 PASS / 23 FAIL ×5; SET PWM 100 відхиляється, GET TEMP — невалідний JSON | E12, E13 | Yes | **FAIL** |
| T08 | R03 Відмова датчика не детектується | P1 | System | DHT22 відключено → sensor / STATUS | Wokwi | Явна помилка датчика | 0.0 °C / 0.0 % як валідні дані | E10 | Yes | **FAIL** (DEF-04) |
| T09 | R03 / R04 | P1 | Protocol | I2C FAULT ON → OFF, VCD + PulseView | Wokwi Logic Analyzer, PulseView | Обмежені retry, error state, відновлення | Після 1-го NACK шина мовчить, main loop стоп, без recovery | E04, E05, E19 | Yes | **FAIL** (DEF-05), 5/5 |
| T10 | R04 Зависання без відновлення | P1 | Recovery | hang → WDT; 10× hang → reset | Wokwi | Reset ≲ 5 s, ACTIVE, без boot loop | 5.0 s, TASK_WDT, 10/10 | E10 | Yes | PASS |
| T11 | R05 Нагрів ON після reset | P1 | Recovery | relay on → hang → STATUS | Wokwi | Реле OFF | relay=true, LED ON (5/5) | E10, E11 | Yes | **FAIL** (DEF-06) |
| T12 | R05 | P1 | Recovery | relay on → powerloss → STATUS | Wokwi | Реле OFF | relay=true (5/5) | E10 | Yes | **FAIL** (DEF-06) |
| T13 | R05 | P1 | System | SET LED ON / PWM N → RESET → STATUS (pytest) | pytest | led=false, pwm=0 | led=true, pwm без змін (6/6) | E12, E13 | Yes | **FAIL** (DEF-07) |
| T14 | R06 Пошкодження persistent state | P1 | Reliability | relay off + save → powerloss → STATUS ×5 | Wokwi | Старий або новий валідний стан | counter +100 без виявлення (5/5) | E10 | Yes | **FAIL** (DEF-08) |
| T15 | R06 | P1 | Reliability | Штатний reboot після save | Wokwi | Дані збережені | relay, counter збережені | E10 | Yes | PASS |
| T16 | R07 Привод клапана | P1 | System | OPENING → кінцевик OPEN | Wokwi (Uno) | OPEN, реле OFF | Реле лишається ON, OPEN недосяжний (5/5) | E06 | Yes | **FAIL** (DEF-09) |
| T17 | R07 | P1 | System | OPENING > 10 s без кінцевика | Wokwi (Uno) | ERROR, реле OFF | Рух триває, ERROR немає | E06 | Yes | **FAIL** |
| T18 | R07 | P1 | System | Обидва кінцевики активні | Wokwi (Uno) | ERROR, реле OFF | WARNING, реле OPEN ON | E06 | Yes | **FAIL** |
| T19 | R07 | P1 | System | Зустрічні команди, контроль реле | Wokwi (Uno) | Ніколи обидва реле ON; безпечна послідовність реверсу | Обидва реле одночасно ON не спостерігались (TC-12). Послідовність реверсу (TC-10/11) не зафіксована в лозі — Not verified | E06 | Yes | PASS (interlock) |
| T20 | R08 Reconnect storm | P2 | Network | NET DOWN 16 s, інтервали retry | Wokwi + run_scenarios.py | Зростаючий backoff | 500 ms, далі ≈50 ms; 214–278 спроб (3/3) | E14 | Yes | **FAIL** (DEF-10) |
| T21 | R08 | P2 | Network | 20× NET DOWN / UP | Wokwi + run_scenarios.py | 20/20 відновлень | 60/60 reconnect=SUCCESS | E14 | Yes | PASS |
| T22 | R09 Втрата / дублі телеметрії | P1 | Network | NET DOWN, 5 / 8 SEND → NET UP | Wokwi + run_scenarios.py | Кожен ID — 1 publish | Кожен ID — 2 publish (3/3) | E15 | Yes | **FAIL** (DEF-11) |
| T23 | R09 | P1 | Network | NET DOWN, 9 / 12 SEND, STRESS 20 → NET UP | Wokwi + run_scenarios.py | ≤ 8 у буфері, DROP_OLDEST, dropped++ | count 12/8, 20/8; найстаріші ID зникли, dropped=0; новіші 4–6 разів | E15 | Yes | **FAIL** (DEF-12) |
| T24 | R10 Витік пам'яті | P1 | Reliability | STRESS 100 ×10, 20× SEND | Wokwi + run_scenarios.py | Heap стабільний | −80 B на повідомлення, без відновлення (30/30) | E16 | Yes | **FAIL** (DEF-13) |
| T25 | R11 Неточні таймери | P2 | Reliability | sleep 5 / 10 / 20 | Wokwi | Wake ±15 % | Wake ≈10× раніше; WDT reset при sleep ≥ 10 | E10 | Yes | **FAIL** |
| T26 | R12 Неправдивий STATUS | P2 | System | Звірка STATUS з діями | pytest, run_scenarios.py | Значення = реальний стан | pwm у шкалі 0..255; sent рахує дублі; dropped завжди 0 | E12, E15 | Yes | **FAIL** |
| T27 | R05 / R12 Відновлення після аварійного reset не видно | P1 | Recovery | relay on → hang / powerloss → boot log → STATUS | Wokwi | Етап відновлення в лозі (перевірка стану, виходи OFF), лише потім ACTIVE | Жодного рядка [RECOVERY]; одразу ACTIVE (150/150 STATUS, 5/5 регресій) | E10, E11 | Yes | **FAIL** (DEF-26) |
| T28 | R01 | P1 | Component | Натиск, через 50 ms після відпускання — шум 5 ms під час критичної операції ×5 (s4_noise_during_operation) | Wokwi CLI | 1 подія, шум не додає другу | LOGICAL EVENT #2 / ACTIONS total: 2, 5/5 | E01 | Yes | **FAIL** (DEF-27) |

## Підсумок покриття

| Ризик | Pri | Тести | Результат |
|---|---|---|---|
| R01 | P1 | T01–T04, T28 | FAIL |
| R02 | P2 | T05–T07 | FAIL |
| R03 | P1 | T08–T09 | FAIL |
| R04 | P1 | T09–T10 | FAIL (I2C hang) / PASS (WDT) |
| R05 | P1 | T11–T13, T27 | FAIL |
| R06 | P1 | T14–T15 | FAIL |
| R07 | P1 | T16–T19 | FAIL |
| R08 | P2 | T20–T21 | FAIL (storm) / PASS (reconnect) |
| R09 | P1 | T22–T23 | FAIL |
| R10 | P1 | T24 | FAIL |
| R11 | P2 | T25 | FAIL |
| R12 | P2 | T26, T27 | FAIL |

28 тестів (з них T07 — 67 автоматизованих тест-кейсів), 12 ризиків покрито на 100 %. PASS — 5, FAIL — 23.
