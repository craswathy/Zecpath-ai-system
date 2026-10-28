import html
import json
import os
from utils.logger import logger

LEVEL_LABELS = {"high": "HIGH", "medium": "MEDIUM", "info": "INFO"}


def render_text(report):
    """Plain-text version of the report. Opens anywhere and prints cleanly."""
    c, h = report["candidate"], report["headline"]
    lines = ["=" * 70, "HIRING INTELLIGENCE REPORT", "=" * 70,
             f"Candidate: {c['candidate_id']} | Job: {c['job_id']} | Role profile: {c['role_category']}",
             f"Generated: {report['metadata']['timestamp'][:19]} | Model: {report['metadata']['model_version']}",
             "", "AT A GLANCE",
             f"  Recommendation: {h['decision'].upper()}",
             f"  {h['recommendation']}",
             f"  Hiring fit: {h['hiring_fit_percentage']}% ({h['fit_category']}, {h['result_status']})",
             f"  Confidence: {h['confidence_score']} ({h['confidence_band']})",
             "", "ROUND SCORES", f"  {'Round':<22}{'Score':>7}{'Weight':>8}{'Points':>8}"]
    for r in report["round_scores"]:
        score = "-" if r["score"] is None else r["score"]
        weight = "-" if r["weight"] is None else r["weight"]
        points = "-" if r["points"] is None else r["points"]
        note = "  (half weight, low reliability)" if r["low_reliability"] else ""
        lines.append(f"  {r['label']:<22}{score:>7}{weight:>8}{points:>8}{note}")

    lines += ["", "STRENGTHS"] + [f"  + {s}" for s in report["strengths"]]
    lines += ["", "WEAKNESSES"] + [f"  - {s}" for s in report["weaknesses"]]
    lines += ["", "RISK INDICATORS"] + [f"  [{LEVEL_LABELS[r['level']]}] {r['text']}" for r in report["risk_indicators"]]

    lines += ["", "DETAILS BY STAGE"]
    for sec in report["sections"].values():
        score = "" if sec["score"] is None else f" (score {sec['score']})"
        lines.append(f"  {sec['title']}{score}")
        lines += [f"    {line}" for line in sec["lines"]]

    f = report["final_recommendation"]
    lines += ["", "FINAL RECOMMENDATION", f"  {f['decision'].upper()}: {f['recommendation']}",
              f"  Score alone suggests: {f['score_based_decision']}"]
    for r in f["rules_triggered"]:
        lines.append(f"  Rule {r['id']}: {r['reason']}" + (" [moved to Hold / Review]" if r["moved_to_hold"] else ""))
    lines += [f"  Next: {step}" for step in f["next_steps"]]
    lines += ["", "HUMAN REVIEW (required)",
              "  Final decision: ____________________  Reviewer: ____________________  Date: __________",
              "  Comment: ________________________________________________________________",
              "", "LIMITS"] + [f"  - {t}" for t in report["limitations"]]
    return "\n".join(lines)


CSS = """
body{font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;margin:0;background:#f4f5f7}
.page{max-width:860px;margin:0 auto;padding:24px;background:#fff}
h1{font-size:22px;margin:0 0 4px} h2{font-size:16px;margin:22px 0 8px;border-bottom:2px solid #d0d4da;padding-bottom:4px}
.meta{color:#555;font-size:13px}
.glance{display:flex;gap:12px;flex-wrap:wrap;margin-top:14px}
.card{flex:1;min-width:190px;border:1px solid #c9ced6;border-radius:6px;padding:10px 12px}
.card .label{font-size:12px;color:#555} .card .value{font-size:20px;font-weight:bold;margin-top:2px}
.badge{display:inline-block;padding:3px 10px;border-radius:4px;font-weight:bold;border:2px solid}
.selected{background:#e3f4e6;border-color:#2e7d32;color:#1b5e20}
.hold{background:#fff4d6;border-color:#b26a00;color:#7a4700}
.rejected{background:#fde4e4;border-color:#b71c1c;color:#7f1212}
table{border-collapse:collapse;width:100%;font-size:14px} th,td{border:1px solid #d0d4da;padding:6px 8px;text-align:left}
th{background:#eef0f3} .bar{background:#e4e7ec;height:10px;border-radius:5px;min-width:100px} .bar div{background:#4a6fa5;height:10px;border-radius:5px}
.cols{display:flex;gap:16px;flex-wrap:wrap} .col{flex:1;min-width:230px} ul{margin:4px 0 0 18px;padding:0}
.tag{font-weight:bold;font-size:12px;padding:1px 6px;border-radius:3px;border:1px solid #888}
.stage{margin-bottom:10px} .stage p{margin:2px 0;font-size:14px}
.sign td{height:34px} .small{font-size:12px;color:#444}
@media print{body{background:#fff}.page{max-width:none;padding:0}h2{break-after:avoid}.stage,.card{break-inside:avoid}}
"""


def _e(value):
    return html.escape(str(value))


