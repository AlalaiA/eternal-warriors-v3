"""
fix_bg_sprites.py
Eternal Warriors v3.0 — Elimina fondo gris (RGB ~78) de los sprites

El fondo de Gemini es gris RGB(78,78,78), no negro puro.
Umbral ajustado: píxeles con R≈G≈B y valor < 100 se hacen transparentes.

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_bg_sprites.py
"""

from pathlib import Path
from PIL import Image
import numpy as np

DEST = Path(r"E:\0000ew V2Claude\frontend\assets\buildings")

# Sprites que necesitan fondo eliminado (los que tenían fondo gris/negro)
TARGETS = [
    "centro_ciudad.png",
    "torre_vigilancia.png",
    "centro_viajes.png",
    "almacen.png",
    "cuartel.png",
]

def remove_gray_bg(img: Image.Image, threshold=110, gray_tolerance=18) -> Image.Image:
    """
    Elimina fondo gris/negro.
    - threshold: brillo máximo para considerar fondo (0-255)
    - gray_tolerance: diferencia máxima entre R,G,B para ser "gris neutro"
    """
    img = img.convert("RGBA")
    arr = np.array(img, dtype=np.int32)
    r, g, b, a = arr[...,0], arr[...,1], arr[...,2], arr[...,3]

    # Píxeles que son grises neutros oscuros
    brightness = (r + g + b) / 3
    is_dark = brightness < threshold
    is_gray = (np.abs(r - g) < gray_tolerance) & \
              (np.abs(r - b) < gray_tolerance) & \
              (np.abs(g - b) < gray_tolerance)
    is_bg = is_dark & is_gray

    result = arr.copy()
    result[..., 3] = np.where(is_bg, 0, arr[..., 3])

    # Suavizar bordes: píxeles semitransparentes en el límite
    alpha = result[..., 3].astype(np.float32)
    # Reducir alfa de píxeles casi-fondo (brillo 100-140, gris)
    semi_bg = (brightness >= threshold) & (brightness < threshold + 40) & is_gray
    alpha = np.where(semi_bg, alpha * 0.3, alpha)
    result[..., 3] = alpha.clip(0, 255).astype(np.uint8)

    return Image.fromarray(result.astype(np.uint8), "RGBA")

for fname in TARGETS:
    path = DEST / fname
    if not path.exists():
        print(f"  SKIP (no encontrado): {fname}")
        continue
    img = Image.open(path)
    clean = remove_gray_bg(img)
    clean.save(path, "PNG")
    print(f"  OK: {fname}")

print()
print("HECHO — fondos grises eliminados.")
print()
print("Para verificar:")
print("  Ctrl+C → run.bat → Ctrl+Shift+R en http://127.0.0.1:8000/game")
