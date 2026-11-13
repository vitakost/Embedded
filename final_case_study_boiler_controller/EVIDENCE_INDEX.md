# Evidence Package Index

Кожен висновок у [FINAL_TEST_MATRIX.md](FINAL_TEST_MATRIX.md) і [BUG_REPORTS.md](BUG_REPORTS.md) спирається на файл нижче. Шляхи — відносно цієї папки.

| Evidence ID | Related Test / Risk | Type | Description | File / Link |
|---|---|---|---|---|
| E01 | T01–T03, T28 / R01 | Test log + Serial | Debounce: 8 тест-кейсів, 3 bug reports; Serial Logger 26 прогонів Wokwi CLI (норма, шум 5 ms, шум під час операції, heavy bounce — по 5) | [Debounce_Test_Sheet_Test_Log.docx](evidence/hw2_button_debounce/Debounce_Test_Sheet_Test_Log.docx), [logs/](evidence/hw2_button_debounce/logs/) |
| E02 | T01–T03, T28 / R01 | Logic trace + scenarios | VCD D0 / D1 (ручна сесія 28.09) і графік одного натиску; 6 сценаріїв Wokwi CLI (по одному на тест) і перша версія спільного сценарію | [button_trace.vcd](evidence/hw2_button_debounce/button_trace.vcd), [графік](evidence/hw2_button_debounce/logic_analyzer_one_press.png), [scenarios/](evidence/hw2_button_debounce/scenarios/), [scenario.yaml](evidence/hw2_button_debounce/scenario.yaml) |
| E03 | T05–T06 / R02 | Test report + Serial | UART CLI: 36 тестів, межі speed / timeout і довжини рядка (40 / 41), 6 bug reports; логи повного набору, межі довжини і 5 прогонів дефектів; скриншоти DIRTY / SAVED | [UART_CLI_Test_Report.docx](evidence/hw3_uart_cli/UART_CLI_Test_Report.docx), [logs/](evidence/hw3_uart_cli/logs/), [screenshots/](evidence/hw3_uart_cli/screenshots/) |
| E04 | T09 / R03, R04 | Logic trace | I2C SDA / SCL, 0–18.24 s: 11 нормальних циклів, перший NACK 11.525565 s, далі тиша | [i2c_trace.vcd](evidence/hw4_i2c_sensor/i2c_trace.vcd) |
| E05 | T09 / R03, R04 | PulseView screenshots + sheet | Увесь запис, last ACK 10.524791 s, first NACK; transaction log і fault timeline | [full](evidence/hw4_i2c_sensor/pulseview_full_capture.png), [last ACK](evidence/hw4_i2c_sensor/pulseview_last_ack.png), [first NACK](evidence/hw4_i2c_sensor/pulseview_first_nack.png), [sheet](evidence/hw4_i2c_sensor/Protocol_Analysis_Sheet.docx) |
| E06 | T16–T19 / R07 | Test log | Привод (state machine, кінцевики, таймаут, interlock): 24 тест-кейси, 4 дефекти (протокол оновлено після рев'ю) | [Hardware_Test_Sheet_Test_Log.docx](evidence/hw1_valve_actuator/Hardware_Test_Sheet_Test_Log.docx), [requirements](evidence/hw1_valve_actuator/requirements_actuator.md) |
| E10 | T04, T08, T10–T12, T14–T15, T25, T27 / R01, R03–R06, R11 | Test sheet | Recovery & fault injection: 20 тестів, 10 дефектів, reproducibility 5/5 | [Recovery_Fault_Injection_Test_Sheet.docx](evidence/hw5_recovery_persistence/Recovery_Fault_Injection_Test_Sheet.docx) |
| E11 | T11–T14 / R05, R06 | Serial / reset log | Boot log, reset reason, relay / counter до і після hang / powerloss, 5 регресійних прогонів | [serial_log_2026-10-19.txt](evidence/hw5_recovery_persistence/serial_log_2026-10-19.txt) |
| E12 | T07, T13, T26 / R02, R05, R12 | Pytest | Вивід pytest: baseline (timeout 1.0 s) і 5 регресій (3.0 s) | [pytest_run1..5.txt](evidence/hw6_pytest_cli/), [pytest_baseline_t1.txt](evidence/hw6_pytest_cli/pytest_baseline_t1.txt) |
| E13 | T07, T13 / R02, R05 | Serial + bug evidence | Сирий UART-лог кожного прогону; витяги по кожному дефекту | [serial_run1..5.log](evidence/hw6_pytest_cli/), [bugs/](evidence/hw6_pytest_cli/bugs/) |
| E14 | T20–T21 / R08 | Network log | NET DOWN / UP, retry з мітками часу, 20× reconnect, 3 прогони | [run1..3_A_connection_loss.log](evidence/hw7_network_memory/), [run1..3_E_reconnect_x20.log](evidence/hw7_network_memory/) |
| E15 | T22–T23, T26 / R09, R12 | Message IDs | Queued / publish ID, flush order, лічильники для 5 / 8 / 9 / 12 SEND і STRESS 20 | [run1..3_B / C / F_*.log](evidence/hw7_network_memory/) |
| E16 | T24 / R10 | Metrics | Heap на кожній з 10 ітерацій STRESS 100 ×3 прогони, 20× SEND | [run1..3_D_stress_memory.log](evidence/hw7_network_memory/), [run1..3_F_send_heap.log](evidence/hw7_network_memory/) |
| E17 | R08–R10 | Test sheet | State model, Fault Log, Memory Stability Log, Message ID evidence, 4 bug reports | [IoT_Network_Memory_Test_Sheet_Webinar_7_FAIL.docx](evidence/hw7_network_memory/IoT_Network_Memory_Test_Sheet_Webinar_7_FAIL.docx) |
| E18 | R02, R05, R12 | Test sheet | Execution log 67 тест-кейсів, класифікація FAIL, 4 bug reports | [Python_Pytest_Test_Sheet_Webinar_6_FAIL.docx](evidence/hw6_pytest_cli/Python_Pytest_Test_Sheet_Webinar_6_FAIL.docx) |
| E19 | T09 / R03, R04 | Logic trace + Serial | 5 повторних прогонів I2C FAULT ON → OFF, FAULT записано на D2 (GPIO27): моменти ON/OFF, last ACK, first NACK, 0 повторів, тиша після OFF — 5/5 | [rerun_logs/run1..5](evidence/hw4_i2c_sensor/rerun_logs/) |

## Відповідність ID дефектів: протоколи тижнів → реєстр DEF

У протоколах тижнів 1–7 дефекти мають свої оригінальні ID (BUG-xx, номери тест-кейсів). У [BUG_REPORTS.md](BUG_REPORTS.md), [FINAL_TEST_MATRIX.md](FINAL_TEST_MATRIX.md) і [RELEASE_DECISION.md](RELEASE_DECISION.md) вони зведені в єдиний реєстр DEF-xx. Таблиця дозволяє від кожного DEF перейти до оригінального звіту і навпаки.

| Тиждень / стенд | Оригінальний ID | DEF | Evidence |
|---|---|---|---|
| 1 — привод (Smart Gate) | BUG-1 | DEF-09 | E06 |
| 1 — привод (Smart Gate) | BUG-2 | — знято: TC-04 Blocked by BUG-1, окремий баг не потрібен | E06 |
| 1 — привод (Smart Gate) | BUG-3 | — знято: ERROR у TC-09 — штатний movement timeout, причинний зв'язок з повторним CLOSE не доведено | E06 |
| 1 — привод (Smart Gate) | BUG-4 | DEF-14 | E06 |
| 1 — привод (Smart Gate) | BUG-5 | DEF-15 | E06 |
| 1 — привод (Smart Gate) | BUG-6 | DEF-16 | E06 |
| 2 — кнопка, debounce | BUG-01 (TC-05, шум 5 ms) | DEF-01 | E01, E02 |
| 2 — кнопка, debounce | BUG-02 (TC-06, шум під час критичної операції) | DEF-27 | E01, E02 |
| 2 — кнопка, debounce | BUG-03 (TC-08, heavy bounce) | DEF-28 | E01, E02 |
| 3 — UART CLI | BUG-01 | DEF-17 | E03 |
| 3 — UART CLI | BUG-02 | DEF-03 | E03 |
| 3 — UART CLI | BUG-03 | DEF-18 | E03 |
| 3 — UART CLI | BUG-04 | DEF-18 | E03 |
| 3 — UART CLI | BUG-05 | DEF-03 | E03 |
| 3 — UART CLI | BUG-06 | DEF-17 | E03 |
| 4 — I2C | Bug Report (без ID) | DEF-05 | E04, E05, E19 |
| 5 — recovery | BUG-01 | DEF-06 | E10, E11 |
| 5 — recovery | BUG-02 | DEF-08 | E10, E11 |
| 5 — recovery | BUG-03 | DEF-22 | E10, E11 |
| 5 — recovery | BUG-04 | DEF-04 | E10, E11 |
| 5 — recovery | BUG-05 | DEF-02 | E10, E11 |
| 5 — recovery | BUG-06 | DEF-23 | E10, E11 |
| 5 — recovery | BUG-07 | DEF-24 | E10, E11 |
| 5 — recovery | BUG-08 | DEF-06 | E10, E11 |
| 5 — recovery | BUG-09 | DEF-25 | E10, E11 |
| 5 — recovery | BUG-10 | DEF-26 | E10, E11 |
| 6 — pytest CLI | BUG-01 (`bugs/BUG-01_SET_PWM_100_rejected_*`) | DEF-19 | E12, E13, E18 |
| 6 — pytest CLI | BUG-02 (`bugs/BUG-02_GET_TEMP_invalid_JSON_*`) | DEF-20 | E12, E13, E18 |
| 6 — pytest CLI | BUG-03 (`bugs/BUG-03_RESET_not_safe_state_*`) | DEF-07 | E12, E13, E18 |
| 6 — pytest CLI | BUG-04 (`bugs/BUG-04_STATUS_pwm_wrong_scale_*`) | DEF-21 | E12, E13, E18 |
| 7 — мережа, пам'ять | BUG-01 | DEF-10 | E14, E17 |
| 7 — мережа, пам'ять | BUG-02 | DEF-11 | E15, E17 |
| 7 — мережа, пам'ять | BUG-03 | DEF-12 | E15, E17 |
| 7 — мережа, пам'ять | BUG-04 | DEF-13 | E16, E17 |

Спостереження тижня 7 (OBS-01, OBS-02: `sent` рахує дублікати, `dropped` завжди 0) окремих DEF не мають — вони покриті тестом T26 (ризик R12).

## Відповідність шаблону курсу (E01–E08)

| Шаблон | Ризик курсу | Evidence у цьому пакеті |
|---|---|---|
| E01 Button / debounce | R01 | E01, E02, E10 |
| E02 CLI automation result | R02 | E12, E13, E03 |
| E03 I2C / SPI trace | R03 | E04, E05, E19 |
| E04 WDT recovery | R04 | E10, E11 |
| E05 Persistence integrity | R05 | E10, E11 |
| E06 Reconnect lifecycle | R06 | E14 |
| E07 Buffer / duplicate evidence | R07 | E15, E17 |
| E08 Heap trend | R08 | E16, E17 |

## Rule
Evidence має дозволяти іншій людині перевірити висновок QA: кожен файл містить команди або дії і відповіді пристрою з мітками часу.
