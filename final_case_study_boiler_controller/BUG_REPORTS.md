# Defect Register & Key Bug Reports

Дефекти знайдено на окремих стендах підсистем (тижні 1–7) і зведено до одного продукту. Severity переоцінено в контексті котла: усе, що може залишити нагрів увімкненим без контролю або приховати реальну температуру, — Critical.

## 1. Defect Register

| DEF | Підсистема | Дефект | Ризик | Severity (котел) | Repro | Джерело |
|---|---|---|---|---|---|---|
| DEF-01 | Кнопка BOOST | Імпульс шуму 5 ms створює логічну подію і дію; heavy bounce — подію до стабілізації входу | R01 | Critical | 5/5 | Тиждень 2, TC-05 / TC-08 |
| DEF-02 | Кнопка BOOST | Один натиск — кілька подій (10 натисків → 12–16 подій) | R01 | Major | 5/5 | Тиждень 5, BUG-05 |
| DEF-03 | Сервісний CLI | `set speed 40 / status / set` і довгий рядок → SYSTEM FAULT, SW_CPU_RESET | R02 | Critical | Always | Тиждень 3, BUG-02, BUG-05 |
| DEF-04 | Датчик DHT22 | Відключений датчик → 0.0 °C / 0.0 % як валідні дані, без помилки | R03 | Critical | 5/5 | Тиждень 5, BUG-04 |
| DEF-05 | I2C-датчик | Після першого NACK прошивка зависає: немає retry, error state і відновлення, WDT не спрацьовує | R03, R04 | Critical | 5/5 | Тиждень 4 |
| DEF-06 | Реле нагріву | Після WDT reset і power loss реле відновлюється у стані ON | R05 | Critical | 5/5 | Тиждень 5, BUG-01, BUG-08 |
| DEF-07 | Реле / PWM | RESET відповідає `reset:true`, але виходи не вимикаються | R05 | Critical | 6/6 | Тиждень 6, BUG-03 |
| DEF-08 | NVS | Power loss під час save змінює counter (+100) без перевірки цілісності | R06 | Critical | 5/5 | Тиждень 5, BUG-02 |
| DEF-09 | Привод клапана | На кінцевику OPEN реле не вимикається, стан OPEN недосяжний | R07 | Critical | 5/5 | Тиждень 1, BUG-1 |
| DEF-10 | Мережа | Reconnect storm: retry кожні ≈50 ms без backoff | R08 | Major | 3/3 | Тиждень 7, BUG-01 |
| DEF-11 | Телеметрія | Кожне буферизоване повідомлення публікується двічі | R09 | Major | 3/3 | Тиждень 7, BUG-02 |
| DEF-12 | Телеметрія | Overflow буфера: count > 8, мовчазна втрата найстаріших, новіші — 4–6 разів | R09 | Critical | 3/3 | Тиждень 7, BUG-03 |
| DEF-13 | Пам'ять | Витік 80 B на кожне повідомлення, без відновлення | R10 | Critical | 3/3 | Тиждень 7, BUG-04 |
| DEF-14 | Привод клапана | OPENING > 10 s без кінцевика не переходить у ERROR | R07 | Critical | — | Тиждень 1, BUG-4 |
| DEF-15 | Привод клапана | Обидва кінцевики активні → WARNING замість ERROR, реле OPEN ON | R07 | Critical | — | Тиждень 1, BUG-5 |
| DEF-16 | Привод клапана | Повторна CLOSE під час CLOSING призводить до ERROR по таймауту | R07 | Medium | — | Тиждень 1, BUG-3 |
| DEF-17 | Сервісний CLI | `set timeout 0` приймається; `set speed 256` → 255 без помилки | R02 | Major | Always | Тиждень 3, BUG-01, BUG-06 |
| DEF-18 | Сервісний CLI | `STATUS` у верхньому регістрі і `!@#$%^&*()` приймаються як коректні | R02 | Minor | Always | Тиждень 3, BUG-03, BUG-04 |
| DEF-19 | Сервісний CLI | `SET PWM 100` відхиляється (off-by-one на верхній межі) | R02 | Major | 6/6 | Тиждень 6, BUG-01 |
| DEF-20 | Сервісний CLI | `GET TEMP` повертає обрізаний JSON без `}` | R02, R03 | Major | 6/6 | Тиждень 6, BUG-02 |
| DEF-21 | Діагностика | STATUS показує pwm у шкалі 0..255 замість 0..100 | R12 | Major | 6/6 | Тиждень 6, BUG-04 |
| DEF-22 | Таймери | `sleep N` прокидається ≈10× раніше | R11 | Major | 5/5 | Тиждень 5, BUG-03 |
| DEF-23 | Таймери | WDT reset при вході в sleep ≥ 10 s | R11 | Major | 5/5 | Тиждень 5, BUG-06 |
| DEF-24 | Таймери | Налаштований WDT timeout 4000 ms не застосовується (≈4.8–5.0 s) | R11 | Minor | 5/5 | Тиждень 5, BUG-07 |
| DEF-25 | Сервісний CLI | `sleep abc / 0 / -5 / 999` приймаються без помилки | R02 | Major | 5/5 | Тиждень 5, BUG-09 |

Разом: 25 дефектів — Critical 12, Major 10, Medium 1, Minor 2.

## 2. Key Bug Reports

