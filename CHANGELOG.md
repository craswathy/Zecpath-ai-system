# Changelog -- HR Interview AI

## v1.0 (Day 45) -- final demo and handover

* Added final demo runner (ats\_engine/run\_final\_demo.py) and demo dataset (data/demo\_dataset/)
* Added tests/test\_final\_demo.py
* Post-demo changes: \[list each change made after manager feedback, or write "none requested"]

## v1.1 (Day 57) -- debugging and stabilization
- Fixed 13 bugs and 3 API problems (see docs/stability/DEBUGGING_REPORT_DAY57.md)
- Decision rules RESUME_FAILED and STAGE_ERROR (decision_v1.2)
- Stages return no score instead of a fake 0 when there is nothing to score
- API input limits, score bounds, one error shape for unexpected errors
- Added edge-case battery, random-input test, bug repro script, 30 new tests
