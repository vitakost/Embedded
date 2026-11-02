# Embedded QA Case Study — Smart Boiler Safety Controller

## 1. Project
Контролер електричного котла для опалення на ESP32: читає температуру приміщення (DHT22) і теплоносія (I2C), керує реле ТЕН, ступенями потужності або циркуляційним насосом (PWM) і приводом змішувального клапана, має кнопку BOOST, сервісний UART CLI, зберігає налаштування в NVS, захищений watchdog і передає телеметрію через Wi-Fi / MQTT з офлайн-буфером.
Тестування — black-box на Wokwi-стендах підсистем з BUGGY-збірками прошивки.

## 2. My QA Goal
Підтримати рішення: **чи можна випускати контролер у пілот**. Для котла головний критерій — fail-safe: за будь-якого збою нагрів вимкнений, а дані про температуру правдиві.

## 3. System Overview
```
           ┌──────────── ESP32 DevKit V1 ────────────┐
DHT22 ───► │ GPIO15                                  │──► Реле ТЕН (GPIO5)    
I2C датчик │ SDA21 / SCL22                           │──► PWM: потужність / насос (GPIO2)
Кнопка ──► │ GPIO (debounce)                         │──► Привод клапана: OPEN / CLOSE реле
Кінцевики► │ GPIO                                    │
UART CLI ◄►│ 115200  ◄── Python / pytest (RFC2217)    │
           │ NVS · Task WDT · deep sleep             │──► Wi-Fi / MQTT ──► брокер
           └─────────────────────────────────────────┘     (офлайн-буфер 8)
```
Деталі — [MASTER_TEST_PLAN.md §2](MASTER_TEST_PLAN.md).

## 4. Critical Risks
Пріоритетні ризики — ті, через які котел стає небезпечним або дані недостовірними:
1. **R05** — нагрів ON після reset / power loss / RESET.
2. **R03 / R04** — відмова датчика маскується або заморожує контролер.
3. **R01** — шум на кнопці вмикає нагрів.
4. **R07** — привод клапана не зупиняється на кінцевику, немає таймауту.
5. **R06** — пошкодження налаштувань при втраті живлення.
6. **R09 / R10** — втрата і дублі телеметрії, витік пам'яті.

Повна таблиця з 12 ризиків, impact і probability — [MASTER_TEST_PLAN.md §7](MASTER_TEST_PLAN.md).

## 5. Test Strategy
Кожен ризик → рівень → метод → середовище → evidence:

| Ризик | Рівень | Метод | Середовище | Evidence |
|---|---|---|---|---|
| R01 | Component | Скриптовий шум і дребезг | Wokwi CLI scenario.yaml + Logic Analyzer | Serial counters, VCD |
| R02 | Interface | Boundary / negative CLI | Serial, pytest | Test report, вивід pytest |
| R03, R04 | Protocol / Recovery | I2C FAULT ON / OFF; hang | Logic Analyzer + PulseView | VCD, скриншоти з маркерами |
| R05, R06 | Recovery / Persistence | hang, powerloss, RESET | Wokwi + Serial / pytest | Boot log, before / after |
| R07 | System | State machine, кінцевики | Wokwi | Test log |
| R08–R10 | Network / Reliability | NET DOWN / UP, overflow, stress | run_scenarios.py | Логи з ID, heap trend |

Матриця тестів — [FINAL_TEST_MATRIX.md](FINAL_TEST_MATRIX.md).

## 6. Key Scenarios
1. **relay on → hang → WDT reset → status** — reset відбувається за 5.0 s, але реле знову ON (DEF-06). Показує різницю між «reset відбувся» і «recovery безпечний».
2. **I2C FAULT ON → OFF з PulseView** — last ACK 10.524791 s, first NACK 11.525565 s, далі 6.7 s тиші, 0 retry (DEF-05). Протокольний трейс доводить, що шина вільна і проблема в прошивці.
3. **DHT22 відключено** — `0.0C / 0.0%` без помилки (DEF-04). Для термостата це «холодно» → нескінченний нагрів.
4. **Шум 5 ms на кнопці ×5** — хибна дія 5/5 (DEF-01).
5. **12× SEND офлайн → NET UP** — 24 publish замість 8, 4 ID втрачено, `dropped=0` (DEF-12).
6. **STRESS 100 ×10** — рівно −8000 B щоразу, 30/30 ітерацій (DEF-13).

