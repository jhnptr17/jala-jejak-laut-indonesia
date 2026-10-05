"""
JALA -- Jejak Laut Indonesia
Dashboard UAS Visualisasi Data dan Informasi (Politeknik Statistika STIS)
Tema: Produksi dan Ekspor Perikanan Tangkap Indonesia (BPS)
Topik: Multivariat (38 provinsi) + Geospasial (514 kab/kota) +
       Aliran (Sankey 3-lapis provinsi->Indonesia->negara, flow map datar, tren)
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import json
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

st.set_page_config(page_title="JALA \u2014 Jejak Laut Indonesia",
                    page_icon="\U0001F41F", layout="wide")

# ---------------------------------------------------------------------------
# THEME / CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Inter:wght@400;500;600&display=swap');
:root{
  --navy:#04385C; --ink:#0B2A42; --muted:#2B4F68; --blue:#0072B2; --amber:#E69F00;
  --green:#009E73; --vermil:#D55E00; --depth:0; --acc:#0072B2;
}
html, body, [class*="css"]{ font-family:'Inter',sans-serif; color:var(--ink); }
h1,h2,h3,.hero h1,.beat h3,.beat .big{ font-family:'Bricolage Grotesque','Inter',sans-serif; }
footer{ visibility:hidden; }

/* ---------- latar laut: makin gulir makin dalam ---------- */
.stApp{ background:linear-gradient(180deg,#EAF7FF 0%,#D3ECFA 35%,#B5DCF3 70%,#9CCBEA 100%) fixed; }
.stApp::after{ content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background:var(--navy); opacity:calc(var(--depth) * .14); transition:opacity .3s; }
[data-testid="stMain"], .block-container{ position:relative; z-index:1; }
.block-container{ max-width:1180px; padding-top:2rem; }

/* ---------- scroll-reveal ---------- */
.reveal{ opacity:0; transform:translateY(18px); transition:opacity .6s ease, transform .6s ease; }
.reveal.visible{ opacity:1; transform:none; }
.reveal.from-left{ transform:translateX(-36px); } .reveal.from-right{ transform:translateX(36px); }
.reveal.from-left.visible, .reveal.from-right.visible{ transform:none; }
@media (prefers-reduced-motion:reduce){ .reveal{ opacity:1; transform:none; transition:none; } .hero{ animation:none!important; } .boat-bob{ animation:none!important; } }

/* ---------- hero ---------- */
.hero{ position:relative; overflow:hidden; color:#fff; border-radius:24px; padding:2.8rem 2.6rem 4.6rem;
  background:linear-gradient(120deg,#041C32 0%,#04385C 42%,#0A6EBD 78%,#4FB7E8 100%);
  background-size:220% 220%; animation:drift 18s ease-in-out infinite;
  box-shadow:0 14px 34px rgba(4,56,92,.25); margin-bottom:.4rem; }
@keyframes drift{ 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }
.hero h1{ font-size:3rem; font-weight:800; margin:0 0 .3rem; line-height:1.05; letter-spacing:-.01em; }
.hero h1 span{ font-weight:500; opacity:.82; }
.hero .tagline{ font-size:1.05rem; opacity:.88; margin-bottom:1.1rem; }
.hero p.lede{ font-size:1.06rem; line-height:1.7; max-width:700px; opacity:.97; position:relative; z-index:2; }
.hero .wave{ position:absolute; left:0; right:0; bottom:-2px; line-height:0; z-index:3; }
.hero .deco{ position:absolute; pointer-events:none; z-index:1; }
.hero .deco.boat{ right:3%; top:7%; width:290px; opacity:.9; }
.hero .deco.school{ right:4%; top:46%; width:210px; opacity:.35; }
.boat-bob{ animation:bob 7s ease-in-out infinite; transform-origin:50% 90%; }
@keyframes bob{ 0%,100%{ transform:translateY(0) rotate(-1deg) } 50%{ transform:translateY(5px) rotate(1deg) } }
.stat-row{ display:grid; grid-template-columns:repeat(4,1fr); gap:18px; margin-top:1.6rem; position:relative; z-index:2; }
.stat-card{ border-left:2px solid rgba(255,255,255,.4); padding:.1rem 0 .1rem .9rem; }
.stat-card svg{ width:26px; height:26px; margin-bottom:4px; fill:none; stroke:#BFE3F7; stroke-width:1.7; stroke-linecap:round; stroke-linejoin:round; }
.stat-card .big{ font-family:'Bricolage Grotesque',sans-serif; font-size:1.6rem; font-weight:800; line-height:1.15; }
.stat-card .lbl{ font-size:.82rem; color:#D7EEFB; }
@media(max-width:900px){ .stat-row{ grid-template-columns:repeat(2,1fr);} .hero .deco{ display:none; } .hero h1{ font-size:2.2rem; } }

/* ---------- sumber & narasi ---------- */
.srcbar{ display:flex; align-items:center; gap:14px; flex-wrap:wrap; padding:.3rem 0; margin:.2rem 0 1rem; font-size:.92rem; color:var(--navy); }
.srcbar .lbl{ font-weight:700; } .srcbar .it{ display:flex; align-items:center; gap:8px; font-weight:600; }
.srcbar img{ height:34px; } .srcbar .sep{ width:1px; height:26px; background:#8FBBD6; }
.srcbar .badge{ width:34px; height:34px; border-radius:50%; background:var(--blue); color:#fff; display:flex; align-items:center; justify-content:center; font-size:.7rem; font-weight:800; }
.src{ font-size:.78rem; color:var(--muted); margin:-.2rem 0 1.2rem; }

.beat{ max-width:640px; margin:2.6rem 0 1.2rem; padding:.2rem 0 .2rem 1.4rem; border-left:6px solid var(--acc); }
.beat.right{ margin-left:auto; padding:.2rem 1.4rem .2rem 0; border-left:none; border-right:6px solid var(--acc); text-align:right; }
.beat .big{ font-size:3.2rem; font-weight:800; color:var(--acc); line-height:1; }
.beat .kk{ font-size:.82rem; font-weight:600; color:var(--acc); }
.beat h3{ font-size:1.45rem; font-weight:700; margin:.2rem 0 .5rem; color:var(--navy); }
.beat p{ font-size:1.02rem; line-height:1.75; margin:0; }
@media(max-width:640px){ .beat,.beat.right{ max-width:100%; text-align:left; margin-left:0; border-right:none; border-left:5px solid var(--acc); padding:.2rem 0 .2rem 1rem; } .beat .big{ font-size:2.4rem; } }

.insight-card{ max-width:760px; margin:1rem 0; padding:.2rem 0 .2rem 1.2rem; border-left:4px solid var(--amber); }
.insight-card .kicker2{ font-size:.82rem; font-weight:700; color:var(--blue); }
.insight-card .txt{ font-size:1.02rem; line-height:1.65; margin-top:3px; }
.insight-card b{ background:linear-gradient(transparent 58%,#FFE08A 58%); }
.note-card{ max-width:760px; margin:.8rem 0; font-size:.92rem; font-style:italic; color:var(--muted); }

/* ---------- kontrol, tab, chart ---------- */
div[data-testid="stPlotlyChart"]{ border-radius:18px; overflow:hidden; }
.legend-note{ font-size:.82rem; color:var(--muted); margin:-.3rem 0 .8rem; line-height:1.55; }

/* ---------- pemisah bergambar ---------- */
.divider{ display:flex; justify-content:center; margin:2.6rem 0 1rem; opacity:.55; }
.divider svg{ width:min(420px,80%); height:auto; }
</style>
""", unsafe_allow_html=True)


