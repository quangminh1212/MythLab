# -*- coding: utf-8 -*-
import os, glob, re, sys

sys.stdout.reconfigure(encoding='utf-8')
target_dir = r"c:\Dev\XLab_MTC\Niên Đại Thương Gia"
py_files = glob.glob(os.path.join(target_dir, "*.py"))

print(f"Analyzing {len(py_files)} Python files in target directory...")

suspicious_terms = [
    "mock", "fake", "hardcode", "return 9.", "return 10", "override",
    "score95_final.json", "score =", "score: 9"
]

findings = []

for pf in py_files:
    fname = os.path.basename(pf)
    with open(pf, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            # Check for suspicious patterns
            if "score" in line.lower() and ("=" in line or ":" in line):
                # Analyze if it's dynamic or static hardcode
                if re.search(r'score\s*[:=]\s*(?:9\.[5-9]|10(?:\.0)?)', line) and not "round(" in line and not "sum(" in line:
                    findings.append(f"{fname}:{idx}: Hardcoded high score detected -> {line.strip()}")
            for term in ["mock", "fake_score"]:
                if term in line.lower():
                    findings.append(f"{fname}:{idx}: Suspicious term '{term}' -> {line.strip()}")

print(f"\nStatic Analysis complete. Findings count: {len(findings)}")
for f in findings:
    print("  -", f)
