#!/usr/bin/env python3
"""Phase 6 (Report) validator.

Run from the project root, after py tools\\build_report.py:
    py tools\\validate_phase6.py
Re-runs the Phase 5 validator (which re-runs Phases 0 to 4), then checks the report
sources, the figures, the built HTML/PDF/DOCX and the number cross-check.
Standard library only.
"""
import re
import subprocess
import sys
import zipfile

from vcommon import Report, root_from_argv, run_previous

REP = "06-report"
NAME = "ShopNova-threat-management-report"
CHAPTERS = ["00-executive-summary.md", "01-introduction-and-scope.md", "02-governance.md", "03-risk-management.md",
            "04-vulnerability-management.md", "05-incident-response.md", "06-integration.md",
            "07-limitations.md", "08-conclusion.md", "90-appendix-evidence.md", "99-references.md"]
FIGURES = ["fig1-data-flow", "fig2-heatmap-before-after", "fig3-scans-before-after", "fig4-incident-timeline"]
LIMITS = ["synthetic", "lab", "simulated", "DPO", "Greenbone", "independent controller", "NIS2", "UTC+1"]


def main():
    root = root_from_argv()
    rep = Report("Phase 6 validation")
    run_previous(root, "validate_phase5.py", rep, "Phases 0 to 5")

    texts = {}
    for ch in CHAPTERS:
        p = root / REP / ch
        if not p.is_file():
            rep.fail(f"missing chapter: {REP}/{ch}")
            continue
        texts[ch] = p.read_text(encoding="utf-8")
    if len(texts) == len(CHAPTERS):
        rep.ok(f"all {len(CHAPTERS)} report parts present (chapters 1 to 8, Appendix A, references)")
    allt = "\n".join(texts.values())
    ph = re.findall(r"GREENBONE_STATUS|\[Your name|TODO|TBD", allt)
    (rep.fail if ph else rep.ok)(f"placeholders left in the report: {sorted(set(ph))}" if ph else "no placeholders left")
    lim = texts.get("07-limitations.md", "")
    lack = [w for w in LIMITS if w not in lim]
    (rep.fail if lack else rep.ok)(f"limitations section misses {lack}" if lack else
                                   "limitations cover synthetic data, lab, simulated sign-offs and DPO, Greenbone, "
                                   "the two legal points and UTC")
    figs_md = re.findall(r"!\[Figure (\d+):", allt)
    (rep.ok if sorted(set(figs_md)) == ["1", "2", "3", "4"] else rep.fail)(
        f"figures referenced in the text: {sorted(set(figs_md))} (need 1 to 4)")
    for f in FIGURES:
        if not (root / REP / "figures" / f"{f}.png").is_file():
            rep.fail(f"figure missing: {REP}/figures/{f}.png")
    for m in re.findall(r"`(evidence/[^`]+)`", texts.get("90-appendix-evidence.md", "")):
        if not (root / m).is_file():
            rep.fail(f"Appendix A lists a missing evidence file: {m}")
    n_ev = len(re.findall(r"^\| \d+ \| `evidence/", texts.get("90-appendix-evidence.md", ""), re.M))
    (rep.ok if n_ev else rep.fail)(f"Appendix A lists {n_ev} evidence files, all present")

    # --- built outputs ---------------------------------------------------------
    html = root / REP / f"{NAME}.html"
    pdf = root / REP / "build" / f"{NAME}.pdf"
    docx = root / REP / "build" / f"{NAME}.docx"
    import hashlib, json
    info_p = root / REP / "build" / "build-info.json"
    info = json.loads(info_p.read_text(encoding="utf-8")).get("sources", {}) if info_p.is_file() else {}
    stale = [ch for ch in CHAPTERS if (root / REP / ch).is_file()
             and info.get(ch) != hashlib.sha256((root / REP / ch).read_bytes().replace(b"\r\n", b"\n")).hexdigest()]
    for p in (html, pdf, docx):
        if not p.is_file():
            rep.fail(f"build output missing: {p.relative_to(root)} (run py tools\\build_report.py)")
    (rep.fail if stale or not info else rep.ok)(
        f"build outputs are older than these chapters: {stale}; rebuild" if stale else
        ("build-info.json missing; rebuild" if not info else "build outputs match the current chapter sources (hash check)"))
    if html.is_file():
        h = html.read_text(encoding="utf-8")
        heads = re.findall(r'<h1 id="[^"]+">(\d) ', h)
        ok = heads == [str(i) for i in range(1, 9)] and 'id="contents"' in h and "Appendix A" in h and ">References<" in h
        (rep.ok if ok else rep.fail)(f"HTML: contents, chapters {', '.join(heads)}, Appendix A and references")
    if pdf.is_file():
        pages = len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))
        (rep.ok if pages >= 20 else rep.fail)(f"PDF: {pages} pages")
    if docx.is_file():
        z = zipfile.ZipFile(docx)
        media = [n for n in z.namelist() if n.startswith("word/media/")]
        doc = z.read("word/document.xml").decode("utf-8")
        links = len(re.findall(r"r:link=", doc))
        (rep.ok if len(media) >= 4 and links == 0 else rep.fail)(
            f"DOCX: {len(media)} embedded images, {links} external image links")

    # --- numbers ---------------------------------------------------------------
    r = subprocess.run([sys.executable, str(root / "tools" / "check_report_numbers.py")],
                       capture_output=True, text=True, encoding="utf-8", cwd=root)
    summ = next((ln for ln in r.stdout.splitlines() if "checks match" in ln), "no summary")
    (rep.ok if r.returncode == 0 else rep.fail)(f"number cross-check: {summ}")
    for ln in r.stdout.splitlines():
        if ln.strip().startswith("MISMATCH:"):
            rep.fail(f"number mismatch: {ln.strip()[10:]}")
    return rep.finish(root, "Phase 6 is complete. The report is ready.")


if __name__ == "__main__":
    sys.exit(main())