def embed_html(html, height):
    """st.iframe (baru) jika tersedia, fallback ke components.html (lama)."""
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:
        components.html(html, height=height, scrolling=False)

# Script animasi scroll-reveal HARUS lewat iframe (bukan st.markdown) --
# tag <script> yang disisipkan lewat innerHTML/markdown tidak akan dieksekusi
# browser, jadi perlu "rumah" iframe sendiri yang punya akses ke dokumen induk.
embed_html("""
<script>
(function(){
    function setup(){
        const doc = window.parent.document;
        const obs = new IntersectionObserver((entries)=>{
            entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('visible'); obs.unobserve(e.target);} });
        }, {threshold:0.1});
        function observeAll(){ doc.querySelectorAll('.reveal:not(.visible)').forEach(el=>obs.observe(el)); }
        observeAll();
        new MutationObserver(observeAll).observe(doc.body, {childList:true, subtree:true});
    }
    setTimeout(setup, 200);
    setTimeout(function(){const d=window.parent.document,m=d.querySelector('[data-testid="stMain"]')||d.documentElement;
      m.addEventListener('scroll',function(){const p=m.scrollTop/Math.max(1,m.scrollHeight-m.clientHeight);
      d.documentElement.style.setProperty('--depth',Math.min(1,p));},{passive:true});},400);
})();
</script>
""", height=1)

WAVE_SVG = """
<div class="wave"><svg viewBox="0 0 1440 90" xmlns="http://www.w3.org/2000/svg">
<path fill="#F6FBFF" d="M0,32L80,42.7C160,53,320,75,480,74.7C640,75,800,53,960,42.7C1120,32,1280,32,1360,32L1440,32L1440,100L0,100Z"></path>
</svg></div>
"""


# ---------------------------------------------------------------------------
# ASET SVG: siluet ikan dan kapal (inline, tanpa file gambar)
# ---------------------------------------------------------------------------
def _fish(x, y, sc=1.0, flip=False):
    t = f"translate({x},{y}) scale({-sc if flip else sc},{sc})"
    return f'<g transform="{t}"><path d="M2 10C9 1 22 1 31 10 18 19 9 19 2 10Z M29 10L40 3L37 10L40 17Z"/></g>'

_WAVE_LINE = "M0 {y}" + "q10.5-8 21 0t21 0" * 10

BOAT_HERO = (
    '<svg class="deco boat boat-bob" viewBox="0 0 320 210" fill="#fff" aria-hidden="true">'
    '<path d="M10 118H310C298 150 276 170 246 174H84C54 170 22 150 10 118Z"/>'
    '<path fill-rule="evenodd" d="M180 78H234V118H180Z M190 88H202V100H190Z M212 88H224V100H212Z"/>'
    '<rect x="172" y="70" width="70" height="9" rx="2"/>'
    '<rect x="96" y="22" width="5" height="96"/><path d="M101 22L126 31L101 40Z"/>'
    '<path d="M98 34L44 114M98 34L152 114" stroke="#fff" stroke-width="2.5" fill="none" opacity=".8"/>'
    f'<path d="{_WAVE_LINE.format(y=186)}" fill="none" stroke="#fff" stroke-width="3" opacity=".55"/>'
    f'<path d="{_WAVE_LINE.format(y=200)}" fill="none" stroke="#fff" stroke-width="3" opacity=".3"/>'
    '</svg>')

FISH_SCHOOL = (
    '<svg class="deco school" viewBox="0 0 230 120" fill="#fff" aria-hidden="true">'
    + _fish(150, 8, 1.1, True) + _fish(205, 34, .8, True) + _fish(120, 46, .7, True)
    + _fish(185, 66, 1.0, True) + _fish(90, 78, .9, True) + _fish(150, 98, .6, True) + '</svg>')

