import sys
sys.path.append(".")

from ats_engine import release_validator as rv
from ats_engine.edge_case_probe import find_crashes


def test_no_empty_or_broken_modules():
    assert rv.check_empty_and_syntax() == []


def test_every_module_imports():
    assert rv.check_imports() == []


def test_run_modules_define_run():
    assert rv.check_run_functions() == []


def test_json_outputs_valid_and_in_range():
    assert rv.check_json_outputs() == []


def test_awkward_inputs_never_crash():
    assert find_crashes() == []