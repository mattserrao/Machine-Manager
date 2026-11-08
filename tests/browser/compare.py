"""Compare two screenshot folders from visual.py; prints changed pixels per image."""
import sys, os
from PIL import Image, ImageChops
a, b = sys.argv[1], sys.argv[2]
bad = 0
for f in sorted(os.listdir(a)):
    if not f.endswith('.png'): continue
    if not os.path.exists(os.path.join(b, f)): print(f"MISSING {f}"); bad += 1; continue
    x, y = Image.open(os.path.join(a, f)).convert('RGB'), Image.open(os.path.join(b, f)).convert('RGB')
    if x.size != y.size: print(f"SIZE {f}"); bad += 1; continue
    # Anti-aliasing at fractional zoom flickers a little between runs; count only clear changes.
    d = ImageChops.difference(x, y).convert('L').point(lambda v: 255 if v > 80 else 0)
    n = d.histogram()[255]
    ok = n <= 150
    print(f"{'same' if ok else 'DIFF'} {f}" + (f" {n} px, box {d.getbbox()}" if n else ""))
    if not ok:
        bad += 1; d.save(os.path.join(b, 'diff-' + f))
sys.exit(1 if bad else 0)
