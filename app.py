# app.py — HustleVision (UI nera, glow neon bianco, difetti con quantità, +5€ se Nuovo, € nei prezzi)
import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path
from unidecode import unidecode

REQUIRED = ["title","brand","category","condition","price","listed_at"]
DEFAULTS = ["comps_ready.csv", "comps_ready_semicolon.csv"]

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="HustleVision – Resell Detector", page_icon="🧢", layout="centered")

# CSS: dark + NEON bianco
st.markdown("""
<style>
/* Sfondo nero full app */
.stApp { background: #000000; }

/* Base text neon (leggero glow) */
html, body, [class*="css"]  {
  color: #f8f8f8 !important;
  text-shadow: 0 0 2px rgba(255,255,255,0.55), 0 0 8px rgba(255,255,255,0.25);
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji','Segoe UI Emoji';
}

/* Titolo super big + neon forte */
h1 {
  font-size: 3rem !important;
  font-weight: 900 !important;
  letter-spacing: 0.5px;
  color: #ffffff !important;
  text-shadow:
    0 0 6px rgba(255,255,255,0.9),
    0 0 16px rgba(255,255,255,0.65),
    0 0 28px rgba(255,255,255,0.35);
}

/* Sottotitoli con glow medio */
h2, .stMarkdown h2, h3, .stMarkdown h3 {
  color: #ffffff !important;
  text-shadow:
    0 0 4px rgba(255,255,255,0.8),
    0 0 14px rgba(255,255,255,0.45);
  font-weight: 800 !important;
}

/* P, label, ecc. glow soft */
div[data-testid="stMarkdownContainer"] p,
label, span, .stSelectbox, .stNumberInput, .stTextInput {
  font-size: 1.07rem !important;
  color: #f6f6f6 !important;
  text-shadow:
    0 0 2px rgba(255,255,255,0.7),
    0 0 10px rgba(255,255,255,0.25);
}

/* Contenitore centrale */
.block-container { padding-top: 1.5rem; max-width: 900px; }

/* Pulsante primario (accent neon verde) */
button[kind="primary"] {
  background: linear-gradient(135deg, #00E676 0%, #00BFA5 100%) !important;
  color: #000 !important; font-weight: 900 !important;
  border: 0 !important; border-radius: 14px !important;
  box-shadow: 0 0 16px rgba(0, 255, 200, 0.45), 0 0 32px rgba(0, 255, 180, 0.25) !important;
}
button[kind="primary"]:hover { filter: brightness(1.08); }

/* Inputs con bordo neon */
div[data-baseweb="select"], div[data-baseweb="input"] {
  background: #0c0c0c !important;
  border: 1px solid rgba(255,255,255,0.22) !important;
  border-radius: 12px !important;
  box-shadow: inset 0 0 12px rgba(255,255,255,0.08);
}
div[data-baseweb="select"]:hover, div[data-baseweb="input"]:hover {
  border-color: rgba(255,255,255,0.35) !important;
}

/* Tabelle su sfondo scuro (se mai usate in futuro) */
[data-baseweb="table"] {
  background: #101010 !important;
  border-radius: 12px !important;
  border: 1px solid #1e1e1e !important;
}

/* Divider sottile */
hr { border-color: rgba(255,255,255,0.1) !important; }
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER (logo opzionale) -----------------
logo_path = Path("logo.png")
col_logo, col_title = st.columns([1, 3])
with col_logo:
    if logo_path.exists():
        # compatibile con Streamlit vecchie: usa width
        st.image(str(logo_path), width=150)
    else:
        st.write("")
with col_title:
    st.title("HustleVision — Resell Detector")

st.markdown("""
<div style='text-align: center; margin-top: 0.5em;'>
    <p style='font-size:1.3rem; font-weight:700; color:#00E676;'>
        Non è solo un prezzo — è la tua prossima mossa💸
    </p>
    <p style='font-size:1.1rem;'>
        <a href='https://solo.to/hustlevision' target='_blank' style='color:#00BFA5; font-weight:700; text-decoration:none;'>
            🔗 Contatti: solo.to/hustlevision
        </a>
    </p>
    <p style='font-size:0.95rem; color:gray; margin-top: -0.3em;'>
        🤖 Il bot è in fase di miglioramento continuo — stay tuned.
    </p>
</div>
""", unsafe_allow_html=True)

# ----------------- FUNZIONI UTILI -----------------
def norm(s):
    if s is None: return ""
    return unidecode(str(s)).lower().strip()

def coerce_price(x):
    try:
        return float(str(x).replace("€","").replace(",","."))
    except:
        return np.nan

def load_csv_auto(p: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(p)
    except:
        return pd.read_csv(p, sep=";")

def validate(df: pd.DataFrame) -> pd.DataFrame:
    miss = [c for c in REQUIRED if c not in df.columns]
    if miss:
        raise ValueError(f"Mancano colonne: {miss}")
    out = df.copy()
    out["price"] = out["price"].map(coerce_price)
    out = out.dropna(subset=["price"])
    out["brand_n"]     = out["brand"].map(norm)
    out["category_n"]  = out["category"].map(norm)
    out["condition_n"] = out["condition"].map(norm)
    return out

def fmt_eur(x: float) -> str:
    if x is None or np.isnan(x): return "—"
    return f"{x:.2f} €"

# ----------------- DATASET LOADER -----------------
st.sidebar.header("📥 Dataset")
up = st.sidebar.file_uploader("Carica comps CSV (title,brand,category,condition,price,listed_at)", type=["csv"])
df = None
if up:
    try:
        df = pd.read_csv(up)
    except:
        up.seek(0); df = pd.read_csv(up, sep=";")
else:
    for name in DEFAULTS:
        p = Path(name)
        if p.exists():
            df = load_csv_auto(p); break

if df is None:
    st.error("Nessun dataset trovato. Genera prima 'comps_ready.csv'.")
    st.stop()

try:
    df = validate(df)
except Exception as e:
    st.error(f"CSV non valido: {e}")
    st.stop()

st.sidebar.success(f"Comps caricati: {len(df)}")

# ----------------- FILTRI BRAND -> CATEGORIA -----------------
brands = sorted(df["brand"].dropna().unique(), key=lambda x: unidecode(x).lower())
brand = st.selectbox("Brand", brands)

cats = sorted(df[df["brand"] == brand]["category"].dropna().unique(), key=lambda x: unidecode(x).lower())
category = st.selectbox("Categoria", cats)

# ----------------- DIFETTI & NUOVO -----------------
st.subheader("Difetti e condizioni")

col_type, col_sev, col_qty, col_new = st.columns([1.2, 1.4, 1.1, 1.1])

with col_type:
    difetto_tipo = st.selectbox("Tipo difetto", ["Nessuno", "Macchia", "Buco"])

with col_sev:
    if difetto_tipo == "Nessuno":
        severita = st.selectbox("Severità", ["—"], disabled=True)
    elif difetto_tipo == "Macchia":
        severita = st.selectbox("Severità", ["Non evidente (−5 €)", "Evidente (−10 €)"])
    else:  # Buco
        severita = st.selectbox("Severità", ["Piccolo (−5 €)", "Grande (−10 €)"])

with col_qty:
    if difetto_tipo == "Nessuno":
        quantita = st.number_input("Quantità", min_value=0, max_value=50, value=0, step=1)
    else:
        quantita = st.number_input("Quantità", min_value=1, max_value=50, value=1, step=1)

with col_new:
    nuovo = st.toggle("Nuovo (+5 €)", value=False, help="Capo nuovo, con etichetta?")

def defect_unit_delta(tipo: str, sev: str) -> int:
    if tipo == "Macchia":
        return -10 if "Evidente" in sev else -5
    if tipo == "Buco":
        return -10 if "Grande" in sev else -5
    return 0

def apply_adjustments(med, lo, hi, nuovo_flag, tipo, sev, qty):
    adj = 0
    if nuovo_flag:
        adj += 5
    if tipo != "Nessuno" and qty > 0:
        adj += defect_unit_delta(tipo, sev) * qty
    med_a = max(0.0, round(med + adj, 2))
    lo_a  = max(0.0, round(lo  + adj, 2))
    hi_a  = max(0.0, round(hi  + adj, 2))
    return med_a, lo_a, hi_a, adj

# ----------------- STIMA -----------------
st.markdown("---")
cta = st.button("Calcola stima 💡", type="primary")

if cta:
    sub = df[(df["brand"] == brand) & (df["category"] == category)]
    n = len(sub)
    if n == 0:
        st.warning("Nessun comp per questa combinazione.")
    else:
        p = sub["price"].astype(float).values
        med = float(np.median(p))
        q1, q3 = float(np.percentile(p, 25)), float(np.percentile(p, 75))
        iqr = q3 - q1
        lo = max(0, round(med - 0.5*iqr, 2))
        hi = round(med + 0.5*iqr, 2)

        med_a, lo_a, hi_a, adj = apply_adjustments(med, lo, hi, nuovo, difetto_tipo, severita, quantita)

        st.subheader("💰 Stima")
        st.markdown(
            f"**Mediana base:** {fmt_eur(med)} &nbsp;&nbsp;—&nbsp;&nbsp; "
            f"**Range base:** {fmt_eur(lo)} – {fmt_eur(hi)}  "
        )
        adj_label = f"{adj:+.0f} €"
        desc_bits = []
        if nuovo: desc_bits.append("+5 € nuovo")
        if difetto_tipo != "Nessuno" and quantita > 0:
            desc_bits.append(f"{difetto_tipo.lower()} ×{quantita} ({severita})")
        st.markdown(f"**Aggiustamento:** {adj_label}  {' | '.join(desc_bits) if desc_bits else ''}")

        st.success(
            f"**Prezzo consigliato:** {fmt_eur(med_a)}  —  **Range consigliato:** {fmt_eur(lo_a)} – {fmt_eur(hi_a)}  \n"
            f"(basato su {n} comps)"
        )

# NIENTE “Comps recenti”: rimossi su richiesta
