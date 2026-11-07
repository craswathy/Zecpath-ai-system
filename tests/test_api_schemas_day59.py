import json
import sys
sys.path.append(".")

with open("api_schemas_day59.json", "r", encoding="utf-8") as f:
    SCHEMAS = json.load(f)["definitions"]

REQUIRED_SCHEMAS = [
    "ResumeParseRequest", "AsyncJobResponse", "ATSScoreRequest", "ATSScoreResponse",
    "ScreeningCallRequest", "ScreeningReportResponse", "InterviewTurnScoreRequest",
    "InterviewTurnScoreResponse", "DecisionRequest", "DecisionResponse",
    "WebhookEvent", "ErrorResponse",
]


def test_all_five_apis_have_schemas():
    for name in REQUIRED_SCHEMAS:
        assert name in SCHEMAS


def test_every_schema_declares_required_fields_that_exist():
    for name, schema in SCHEMAS.items():
        for field in schema.get("required", []):
            assert field in schema["properties"], f"{name}: {field} missing"


def test_responses_carry_model_version():
    for name in ["ATSScoreResponse", "DecisionResponse"]:
        assert "model_version" in SCHEMAS[name]["properties"]


def test_error_schema_has_retryable_flag():
    assert "retryable" in SCHEMAS["ErrorResponse"]["properties"]["error"]["properties"]