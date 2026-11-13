# Webinar 5 — Recovery / Fault Injection: sleep, watchdog, power loss, persistence

IoT-контролер на ESP32 (Wokwi): DHT22, кнопка, реле, LED, UART CLI, NVS. Fault injection через CLI: `hang` (зависання → WDT), `powerloss` (перерване збереження), `sleep N` (deep sleep), відключення DHT22 у схемі.
Перевірялось за вимогами R1–R7: boot і reset reason, відмова датчика, кнопка, sleep / wake, watchdog, перерване збереження, діагностика через `status`.

## Файли

| Файл | Що всередині |
|---|---|
| `Recovery_Fault_Injection_Test_Sheet_Webinar_5_FAIL.docx` | Протокол: ризики, Test Matrix, трасування R1–R7, 20 тестів, 10 bug reports, матриця відтворюваності, release decision |
| `serial_log_buggy_wokwi_2026-10-19.txt` | Serial-лог усіх прогонів з часом симуляції: Run 1–3 і 5 регресійних прогонів REG-1…REG-5 |

## Результати (19.10.2026)

20 тестів: PASS — 7, FAIL — 13. 10 дефектів, кожен відтворено в 5 з 5 регресійних прогонів.

| ID | Дефект | Severity |
|---|---|---|
| BUG-01 | Реле відновлюється у стані ON після WDT reset | Critical |
| BUG-02 | Power loss під час запису змінює counter (+100) без перевірки цілісності | Critical |
| BUG-08 | Реле лишається ON після power loss | Critical |
| BUG-03 | `sleep N` прокидається ≈ у 10 разів раніше | Major |
| BUG-04 | Відключений DHT22 → 0.0 °C / 0.0 % без помилки | Major |
| BUG-05 | Один натиск кнопки → кілька подій (10 натисків → 12–16) | Major |
| BUG-09 | `sleep abc / 0 / -5 / 999` приймаються без помилки | Major |
| BUG-10 | Після аварійного reset немає етапу відновлення: жодних логів [RECOVERY], стан одразу ACTIVE | Major |
| BUG-06 | Зайвий WDT reset при вході в sleep ≥ 10 s (ймовірно артефакт Wokwi) | Minor |
| BUG-07 | WDT спрацьовує за ≈ 5 s замість заявлених 4000 ms | Minor |

Рішення: **NO-GO** — небезпечний стан реле після будь-якого аварійного reset і пошкодження збереженого стану без виявлення.

## Оновлення після рев'ю
- BUG-06: severity Major → Minor. Дефект спостерігався лише в симуляторі й найімовірніше є артефактом моделювання deep sleep; позначка про обов'язкову перевірку на реальному ESP32 залишилась.
- Додано BUG-10: після WDT reset і power loss у лозі немає жодного повідомлення про відновлення, а `status` одразу показує ACTIVE (150 з 150 відповідей, зокрема 41 після TASK_WDT). Через це небезпечний стан реле (BUG-01, BUG-08) пристрій не виявляє і не виправляє.
