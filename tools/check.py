"""Local guardrails for the canvas-glow docs. Run: python tools/check.py

--update-numbers rewrites tools/numbers.snapshot, then runs the checks.
Only do that after re-verifying a changed number (AGENTS.md > Numbers).
"""
import difflib
import hashlib
import re
import subprocess
import sys
import xml.dom.minidom
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "tools" / "numbers.snapshot"
REFERENCE = "docs/reference/canvas-glow-v5.html"
REFERENCE_SHA256 = "7276d0611446bf7d1fd0509540d8a890bdac91705d7e6f141bd5b766f4d8363c"
LEVELS = ["FAIL", "WARN", "PASS"]

GUIDE_HEADINGS = [
    "1. Parts", "2. Power budget", "3. How it works", "4. Circuit", "5. Transistors",
    "6. Light layout", "7. Build order", "8. Checks", "9. Troubleshooting",
    "10. 3D prints (bonus)", "11. Ideas",
]
HEADINGS = {
    "docs/GUIDE.md": GUIDE_HEADINGS + ["12. Changes from the v5 guide"],
    "docs/GUIDE-IC.md": GUIDE_HEADINGS + ["12. Relation to the discrete version"],
    "docs/BREADBOARD.md": ["Setup", "Step 1: oscillator + LED", "Step 2: power stage"],
    "docs/BREADBOARD-IC.md": ["Setup", "Step 1: 555 + LED", "Step 2: power stage"],
}
FOOTERS = {
    "README.md": "[Next: Discrete build guide →](docs/GUIDE.md)",
    "docs/GUIDE.md": "[← Previous: README](../README.md) · [Contents](../README.md#documentation) · [Next: Discrete breadboard test →](BREADBOARD.md)",
    "docs/BREADBOARD.md": "[← Previous: Discrete build guide](GUIDE.md) · [Contents](../README.md#documentation) · [Next: IC build guide →](GUIDE-IC.md)",
    "docs/GUIDE-IC.md": "[← Previous: Discrete breadboard test](BREADBOARD.md) · [Contents](../README.md#documentation) · [Next: IC breadboard test →](BREADBOARD-IC.md)",
    "docs/BREADBOARD-IC.md": "[← Previous: IC build guide](GUIDE-IC.md) · [Contents](../README.md#documentation)",
}
GUIDES = ["docs/GUIDE.md", "docs/GUIDE-IC.md"]
NUMBER_FILES = ["README.md"] + [p for p in FOOTERS if p.startswith("docs/")]
SHARED_SAME = ["6. Light layout", "11. Ideas"]
SHARED_WARN = ["1. Parts", "5. Transistors", "8. Checks", "10. 3D prints (bonus)"]

HEADING = re.compile(r"^(#{1,6}) +(.+?)\s*$")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)[^)]*\)")
NUMBER = re.compile(
    r"(?<![\w.])[~≈]?\d+(?:[.,]\d+)?(?:[ \u00a0]?[–-][ \u00a0]?\d+(?:\.\d+)?)?[ \u00a0]?"
    r"(?:kΩ|MΩ|Ω|W/m|mW|W|kHz|Hz|nF|µF|μF|uF|pF|mV|µA|μA|mA|V|A|ms|µs|μs|%|°C|mm|cm|m|k|M|AWG)(?!\w)"
)


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def scan(text):
    """Yield (lineno, line, in_code); fence marker lines count as code."""
    fenced = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            yield n, line, True
        else:
            yield n, line, fenced


def headings(text):
    """Return (level, title) for every heading outside code fences."""
    out = []
    for _, line, code in scan(text):
        m = None if code else HEADING.match(line)
        if m:
            out.append((len(m.group(1)), m.group(2).strip()))
    return out


def sections(text):
    """Map each level-2 heading title to the lines under it."""
    out, title, body = {}, None, []
    for _, line, code in scan(text):
        m = None if code else HEADING.match(line)
        if m and len(m.group(1)) == 2:
            if title is not None:
                out[title] = body
            title, body = m.group(2).strip(), []
        elif title is not None:
            body.append(line)
    if title is not None:
        out[title] = body
    return out