## 7. Automation
- **pytest-набір** ([automation/pytest_cli](automation/pytest_cli/)): 67 тест-кейсів CLI — межі PWM 0..100 і повний перебір, negative, невідомі команди, RESET з 4 станів, повторні GET TEMP, timeout. Фікстура: RESET до і після кожного тесту з очікуванням відповіді, сирий UART-лог кожного прогону.
- **run_scenarios.py** ([automation/network_scenarios](automation/network_scenarios/)): мережеві сценарії A–F, 20× reconnect, stress — однаковий таймінг і логи з мітками часу для 3 прогонів.
- **scenario.yaml** ([automation/button_scenario](automation/button_scenario/), Wokwi CLI): шум і дребезг кнопки з точною тривалістю імпульсів.

Чому саме це: ці сценарії треба повторювати після кожної зміни (регресія), вони вимагають точних таймінгів або великої кількості повторів (101 значення PWM, 20 reconnect, 1000 повідомлень), які вручну ненадійні.
Що свідомо ручне: PulseView-аналіз, зміна схеми (відключення датчика), recovery-сценарії тижня 5.

## 8. Fault Injection
| Fault | Як вводився | Що перевірялось |
|---|---|---|
| Шум / дребезг | scenario.yaml: імпульс 5 ms, тоглінг 2 ms | Кількість логічних подій і дій |
| Відмова DHT22 | Видалення з'єднання в diagram.json | Явна помилка vs 0.0 °C |
| Відмова I2C | Перемикач FAULT (адреса 0x68 → 0x69) | Retry, error state, recovery |
| Зависання | Команда `hang` | WDT, reset reason, стан виходів |
| Втрата живлення | Команда `powerloss` під час save | Цілісність NVS, стан реле |
| Недоступність брокера | `NET DOWN / NET UP` | Backoff, буфер, flush, дублікати |
| Навантаження | `STRESS 100` ×10 | Тренд heap |

## 9. Evidence
18 джерел доказів: Serial logs з мітками часу, VCD-трейси, скриншоти PulseView, вивід pytest (6 прогонів), сирі UART-логи, мережеві логи (24 файли), Memory Stability Log. Індекс — [EVIDENCE_INDEX.md](EVIDENCE_INDEX.md).

## 10. Findings
25 дефектів: Critical 12, Major 10, Medium 1, Minor 2 — [BUG_REPORTS.md](BUG_REPORTS.md). Найважливіші:
- нагрів ON після аварійного reset і після RESET (DEF-06, DEF-07);
- контролер «замерзає» при збої I2C-датчика (DEF-05);
- відмова датчика видається за 0.0 °C (DEF-04);
- хибна дія від шуму на кнопці (DEF-01);
- мовчазна втрата телеметрії і витік пам'яті (DEF-12, DEF-13).

Класифікація FAIL автотестів: з 23 падінь pytest 21 спричинені дефектами прошивки, 1 — затримкою зв'язку з симулятором, 1 — помилкою в самому тесті.

## 11. Regression
Після будь-якої зміни — smoke (≈10 хв): pytest status / ping / LED / RESET / межі PWM, сценарії A і B мережі, boot і reset reason.
Після зміни підсистеми — її повний пакет; перед релізом — усе разом і 3 прогони. Деталі — [MASTER_TEST_PLAN.md §13](MASTER_TEST_PLAN.md).

## 12. Limitations
Котел розглядається лише як опалювальний електричний: силова частина (контактори ТЕН, УЗО, ізоляція) і контур ГВП не входять у scope.

Wokwi не доводить:
- електричну поведінку: brown-out, Flash / NVS при фізичній втраті живлення, реальний дребезг і наводки;
- реальну мережу: Wi-Fi ≠ broker, QoS / PUBACK;
- реальні таймінги (швидкість симуляції ≠ реальний час);
- роботу всіх підсистем в одній збірці.

На реальному ESP32 перед пілотом: fail-safe виходів при brown-out, NVS при вимиканні живлення під час запису, дребезг реальної кнопки (логічний аналізатор / осцилограф), обрив лінії I2C і DHT22, багатогодинний прогін до стабільного heap, реальний MQTT-брокер з кількома нодами.

## 13. Release / Quality Conclusion
**NO-GO.** Продукт протестовано за risk-based підходом; evidence підтверджує дефекти саме в safety-функціях (R05, R03, R04, R07), тож рішення визначають критичні ризики, а не кількість пройдених тестів. Деталі — [RELEASE_DECISION.md](RELEASE_DECISION.md).

## 14. What I Would Improve Next
1. Інтеграційний стенд: одна збірка з усіма підсистемами і комбінованими збоями (I2C fault + MQTT flush + WDT).
2. Розширити pytest на recovery і мережу (hang / powerloss / NET DOWN через CLI) і запускати в CI з Wokwi CLI.
3. Автоматичний аналіз VCD (sigrok-cli) замість ручного PulseView.
4. Довгий soak-тест з графіком heap.
5. Валідація на реальному ESP32 з логічним аналізатором.
