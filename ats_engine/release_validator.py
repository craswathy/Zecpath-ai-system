import ast
import importlib
import json
import os

FOLDERS = ["parsers", "ats_engine", "utils"]
SKIP_IMPORT = {"summarize_matches"}  # script-style module: compiled but not executed
SCORE_KEYS = {"final_score", "ats_score", "hiring_fit_percentage"}


def module_files():
    for folder in FOLDERS:
        for name in sorted(os.listdir(folder)):
            if name.endswith(".py") and not name.startswith("__"):
                yield folder, name


def check_empty_and_syntax():
    problems = []
    for folder, name in module_files():
        path = os.path.join(folder, name)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        if not text.strip():
            problems.append((path, "empty file"))
            continue
        try:
            ast.parse(text)
        except SyntaxError as exc:
            problems.append((path, f"syntax error at line {exc.lineno}"))
    return problems


def check_imports():
    problems = []
    for folder, name in module_files():
        module = name[:-3]
        if module in SKIP_IMPORT:
            continue
        try:
            importlib.import_module(f"{folder}.{module}")
        except Exception as exc:
            problems.append((f"{folder}/{name}", f"{type(exc).__name__}: {str(exc)[:80]}"))
    return problems


def check_run_functions():
    """Every run_*.py module should define run(). A miss often means wrong code was pasted."""
    problems = []
    for folder, name in module_files():
        if not name.startswith("run_"):
            continue
        path = os.path.join(folder, name)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        if not text.strip():
            continue
        tree = ast.parse(text)
        funcs = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
        if "run" not in funcs:
            problems.append((path, "no run() function"))
    return problems


def _scan_scores(node, path, found):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in SCORE_KEYS and isinstance(value, (int, float)) and not 0 <= value <= 100:
                found.append((path, f"{key}={value}"))
            _scan_scores(value, path, found)
    elif isinstance(node, list):
        for item in node:
            _scan_scores(item, path, found)


def check_json_outputs():
    problems = []
    for root, _, files in os.walk("data"):
        for name in files:
            if not name.endswith(".json"):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as exc:
                problems.append((path, f"unreadable JSON: {type(exc).__name__}"))
                continue
            _scan_scores(data, path, problems)
    return problems


def duplicate_candidates():
    names = [n for _, n in module_files()]
    return sorted(n for n in names if "_v2" in n or n in
                  ("unified_candidate_object.py", "unified_candidate_score_object.py"))


def run():
    report = {
        "empty_or_syntax": check_empty_and_syntax(),
        "import_failures": check_imports(),
        "run_function_missing": check_run_functions(),
        "json_problems": check_json_outputs(),
    }
    total = 0
    for name, items in report.items():
        print(f"\n{name}: {len(items)}")
        for item in items:
            print("   -", item)
        total += len(items)
    print("\nPossible duplicate modules (review by hand):", duplicate_candidates())
    print(f"\nTOTAL PROBLEMS: {total}")
    with open("data/release_validation_day68.json", "w", encoding="utf-8") as f:
        json.dump({k: [list(i) for i in v] for k, v in report.items()}, f, indent=2)
    return report


if __name__ == "__main__":
    run()