def slug(title):
    return re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")


def anchors(text):
    seen, out = Counter(), set()
    for _, title in headings(text):
        s = slug(title)
        out.add(s if seen[s] == 0 else f"{s}-{seen[s]}")
        seen[s] += 1
    return out


def last_line(text):
    return next((l for l in reversed(text.splitlines()) if l.strip()), "")


def number_tokens():
    counts = Counter()
    for rel in NUMBER_FILES:
        for tok in NUMBER.findall(read(rel)):
            counts[(rel, re.sub(r"\s+", " ", tok))] += 1
    return counts


def load_snapshot():
    counts = Counter()
    for line in SNAPSHOT.read_text(encoding="utf-8").splitlines():
        rel, tok, n = line.split("\t")
        counts[(rel, tok)] = int(n)
    return counts


def write_snapshot(counts):
    lines = [f"{rel}\t{tok}\t{n}" for (rel, tok), n in sorted(counts.items())]
    SNAPSHOT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"snapshot written: {len(lines)} tokens -> {SNAPSHOT}")


def check_headings():
    issues = []
    for rel, want in HEADINGS.items():
        got = [t for lvl, t in headings(read(rel)) if lvl == 2]
        if got != want:
            issues.append(("FAIL", f"{rel}: '## ' headings differ from the frozen list. "
                           f"Fix: restore exactly these headings, in this order (section numbers "
                           f"are referenced elsewhere): {' | '.join(want)}. Found: {' | '.join(got) or 'none'}."))
    return issues


def check_footers():
    issues = []
    for rel, want in FOOTERS.items():
        last = last_line(read(rel))
        if last != want:
            issues.append(("FAIL", f"{rel}: last line is not the footer. Fix: make the last line exactly "
                           f"`{want}` (found `{last}`)."))
    for p in sorted((ROOT / "docs").glob("*.md")):
        if f"docs/{p.name}" not in FOOTERS:
            issues.append(("FAIL", f"docs/{p.name} is a new page. Fix: do not add pages without asking "
                           "the maintainer; delete the file or move its content into an existing page."))
    return issues


def link_problem(rel, target):
    path, _, anchor = target.partition("#")
    dest = ((ROOT / rel).parent / path).resolve() if path else (ROOT / rel)
    if not dest.exists():
        return "points to a missing file"
    if anchor and dest.suffix == ".md" and anchor not in anchors(dest.read_text(encoding="utf-8")):
        return f"anchor #{anchor} matches no heading in {dest.name}"
    return None


def check_links():
    issues = []
    files = ["README.md", "AGENTS.md", "sim/README.md"] + [
        f"docs/{p.name}" for p in sorted((ROOT / "docs").glob("*.md"))]
    for rel in files:
        for n, line, code in scan(read(rel)):
            if code:
                continue
            for target in LINK.findall(line):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                problem = link_problem(rel, target)
                if problem:
                    issues.append(("FAIL", f"{rel}:{n}: link ({target}) {problem}. Fix: point it at an "
                                   "existing file, or correct the #anchor to match a heading in that file."))
    return issues


def check_reference():
    if hashlib.sha256((ROOT / REFERENCE).read_bytes()).hexdigest() == REFERENCE_SHA256:
        return []
    return [("FAIL", "docs/reference is history and must not be edited; restore it with "
             "`git checkout main -- docs/reference`.")]


def check_svg():
    issues = []
    for p in sorted((ROOT / "docs" / "img").glob("*.svg")):
        try:
            xml.dom.minidom.parse(str(p))
        except Exception as e:
            issues.append(("FAIL", f"docs/img/{p.name} does not parse: {e}. Fix: correct the XML at "
                           "that line and column, then re-run."))
    return issues


def tracked_files():
    try:
        out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return [f for f in out.decode("utf-8").split("\0") if f]