DIVIDER_SVG = (
    '<div class="divider"><svg viewBox="0 0 420 46" fill="#04385C" aria-hidden="true">'
    f'<path d="{_WAVE_LINE.format(y=36)}" fill="none" stroke="#04385C" stroke-width="2" stroke-linecap="round"/>'
    + _fish(34, 6, .8) + _fish(92, 14, .55) + _fish(66, 0, .45)
    + '<g transform="translate(180,6)"><path d="M0 22H60L52 31H8Z"/><path d="M28 10H44V22H28Z"/><rect x="17" y="0" width="2.4" height="22"/></g>'
    + _fish(330, 8, .7, True) + _fish(386, 16, .5, True) + _fish(360, 2, .45, True)
    + '</svg></div>')

def _icon(inner):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{inner}</svg>'
ICON_NELAYAN = _icon('<path d="M13 4v11a4.5 4.5 0 0 1-9 0v-1"/><circle cx="13" cy="3" r="1"/><path d="M2 13l2-2.5 2 2.5"/>')
ICON_KAPAL = _icon('<path d="M3 15h18l-3 5H6z"/><path d="M12 15V5l5 7h-5"/>')
ICON_IKAN = _icon('<path d="M3 12c3-5 9-5 13 0-4 5-10 5-13 0z"/><path d="M16 12l5-4v8z"/>')
ICON_EKSPOR = _icon('<path d="M3 16h18l-2 4H5z"/><rect x="5" y="9" width="4" height="5"/><rect x="10" y="9" width="4" height="5"/><rect x="15" y="11" width="3" height="3"/>')

def reveal(html, cls=""):
    st.markdown(f'<div class="reveal {cls}">{html}</div>', unsafe_allow_html=True)

def beat(kicker, headline, body, side="left", big="", acc="#0072B2"):
    b = f'<div class="big">{big}</div>' if big else ""
    reveal(f'<div class="beat {side}" style="--acc:{acc}">{b}<div class="kk">{kicker}</div>'
           f'<h3>{headline}</h3><p>{body}</p></div>', cls=f"from-{side}")

def sumber(t=""):
    st.markdown(f'<div class="src">Sumber: BPS. {t}</div>', unsafe_allow_html=True)

def clean(fig):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#0B2A42")
    return fig

def logo(fn, alt, ini):
    import base64, os
    p = os.path.join("assets", fn)
    if os.path.exists(p):
        b = base64.b64encode(open(p, "rb").read()).decode()
        return f'<img src="data:image/png;base64,{b}" alt="{alt}">'
    return f'<span class="badge">{ini}</span>'

# ---------------------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------------------

@st.cache_data
def load_multivariat():
    return pd.read_csv("data/multivariat_provinsi.csv")

@st.cache_data
def load_geospasial():
    df = pd.read_csv("data/geospasial_kabkota.csv", dtype={"kode_wilayah": str})
    df["kode_wilayah"] = df["kode_wilayah"].str.zfill(4)
    t = df["produksi_perikanan_tangkap_kg"]
    # Rasio untuk choropleth. Tanpa produksi (t == 0), rasio tidak terdefinisi -> NaN.
    df["harga_rp_kg"] = np.where(t > 0, df["nilai_produksi_perikanan_tangkap_rupiah"] / t, np.nan)
    df["pct_laut"] = np.where(t > 0, df["produksi_perikanan_tangkap_laut_kg"] / t * 100, np.nan)
    return df

@st.cache_data
def load_geojson():
    with open("data/kabkota_simplified.geojson") as f:
        return json.load(f)

@st.cache_data
def load_aliran_negara():
    return pd.read_csv("data/aliran_ekspor_negara.csv")

@st.cache_data
def load_ekspor_provinsi():
    return pd.read_csv("data/ekspor_provinsi_tahun.csv")

df_mv = load_multivariat()
df_geo = load_geospasial()
geojson = load_geojson()
df_flow = load_aliran_negara()
df_prov_flow = load_ekspor_provinsi()

NEGARA_COORD = {
    "Amerika Serikat": (38.0, -97.0), "Tiongkok": (35.0, 103.0),
    "Jepang": (36.2, 138.0), "Malaysia": (4.2, 102.0),
    "Singapura": (1.35, 103.8), "Taiwan": (23.7, 121.0),
    "Hongkong": (22.3, 114.2), "Arab Saudi": (24.0, 45.0),
    "Australia": (-25.0, 133.0), "Uni Emirat Arab": (24.0, 54.0),
}
INDONESIA_COORD = (-3.0, 112.0)

def idfmt(n):
    return f"{n:,.0f}".replace(",", ".")

