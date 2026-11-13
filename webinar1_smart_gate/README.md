# Webinar 1 — Smart Gate Controller: функціональне black-box тестування

Контролер воріт (Arduino Uno, Wokwi): стани CLOSED / OPENING / OPEN / CLOSING / STOPPED / ERROR, два реле напрямку, кінцевики LIMIT_OPEN / LIMIT_CLOSE, кнопки OPEN / CLOSE / STOP / RESET, LED-індикація, таймаут руху 10 s.
Тестування black-box за вимогами курсу: дії на схемі та Serial-лог.

## Файли

| Файл | Що всередині |
|---|---|
| `Hardware_Test_Sheet_Test_Log.docx` | Протокол: 24 тест-кейси з Actual Result, 4 bug reports, підсумок сесії |
| `Smart_Gate_Test_Cases.xlsx` | Тест-кейси переходів станів (TC-01…TC-10) |

## Результати (21.09.2026)

24 тест-кейси: PASS — 16, FAIL — 5, Blocked — 1, Not verified — 2.

| ID | Дефект | Severity | Тест |
|---|---|---|---|
| BUG-1 | LIMIT_OPEN не переводить OPENING → OPEN, реле OPEN лишається ON (5/5) | High | TC-03; блокує TC-04 |
| BUG-4 | Немає таймауту руху в OPENING: > 10 s без кінцевика — без ERROR | High | TC-13 |
| BUG-5 | Обидва кінцевики активні → лише WARNING, реле OPEN ON, ERROR немає | Critical | TC-15 |
| BUG-6 | У стані STOPPED світиться LED OPEN | Medium | TC-06, TC-07 |

## Оновлення після рев'ю
- BUG-1: severity Critical → High.
- BUG-2 знято: TC-04 позначено «Blocked by BUG-1», окремий баг не потрібен.
- BUG-3 знято: у TC-09 повторний CLOSE коректно проігноровано, а ERROR — штатний movement timeout; причинний зв'язок не доведено, TC-09 → PASS.
- BUG-6 додано: у TC-06/07 зафіксовано OPEN LED ON у STOPPED, а за уточненою вимогою в STOPPED усі LED мають бути OFF.
- TC-10/11 → Not verified: у лозі немає стану реле під час зміни напрямку, тож безпечну послідовність реверсу (без миттєвого переключення реле на реле) не підтверджено. Потрібен повторний прогін із логом станів реле.
