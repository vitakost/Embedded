# Evidence Package Index

Кожен висновок у [FINAL_TEST_MATRIX.md](FINAL_TEST_MATRIX.md) і [BUG_REPORTS.md](BUG_REPORTS.md) спирається на файл нижче. Шляхи — відносно цієї папки.

| Evidence ID | Related Test / Risk | Type | Description | File / Link |
|---|---|---|---|---|
| E01 | T01–T03 / R01 | Test log + Serial | Debounce: норма, шум 5 ms, heavy bounce — 5 прогонів, RAW / logical / actions | [Debounce_Test_Sheet_Test_Log.docx](evidence/hw2_button_debounce/Debounce_Test_Sheet_Test_Log.docx) |
| E02 | T02–T03 / R01 | Logic trace + scenario | VCD входу кнопки (D0) і виходу (D1); скрипт сценарію Wokwi CLI | [button_trace.vcd](evidence/hw2_button_debounce/button_trace.vcd), [scenario.yaml](evidence/hw2_button_debounce/scenario.yaml) |
| E03 | T05–T06 / R02 | Test report | UART CLI: 30 тест-кейсів, межі поведінки 1 / 40 / 255, SYSTEM FAULT + SW_CPU_RESET | [UART_CLI_Test_Report.docx](evidence/hw3_uart_cli/UART_CLI_Test_Report.docx) |
| E04 | T09 / R03, R04 | Logic trace | I2C SDA / SCL, 0–18.24 s: 11 нормальних циклів, перший NACK 11.525565 s, далі тиша | [i2c_trace.vcd](evidence/hw4_i2c_sensor/i2c_trace.vcd) |
| E05 | T09 / R03, R04 | PulseView screenshots + sheet | Увесь запис, last ACK 10.524791 s, first NACK; transaction log і fault timeline | [full](evidence/hw4_i2c_sensor/pulseview_full_capture.png), [last ACK](evidence/hw4_i2c_sensor/pulseview_last_ack.png), [first NACK](evidence/hw4_i2c_sensor/pulseview_first_nack.png), [sheet](evidence/hw4_i2c_sensor/Protocol_Analysis_Sheet.docx) |
| E06 | T16–T19 / R07 | Test log | Привод (state machine, кінцевики, таймаут, interlock): 24 тест-кейси, 5 дефектів | [Hardware_Test_Sheet_Test_Log.docx](evidence/hw1_valve_actuator/Hardware_Test_Sheet_Test_Log.docx), [requirements](evidence/hw1_valve_actuator/requirements_actuator.md) |
| E10 | T04, T08, T10–T12, T14–T15, T25 / R01, R03–R06, R11 | Test sheet | Recovery & fault injection: 20 тестів, 9 дефектів, reproducibility 5/5 | [Recovery_Fault_Injection_Test_Sheet.docx](evidence/hw5_recovery_persistence/Recovery_Fault_Injection_Test_Sheet.docx) |
| E11 | T11–T14 / R05, R06 | Serial / reset log | Boot log, reset reason, relay / counter до і після hang / powerloss, 5 регресійних прогонів | [serial_log_2026-10-19.txt](evidence/hw5_recovery_persistence/serial_log_2026-10-19.txt) |
| E12 | T07, T13, T26 / R02, R05, R12 | Pytest | Вивід pytest: baseline (timeout 1.0 s) і 5 регресій (3.0 s) | [pytest_run1..5.txt](evidence/hw6_pytest_cli/), [pytest_baseline_t1.txt](evidence/hw6_pytest_cli/pytest_baseline_t1.txt) |
| E13 | T07, T13 / R02, R05 | Serial + bug evidence | Сирий UART-лог кожного прогону; витяги по кожному дефекту | [serial_run1..5.log](evidence/hw6_pytest_cli/), [bugs/](evidence/hw6_pytest_cli/bugs/) |
| E14 | T20–T21 / R08 | Network log | NET DOWN / UP, retry з мітками часу, 20× reconnect, 3 прогони | [run1..3_A_connection_loss.log](evidence/hw7_network_memory/), [run1..3_E_reconnect_x20.log](evidence/hw7_network_memory/) |
| E15 | T22–T23, T26 / R09, R12 | Message IDs | Queued / publish ID, flush order, лічильники для 5 / 8 / 9 / 12 SEND і STRESS 20 | [run1..3_B / C / F_*.log](evidence/hw7_network_memory/) |
| E16 | T24 / R10 | Metrics | Heap на кожній з 10 ітерацій STRESS 100 ×3 прогони, 20× SEND | [run1..3_D_stress_memory.log](evidence/hw7_network_memory/), [run1..3_F_send_heap.log](evidence/hw7_network_memory/) |
| E17 | R08–R10 | Test sheet | State model, Fault Log, Memory Stability Log, Message ID evidence, 4 bug reports | [IoT_Network_Memory_Test_Sheet_Webinar_7_FAIL.docx](evidence/hw7_network_memory/IoT_Network_Memory_Test_Sheet_Webinar_7_FAIL.docx) |
| E18 | R02, R05, R12 | Test sheet | Execution log 67 тест-кейсів, класифікація FAIL, 4 bug reports | [Python_Pytest_Test_Sheet_Webinar_6_FAIL.docx](evidence/hw6_pytest_cli/Python_Pytest_Test_Sheet_Webinar_6_FAIL.docx) |

## Відповідність шаблону курсу (E01–E08)

| Шаблон | Ризик курсу | Evidence у цьому пакеті |
|---|---|---|
| E01 Button / debounce | R01 | E01, E02, E10 |
| E02 CLI automation result | R02 | E12, E13, E03 |
| E03 I2C / SPI trace | R03 | E04, E05 |
| E04 WDT recovery | R04 | E10, E11 |
| E05 Persistence integrity | R05 | E10, E11 |
| E06 Reconnect lifecycle | R06 | E14 |
| E07 Buffer / duplicate evidence | R07 | E15, E17 |
| E08 Heap trend | R08 | E16, E17 |

## Rule
Evidence має дозволяти іншій людині перевірити висновок QA: кожен файл містить команди або дії і відповіді пристрою з мітками часу.