# ---------------------------------------------------------------------------
# FLOW MAP datar (Plotly scattergeo)
# ---------------------------------------------------------------------------
def render_flowmap(neg_df, tahun, height=520):
    mx = neg_df["volume_ton"].max()
    fig = go.Figure()
    for _, r in neg_df.iterrows():
        if r["negara_tujuan"] not in NEGARA_COORD:
            continue
        la, lo = NEGARA_COORD[r["negara_tujuan"]]
        fig.add_trace(go.Scattergeo(lat=[INDONESIA_COORD[0], la], lon=[INDONESIA_COORD[1], lo], mode="lines",
            line=dict(width=1.5 + 9 * r["volume_ton"] / mx, color="rgba(213,94,0,0.6)"), hoverinfo="skip"))
    d = neg_df[neg_df.negara_tujuan.isin(NEGARA_COORD)]
    fig.add_trace(go.Scattergeo(lat=[NEGARA_COORD[n][0] for n in d.negara_tujuan],
        lon=[NEGARA_COORD[n][1] for n in d.negara_tujuan], mode="markers+text", text=d.negara_tujuan,
        textposition="top center", textfont=dict(size=11, color="#04385C"),
        marker=dict(color="#D55E00", line=dict(color="white", width=1.5), size=8 + 22 * d.volume_ton / mx),
        customdata=[idfmt(v) for v in d.volume_ton],
        hovertemplate="Indonesia \u2192 %{text}<br>%{customdata} ton<extra></extra>"))
    fig.add_trace(go.Scattergeo(lat=[INDONESIA_COORD[0]], lon=[INDONESIA_COORD[1]], mode="markers+text",
        text=["Indonesia"], textposition="bottom center", marker=dict(color="#0072B2", size=16, line=dict(color="white", width=2)),
        hoverinfo="skip"))
    fig.update_geos(projection_type="natural earth", showland=True, landcolor="#EAF2F7", showocean=True,
        oceancolor="rgba(214,236,250,0.65)", showcountries=True, countrycolor="white", coastlinecolor="#B8CCD9",
        showframe=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    st.plotly_chart(clean(fig), use_container_width=True)
    sumber(f"Ekspor menurut negara tujuan, {tahun}. Batas negara: Plotly/Natural Earth (non-BPS).")

# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------
total_nelayan = int(df_mv["jumlah_nelayan_orang"].sum())
total_kapal = int(df_mv["jumlah_kapal"].sum())
total_produksi_ton = df_geo["produksi_perikanan_tangkap_kg"].sum() / 1000
tahun_terakhir = int(df_flow["tahun"].max())
ekspor_terakhir_ton = df_flow[df_flow.tahun == tahun_terakhir]["volume_ton"].sum()
negara_top = (df_flow[(df_flow.tahun == tahun_terakhir) & (df_flow.negara_tujuan != "Lainnya")]
              .sort_values("volume_ton", ascending=False).iloc[0])

st.markdown(f"""
<div class="hero reveal visible">
{BOAT_HERO}{FISH_SCHOOL}
<h1>JALA <span>Jejak Laut Indonesia</span></h1>
<div class="tagline">Menebar jala, menjaring cerita dari laut Indonesia. Data BPS 2024/2025.</div>
<p class="lede">Subuh di dermaga mana pun di Nusantara selalu mirip: mesin kapal
menyala, es balok diangkut, lampu perahu menyebar ke laut gelap. {idfmt(total_nelayan)}
nelayan dan {idfmt(total_kapal)} kapal bekerja hari itu, dan setahun kemudian angkanya
menjadi hampir {idfmt(total_produksi_ton)} ton ikan. Sebagian mampir ke pasar dekat rumah,
sebagian naik kapal kontainer menuju {negara_top['negara_tujuan']} dan negara lain.
Gulir pelan ke bawah, kita ikuti jejaknya sampai ke seberang samudra.</p>
<div class="stat-row">
  <div class="stat-card">{ICON_NELAYAN}
    <div class="big">{idfmt(total_nelayan)}</div><div class="lbl">Nelayan, 38 provinsi</div></div>
  <div class="stat-card">{ICON_KAPAL}
    <div class="big">{idfmt(total_kapal)}</div><div class="lbl">Kapal perikanan</div></div>
  <div class="stat-card">{ICON_IKAN}
    <div class="big">{idfmt(total_produksi_ton)} ton</div><div class="lbl">Produksi, 514 kab/kota</div></div>
  <div class="stat-card">{ICON_EKSPOR}
    <div class="big">{idfmt(ekspor_terakhir_ton)} ton</div><div class="lbl">Ekspor {tahun_terakhir}</div></div>
</div>
{WAVE_SVG}
</div>
""", unsafe_allow_html=True)




# ===========================================================================
# TAB 1, MULTIVARIAT
# ===========================================================================
if True:
    beat("Bab 1 \u00b7 Profil provinsi, 2024", "Armada besar belum tentu jagoan ekspor",
         "Setiap provinsi kita potret lewat delapan angka: jumlah nelayan, kapal, rumah tangga perikanan, produksi laut, produksi perairan darat, nilai produksi (2024), PDRB perikanan (2024), dan volume ekspor (2025). PCA meringkasnya jadi dua sumbu, jadi provinsi yang berdekatan punya wajah perikanan yang mirip, dan yang menyendiri hampir pasti punya cerita khusus. Tarik kotak seleksi di grafik kiri, lalu lihat garis provinsi terpilih menyala di grafik kanan.",
         "left", "38", "#0072B2")

    numeric_cols = [c for c in df_mv.columns if c != "provinsi"]
    X_scaled = StandardScaler().fit_transform(df_mv[numeric_cols].values)

    n_clusters = st.slider("Jumlah klaster (K-Means)", 2, 8, 4)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_mv = df_mv.copy()
    df_mv["klaster"] = km.fit_predict(X_scaled).astype(str)

    pca = PCA(n_components=2)
    pcs = pca.fit_transform(X_scaled)
    df_mv["PC1"], df_mv["PC2"] = pcs[:, 0], pcs[:, 1]
    var_exp = pca.explained_variance_ratio_

    blues = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#56B4E9", "#CC79A7", "#F0E442", "#555555"]  # Okabe-Ito, aman buta warna
    brush = alt.selection_interval(name="brush")

    col_l, col_r = st.columns(2)
    with col_l:
        scatter = (
            alt.Chart(df_mv).mark_circle(size=110, stroke="white", strokeWidth=0.6)
            .encode(
                x=alt.X("PC1:Q", title=f"PC1 ({var_exp[0]*100:.0f}% varians)"),
                y=alt.Y("PC2:Q", title=f"PC2 ({var_exp[1]*100:.0f}% varians)"),
                color=alt.condition(brush, alt.Color("klaster:N", scale=alt.Scale(range=blues), legend=alt.Legend(title="Klaster")), alt.value("#D9E6EC")),
                tooltip=["provinsi"] + numeric_cols,
            ).add_params(brush)
            .properties(title="PCA Biplot: kemiripan antarprovinsi", height=380)
        )
        st.altair_chart(scatter.configure(background="transparent").configure_view(strokeWidth=0), use_container_width=True)
        sumber("Profil perikanan provinsi: nelayan, kapal, produksi, nilai produksi 2024; PDRB 2024; volume ekspor 2025.")
    with col_r:
        pc_df = df_mv.melt(id_vars=["provinsi", "klaster"], value_vars=numeric_cols,
                            var_name="variabel", value_name="nilai")
        parallel = (
            alt.Chart(pc_df).transform_filter(brush).mark_line(opacity=0.65)
            .encode(
                x=alt.X("variabel:N", title=None, axis=alt.Axis(labelAngle=-35, labelFontSize=9)),
                y=alt.Y("nilai:Q"),
                color=alt.Color("klaster:N", scale=alt.Scale(range=blues), legend=None),
                detail="provinsi:N", tooltip=["provinsi:N"],
            ).properties(title="Parallel Coordinates: seret area di peta kiri", height=380)
        )
        st.altair_chart(parallel.configure(background="transparent").configure_view(strokeWidth=0), use_container_width=True)
        sumber("Data sama dengan biplot (2024/2025).")

    st.caption("Tarik kotak seleksi di PCA biplot (*brushing*), garis yang cocok "
               "ikut menyala di parallel coordinates (*linking*).")

    beat("Rapor tiap provinsi", "Kalau PCA itu peta, heatmap itu rapornya",
         "Kolom adalah provinsi, baris adalah indikator, dan warnanya skor standar (z) supaya tiap indikator sebanding: merah di atas rata-rata nasional, biru di bawahnya. Provinsi satu klaster diurutkan berdampingan. Cari kolom yang merah di hampir semua baris (raksasa serba besar) dan kolom yang merah hanya di satu baris (spesialis).",
         "right", "8", "#D55E00")
    heat_df = df_mv.set_index("provinsi")[numeric_cols]
    heat_df = heat_df.loc[df_mv.sort_values("klaster")["provinsi"]]
    heat_df = (heat_df - heat_df.mean()) / heat_df.std()
    fig = px.imshow(heat_df.T, aspect="auto", color_continuous_scale="RdBu_r", color_continuous_midpoint=0,
                     labels=dict(color="Skor-z"))
    fig.update_layout(height=400, margin=dict(t=10))
    st.plotly_chart(clean(fig), use_container_width=True)
    sumber("Skor-z dari delapan indikator provinsi (2024/2025).")

    top_nelayan = df_mv.loc[df_mv.jumlah_nelayan_orang.idxmax()]
    top_ekspor = df_mv.loc[df_mv.volume_ekspor_2025_ton.idxmax()]
    top_pdrb = df_mv.loc[df_mv.pdrb_pkp_2024_rpmilyar.idxmax()]
    same_cluster = df_mv[df_mv.klaster == top_ekspor.klaster]["provinsi"].tolist()
    reveal(f"""
    <div class="insight-card"><div class="kicker2">Ternyata...</div>
    <div class="txt">Nelayan terbanyak justru ada di <b>{top_nelayan['provinsi']}</b>
    ({idfmt(top_nelayan['jumlah_nelayan_orang'])} orang), tapi yang paling
    rajin kirim ikan ke luar negeri malah <b>{top_ekspor['provinsi']}</b>
    ({idfmt(top_ekspor['volume_ekspor_2025_ton'])} ton di 2025). Dua hal ini
    nggak selalu jalan bareng. <b>{top_pdrb['provinsi']}</b> pun jadi
    penyumbang PDRB perikanan terbesar, provinsi ketiga yang berbeda lagi.
    {top_ekspor['provinsi']} ternyata satu klaster dengan
    {len(same_cluster)-1} provinsi lain yang kemungkinan punya karakter
    "berorientasi ekspor" serupa.</div></div>
    """)

    with st.expander("Provinsi mana yang paling 'beda sendiri'?"):
        centroid_dist = np.linalg.norm(X_scaled - km.cluster_centers_[km.labels_], axis=1)
        out_df = df_mv[["provinsi", "klaster"]].copy()
        out_df["jarak_ke_centroid"] = centroid_dist
        st.dataframe(out_df.sort_values("jarak_ke_centroid", ascending=False).head(10),
                     use_container_width=True)

# ===========================================================================
# TAB 2, GEOSPASIAL
# ===========================================================================
if True:
    beat("Bab 2 \u00b7 Sebaran kab/kota, 2024", "Rata-rata provinsi itu menipu",
         "Satu provinsi bisa menyimpan kabupaten dengan tangkapan jutaan kilogram dan tetangganya yang nyaris sepi. Baru di tingkat 514 kabupaten/kota titik panasnya kelihatan. Peta warna membandingkan rasio (harga rata-rata per kg dan porsi tangkapan laut), jadi luas wilayah dan besarnya produksi tidak otomatis memenangkan peta. Simbol proporsional menjawab pertanyaan lain: seberapa besar produksinya dalam angka absolut. Bandingkan keduanya.",
         "right", "514", "#E69F00")

    RATIO_LABELS = {
        "harga_rp_kg": "Harga rata-rata ikan (Rp per kg)",
        "pct_laut": "Porsi tangkapan laut (% dari produksi total)",
    }
    ABS_LABELS = {
        "produksi_perikanan_tangkap_kg": "Produksi total (kg)",
        "produksi_perikanan_tangkap_laut_kg": "Produksi laut (kg)",
        "produksi_perikanan_tangkap_perairandarat_kg": "Produksi perairan darat (kg)",
        "nilai_produksi_perikanan_tangkap_rupiah": "Nilai produksi (Rp)",
    }
    GRAY, NODATA = "#9AA5AE", "Tidak ada produksi"
    PALETTE = ["#FFFFCC", "#A1DAB4", "#41B6C4", "#2C7FB8", "#253494"]  # ColorBrewer YlGnBu 5 kelas, aman buta warna

    def classify(df, key):
        """Kelas diskret: kuantil 5 kelas untuk harga, kelas manual untuk % laut (dua kutub)."""
        v = df[key]
        if key == "harga_rp_kg":
            edges = [float(round(x, -2)) for x in v.dropna().quantile([.2, .4, .6, .8])]
            labels = ([f"< {idfmt(edges[0])}"]
                      + [f"{idfmt(lo)}\u2013{idfmt(hi)}" for lo, hi in zip(edges[:-1], edges[1:])]
                      + [f"\u2265 {idfmt(edges[-1])}"])
            idx = np.digitize(v.fillna(-1), edges)
        else:
            labels = ["0% (tanpa tangkapan laut)", "> 0\u201350%", "> 50\u201390%", "> 90% sampai < 100%", "100% (semua dari laut)"]
            idx = np.select([v == 0, v <= 50, v <= 90, v < 100], [0, 1, 2, 3], default=4)
        kelas = pd.Series(np.array(labels, dtype=object)[idx], index=df.index)
        kelas[v.isna()] = NODATA
        return kelas, labels

    c1, c2 = st.columns([1, 1])
    map_type = c1.radio("Jenis peta", ["Choropleth (rasio)", "Proportional symbol (angka absolut)"], horizontal=True)
    is_choro = map_type.startswith("Choropleth")
    if is_choro:
        metric = c2.selectbox("Indikator rasio", list(RATIO_LABELS), format_func=lambda x: RATIO_LABELS[x])
    else:
        metric = c2.selectbox("Indikator absolut", list(ABS_LABELS), format_func=lambda x: ABS_LABELS[x])

    geo_ids = {f["properties"]["kode_wilayah"] for f in geojson["features"]}
    n_match = int(df_geo["kode_wilayah"].isin(geo_ids).sum())

    if is_choro:
        d = df_geo[["kode_wilayah", "kabupaten", "provinsi"]].copy()
        d["kelas"], labels = classify(df_geo, metric)
        if metric == "harga_rp_kg":
            d["nilai"] = df_geo[metric].map(lambda x: "Tidak ada produksi" if pd.isna(x) else f"Rp {idfmt(x)}/kg")
        else:
            d["nilai"] = df_geo[metric].map(lambda x: "Tidak ada produksi" if pd.isna(x) else f"{x:.1f}%".replace(".", ","))
        cmap = dict(zip(labels, PALETTE)); cmap[NODATA] = GRAY
        fig = px.choropleth_map(
            d, geojson=geojson, locations="kode_wilayah", featureidkey="properties.kode_wilayah",
            color="kelas", color_discrete_map=cmap, category_orders={"kelas": labels + [NODATA]},
            map_style="carto-positron", zoom=3.6, center={"lat": -2.2, "lon": 118}, opacity=0.88,
            hover_name="kabupaten", hover_data={"provinsi": True, "nilai": True, "kelas": False, "kode_wilayah": False},
            labels={"nilai": "Nilai", "provinsi": "Provinsi"},
        )
        fig.update_traces(marker_line_width=0.4, marker_line_color="#7C93A3")
        fig.update_layout(height=580, margin=dict(l=0, r=0, t=0, b=64),
                          legend=dict(title_text=RATIO_LABELS[metric], orientation="h", yanchor="top", y=-0.01, x=0,
                                      font=dict(size=11), bgcolor="rgba(0,0,0,0)"))
    else:
        plot_df = df_geo.dropna(subset=["lat", "lon"])
        fig = px.scatter_map(
            plot_df, lat="lat", lon="lon", size=metric, color=metric,
            color_continuous_scale="YlOrRd", hover_name="kabupaten",
            hover_data={"provinsi": True, metric: True, "lat": False, "lon": False},
            zoom=3.6, size_max=32, labels={metric: ABS_LABELS[metric]},
        )
        fig.update_layout(map_style="carto-positron", height=580, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(clean(fig), use_container_width=True)
    sumber("Produksi dan nilai produksi perikanan tangkap kab/kota 2024. Batas wilayah: non-BPS.")

    n_nodata = int(df_geo["harga_rp_kg"].isna().sum())
    if is_choro and metric == "harga_rp_kg":
        v = df_geo["harga_rp_kg"].dropna()
        n_out = int((v > 100000).sum())
        st.markdown(f'''<div class="legend-note">Harga = nilai produksi dibagi volume produksi. Lima kelas kuantil
        (tiap kelas memuat sekitar 20% kab/kota) dipilih karena sebarannya sangat miring: median Rp {idfmt(v.median())} per kg,
        sedangkan nilai maksimum mencapai jutaan. Kelas interval sama akan menumpuk hampir semua wilayah di satu warna.
        Abu-abu: {n_nodata} kab/kota tanpa produksi, jadi harga tidak terdefinisi.</div>''', unsafe_allow_html=True)
        reveal(f'''<div class="insight-card"><div class="kicker2">Baca dengan hati-hati</div>
        <div class="txt">Separuh kab/kota menjual ikan di kisaran <b>Rp {idfmt(v.quantile(.25))} sampai
        Rp {idfmt(v.quantile(.75))} per kg</b>. Tetapi {n_out} kab/kota mencatat harga di atas Rp 100.000 per kg,
        sebagian besar wilayah non-pesisir dengan tangkapan sangat kecil. Angka sekecil itu rawan salah satuan atau
        salah catat, jadi kelas teratas lebih mencerminkan masalah data daripada ikan yang benar-benar mahal.</div></div>''')
    elif is_choro:
        v = df_geo["pct_laut"].dropna()
        n0, n100 = int((v == 0).sum()), int((v == 100).sum())
        st.markdown(f'''<div class="legend-note">Porsi laut = produksi laut dibagi produksi total. Sebarannya dua kutub:
        {n0} kab/kota 0% dan {n100} kab/kota 100%, sehingga kuantil menghasilkan batas kelas kembar. Dipakai lima kelas manual
        dengan dua kutub sebagai kelas tersendiri. Abu-abu: {n_nodata} kab/kota tanpa produksi.</div>''', unsafe_allow_html=True)
        reveal(f'''<div class="insight-card"><div class="kicker2">Yang mencolok</div>
        <div class="txt">Dari {len(v)} kab/kota yang berproduksi, <b>{n100} ({n100/len(v)*100:.0f}%)</b> menangkap ikan
        hanya di laut dan <b>{n0} ({n0/len(v)*100:.0f}%)</b> hanya di perairan darat. Hanya {len(v)-n0-n100} wilayah yang
        bercampur. Perikanan tangkap kita terbelah dua dunia, laut dan air tawar, hampir tanpa wilayah di tengah.</div></div>''')
    else:
        top10 = df_geo.nlargest(10, metric)[["provinsi", "kabupaten", metric]]
        reveal(f'''<div class="insight-card"><div class="kicker2">Yang mencolok</div>
        <div class="txt">Juara satunya <b>{top10.iloc[0]['kabupaten']}</b>,
        {top10.iloc[0]['provinsi']}, angkanya {idfmt(top10.iloc[0][metric])}.
        Tapi yang lebih menarik: <b>{top10['provinsi'].mode()[0]}</b> paling
        sering muncul di 10 besar, artinya sentra produksinya menyebar di banyak
        kabupaten/kota sekaligus, bukan menumpuk di satu titik saja.</div></div>''')

    st.caption(f"{n_match} dari {len(df_geo)} kab/kota ({n_match/len(df_geo)*100:.1f}%) cocok dengan batas wilayah digital; "
               f"{len(df_geo)-n_match} sisanya (mayoritas di Papua dan Papua Barat) tidak tergambar pada choropleth.")

    if is_choro:
        with st.expander("Jumlah kab/kota per kelas"):
            kelas_all, labels_all = classify(df_geo, metric)
            cnt = kelas_all.value_counts().reindex(labels_all + [NODATA], fill_value=0)
            st.dataframe(cnt.rename("Jumlah kab/kota").to_frame(), use_container_width=True)
    else:
        with st.expander("10 kab/kota teratas"):
            st.dataframe(df_geo.nlargest(10, metric)[["provinsi", "kabupaten", metric]], use_container_width=True)

# ===========================================================================
# TAB 3, ALIRAN
# ===========================================================================
if True:
    beat("Bab 3 \u00b7 Arus ekspor, 2012-2025", "Dari dermaga ke meja makan dunia",
         "Tidak semua ikan berhenti di pasar lokal. Hasil tangkapan puluhan provinsi (ekspor provinsi 2019-2026) berkumpul jadi ekspor Indonesia, lalu menyeberang ke negara tujuan (2012-2025). Geser tahunnya dan perhatikan: pita mana yang menebal, dan apakah pembeli terbesarnya selalu itu-itu saja.",
         "left", "3", "#009E73")

    years_common = sorted(set(df_prov_flow.tahun) & set(df_flow.tahun))
    tahun = st.select_slider("Pilih tahun", options=years_common, value=years_common[-1])

    beat("Tiga lapis perjalanan", "Satu pita, satu cerita",
         "Kiri provinsi pengirim, tengah Indonesia, kanan negara tujuan. Lebar pita adalah volume ekspor pada tahun terpilih, dalam ton. Arahkan kursor ke pita untuk melihat angkanya.",
         "right", "", "#0072B2")
    prov_y = df_prov_flow[(df_prov_flow.tahun == tahun) & (df_prov_flow.volume_ekspor_ton > 0)].copy()
    prov_y = prov_y.nlargest(25, "volume_ekspor_ton")
    neg_y = df_flow[(df_flow.tahun == tahun) & (df_flow.volume_ton > 0)].copy()

    nodes = prov_y["provinsi"].tolist() + ["Indonesia"] + neg_y["negara_tujuan"].tolist()
    node_idx = {n: i for i, n in enumerate(nodes)}
    idx_indonesia = node_idx["Indonesia"]
    node_colors = (["#56B4E9"] * len(prov_y) + ["#E69F00"] +
                   ["#0072B2" if n != "Lainnya" else "#B9C4CC" for n in neg_y["negara_tujuan"]])
    src = [node_idx[p] for p in prov_y["provinsi"]] + [idx_indonesia] * len(neg_y)
    tgt = [idx_indonesia] * len(prov_y) + [node_idx[n] for n in neg_y["negara_tujuan"]]
    val = prov_y["volume_ekspor_ton"].tolist() + neg_y["volume_ton"].tolist()

    sankey = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(label=nodes, pad=10, thickness=14, color=node_colors, line=dict(color="white", width=0.5)),
        link=dict(source=src, target=tgt, value=val, color="rgba(10,110,189,0.30)"),
    ))
    sankey.update_layout(title=f"Top 25 Provinsi \u2192 Indonesia \u2192 Negara Tujuan ({tahun})",
                          height=620, font_size=11)
    st.plotly_chart(clean(sankey), use_container_width=True)
    sumber(f"Ekspor provinsi 2019-2026 dan ekspor menurut negara tujuan 2012-2025; tahun tampil: {tahun}.")

    reveal("""
    <div class="note-card">Sisi provinsi dan sisi negara pada Sankey ini berasal dari dua tabel BPS
    dengan cakupan berbeda, jadi totalnya tidak otomatis sama. Lebar tautan hanya bermakna proporsional
    <i>di dalam</i> masing-masing sisi, bukan antar-sisi.</div>
    """)

    beat("Peta rute", "Separuh bumi di ujung garis",
         "Garis jingga ditarik dari Indonesia ke tiap negara tujuan. Makin tebal garis dan makin besar titik, makin besar volume ekspor pada tahun terpilih. Pembeli tetangga tampak pendek, pembeli jauh menempuh separuh bumi.",
         "left", "", "#D55E00")
    neg_globe = neg_y[neg_y.negara_tujuan != "Lainnya"]
    render_flowmap(neg_globe, tahun)
    st.caption("Garis tebal dan titik besar berarti volume ekspor besar. Arahkan kursor ke titik untuk angkanya.")

    tahun_terbaru_tren = sorted(df_flow.tahun.unique())[-1]
    beat("Pembeli setia, pembeli musiman", f"Tren 2012-{tahun_terbaru_tren}: siapa setia, siapa naik daun",
         "Lima negara teratas pada tahun pilihanmu dilacak mundur sampai 2012. Garis yang stabil menandakan pasar mapan. Lonjakan tiba-tiba layak ditanyakan: permintaan yang benar-benar naik, perubahan kebijakan, atau sekadar perubahan pencatatan.",
         "right", "", "#009E73")
    top5 = (neg_y[neg_y.negara_tujuan != "Lainnya"].nlargest(5, "volume_ton")["negara_tujuan"].tolist())
    trend_df = df_flow[df_flow.negara_tujuan.isin(top5)]
    line = (
        alt.Chart(trend_df).mark_line(point=True, strokeWidth=2.5)
        .encode(
            x=alt.X("tahun:O", title="Tahun"),
            y=alt.Y("volume_ton:Q", title="Volume ekspor (ton)"),
            color=alt.Color("negara_tujuan:N", scale=alt.Scale(range=blues), title="Negara"),
            tooltip=["negara_tujuan", "tahun", "volume_ton", "nilai_fob_ribu_usd"],
        ).properties(height=380)
    )
    st.altair_chart(line.configure(background="transparent").configure_view(strokeWidth=0), use_container_width=True)
    sumber("Ekspor menurut negara tujuan, 2012-2025.")

    years_all = sorted(df_flow.tahun.unique())
    growth = (trend_df[trend_df.tahun.isin([years_all[0], years_all[-1]])]
              .pivot(index="negara_tujuan", columns="tahun", values="volume_ton"))
    if years_all[0] in growth.columns and years_all[-1] in growth.columns:
        growth["pertumbuhan"] = growth[years_all[-1]] - growth[years_all[0]]
        naik = growth["pertumbuhan"].idxmax()
        reveal(f"""
        <div class="insight-card"><div class="kicker2">Patut digarisbawahi</div>
        <div class="txt">Dari 5 besar {tahun}, <b>{naik}</b> yang paling
        melesat sejak {years_all[0]}, naik {idfmt(growth.loc[naik,'pertumbuhan'])}
        ton. Pertanyaannya: ini tren jangka panjang atau cuma lonjakan sesaat?</div></div>
        """)

    

