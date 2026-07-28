import os

base = r"C:/Dev/XLab_MTC/Niên Đại Thương Gia"
tanaka_files = []
tuan_files = []

for fname in sorted(os.listdir(base)):
    if not fname.endswith('.txt'):
        continue
    fpath = os.path.join(base, fname)
    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    if "Tanaka" in content:
        lines = content.split("\n")
        tanaka_lines = [l for l in lines if "Tanaka" in l]
        if tanaka_lines:
            tanaka_files.append((fname, len(tanaka_lines)))
    
    if "Tuấn" in content:
        lines = content.split("\n")
        tuan_l = [l for l in lines if "Tuấn" in l]
        if tuan_l:
            tuan_files.append((fname, len(tuan_l)))

print("=== Tanaka ===")
for f, c in sorted(tanaka_files):
    print(f"  {f}: {c}")
print("\n=== Tuấn ===")
for f, c in sorted(tuan_files):
    print(f"  {f}: {c}")
