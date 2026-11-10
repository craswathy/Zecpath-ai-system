import ast
import os

FOLDERS = ["parsers", "ats_engine", "utils"]
OUTPUT = "MODULE_INDEX.md"


def first_line(doc):
    return doc.strip().splitlines()[0] if doc and doc.strip() else "(no docstring)"


def describe(path):
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]
    classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
    return funcs, classes


def run():
    lines = ["# Module Index -- Zecpath AI System", "",
             "Generated automatically by ats_engine/generate_module_index.py.",
             "Re-run it after adding modules.", ""]
    total = 0
    for folder in FOLDERS:
        lines += [f"## {folder}/", "", "| File | Classes | Public functions |", "|---|---|---|"]
        for name in sorted(os.listdir(folder)):
            if not name.endswith(".py") or name.startswith("__"):
                continue
            funcs, classes = describe(os.path.join(folder, name))
            lines.append(f"| {name} | {', '.join(classes) or '-'} | {', '.join(funcs) or '-'} |")
            total += 1
        lines.append("")
    lines.append(f"Total modules indexed: {total}")
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Done. {total} modules indexed in {OUTPUT}")


if __name__ == "__main__":
    run()