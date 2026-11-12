# Action Plan -- Day 64

Dates are placeholders. Set them with your mentor, based on the time you have left.

## Now (this week)
| Action | Improvement | Done when | Date |
|---|---|---|---|
| Fix or explain each walkthrough mismatch | I3 | Each has a documented cause | [ ] |
| Check run_answer_understanding.py and the duplicate modules | I5 | Index shows correct functions, duplicates explained or removed | [ ] |
| Update the handbook | I6 | The handbook documentation test passes with the new modules named | [ ] |
| Collect written reviewer feedback | all | Forms returned and summarised in the report | [ ] |

## Next
| Action | Improvement | Done when | Date |
|---|---|---|---|
| Add reasons to candidate reports | I7 | A report shows why each score was given | [ ] |
| Add column-aware extraction or an OCR fallback | I2 | A multi-column and a scanned test file extract text | [ ] |
| Re-run the load test with a real HTTP tool | I9 | Report updated with new numbers | [ ] |

## Later (needs data or infrastructure)
| Action | Improvement | Depends on |
|---|---|---|
| Validate thresholds on real data | I1 | Real recruiter-labelled outcomes |
| Trained NER model | I4 | Labelled resume data |
| Database, queue, authentication | I8 | Backend team and infrastructure |
| Multilingual support, dashboard | I10, I11 | Product decisions |

## Review checkpoints
Re-run python -m ats_engine.run_system_walkthrough and pytest tests\ after
each action. Update the report with the new results.