st.markdown(DIVIDER_SVG, unsafe_allow_html=True)
_y = sorted(df_flow.tahun.unique())
_t0 = df_flow[df_flow.tahun == _y[0]].volume_ton.sum(); _t1 = df_flow[df_flow.tahun == _y[-1]].volume_ton.sum()
_share = df_geo.nlargest(10, "produksi_perikanan_tangkap_kg")["produksi_perikanan_tangkap_kg"].sum() / df_geo["produksi_perikanan_tangkap_kg"].sum() * 100
_k = df_geo.loc[df_geo.produksi_perikanan_tangkap_kg.idxmax()]
beat("Kesimpulan", "Jejak laut kita lebih dari sekadar berapa banyak ikan ditangkap",
     "Tiga hal yang kita temukan sepanjang perjalanan ini, dari provinsi, kabupaten/kota, sampai pelabuhan di seberang samudra.",
     "left", "", "#0072B2")
c1, c2, c3 = st.columns(3)
with c1:
    beat("Provinsi (2024/2025)", "Ukuran armada bukan ukuran ekspor",
         f"{top_nelayan['provinsi']} punya nelayan terbanyak, tetapi {top_ekspor['provinsi']} memimpin ekspor 2025. Delapan indikator provinsi membentuk klaster yang berbeda-beda: ada raksasa serba besar, ada spesialis.",
         "left", f"{len(set(df_mv.klaster))}", "#0072B2")
with c2:
    beat("Kab/kota (2024)", "Produksi menumpuk di segelintir daerah",
         f"Sepuluh dari 514 kabupaten/kota menyumbang {_share:.0f}% produksi tangkap nasional. Yang teratas {_k['kabupaten']}, {_k['provinsi']}. Rata-rata provinsi menyembunyikan ketimpangan di dalamnya.",
         "left", f"{_share:.0f}%", "#E69F00")
with c3:
    beat(f"Ekspor ({_y[0]}-{_y[-1]})", "Pasar tujuan terus bergeser",
         f"Total ekspor ke negara tujuan berubah {(_t1/_t0-1)*100:+.0f}% dari {_y[0]} ke {_y[-1]}, dengan {negara_top['negara_tujuan']} sebagai pembeli terbesar di {tahun_terakhir}. Pasar yang bergantung pada sedikit negara rentan terhadap perubahan permintaan.",
         "left", f"{(_t1/_t0-1)*100:+.0f}%", "#009E73")

st.markdown('<p style="text-align:center;font-weight:600;color:#04385C;">JALA \u2014 Jejak Laut Indonesia</p>', unsafe_allow_html=True)
