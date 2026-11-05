# System Performance Analysis -- Day 56

Timings are for the code in this test only. Stand-ins are fast. The real ATS and model loading (Whisper, sentence-transformers) are not included.

Runs timed: 240 (all candidates, repeated, with logging in batch mode)

| Stage | Average milliseconds |
|---|---|
| resume_upload | 0.024 |
| ats | 0.003 |
| screening | 0.091 |
| hr_interview | 0.436 |
| technical_interview | 0.413 |
| final_decision | 0.054 |

Whole journey per candidate: 0.961 ms
Throughput: about 1040.8 candidates per second on this machine
