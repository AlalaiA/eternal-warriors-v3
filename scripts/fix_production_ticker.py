"""
fix_production_ticker.py
Eternal Warriors v3.0 — Añade ticker de producción al frontend

Inserta en city.js:
  1. Al cargar la ciudad: guarda las tasas/seg del backend
  2. Ticker cada 1 segundo: actualiza los valores de recursos en el DOM
  3. Cada 30 segundos: llama /api/city/tick para sincronizar con backend
  4. Muestra tasa de producción debajo de cada recurso

Corre desde: E:\\0000ew V2Claude\\
Comando:     python fix_production_ticker.py
"""

from pathlib import Path
import sys

TARGET = Path(r"E:\0000ew V2Claude\frontend\js\screens\city.js")
src = TARGET.read_text(encoding="utf-8")

# ── FIX 1: render() — guardar tasas y arrancar ticker ────────────────────────
OLD_RENDER_END = """\
  setTimeout(() => drawCity(c), 120);
  window.addEventListener('resize', () => drawCity(c));
}"""

NEW_RENDER_END = """\
  setTimeout(() => drawCity(c), 120);
  window.addEventListener('resize', () => drawCity(c));

  // Ticker de producción — actualiza recursos por segundo en el DOM
  if (window._prodTicker) clearInterval(window._prodTicker);
  if (window._syncTicker) clearInterval(window._syncTicker);

  // Guardar tasas y estado actual
  window._prodTasas  = data.tasas  || {};
  window._prodCity   = data.city   || {};
  window._prodJugador = jugador;
  window._prodCapital = capital;

  // Tick local cada 1 segundo — actualiza DOM sin llamar al backend
  window._prodTicker = setInterval(() => {
    _tickProduccion();
  }, 1000);

  // Sync con backend cada 30 segundos — persiste cambios
  window._syncTicker = setInterval(async () => {
    try {
      const r = await fetch(`/api/city/${jugador}/${capital}/tick`, {method:'POST'});
      const d = await r.json();
      if (d.ok) {
        window._prodTasas = d.tasas || window._prodTasas;
        window._prodCity  = d.city  || window._prodCity;
      }
    } catch(e) { /* silencioso */ }
  }, 30000);
}

function _tickProduccion() {
  const tasas = window._prodTasas || {};
  const city  = window._prodCity  || {};
  if (!tasas || !Object.keys(tasas).length) return;

  // Acumular en el objeto ciudad local
  const recursos = ['MADERA','PIEDRA','HIERRO','ORO','CARBON','MANA'];
  recursos.forEach(r => {
    if (tasas[r]) {
      city[r] = (parseFloat(city[r]) || 0) + tasas[r];
    }
  });
  window._prodCity = city;

  // Actualizar DOM — stat-rows del panel izquierdo
  _updateStatDOM('Madera',  city.MADERA,  tasas.MADERA);
  _updateStatDOM('Piedra',  city.PIEDRA,  tasas.PIEDRA);
  _updateStatDOM('Hierro',  city.HIERRO,  tasas.HIERRO);
  _updateStatDOM('Carbón',  city.CARBON,  tasas.CARBON);
  _updateStatDOM('Oro',     city.ORO,     tasas.ORO);
  _updateStatDOM('Maná',    city.MANA,    tasas.MANA);
  _updateStatDOM('Aldeanos',city.ALDEANO, tasas.ALDEANOS_POR_HORA ? tasas.ALDEANOS_POR_HORA/3600 : 0);
}

function _updateStatDOM(label, valor, tasaSegundo) {
  // Buscar el stat-row por el texto del label
  const rows = document.querySelectorAll('.stat-row');
  for (const row of rows) {
    const lbl = row.querySelector('.stat-label');
    if (lbl && lbl.textContent.includes(label)) {
      const val = row.querySelector('.stat-val');
      if (val) {
        val.textContent = _fmtNum(valor);
        // Añadir tasa si existe
        let rateEl = row.querySelector('.stat-rate');
        if (!rateEl && tasaSegundo > 0) {
          rateEl = document.createElement('span');
          rateEl.className = 'stat-rate';
          rateEl.style.cssText = 'font-size:9px;color:#6a8040;margin-left:4px;';
          row.appendChild(rateEl);
        }
        if (rateEl && tasaSegundo > 0) {
          rateEl.textContent = '+' + _fmtNum(tasaSegundo) + '/s';
        }
      }
      break;
    }
  }
}

function _fmtNum(val) {
  if (val === undefined || val === null) return '—';
  const n = Number(val);
  if (isNaN(n) || n === 0) return '0';
  const abs = Math.abs(n), s = n < 0 ? '-' : '';
  const tiers = [
    [1e48,'Qd'],[1e45,'Td'],[1e42,'Dd'],[1e39,'Nd'],
    [1e36,'Ud'],[1e33,'Dc'],[1e30,'No'],[1e27,'Oc'],
    [1e24,'Sp'],[1e21,'Sx'],[1e18,'Qi'],[1e15,'Q'],
    [1e12,'T'],[1e9,'B'],[1e6,'M'],[1e3,'K']
  ];
  for (const [d, sfx] of tiers) {
    if (abs >= d) {
      const v = abs/d;
      return s + (v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v.toFixed(2)) + sfx;
    }
  }
  return s + Math.round(abs).toLocaleString('es');
}"""

c = src.count(OLD_RENDER_END)
if c != 1:
    print(f"ERROR fix 1: {c}x. Abortando.")
    sys.exit(1)
src = src.replace(OLD_RENDER_END, NEW_RENDER_END)
print("OK fix 1: ticker de producción insertado")

TARGET.write_text(src, encoding="utf-8")
print()
print("HECHO.")
print("  Ctrl+C → run.bat → Ctrl+Shift+R en http://127.0.0.1:8000/game")
print()
print("Los recursos se actualizarán visualmente cada segundo.")
print("Cada 30 segundos se sincroniza con el backend.")