def render_html(report):
    """Self-contained, printable HTML. In a browser: Print, then Save as PDF."""
    c, h, f = report["candidate"], report["headline"], report["final_recommendation"]
    css_class = {"Selected": "selected", "Hold / Review": "hold", "Rejected": "rejected"}.get(h["decision"], "hold")

    out = ["<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>",
           f"<title>Hiring Intelligence Report - {_e(c['candidate_id'])}</title><style>{CSS}</style></head><body><div class='page'>",
           "<h1>Hiring Intelligence Report</h1>",
           f"<div class='meta'>Candidate: {_e(c['candidate_id'])} | Job: {_e(c['job_id'])} | Role profile: {_e(c['role_category'])}<br>"
           f"Generated: {_e(report['metadata']['timestamp'][:19])} | Model: {_e(report['metadata']['model_version'])}</div>",
           "<div class='glance'>",
           f"<div class='card'><div class='label'>Recommendation</div><div class='value'><span class='badge {css_class}'>{_e(h['decision'])}</span></div></div>",
           f"<div class='card'><div class='label'>Hiring fit</div><div class='value'>{_e(h['hiring_fit_percentage'])}%</div><div class='small'>{_e(h['fit_category'])} ({_e(h['result_status'])})</div></div>",
           f"<div class='card'><div class='label'>Decision confidence</div><div class='value'>{_e(h['confidence_score'])}</div><div class='small'>{_e(h['confidence_band'])}</div></div>",
           "</div>", f"<p>{_e(h['recommendation'])}</p>",
           "<h2>Round scores</h2><table><tr><th>Round</th><th>Score</th><th></th><th>Weight</th><th>Points</th></tr>"]
    for r in report["round_scores"]:
        if r["score"] is None:
            out.append(f"<tr><td>{_e(r['label'])}</td><td>-</td><td></td><td>-</td><td>-</td></tr>")
        else:
            note = " (half weight, low reliability)" if r["low_reliability"] else ""
            out.append(f"<tr><td>{_e(r['label'])}{_e(note)}</td><td>{_e(r['score'])}</td>"
                       f"<td><div class='bar'><div style='width:{_e(r['score'])}%'></div></div></td>"
                       f"<td>{_e(r['weight'])}</td><td>{_e(r['points'])}</td></tr>")
    out.append("</table>")

    out.append("<h2>Strengths, weaknesses and risks</h2><div class='cols'>")
    out.append("<div class='col'><b>Strengths</b><ul>" + "".join(f"<li>{_e(s)}</li>" for s in report["strengths"]) + "</ul></div>")
    out.append("<div class='col'><b>Weaknesses</b><ul>" + "".join(f"<li>{_e(s)}</li>" for s in report["weaknesses"]) + "</ul></div>")
    out.append("<div class='col'><b>Risk indicators</b><ul>"
               + "".join(f"<li><span class='tag'>{LEVEL_LABELS[r['level']]}</span> {_e(r['text'])}</li>" for r in report["risk_indicators"])
               + "</ul></div></div>")

    out.append("<h2>Details by stage</h2>")
    for sec in report["sections"].values():
        score = "" if sec["score"] is None else f" - score {_e(sec['score'])}"
        out.append(f"<div class='stage'><b>{_e(sec['title'])}{score}</b>" + "".join(f"<p>{_e(line)}</p>" for line in sec["lines"]) + "</div>")

    out.append("<h2>Final recommendation</h2>")
    out.append(f"<p><span class='badge {css_class}'>{_e(f['decision'])}</span> {_e(f['recommendation'])}</p>")
    out.append(f"<p class='small'>Score alone suggests: {_e(f['score_based_decision'])}</p>")
    if f["rules_triggered"]:
        out.append("<ul>" + "".join(f"<li>Rule {_e(r['id'])}: {_e(r['reason'])}" + (" (moved to Hold / Review)" if r["moved_to_hold"] else "") + "</li>"
                                    for r in f["rules_triggered"]) + "</ul>")
    out.append("<p><b>Next steps</b></p><ul>" + "".join(f"<li>{_e(s)}</li>" for s in f["next_steps"]) + "</ul>")

    out.append("<h2>Human review (required)</h2><table class='sign'><tr><td>Final decision</td><td></td><td>Reviewer</td><td></td><td>Date</td><td></td></tr>"
               "<tr><td>Comment</td><td colspan='5'></td></tr></table>")
    out.append("<h2>Limits</h2><ul class='small'>" + "".join(f"<li>{_e(t)}</li>" for t in report["limitations"]) + "</ul>")
    out.append("</div></body></html>")
    return "\n".join(out)


def export_report(report, folder):
    """Write the report as .html, .txt and .json. Returns the three file paths."""
    os.makedirs(folder, exist_ok=True)
    base = os.path.join(folder, report["candidate"]["candidate_id"] + "_report")
    paths = {"html": base + ".html", "txt": base + ".txt", "json": base + ".json"}
    with open(paths["html"], "w", encoding="utf-8") as fh:
        fh.write(render_html(report))
    with open(paths["txt"], "w", encoding="utf-8") as fh:
        fh.write(render_text(report))
    with open(paths["json"], "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    logger.info(f"Exported report for {report['candidate']['candidate_id']}")
    return paths