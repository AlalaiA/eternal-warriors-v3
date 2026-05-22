"""
prep_sprites.py
Eternal Warriors v3.0 — Elimina fondo negro de PNGs y los renombra correctamente

Requiere Pillow:
  pip install Pillow

Corre desde la carpeta donde están los PNGs:
  cd E:\\0000ew V2Claude
  python prep_sprites.py

Qué hace:
  1. Lee cada PNG de la carpeta 'sprites_raw\\'
  2. Convierte fondo negro puro (y grises muy oscuros) a transparente
  3. Guarda en 'frontend\\assets\\buildings\\'  con el nombre correcto

Nombres de archivo fuente esperados (los que subiste):
  centro_de_ciudad.png  → centro_ciudad.png
  templo.png            → templo.png
  santuario_arcano.png  → santuario.png
  universidad.png       → universidad.png
  almacen.png           → almacen.png
  torre_de_vigilancia.png → torre_vigilancia.png  (usada en muralla)
  centro_de_viajes.png  → centro_viajes.png
  casa.png              → casa.png
  cuartel.png          → cuartel.png
  herreria.png          → herreria.png
  escondite.png         → escondite.png
"""

from pathlib import Path
from PIL import Image
import numpy as np
import shutil

RAW  = Path(__file__).parent / "sprites_raw"
DEST = Path(r"E:\0000ew V2Claude\frontend\assets\buildings")

RENAME = {
    "centro_de_ciudad.png":     "centro_ciudad.png",
    "templo.png":               "templo.png",
    "santuario_arcano.png":     "santuario.png",
    "universidad.png":          "universidad.png",
    "almacen.png":              "almacen.png",
    "torre_de_vigilancia.png":  "torre_vigilancia.png",
    "centro_de_viajes.png":     "centro_viajes.png",
    "casa.png":                 "casa.png",
    "cuartel.png":              "cuartel.png",
    "herreria.png":             "herreria.png",
    "escondite.png":            "escondite.png",
}

# Umbral: píxeles con R+G+B < este valor se consideran "negro" y se hacen transparentes
BLACK_THRESHOLD = 30

def remove_black_bg(img: Image.Image) -> Image.Image:
    """Convierte píxeles muy oscuros a transparentes."""
    img = img.convert("RGBA")
    data = np.array(img, dtype=np.uint16)
    r, g, b, a = data[...,0], data[...,1], data[...,2], data[...,3]
    # Píxeles casi negros
    mask = (r.astype(int) + g.astype(int) + b.astype(int)) < BLACK_THRESHOLD
    data[..., 3] = np.where(mask, 0, a)
    return Image.fromarray(data.astype(np.uint8), "RGBA")

def already_transparent(img: Image.Image) -> bool:
    """Devuelve True si la imagen ya tiene canal alfa con transparencia real."""
    if img.mode != "RGBA":
        return False
    arr = np.array(img)
    # Si más del 5% de píxeles tienen alfa < 200 → ya tiene transparencia
    transparent_ratio = (arr[..., 3] < 200).sum() / arr[..., 3].size
    return transparent_ratio > 0.05

if not RAW.exists():
    RAW.mkdir()
    print(f"Carpeta creada: {RAW}")
    print("Pon los PNGs dentro de 'sprites_raw\\' y vuelve a correr el script.")
    exit(0)

DEST.mkdir(parents=True, exist_ok=True)
processed = []
skipped = []

for src_name, dst_name in RENAME.items():
    src_path = RAW / src_name
    if not src_path.exists():
        print(f"  SKIP (no encontrado): {src_name}")
        skipped.append(src_name)
        continue

    img = Image.open(src_path)

    if already_transparent(img):
        # Ya tiene fondo transparente — copiar directo
        img = img.convert("RGBA")
        img.save(DEST / dst_name, "PNG")
        print(f"  OK (ya transparente): {src_name} → {dst_name}")
    else:
        # Eliminar fondo negro
        img_clean = remove_black_bg(img)
        img_clean.save(DEST / dst_name, "PNG")
        print(f"  OK (fondo eliminado): {src_name} → {dst_name}")

    processed.append(dst_name)

print()
print(f"Procesados: {len(processed)} | Skipped: {len(skipped)}")
if skipped:
    print(f"Faltantes:  {', '.join(skipped)}")
print(f"Destino:    {DEST}")
print()
print("Siguiente paso:")
print("  python install_png.py")
