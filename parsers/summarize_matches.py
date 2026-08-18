import json

with open("data/semantic_matches/all_matches.json", "r", encoding="utf-8") as f:
    all_matches = json.load(f)

resumes = {}
for entry in all_matches:
    r = entry["resume"]
    if r not in resumes or entry["overall_similarity"] > resumes[r]["overall_similarity"]:
        resumes[r] = entry

print(f"{'Resume':<25} {'Best Match JD':<30} {'Score':<8}")
print("-" * 65)
for resume, entry in resumes.items():
    print(f"{resume:<25} {entry['job']:<30} {entry['overall_similarity']:<8}")