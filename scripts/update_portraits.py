from pathlib import Path

# Actualizar login.html con las imágenes reales
login = Path(r"E:\0000ew V2Claude\frontend\index.html")
src = login.read_text(encoding="utf-8")

OLD = '''    <div class="login-header">
      <div class="login-alalaia">
        <img src="/static/assets/ui/alalaia_portrait.png" alt="AlalaiA" onerror="this.style.display=\'none\'">
        <span class="login-title-sub">EQUILIBRIO · MEMORIA · LUZ</span>
      </div>
      <div class="login-title-center">
        <h1 class="login-title">ETERNAL WARRIORS</h1>
        <span class="login-version">v3.0 — Ciclo NG+</span>
      </div>
      <div class="login-karlaka">
        <img src="/static/assets/ui/karlaka_portrait.png" alt="KarlakÁ" onerror="this.style.display=\'none\'">
        <span class="login-title-sub">GUERRA · TIERRA · VOLUNTAD</span>
      </div>
    </div>'''

NEW = '''    <div class="login-header">
      <div class="login-alalaia">
        <img src="/static/assets/ui/alalaia_portrait.jpg" alt="AlalaiA">
        <span class="login-title-sub">EQUILIBRIO · MEMORIA · LUZ</span>
      </div>
      <div class="login-title-center">
        <h1 class="login-title">ETERNAL WARRIORS</h1>
        <span class="login-version">v3.0 — Ciclo NG+</span>
      </div>
      <div class="login-karlaka">
        <img src="/static/assets/ui/karlaka_portrait.png" alt="KarlakÁ">
        <span class="login-title-sub">GUERRA · TIERRA · VOLUNTAD</span>
      </div>
    </div>'''

c = src.count(OLD)
if c != 1:
    print(f"ERROR login: {c} veces"); exit(1)
src = src.replace(OLD, NEW)
login.write_text(src, encoding="utf-8")
print("OK index.html — retratos actualizados")

# Actualizar CSS login para imágenes más grandes y con efecto
css = Path(r"E:\0000ew V2Claude\frontend\css\login.css")
csrc = css.read_text(encoding="utf-8")

OLD2 = """.login-alalaia img, .login-karlaka img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 2px solid var(--color-gold);
  object-fit: cover;
}"""

NEW2 = """.login-alalaia img {
  width: 160px;
  height: 200px;
  border-radius: 8px;
  border: 2px solid rgba(150,200,255,0.6);
  object-fit: cover;
  object-position: top;
  box-shadow: 0 0 40px rgba(150,200,255,0.3);
}

.login-karlaka img {
  width: 160px;
  height: 200px;
  border-radius: 8px;
  border: 2px solid rgba(200,80,20,0.6);
  object-fit: cover;
  object-position: top;
  box-shadow: 0 0 40px rgba(200,80,20,0.3);
}"""

c2 = csrc.count(OLD2)
if c2 != 1:
    print(f"ERROR css: {c2} veces"); exit(1)
csrc = csrc.replace(OLD2, NEW2)

# Ampliar container login para las imágenes más grandes
OLD3 = """.login-container {
  width: 680px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}"""

NEW3 = """.login-container {
  width: 860px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}"""

c3 = csrc.count(OLD3)
if c3 != 1:
    print(f"ERROR container: {c3} veces"); exit(1)
csrc = csrc.replace(OLD3, NEW3)

# Ampliar columnas laterales
OLD4 = """.login-alalaia, .login-karlaka {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 140px;
}"""

NEW4 = """.login-alalaia, .login-karlaka {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 180px;
}"""

c4 = csrc.count(OLD4)
if c4 != 1:
    print(f"ERROR columns: {c4} veces"); exit(1)
csrc = csrc.replace(OLD4, NEW4)

css.write_text(csrc, encoding="utf-8")
print("OK login.css — estilos de retratos actualizados")
print("\n✅ Copia las imágenes a frontend/assets/ui/ y recarga.")