### DEF-06 — Нагрів залишається ввімкненим після аварійного reset
- **Requirement / Risk:** після аварійного reset виконавчий елемент має бути OFF (R05).
- **Environment:** Wokwi for VS Code, ESP32 DevKit V1, реле GPIO5, Serial 115200.
- **Preconditions:** пристрій ACTIVE, Serial log увімкнено.
- **Steps:** 1) `relay on`; 2) `status` → relay=true; 3) `hang`; 4) дочекатися WDT reset; 5) `status`, перевірити LED реле. Те саме з `powerloss` замість `hang`.
- **Expected:** після reset relay=false, LED не світиться.
- **Actual:** relay=true, LED світиться — пристрій повертає нагрів у стан до збою.
- **Timing / reset reason:** hang → WDT через 5.0 s, `reset_reason=TASK_WDT`.
- **Evidence:** E10, E11 (`serial_log_2026-10-19.txt`, REG-1…REG-5).
- **Severity:** Critical — після зависання ТЕН продовжує гріти без контролю логіки.
- **Reproducibility:** 5/5 регресійних прогонів для WDT і для power loss.
- **Suggested fix:** на старті явно переводити всі виходи в OFF до відновлення стану; відновлювати нагрів лише після валідного вимірювання і явної команди.

### DEF-05 — Прошивка зависає після першого NACK I2C-датчика
- **Requirement / Risk:** помилка I2C обробляється контрольовано, main loop працює, після усунення збою — відновлення (R03, R04).
- **Environment:** ESP32 DevKit + MPU6050 (0x68), SDA GPIO21 / SCL GPIO22, ~100 kHz; Wokwi Logic Analyzer, PulseView (I2C decoder).
- **Steps:** 1) робота ~11 s; 2) FAULT ON; 3) спостерігати UART і I2C; 4) FAULT OFF; 5) спостерігати ≥ 5 s; 6) декодувати VCD.
- **Expected:** обмежені retry з таймаутом, error state, `[SYSTEM] Main loop alive` продовжується; після FAULT OFF обмін відновлюється.
- **Actual:** last ACK 10.524791 s; first NACK (0x69 W) 11.525565 s; далі 6.7 s тиші на шині, 0 повторних спроб, `[DATA]` і `[SYSTEM]` зникають, після FAULT OFF відновлення немає, WDT не спрацьовує.
- **Evidence:** E04, E05 — VCD і три скриншоти PulseView з маркерами.
- **Severity:** Critical — контролер «замерзає» в останньому стані виходів, захист від перегріву не працює.
- **Reproducibility:** 5/5.
- **Suggested fix:** перевіряти результат кожної I2C-операції, таймаут і ліміт повторів, error state з безпечними виходами і періодичною повторною ініціалізацією; WDT має покривати і цей сценарій.

### DEF-04 — Відключений датчик температури видає 0.0 °C як валідне значення
- **Requirement / Risk:** невалідні дані не є вимірюванням, має бути явна помилка (R03).
- **Preconditions:** у diagram.json прибрано з'єднання esp:D15 → dht:SDA.
- **Steps:** 1) `status`; 2) `sensor` ×3; 3) `relay on`; 4) `sensor`; 5) `status`.
- **Expected:** `sensor` повідомляє про помилку датчика без чисел.
- **Actual:** `temp=0.0C humidity=0.0%` без помилки; лише в STATUS `sensor_ok=false`. Те саме одразу після reset з підключеним датчиком.
- **Evidence:** E10, E11.
- **Severity:** Critical (у котлі) — термостат бачить «0 °C», вважає приміщення холодним і гріє без обмеження.
- **Reproducibility:** 5/5.
- **Suggested fix:** повертати явну помилку (NaN / error code), блокувати керування нагрівом при `sensor_ok=false`.

### DEF-12 — Overflow офлайн-буфера: мовчазна втрата і множинні дублі телеметрії
- **Requirement / Risk:** capacity 8, policy DROP_OLDEST, drop видно в counter / log (R09).
- **Steps:** 1) `NET DOWN`; 2) `SEND` ×12; 3) `BUFFER`, `STATUS`; 4) `NET UP`.
- **Expected:** buffer ≤ 8, dropped=4, після NET UP — 8 найновіших ID по одному publish.
- **Actual:** `count=12/8`, `dropped=0`; flush — 24 publish: ID 5–8 від початку серії по 2 рази, ID 9–12 по 4 рази; 4 найстаріші ID зникли без обліку. При STRESS 20 — `count=20/8`, втрачено 12 ID.
- **Evidence:** E15, E17.
- **Severity:** Critical — історія температур і подій котла недостовірна, втрати не видно в моніторингу.
- **Reproducibility:** 3/3 прогони × 3 сценарії (9, 12 SEND, STRESS 20).
- **Suggested fix:** при повному буфері зсувати tail, не збільшувати count понад capacity, інкрементувати dropped і логувати кожен drop.

### DEF-13 — Витік пам'яті 80 B на кожне повідомлення
- **Requirement / Risk:** free heap не падає систематично при SEND / STRESS (R10).
- **Steps:** 1) `STATUS` (baseline); 2) `STRESS 100` → `STATUS` ×10; 3) `RESET STATS` → `STATUS`; 4) окремо 20× `SEND`.
- **Expected:** heap коливається навколо baseline.
- **Actual:** −8000 B на кожну ітерацію (30/30), 80 B на повідомлення; 20× SEND → −1600 B; RESET STATS heap не повертає. За сесію 350868 → 92832 B (−73,5 %).
- **Evidence:** E16, E17 (Memory Stability Log).
- **Severity:** Critical — пам'ять вичерпується приблизно через 4400 повідомлень (≈12 год при телеметрії раз на 10 s), далі відмова контролера.
- **Reproducibility:** 3/3 прогони.
- **Suggested fix:** звільняти пам'ять повідомлення після publish / буферизації; статичний пул або кільцевий буфер фіксованого розміру.

Повні звіти по всіх дефектах — у протоколах підсистем ([EVIDENCE_INDEX.md](EVIDENCE_INDEX.md)).
