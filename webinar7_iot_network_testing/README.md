# Webinar 7 — IoT & Network Testing

Тестування IoT-ноди ESP32 (`homework_buggy`, Wokwi) у неідеальній мережі: втрата зв'язку, retry/backoff, offline buffer, межа буфера, дублікати після reconnect, stress і стабільність пам'яті.
Очікувані результати — за вимогами R1–R8 з `device_requirements.md` курсу.

## Структура

| Файл | Призначення |
|---|---|
| `IoT_Network_Memory_Test_Sheet_Webinar_7.docx` | Test Sheet: state model, ризики, Test Matrix, Fault Log, Memory Stability Log, Message ID evidence, bug reports, висновок |
| `state_model.png` | Network state model за фактичними переходами з логу |
| `run_scenarios.py` | Відправляє команди CLI сценаріїв A–D у Serial через RFC2217 і пише лог з мітками часу |
| `evidence/runN_<scenario>.log` | Повний Serial-лог кожного сценарію, 3 прогони (24 файли) |

## Сценарії

| Лог | Що виконано |
|---|---|
| `A_connection_loss` | RESET STATS → NET DOWN 16 s → NET UP → STATUS |
| `B_offline_buffer_5` | NET DOWN → 5× SEND → BUFFER → NET UP → STATUS |
| `C_boundary_8`, `C_boundary_9`, `C_overflow_12` | NET DOWN → 8 / 9 / 12× SEND → BUFFER → NET UP |
| `E_reconnect_x20` | 20 циклів NET DOWN 3 s / NET UP 4 s → STATUS |
| `D_stress_memory` | 10× (STRESS 100 → STATUS) → RESET STATS |
| `F_send_heap` | 20× SEND у CONNECTED; STRESS 20 при NET DOWN → NET UP |

## Запуск

Симуляція `homework_buggy` запущена у VS Code (Wokwi), Serial Monitor закритий.

```powershell
pip install pyserial
python run_scenarios.py 1        # усі сценарії, логи в evidence/run1_*.log
python run_scenarios.py 2 A C12  # лише вибрані сценарії
```

`DEVICE_PORT` — порт Serial (за замовчуванням `rfc2217://localhost:4000`).

## Результати (01.11.2026, 3 прогони)

| ID | Дефект | Вимога | Severity | Repro |
|---|---|---|---|---|
| BUG-01 | Reconnect storm: після першої спроби (500 ms) retry кожні ≈50 ms без зростання backoff; 214–278 спроб за 16 s | R2 | Major | 3/3 |
| BUG-02 | Після reconnect кожне буферизоване повідомлення публікується двічі (5 SEND → sent=10, duplicates=5) | R6 | Major | 3/3 |
| BUG-03 | Overflow буфера: count до 12/8 і 20/8, найстаріші ID втрачаються при dropped=0, новіші публікуються 4–6 разів | R4, R5, R6 | Critical | 3/3 |
| BUG-04 | Витік пам'яті 80 B на кожне повідомлення: STRESS 100 → −8000 B щоразу, без відновлення (350868 → 92832 B за сесію) | R7 | Critical | 3/3 |

R1, R3 — PASS; R8 — поля STATUS є, але `sent` рахує дублікати, а `dropped` завжди 0.
Висновок: нода відновлює з'єднання (60/60 reconnect, без зависань), але не стабільна в неідеальній мережі — дублікати, мовчазна втрата даних на межі буфера, reconnect storm і витік пам'яті.
