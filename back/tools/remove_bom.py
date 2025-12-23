import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python remove_bom.py <fixture.json>")
    sys.exit(1)

p = Path(sys.argv[1])
if not p.exists():
    print(f"File not found: {p}")
    sys.exit(1)

# read with utf-8-sig to strip BOM if present
text = p.read_text(encoding='utf-8-sig')
# write back as plain utf-8
p.write_text(text, encoding='utf-8')
print(f"Rewrote {p} without BOM")
