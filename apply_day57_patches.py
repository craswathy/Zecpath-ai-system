"""
Day 57 patch tool. Applies small, exact text fixes to existing files.
Each fix replaces one unique piece of text. A fix that is already applied is skipped.
A fix whose text is not found is reported, and nothing in that file is changed.
Originals are copied to <file>.bak before the first change.
"""
import os
import shutil
import sys

PATCHES = {
    "ats_engine/refined_intent.py": [
        (r'''|\bkind of\b|\bsort of\b"''',
         r'''|(?<!what )(?<!this )(?<!that )(?<!any )(?<!every )(?<!some )(?<!each )(?<!same )(?<!which )(?<!a )(?<!the )\b(?:kind|sort) of\b"'''),
    ],
    "ats_engine/transcript_normalizer.py": [
        ('    text = raw_text.strip()', '    text = str(raw_text).strip()'),
    ],
    "ats_engine/cross_round_aggregation_engine.py": [
        ('    base_weights, role_used = get_role_weights(role_category)',
         '    round_scores = round_scores if isinstance(round_scores, dict) else {}\n'
         '    base_weights, role_used = get_role_weights(role_category)'),
    ],
    "ats_engine/technical_scoring_engine.py": [
        ('    answer_text = (answer_text or "").strip()', '    answer_text = str(answer_text or "").strip()'),
        ('    q_type, level = question["type"], question["level"]',
         '    q_type, level = question["type"], question["level"]\n'
         '    if q_type not in PARAMETER_WEIGHTS or level not in LEVEL_WEIGHTS:\n'
         '        raise ValueError(f"Unknown question type or level for {question.get(\'id\')}: {q_type}, {level}")'),
        ('        return {"technical_score": 0.0, "band": "No data", "skills": {}, "explanation": "No answers to score."}',
         '        return {"technical_score": None, "band": "No data", "band_adjusted_from": None, "skills": {},\n'
         '                "weak_skills": [], "parameter_averages": {}, "answers_scored": 0, "reliability": "low_reliability",\n'
         '                "shallow_answers": 0, "keyword_listing_answers": 0, "explanation": "No answers to score."}'),
    ],
    "ats_engine/governance_controls.py": [
        ('    entry = (consent or {}).get("purposes", {}).get(purpose)',
         '    purposes = consent.get("purposes") if isinstance(consent, dict) else None\n'
         '    entry = purposes.get(purpose) if isinstance(purposes, dict) else None\n'
         '    if not isinstance(entry, dict):\n'
         '        return False'),
        ('    allowed, reason = is_allowed(user, action, candidate)',
         '    if not isinstance(user, dict) or not user.get("user_id"):\n'
         '        audit.log("access", "unknown", None, {"action": action, "allowed": False, "reason": "no verified user"})\n'
         '        return False, "no verified user"\n'
         '    allowed, reason = is_allowed(user, action, candidate)'),
        ('        return hashlib.sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()',
         '        return hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode("utf-8")).hexdigest()'),
        (r'''                f.write(json.dumps(entry) + "\n")''',
         r'''                f.write(json.dumps(entry, default=str) + "\n")'''),
        ('        days = RETENTION_DAYS.get(r["type"])', '        days = RETENTION_DAYS.get(r.get("type"))'),
        ('        created = datetime.fromisoformat(r["created_at"])',
         '        try:\n'
         '            created = datetime.fromisoformat(r["created_at"])\n'
         '        except (KeyError, TypeError, ValueError):\n'
         '            logger.warning(f"Skipped record with unreadable created_at: {r.get(\'id\')}")\n'
         '            continue'),
        ('        if r["candidate_id"] != candidate_id or r.get("legal_hold") or r["type"] == "audit_log":',
         '        if r.get("candidate_id") != candidate_id or r.get("legal_hold") or r.get("type") == "audit_log":'),
        ('        purpose = DATA_PURPOSE.get(r["type"])', '        purpose = DATA_PURPOSE.get(r.get("type"))'),
    ],
    "ats_engine/run_e2e_simulation.py": [
        ('    timings, errors, stages = {}, [], {}',
         '    timings, errors, stages = {}, [], {}\n'
         '    for field in ("resume", "screening", "hr", "tech"):\n'
         '        key = cand.get(field)\n'
         '        if key is not None and key not in banks.get(field, {}):\n'
         '            errors.append(f"{field}: unknown data key \'{key}\'")'),
        ('banks["resume"][cand["resume"]]', 'banks["resume"].get(cand["resume"], "")'),
        ('banks["screening"][cand["screening"]]', 'banks["screening"].get(cand["screening"])'),
        ('banks["hr"][cand["hr"]]', 'banks["hr"].get(cand["hr"])'),
        ('banks["tech"][cand["tech"]]', 'banks["tech"].get(cand["tech"])'),
        ('    context = {"integrity_review_priority": cand.get("integrity", "No concern"),',
         '    context = {"resume_status": stages["resume_upload"]["status"], "pipeline_errors": len(errors),\n'
         '               "integrity_review_priority": cand.get("integrity", "No concern"),'),
        ('    ok, bad_seq = audit.verify()',
         '    check("Failed resume upload never gives Selected or Rejected",\n'
         '          all(j["decision"]["decision"] == "Hold / Review" for j in journeys if j["stages"]["resume_upload"]["status"] != "ok"))\n'
         '    ok, bad_seq = audit.verify()'),
    ],
    "ats_engine/hr_api_server.py": [
        ('    question_id: str', '    question_id: str = Field(min_length=1, max_length=100)'),
        ('    answer_text: str', '    answer_text: str = Field(max_length=5000)'),
        ('    candidate_id: str', '    candidate_id: str = Field(min_length=1, max_length=100)'),
        ('    job_id: str', '    job_id: str = Field(min_length=1, max_length=100)'),
        ('    communication_score: Optional[float] = None', '    communication_score: Optional[float] = Field(default=None, ge=0, le=100)'),
        ('    behavioral_confidence_score: Optional[float] = None',
         '    behavioral_confidence_score: Optional[float] = Field(default=None, ge=0, le=100)'),
        ('    per_turn_data: List[TurnData]', '    per_turn_data: List[TurnData] = Field(max_length=200)'),
        ('@app.post("/api/v1/hr-interviews", status_code=201)',
         '@app.exception_handler(Exception)\n'
         'async def unexpected_error_handler(request, exc):\n'
         '    logger.error(f"Unexpected error on {request.url.path}: {type(exc).__name__}")\n'
         '    return JSONResponse(\n'
         '        status_code=500,\n'
         '        content={"error": {"code": "INTERNAL_ERROR", "message": "Something went wrong. The error was logged."}},\n'
         '    )\n'
         '\n\n'
         '@app.post("/api/v1/hr-interviews", status_code=201)'),
    ],
    "tests/test_e2e_simulation.py": [
        ('    assert kinds["e2e_08"] == "AI firmer than the human"',
         '    assert kinds["e2e_08"] == "match"          # Day 57: a failed resume upload now goes to Hold / Review'),
    ],
    "tests/test_day54_refinement.py": [
        ('    assert d["metadata"]["model_version"] == "decision_v1.1"',
         '    assert d["metadata"]["model_version"] == "decision_v1.2"'),
    ],
}


def apply():
    applied = skipped = failed = 0
    for path, edits in PATCHES.items():
        if not os.path.exists(path):
            print(f"MISSING FILE  {path}")
            failed += len(edits)
            continue
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        changed = 0
        for n, (old, new) in enumerate(edits, 1):
            count = text.count(old)
            if new in text:
                skipped += 1
                print(f"already applied  {path} fix {n}")
            elif count == 1:
                text = text.replace(old, new)
                changed += 1
                applied += 1
            else:
                failed += 1
                print(f"NOT APPLIED   {path} fix {n}: text found {count} times (needs exactly 1)")
        if changed:
            if not os.path.exists(path + ".bak"):
                shutil.copy(path, path + ".bak")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"patched       {path} ({changed} fix{'es' if changed != 1 else ''})")
    print(f"\nDone. Applied {applied}, already applied {skipped}, not applied {failed}.")
    return failed


if __name__ == "__main__":
    sys.exit(1 if apply() else 0)