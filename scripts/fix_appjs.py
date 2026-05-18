from pathlib import Path

path = Path(r"E:\0000ew V2Claude\frontend\js\app.js")
src = path.read_text(encoding="utf-8")

OLD = """async function loadScreen(screen) {
  // Actualizar nav
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById('nav-' + (screen === 'city' ? 'city' :
              screen === 'army' ? 'army' : screen === 'invocations' ? 'inv' :
              screen === 'map' ? 'map' : screen === 'reports' ? 'rep' : 'set'));
  if (btn) btn.classList.add('active');

  const main = document.getElementById('main-content');
  main.innerHTML = '<div class="screen-loading"><span>Cargando...</span></div>';

  try {
    const mod = await import(`/static/js/screens/${screen}.js`);
    await mod.render(main, JUGADOR, CAPITAL);
  } catch(e) {
    main.innerHTML = `<div class="screen-loading"><span>Pantalla en construcción: ${screen}</span></div>`;
  }
}"""

NEW = """async function loadScreen(screen) {
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  const navMap = {city:'city',army:'army',invocations:'inv',map:'map',reports:'rep',settings:'set'};
  const btn = document.getElementById('nav-' + (navMap[screen]||'city'));
  if (btn) btn.classList.add('active');

  const main = document.getElementById('main-content');
  main.innerHTML = '<div class="screen-loading"><span>Cargando...</span></div>';

  try {
    const mod = await import(`/static/js/screens/${screen}.js?v=${Date.now()}`);
    await mod.render(main, JUGADOR, CAPITAL);
  } catch(e) {
    console.error('Error cargando pantalla:', screen, e);
    main.innerHTML = `<div class="screen-loading"><span>Error: ${e.message}</span></div>`;
  }
}"""

c = src.count(OLD)
if c != 1:
    print(f"ERROR: {c} veces"); exit(1)
src = src.replace(OLD, NEW)
path.write_text(src, encoding="utf-8")
print("OK app.js — error detallado + cache bust")
print("✅ Recarga en incógnito con Ctrl+Shift+R")