def check_line_endings():
    files = tracked_files()
    if files is None:
        return [("WARN", "git is not available here; line endings were not checked.")]
    bad = []
    for rel in files:
        p = ROOT / rel
        if p.is_file():
            data = p.read_bytes()
            if b"\0" not in data and b"\r" in data:
                bad.append(rel)
    if bad:
        return [("FAIL", "these files contain CR bytes: " + ", ".join(bad) + ". Fix: save them with LF "
                 "line endings (the repo is eol=lf); in Python use open(..., newline=\"\\n\").")]
    return []


def check_numbers():
    if not SNAPSHOT.exists():
        return [("FAIL", "tools/numbers.snapshot is missing. Fix: run `python tools/check.py --update-numbers`.")]
    current, saved = number_tokens(), load_snapshot()
    diffs = []
    for key in sorted(set(current) | set(saved)):
        rel, tok = key
        a, b = saved.get(key), current.get(key)
        if a == b:
            continue
        if a is None:
            diffs.append(f"  added    {rel}: {tok} x{b}")
        elif b is None:
            diffs.append(f"  removed  {rel}: {tok} (was x{a})")
        else:
            diffs.append(f"  changed  {rel}: {tok} x{a} -> x{b}")
    if not diffs:
        return []
    return [("FAIL", "A number in the guides changed. AGENTS.md › Numbers: re-verify it against the circuit "
             "(arithmetic, simulation or bench), state the check in the commit message, then run "
             "`python tools/check.py --update-numbers`.\n" + "\n".join(diffs))]


def check_shared_sections():
    a, b = (sections(read(g)) for g in GUIDES)
    issues = []
    for title in SHARED_SAME + SHARED_WARN:
        if title not in a or title not in b or a[title] == b[title]:
            continue
        diff = list(difflib.unified_diff(a[title], b[title], GUIDES[0], GUIDES[1], lineterm="", n=1))
        if title in SHARED_SAME:
            body = "\n".join("  " + l for l in diff[:30])
            issues.append(("FAIL", f"section '{title}' must be identical in both guides. Fix: copy it from "
                           "one guide to the other, or list the difference in GUIDE-IC §12.\n" + body))
        else:
            changed = sum(1 for l in diff[2:] if l[:1] in "+-")
            issues.append(("WARN", f"section '{title}' differs ({changed} lines); shared section differs; if you "
                           "edited one guide, mirror the edit in the other unless GUIDE-IC §12 lists it as intentional"))
    return issues


def check_branch():
    try:
        r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT,
                           capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return [("WARN", "could not read the git branch.")]
    if r.stdout.strip() in ("main", "master"):
        return [("WARN", "you are on main: create a branch before committing (git switch -c <name>).")]
    return []


CHECKS = [
    ("headings", check_headings),
    ("footers", check_footers),
    ("links", check_links),
    ("reference-frozen", check_reference),
    ("svg", check_svg),
    ("line-endings", check_line_endings),
    ("numbers", check_numbers),
    ("shared-sections", check_shared_sections),
    ("branch", check_branch),
]


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if "--update-numbers" in argv:
        write_snapshot(number_tokens())
    tally = Counter()
    problems = Counter()
    for name, fn in CHECKS:
        try:
            issues = fn()
        except OSError as e:
            issues = [("FAIL", f"could not read {e.filename}: {e.strerror}. Fix: restore the file from git.")]
        issues.sort(key=lambda i: LEVELS.index(i[0]))
        status = issues[0][0] if issues else "PASS"
        tally[status] += 1
        problems.update(lvl for lvl, _ in issues)
        if len(issues) == 1:
            print(f"{status} {name}: {issues[0][1]}".replace("\n", "\n    "))
        elif not issues:
            print(f"{status} {name}")
        else:
            print(f"{status} {name}: {len(issues)} problems")
            for lvl, msg in issues:
                print(f"    {lvl}: {msg}".replace("\n", "\n    "))
    print(f"\nSummary: {tally['PASS']} PASS, {tally['WARN']} WARN, {tally['FAIL']} FAIL "
          f"(problems: {problems['FAIL']} FAIL, {problems['WARN']} WARN)")
    return 1 if tally["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
