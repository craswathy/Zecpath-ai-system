# System Performance Analysis -- Day 56

Timings are for the code in this test only. Stand-ins are fast. The real ATS and model loading (Whisper, sentence-transformers) are not included.

Runs timed: 240 (all candidates, repeated, with logging in batch mode)

| Stage | Average milliseconds |
|---|---|
| resume_upload | 0.021 |
| ats | 0.002 |
| screening | 0.029 |
| hr_interview | 0.373 |
| technical_interview | 0.331 |
| final_decision | 0.042 |

Whole journey per candidate: 0.748 ms
Throughput: about 1337.6 candidates per second on this machine
