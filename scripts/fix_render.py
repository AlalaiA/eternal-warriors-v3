from pathlib import Path

path = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = path.read_text(encoding="utf-8")

# Renombrar función interna 'render' a 'renderFrame'
OLD1 = "    render(canvas, W, H, c);"
NEW1 = "    renderFrame(canvas, W, H, c);"

OLD2 = "function render(canvas, W, H, c) {"
NEW2 = "function renderFrame(canvas, W, H, c) {"

for old, new in [(OLD1,NEW1),(OLD2,NEW2)]:
    c = src.count(old)
    if c != 1:
        print(f"ERROR '{old[:30]}': {c} veces"); exit(1)
    src = src.replace(old, new)
    print(f"OK — renombrado")

path.write_text(src, encoding="utf-8")
print("✅ Recarga en incógnito.")
