# Smart Gate Controller — Student Requirements

## States
- CLOSED — ворота закриті.
- OPENING — ворота відкриваються.
- OPEN — ворота повністю відкриті.
- CLOSING — ворота закриваються.
- STOPPED — рух зупинено командою STOP.
- ERROR — небезпечний або некоректний стан.

## Functional requirements
R1. Після запуску контролер перебуває у CLOSED.
R2. OPEN у CLOSED або STOPPED запускає OPENING.
R3. CLOSE у OPEN або STOPPED запускає CLOSING.
R4. OPEN під час CLOSING та CLOSE під час OPENING не повинні створювати небезпечного переходу; спочатку рух має бути безпечно зупинений.
R5. STOP у будь-якому стані руху негайно вимикає обидва реле та переводить систему у STOPPED.
R6. LIMIT_OPEN під час OPENING вимикає OPEN relay і переводить систему в OPEN.
R7. LIMIT_CLOSE під час CLOSING вимикає CLOSE relay і переводить систему в CLOSED.
R8. Обидва реле ніколи не можуть бути активними одночасно.
R9. Рух довше 10 секунд без досягнення кінцевика переводить систему в ERROR.
R10. Одночасно активні LIMIT_OPEN і LIMIT_CLOSE — ERROR.
R11. У ERROR рух заборонений. Для виходу потрібен RESET.
R12. RESET поза ERROR не повинен змінювати стан системи.
R13. Некоректна команда не повинна запускати рух і має бути явно відображена в diagnostics.
R14. OPEN LED відповідає стану OPEN/OPENING; CLOSE LED — CLOSING; ERROR LED — ERROR.
R15. У CLOSED та OPEN обидва реле вимкнені.
R16. Одне натискання кнопки генерує одну команду.

## QA task
Не шукайте причину в коді. Тестуйте контролер як black box.
Знайдіть якомога більше дефектів, використовуючи state transition, negative, boundary/timing та output testing.
Не повідомляйте студентам кількість захованих багів.
