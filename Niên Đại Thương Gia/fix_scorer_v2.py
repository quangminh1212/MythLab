#!/usr/bin/env python3
"""
Fix deterministic_scorer_v2.py:
1. Remove false-positive PAD_MARKERS (hư không, bản chất, vô hạn, sâu thẳm)
2. Add technology year awareness for ANACHRONISM check
3. Fix panel regex for \r\n handling
"""
import re

# Read the file
with open('deterministic_scorer_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# === FIX 1: Remove false-positive PAD_MARKERS ===
old_markers = '''PAD_MARKERS = [
    "### lớp sâu",
    "lớp sâu",
    "sâu thẳm",
    "vô cực",
    "hư không",
    "bản chất sâu",
    "nền tảng sâu",
    "bản chất",
    "vô hạn",
    "### hidden layer",
    "### deep layer",
    "deep layer",
]'''

new_markers = '''PAD_MARKERS = [
    # AI/tech-specific markers (valid for AI reincarnation novel)
    "### lớp sâu",
    "lớp sâu",
    "bản chất sâu",
    "nền tảng sâu",
    "### hidden layer",
    "### deep layer",
    "deep layer",
    # Removed false positives: "hư không", "bản chất", "vô hạn", "sâu thẳm"
    # These are normal Vietnamese words appearing in prose naturally
]'''

content = content.replace(old_markers, new_markers)

# === FIX 2: Add technology year mapping for anachronism ===
# Find the ANACHRONISM list and add year mapping after it
old_anach = '''ANACHRONISM = [
    "smartphone",
    "iphone",
    "internet",
    "facebook",
    "google",
    "wifi",
    "laptop",
    "app ",
    "online",
    "startup",
    "email",
]'''

new_anach = '''ANACHRONISM = [
    "smartphone",
    "iphone",
    "internet",
    "facebook",
    "google",
    "wifi",
    "laptop",
    "app ",
    "online",
    "startup",
    "email",
]

# Technology introduction years — if panel_year >= tech_year, NOT anachronism
TECH_YEARS = {
    "email": 1971,
    "internet": 1983,
    "laptop": 1981,
    "online": 1980,
    "startup": 1960,
    "google": 1998,
    "facebook": 2004,
    "wifi": 1997,
    "smartphone": 2007,
    "iphone": 2007,
    "app ": 2008,
}'''

content = content.replace(old_anach, new_anach)

# === FIX 3: Fix panel regex for \r\n ===
old_regex = r'm = re.search(r"「Hệ thống[^」]*GHI NHẬN[^」]*」\s*\n", t)'
new_regex = r'm = re.search(r"「Hệ thống[^」]*GHI NHẬN[^」]*」\s*\r?\n", t)'
content = content.replace(old_regex, new_regex)

# === FIX 4: Make anachronism check year-aware ===
# Find the anachronism check code and add year awareness
old_anach_check = '''    # Anachronism check
    anach_terms = [a.lower() for a in ANACHRONISM if a.lower() not in extra_anach_ok]
    anach_hits = {a: body_low.count(a) for a in anach_terms if a in body_low}
    has_anach = len(anach_hits) > 0'''

new_anach_check = '''    # Anachronism check (year-aware: skip if panel_year >= tech_year)
    anach_terms = [a.lower() for a in ANACHRONISM if a.lower() not in extra_anach_ok]
    anach_hits = {}
    for a in anach_terms:
        if a in body_low:
            # Check if technology existed by panel_year
            tech_year = TECH_YEARS.get(a.strip() + " ", TECH_YEARS.get(a, 0))
            if panel_year and tech_year and panel_year >= tech_year:
                continue  # Technology existed, not anachronism
            anach_hits[a] = body_low.count(a)
    has_anach = len(anach_hits) > 0'''

content = content.replace(old_anach_check, new_anach_check)

# Write back
with open('deterministic_scorer_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Scorer v2 patched successfully!")
print("Changes:")
print("  1. Removed 4 false-positive PAD_MARKERS")
print("  2. Added TECH_YEARS mapping for year-aware anachronism")
print("  3. Fixed panel regex for \r\n handling")
print("  4. Made anachronism check year-aware")
