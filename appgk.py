import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import re
import os
import pickle
import io
import tempfile
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak, KeepTogether, HRFlowable

# Logo dell'associazione, incorporato direttamente nel codice (base64) cosicche' non
# serva gestire un file immagine separato: appare su ogni pagina dei PDF esportati.
LOGO_BASE64 = (
    "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"
    "NT/rv//Z"
)
LOGO_BYTES = base64.b64decode(LOGO_BASE64)



st.set_page_config(
    page_title="Goalkeeper Performance Analytics",
    page_icon=PILImage.open(io.BytesIO(LOGO_BYTES)),
    layout="wide"
)

# ============================================================
# CODICE DI ACCESSO PER CARICARE FILE / GESTIRE LA STAGIONE
# Chi conosce questo codice può caricare partite e usare "Reset Season".
# Chi non lo conosce può comunque vedere liberamente Single Game Analysis
# e Seasonal Report. Cambia questo valore quando vuoi (es. a inizio stagione).
# ============================================================
UPLOAD_ACCESS_CODE = "gkmethod2026"

APP_VERSION = "v25 - 2026-08-21 - Fix: grafico timeline non impila più i tiri quando la colonna Timeline è vuota (etichette sempre uniche)"
st.sidebar.caption(f"🔧 App version: {APP_VERSION}")
st.sidebar.caption("If you don't see this version, the app hasn't been restarted correctly.")

st.title("🤾‍♂️ Goalkeeper Performance Index Analytics")
st.markdown("Upload Excel sheets exported from *Videocoach (Sportimization)* to generate tactical charts and reports.")

# 1. PARSING FUNCTIONS & LOGIC
def mappa_macro_settore(s):
    s_str = str(s).lower().strip()
    for m in ['7m', 'lw', 'rw', '6m', 'bt', '9m', 'fb']:
        if s_str.startswith(m):
            return m
    return None

def analizza_timeline(timeline_str):
    if pd.isna(timeline_str) or str(timeline_str).strip().lower() in ('', 'none', 'nan'):
        return 0, "", 0, "0-0"

    t_str = str(timeline_str).strip()
    minuti_totali = 0
    scarto = 0
    punteggio_pulito = "0-0"
    
    try:
        match_tempo = re.search(r"(\d+)'", t_str)
        if match_tempo:
            minuti_totali = int(match_tempo.group(1))
            
        match_punti = re.findall(r"(\d+)\s*-\s*(\d+)", t_str)
        if match_punti:
            pts = match_punti[-1]
            p1, p2 = int(pts[0]), int(pts[1])
            scarto = p1 - p2
            punteggio_pulito = f"{p1}-{p2}"
    except:
        pass
    return minuti_totali, t_str, scarto, punteggio_pulito

def calcola_gpi_riga(macro, esito, minuti, scarto):
    e = str(esito).lower().strip()
    # Money Time = SOLO dal minuto 50'00'' in avanti (soglia fissa), con scarto punteggio tra -5 e +5
    is_money_time = (minuti >= 50) and (-5 <= scarto <= 5)
    
    punti = 0.0
    if e in ['goal', 'g']:
        punti = -1.5 if macro == '9m' else -1.0
    elif e in ['save', 's']:
        punti = 1.5 if macro == '9m' else 2.0
    elif e in ['miss', 'm']:
        punti = 2.0 if macro in ['7m', 'lw', 'rw', 'fb'] else 0.0
        
    if is_money_time:
        if punti > 0: punti += 0.5
        elif punti < 0: punti -= 0.5
    return punti, is_money_time

ORDINE_BLOCCHI = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60']

def calcola_metriche_gruppo(df_gruppo):
    if df_gruppo.empty:
        return 0, 0, 0, 0.0, 0.0
    s = len(df_gruppo[df_gruppo['RESULT_CLEAN'].isin(['save', 's'])])
    g = len(df_gruppo[df_gruppo['RESULT_CLEAN'].isin(['goal', 'g'])])
    m = len(df_gruppo[df_gruppo['RESULT_CLEAN'].isin(['miss', 'm'])])
    
    tot_tiri_specchio = s + g
    tot_tiri_subiti = s + g + m
    
    pct = (s / tot_tiri_specchio * 100) if tot_tiri_specchio > 0 else 0.0
    eff = ((s + m) / tot_tiri_subiti * 100) if tot_tiri_subiti > 0 else 0.0
    
    return s, g, m, pct, eff

# ============================================================
# RACCOLTA DATI STAGIONALI (per portiere e per squadra)
# ============================================================
def raccogli_stagione_per_portiere(elenco_partite, nome_portiere):
    """Scorre l'elenco di partite (in ordine cronologico) e raccoglie, per il portiere indicato,
    solo le partite in cui ha effettivamente affrontato almeno un tiro. Le partite in cui non è
    sceso in campo vengono escluse (non contano come 0)."""
    partite_ordinate = sorted(elenco_partite, key=lambda p: p['data'])
    frammenti = []
    lista_partite = []
    for match in partite_ordinate:
        df_m = match['dati']
        df_gk = df_m[df_m['PORTIERE_CLEAN'] == nome_portiere]
        if df_gk.empty:
            continue
        s, g, m_, pct, eff = calcola_metriche_gruppo(df_gk)
        df_gk_stress = df_gk[df_gk['Is_Stress_Test'] == True]
        gpi_money_time = df_gk_stress['GPI_Tiro'].sum() if not df_gk_stress.empty else None
        frammenti.append(df_gk)
        lista_partite.append({
            'label': f"{match['nome']} ({match['data']})",
            'data': match['data'],
            'gpi_totale': df_gk['GPI_Tiro'].sum(),
            'pct': pct,
            'eff': eff,
            'tiri': len(df_gk),
            'money_time_gpi': gpi_money_time
        })
    df_aggregato = pd.concat(frammenti, ignore_index=True) if frammenti else pd.DataFrame()
    return df_aggregato, lista_partite

def raccogli_stagione_per_squadra(elenco_partite, nome_squadra):
    """Filtra le partite della squadra indicata e raccoglie, per ciascun portiere che vi ha giocato,
    il proprio storico stagionale (stessa logica di raccogli_stagione_per_portiere)."""
    partite_squadra = sorted([p for p in elenco_partite if p['squadra'] == nome_squadra], key=lambda p: p['data'])
    frammenti = [m['dati'] for m in partite_squadra]
    df_aggregato = pd.concat(frammenti, ignore_index=True) if frammenti else pd.DataFrame()

    portieri_unici = sorted(set(
        gk for m in partite_squadra for gk in m['dati']['PORTIERE_CLEAN'].dropna().unique()
    ))
    dati_per_portiere = {}
    for gk in portieri_unici:
        _, lista_partite_gk = raccogli_stagione_per_portiere(partite_squadra, gk)
        dati_per_portiere[gk] = lista_partite_gk
    return df_aggregato, dati_per_portiere

def calcola_media_money_time_per_partita(lista_partite):
    """Media dei GPI TOTALI di Money Time calcolati partita per partita (non media per singolo tiro).
    Esempio: +2 in una partita, +1 nella successiva -> media 1.5. Le partite senza tiri in
    Money Time vengono escluse dalla media (non contano come 0)."""
    valori = [p['money_time_gpi'] for p in (lista_partite or []) if p.get('money_time_gpi') is not None]
    if not valori:
        return None, 0
    return sum(valori) / len(valori), len(valori)

def calcola_dettaglio_portiere(df_gk, lista_partite=None):
    """Calcola, per un insieme di tiri di un portiere (una partita o l'intera stagione),
    tutte le statistiche di dettaglio: per settore specifico, per macro-settore, Money Time.
    Se lista_partite è fornita (contesto stagionale, una voce per partita), il GPI medio di
    Money Time viene calcolato come media dei totali PER PARTITA; altrimenti (singola partita,
    lista_partite=None) coincide semplicemente con il totale di quella partita."""
    s, g, m_, pct, eff = calcola_metriche_gruppo(df_gk)
    gpi_totale = df_gk['GPI_Tiro'].sum() if not df_gk.empty else 0.0

    righe_settore = []
    for settore in sorted(df_gk['TIRO_CLEAN'].dropna().unique()):
        df_s = df_gk[df_gk['TIRO_CLEAN'] == settore]
        s2, g2, m2, pct2, eff2 = calcola_metriche_gruppo(df_s)
        righe_settore.append({
            'Zone': settore, 'Saves': s2, 'Goals': g2, 'Miss': m2,
            'Save %': round(pct2, 1), 'Efficiency %': round(eff2, 1),
            'GPI': round(df_s['GPI_Tiro'].sum(), 1)
        })

    righe_macro = []
    for macro in sorted(df_gk['macro_settore'].dropna().unique()):
        df_ma = df_gk[df_gk['macro_settore'] == macro]
        s3, g3, m3, pct3, eff3 = calcola_metriche_gruppo(df_ma)
        righe_macro.append({
            'Macro-Zone': macro.upper(), 'Saves': s3, 'Goals': g3, 'Miss': m3,
            'Save %': round(pct3, 1), 'Efficiency %': round(eff3, 1),
            'GPI': round(df_ma['GPI_Tiro'].sum(), 1)
        })

    df_stress = df_gk[df_gk['Is_Stress_Test'] == True]
    pct_su_totale_tiri = (len(df_stress) / len(df_gk) * 100) if len(df_gk) > 0 else 0.0
    if not df_stress.empty:
        s4, g4, m4, pct4, eff4 = calcola_metriche_gruppo(df_stress)
        if lista_partite is not None:
            media_mt, n_partite_mt = calcola_media_money_time_per_partita(lista_partite)
            testo_media = (f"Average GPI per Match {media_mt:+.2f} (across {n_partite_mt} matches with Money Time shots)"
                           if media_mt is not None else "Average GPI per Match: n/a")
        else:
            testo_media = f"Total Match GPI {df_stress['GPI_Tiro'].sum():+.2f}"
        money_time_riassunto = (
            f"{len(df_stress)} shots ({pct_su_totale_tiri:.1f}% of total shots), "
            f"{s4} saves, {g4} goals, Save % {pct4:.1f}%, {testo_media}"
        )
    else:
        money_time_riassunto = "No shots in Money Time"

    return {
        'gpi_totale': gpi_totale, 'parate': s, 'gol': g, 'pct': pct, 'eff': eff,
        'tabella_settore': pd.DataFrame(righe_settore) if righe_settore else pd.DataFrame({'Zone': [], 'GPI': []}),
        'tabella_macro': pd.DataFrame(righe_macro) if righe_macro else pd.DataFrame({'Macro-Zone': [], 'GPI': []}),
        'money_time_riassunto': money_time_riassunto
    }

def costruisci_grafico_blocchi(df_aggregato, altezza=520):
    """Costruisce la tabella e il grafico a blocchi da 10 minuti (linea % + barre GPI, 2 pannelli)
    per un qualsiasi insieme di tiri (una partita o l'intera stagione)."""
    righe_blocchi = []
    for blocco in ORDINE_BLOCCHI:
        df_b = df_aggregato[df_aggregato['Blocco_10m'] == blocco] if not df_aggregato.empty else pd.DataFrame()
        s_b, g_b, m_b, pct_b, eff_b = calcola_metriche_gruppo(df_b)
        gpi_b = df_b['GPI_Tiro'].sum() if not df_b.empty else 0.0
        righe_blocchi.append({
            'Block': blocco, 'Save %': round(pct_b, 1), 'Total GPI': round(gpi_b, 1),
            'Shots': len(df_b)
        })
    df_blocchi = pd.DataFrame(righe_blocchi)

    max_gpi_abs = max(df_blocchi['Total GPI'].abs().max(), 1)
    y_top_gpi = max_gpi_abs * 1.35
    y_bottom_gpi = -max_gpi_abs * 1.35
    y_bottom_pct = 6

    fig_blocchi = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12,
        row_heights=[0.5, 0.5],
        subplot_titles=("Save % per block", "Total GPI per block")
    )
    fig_blocchi.add_trace(
        go.Scatter(x=df_blocchi['Block'], y=df_blocchi['Save %'], name='Save %',
                   mode='lines+markers', line=dict(color='#1f77b4', width=3),
                   marker=dict(size=10, color='#1f77b4'), showlegend=False),
        row=1, col=1
    )
    fig_blocchi.add_trace(
        go.Scatter(x=df_blocchi['Block'], y=[y_bottom_pct] * len(df_blocchi), mode='text',
                   text=df_blocchi['Save %'].apply(lambda x: f"{x:.0f}%"),
                   textfont=dict(color='#1f77b4', size=13), showlegend=False),
        row=1, col=1
    )
    fig_blocchi.add_trace(
        go.Bar(x=df_blocchi['Block'], y=df_blocchi['Total GPI'], name='Total GPI',
               marker_color='#ff7f0e', width=0.5, showlegend=False),
        row=2, col=1
    )
    fig_blocchi.add_trace(
        go.Scatter(x=df_blocchi['Block'], y=[y_top_gpi] * len(df_blocchi), mode='text',
                   text=df_blocchi['Total GPI'].apply(lambda x: f"{x:+.1f}"),
                   textfont=dict(color='#ff7f0e', size=13), showlegend=False),
        row=2, col=1
    )
    fig_blocchi.update_layout(
        height=altezza, plot_bgcolor='white', margin=dict(t=50, b=40, l=40, r=40)
    )
    fig_blocchi.update_yaxes(title_text="Save %", range=[0, 115], row=1, col=1)
    fig_blocchi.update_yaxes(title_text="Total GPI", range=[y_bottom_gpi * 1.15, y_top_gpi * 1.15], row=2, col=1)
    fig_blocchi.update_xaxes(title_text="Game block (minutes)", row=2, col=1)
    return df_blocchi, fig_blocchi

def _disegna_grafico_stagione(dati_per_portiere, chiave_valore, etichetta_y, output_path):
    """Disegna, per ciascun portiere, l'andamento del valore (GPI o %) partita per partita,
    integrato con la linea della media cumulativa stagionale (ricalcolata partita dopo partita).
    Le partite in cui il portiere non ha giocato sono già escluse a monte.
    L'asse orizzontale mostra il nome reale di ogni partita (ordine cronologico unificato tra
    tutti i portieri coinvolti, cosicché in modalità squadra ogni punto cada sulla partita giusta)."""
    partita_per_data = {}
    for lista in dati_per_portiere.values():
        for p in lista:
            partita_per_data[p['label']] = p['data']
    if not partita_per_data:
        return False
    etichette_ordinate = sorted(partita_per_data.keys(), key=lambda lbl: partita_per_data[lbl])
    posizione = {lbl: i for i, lbl in enumerate(etichette_ordinate)}

    palette = ['#15304f', '#d62728', '#2ca02c', '#ff7f0e', '#9467bd', '#8c564b', '#17becf', '#e377c2']
    larghezza_pollici = max(7, len(etichette_ordinate) * 0.5)
    fig, ax = plt.subplots(figsize=(larghezza_pollici, 4.3), dpi=140)

    for idx, (gk, lista) in enumerate(dati_per_portiere.items()):
        if not lista:
            continue
        colore = palette[idx % len(palette)]
        x = [posizione[p['label']] for p in lista]
        valori = [p[chiave_valore] for p in lista]
        medie_cumulative = np.cumsum(valori) / np.arange(1, len(valori) + 1)
        ax.plot(x, valori, marker='o', color=colore, linewidth=2, markersize=7, label=f'{gk} — per match')
        ax.plot(x, medie_cumulative, linestyle='--', color=colore, linewidth=1.8, alpha=0.65,
                label=f'{gk} — cumulative average')

    ax.set_xlabel('Match', fontsize=11)
    ax.set_ylabel(etichetta_y, fontsize=11)
    ax.set_xticks(range(len(etichette_ordinate)))
    ax.set_xticklabels(etichette_ordinate, rotation=90, fontsize=9)
    ax.axhline(0, color='black', linewidth=1.2, alpha=0.5)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close(fig)
    return True

# ============================================================
# GENERAZIONE PDF (report singola partita)
# ============================================================
def _disegna_grafico_timeline_pdf(df_match, output_path):
    """Disegna il grafico GPI/timeline completo (un unico grafico, non spezzato) con Matplotlib,
    usando bbox_inches='tight' cosicché l'immagine si espanda automaticamente quanto serve
    per contenere ogni etichetta: nessun taglio, indipendentemente dal numero di tiri."""
    n = len(df_match)
    x_labels = df_match['Label_Asse_X'].values
    y_values = df_match['GPI_Progressivo_Disegno'].values
    gpi_tiro = df_match['GPI_Tiro'].values
    is_stress = df_match['Is_Stress_Test'].values

    colori_punti = []
    marker_shapes = []
    for i in range(n):
        if is_stress[i]:
            colori_punti.append('#ffcc00')
        elif gpi_tiro[i] >= 0:
            colori_punti.append('#2ca02c')
        else:
            colori_punti.append('#d62728')
        marker_shapes.append('s' if is_stress[i] else 'o')

    larghezza_pollici = max(14, n * 0.42)
    fig, ax = plt.subplots(figsize=(larghezza_pollici, 6.5), dpi=150)

    x = list(range(n))
    ax.plot(x, y_values, color='lightgray', linewidth=2, zorder=1)
    for i in range(n):
        ax.scatter(x[i], y_values[i], color=colori_punti[i], marker=marker_shapes[i],
                   s=170, zorder=3, edgecolors='none')
        testo = f"+{gpi_tiro[i]:g}" if gpi_tiro[i] > 0 else f"{gpi_tiro[i]:g}"
        ax.annotate(testo, (x[i], y_values[i]), textcoords='offset points', xytext=(0, 9),
                    ha='center', fontsize=10, fontweight='bold', color='black')

    ax.axhline(0, color='black', linewidth=3, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=90, fontsize=9)
    ax.set_ylabel('Progressive GPI Valuation Index', fontsize=11)
    ax.set_xlim(-0.5, n - 0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    fig.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close(fig)

COLORE_ACCENTO = colors.HexColor('#15304f')
COLORE_TESTATA_TABELLE = colors.HexColor('#1b3a63')

def _df_to_reportlab_table(df_in, col_widths=None, font_size=8):
    dati = [list(df_in.columns)] + df_in.astype(str).values.tolist()
    t = Table(dati, colWidths=col_widths, repeatRows=1)
    stile = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORE_TESTATA_TABELLE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), font_size),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ])
    t.setStyle(stile)
    return t

def _dimensioni_adattate(larghezza_px, altezza_px, max_larghezza_cm, max_altezza_cm):
    """Calcola le dimensioni (in cm) per stare dentro un riquadro massimo, mantenendo le proporzioni originali."""
    scala = min(max_larghezza_cm / larghezza_px, max_altezza_cm / altezza_px)
    return larghezza_px * scala, altezza_px * scala

def _pie_pagina(canvas_obj, doc_obj):
    """Disegna intestazione (linea colorata + logo) e piè di pagina (numero pagina) su ogni pagina."""
    canvas_obj.saveState()
    larghezza_pagina, altezza_pagina = doc_obj.pagesize
    dimensione_logo = 1.15*cm
    y_linea = altezza_pagina - 0.9*cm

    canvas_obj.setStrokeColor(COLORE_ACCENTO)
    canvas_obj.setLineWidth(2)
    canvas_obj.line(1.2*cm, y_linea, larghezza_pagina - 1.4*cm - dimensione_logo, y_linea)

    canvas_obj.drawImage(
        ImageReader(io.BytesIO(LOGO_BYTES)),
        larghezza_pagina - 1.2*cm - dimensione_logo, y_linea - dimensione_logo/2,
        width=dimensione_logo, height=dimensione_logo, mask='auto', preserveAspectRatio=True
    )

    canvas_obj.setFont('Helvetica', 8)
    canvas_obj.setFillColor(colors.grey)
    canvas_obj.drawString(1.2*cm, 0.7*cm, "Goalkeeper Method  •  Goalkeeper Performance Index Analytics")
    canvas_obj.drawRightString(larghezza_pagina - 1.2*cm, 0.7*cm, f"Page {doc_obj.page}")
    canvas_obj.restoreState()

def _separatore():
    return HRFlowable(width="100%", thickness=1, color=colors.HexColor('#dcdcdc'),
                       spaceBefore=10, spaceAfter=10)

def genera_pdf_partita(titolo_partita, righe_gpi_totale, tabella_sequenza, dati_portieri, df_blocchi, df_match, fig_blocchi):
    """Costruisce il PDF completo della pagina Single Game Analysis e lo restituisce come bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=1.6*cm, bottomMargin=1.4*cm,
                             leftMargin=1.2*cm, rightMargin=1.2*cm)
    stili = getSampleStyleSheet()
    titolo_stile = ParagraphStyle('TitoloReport', parent=stili['Title'], fontSize=20,
                                   textColor=COLORE_ACCENTO, spaceAfter=2)
    sottotitolo_stile = ParagraphStyle('Sottotitolo', parent=stili['Heading3'], fontSize=13,
                                        textColor=colors.HexColor('#555555'))
    sezione_stile = ParagraphStyle('Sezione', parent=stili['Heading2'], spaceBefore=4, spaceAfter=6,
                                    textColor=COLORE_ACCENTO)
    elementi = []

    dimensione_logo_copertina = 2.6*cm
    blocco_titolo = Table(
        [[RLImage(io.BytesIO(LOGO_BYTES), width=dimensione_logo_copertina, height=dimensione_logo_copertina),
          [Paragraph("GOALKEEPER PERFORMANCE REPORT", titolo_stile),
           Paragraph(titolo_partita, sottotitolo_stile)]]],
        colWidths=[dimensione_logo_copertina + 0.4*cm, None]
    )
    blocco_titolo.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elementi.append(blocco_titolo)
    elementi.append(Spacer(1, 0.5*cm))

    # Total GPI per goalkeeper
    df_gpi = pd.DataFrame(righe_gpi_totale)
    elementi.append(KeepTogether([
        Paragraph("Total Match GPI per Goalkeeper", sezione_stile),
        _df_to_reportlab_table(df_gpi)
    ]))
    elementi.append(_separatore())

    # Main chart (GPI/timeline line) — single chart, drawn with Matplotlib
    # to guarantee no label is ever cut off (bbox_inches='tight').
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_linee:
        _disegna_grafico_timeline_pdf(df_match, tmp_linee.name)
        larghezza_px, altezza_px = PILImage.open(tmp_linee.name).size
        larghezza_pdf_cm, altezza_pdf_cm = _dimensioni_adattate(larghezza_px, altezza_px, 25.5, 9.0)
        elementi.append(KeepTogether([
            Paragraph("Progressive GPI Trend", sezione_stile),
            RLImage(tmp_linee.name, width=larghezza_pdf_cm*cm, height=altezza_pdf_cm*cm)
        ]))
    elementi.append(_separatore())

    # Chronological shot sequence — starts right after (no wasted blank page),
    # the table automatically continues onto the following pages if needed.
    elementi.append(KeepTogether([
        Paragraph("Chronological Shot Sequence", sezione_stile),
        Spacer(1, 0.15*cm)
    ]))
    elementi.append(_df_to_reportlab_table(tabella_sequenza, font_size=7))
    elementi.append(_separatore())

    # Detailed statistics per goalkeeper
    for gk, info in dati_portieri.items():
        elementi.append(KeepTogether([
            Paragraph(f"Detailed Statistics — {gk}", sezione_stile),
            Paragraph(
                f"Total GPI: {info['gpi_totale']:+.1f}   |   Saves: {info['parate']}   |   "
                f"Goals Conceded: {info['gol']}   |   Save %: {info['pct']:.1f}%   |   Efficiency: {info['eff']:.1f}%",
                stili['Normal']
            ),
            Spacer(1, 0.2*cm),
            Paragraph("By specific shot zone", stili['Heading4']),
        ]))
        elementi.append(_df_to_reportlab_table(info['tabella_settore'], font_size=7))
        elementi.append(Spacer(1, 0.2*cm))
        elementi.append(KeepTogether([
            Paragraph("By aggregated macro-zone", stili['Heading4']),
        ]))
        elementi.append(_df_to_reportlab_table(info['tabella_macro'], font_size=7))
        elementi.append(Spacer(1, 0.2*cm))
        elementi.append(Paragraph(
            f"Money Time (from the 50th minute onward, score margin between -5 and +5): {info['money_time_riassunto']}", stili['Normal']
        ))
        elementi.append(_separatore())

    # 10-minute block performance
    larghezza_blocchi_px, altezza_blocchi_px = 1300, 750
    fig_export_blocchi = go.Figure(fig_blocchi)
    fig_export_blocchi.update_layout(width=larghezza_blocchi_px, height=altezza_blocchi_px)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_blocchi:
        fig_export_blocchi.write_image(tmp_blocchi.name, scale=2)
        larghezza_blocchi_cm, altezza_blocchi_cm = _dimensioni_adattate(larghezza_blocchi_px, altezza_blocchi_px, 16, 9)
        elementi.append(KeepTogether([
            Paragraph("Performance by 10-Minute Blocks", sezione_stile),
            RLImage(tmp_blocchi.name, width=larghezza_blocchi_cm*cm, height=altezza_blocchi_cm*cm)
        ]))
    elementi.append(Spacer(1, 0.3*cm))
    elementi.append(_df_to_reportlab_table(df_blocchi))

    doc.build(elementi, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buffer.seek(0)
    return buffer.getvalue()

def genera_pdf_stagione(titolo_report, righe_gpi_stagione, df_storico, dati_portieri, df_blocchi, df_stagione_totale, fig_blocchi):
    """Costruisce il PDF del report stagionale (portiere singolo o squadra) e lo restituisce come bytes.
    Stessa identità grafica (logo, colori, footer) del report di partita singola."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=1.6*cm, bottomMargin=1.4*cm,
                             leftMargin=1.2*cm, rightMargin=1.2*cm)
    stili = getSampleStyleSheet()
    titolo_stile = ParagraphStyle('TitoloReportStagione', parent=stili['Title'], fontSize=20,
                                   textColor=COLORE_ACCENTO, spaceAfter=2)
    sottotitolo_stile = ParagraphStyle('SottotitoloStagione', parent=stili['Heading3'], fontSize=13,
                                        textColor=colors.HexColor('#555555'))
    sezione_stile = ParagraphStyle('SezioneStagione', parent=stili['Heading2'], spaceBefore=4, spaceAfter=6,
                                    textColor=COLORE_ACCENTO)
    elementi = []

    dimensione_logo_copertina = 2.6*cm
    blocco_titolo = Table(
        [[RLImage(io.BytesIO(LOGO_BYTES), width=dimensione_logo_copertina, height=dimensione_logo_copertina),
          [Paragraph("GOALKEEPER SEASONAL REPORT", titolo_stile),
           Paragraph(titolo_report, sottotitolo_stile)]]],
        colWidths=[dimensione_logo_copertina + 0.4*cm, None]
    )
    blocco_titolo.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elementi.append(blocco_titolo)
    elementi.append(Spacer(1, 0.5*cm))

    # Total season statistics
    s_tot, g_tot, m_tot, pct_tot, eff_tot = calcola_metriche_gruppo(df_stagione_totale)
    gpi_medio_tot = df_stagione_totale['GPI_Tiro'].mean() if not df_stagione_totale.empty else 0.0
    numero_partite_coinvolte = len(set(p['label'] for lista in dati_portieri.values() for p in lista))
    media_cumulativa_gpi = (df_stagione_totale['GPI_Tiro'].sum() / numero_partite_coinvolte) if numero_partite_coinvolte > 0 else 0.0
    elementi.append(KeepTogether([
        Paragraph("Total Season Statistics", sezione_stile),
        Paragraph(
            f"Shots Faced: {len(df_stagione_totale)}   |   Saves: {s_tot}   |   "
            f"Goals Conceded: {g_tot}   |   Save %: {pct_tot:.1f}%   |   Average GPI (per shot): {gpi_medio_tot:+.2f}   |   "
            f"Cumulative Average GPI (per match): {media_cumulativa_gpi:+.2f}",
            stili['Normal']
        )
    ]))
    elementi.append(_separatore())

    # Total season GPI per goalkeeper
    df_gpi = pd.DataFrame(righe_gpi_stagione)
    elementi.append(KeepTogether([
        Paragraph("Total Season GPI per Goalkeeper", sezione_stile),
        _df_to_reportlab_table(df_gpi)
    ]))
    elementi.append(_separatore())

    # Season GPI trend chart
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_gpi:
        _disegna_grafico_stagione(dati_portieri, 'gpi_totale', 'Total Match GPI', tmp_gpi.name)
        larghezza_px, altezza_px = PILImage.open(tmp_gpi.name).size
        larghezza_pdf_cm, altezza_pdf_cm = _dimensioni_adattate(larghezza_px, altezza_px, 25.5, 9.0)
        elementi.append(KeepTogether([
            Paragraph("Season GPI Trend (per match + cumulative average)", sezione_stile),
            RLImage(tmp_gpi.name, width=larghezza_pdf_cm*cm, height=altezza_pdf_cm*cm)
        ]))
    elementi.append(_separatore())

    # Season save % trend chart
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_pct:
        _disegna_grafico_stagione(dati_portieri, 'pct', 'Match Save %', tmp_pct.name)
        larghezza_px, altezza_px = PILImage.open(tmp_pct.name).size
        larghezza_pdf_cm, altezza_pdf_cm = _dimensioni_adattate(larghezza_px, altezza_px, 25.5, 9.0)
        elementi.append(KeepTogether([
            Paragraph("Season Save % Trend (per match + cumulative average)", sezione_stile),
            RLImage(tmp_pct.name, width=larghezza_pdf_cm*cm, height=altezza_pdf_cm*cm)
        ]))
    elementi.append(_separatore())

    # Match history
    elementi.append(KeepTogether([
        Paragraph("Match History", sezione_stile),
        Spacer(1, 0.15*cm)
    ]))
    elementi.append(_df_to_reportlab_table(df_storico, font_size=7))
    elementi.append(_separatore())

    # Detailed statistics per goalkeeper (season cumulative)
    for gk, lista in dati_portieri.items():
        df_gk_tot = df_stagione_totale[df_stagione_totale['PORTIERE_CLEAN'] == gk]
        if df_gk_tot.empty:
            continue
        info = calcola_dettaglio_portiere(df_gk_tot, lista_partite=lista)
        elementi.append(KeepTogether([
            Paragraph(f"Detailed Season Statistics — {gk}", sezione_stile),
            Paragraph(
                f"Total Season GPI: {info['gpi_totale']:+.1f}   |   Saves: {info['parate']}   |   "
                f"Goals Conceded: {info['gol']}   |   Save %: {info['pct']:.1f}%   |   Efficiency: {info['eff']:.1f}%",
                stili['Normal']
            ),
            Spacer(1, 0.2*cm),
            Paragraph("By specific shot zone", stili['Heading4']),
        ]))
        elementi.append(_df_to_reportlab_table(info['tabella_settore'], font_size=7))
        elementi.append(Spacer(1, 0.2*cm))
        elementi.append(KeepTogether([
            Paragraph("By aggregated macro-zone", stili['Heading4']),
        ]))
        elementi.append(_df_to_reportlab_table(info['tabella_macro'], font_size=7))
        elementi.append(Spacer(1, 0.2*cm))
        elementi.append(Paragraph(
            f"Money Time (from the 50th minute onward, score margin between -5 and +5): {info['money_time_riassunto']}", stili['Normal']
        ))
        elementi.append(_separatore())

    # 10-minute block performance (season cumulative)
    larghezza_blocchi_px, altezza_blocchi_px = 1300, 750
    fig_export_blocchi = go.Figure(fig_blocchi)
    fig_export_blocchi.update_layout(width=larghezza_blocchi_px, height=altezza_blocchi_px)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_blocchi:
        fig_export_blocchi.write_image(tmp_blocchi.name, scale=2)
        larghezza_blocchi_cm, altezza_blocchi_cm = _dimensioni_adattate(larghezza_blocchi_px, altezza_blocchi_px, 16, 9)
        elementi.append(KeepTogether([
            Paragraph("Performance by 10-Minute Blocks (season cumulative)", sezione_stile),
            RLImage(tmp_blocchi.name, width=larghezza_blocchi_cm*cm, height=altezza_blocchi_cm*cm)
        ]))
    elementi.append(Spacer(1, 0.3*cm))
    elementi.append(_df_to_reportlab_table(df_blocchi))

    doc.build(elementi, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buffer.seek(0)
    return buffer.getvalue()


# I dati di tutte le partite caricate restano salvati anche se l'app viene
# chiusa e riaperta, finché non si preme "Reset Season". Se sono configurati
# i Secrets di Google (season_sheet_id + gcp_service_account), i dati vengono
# salvati su Google Sheets (permanenti, indipendenti dal server dell'app).
# Altrimenti si usa un file locale come riserva (utile per test in locale).
# ============================================================
SEASON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "season_data.pkl")
GOOGLE_SHEETS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
GOOGLE_SHEETS_HEADER = ['nome', 'data', 'squadra', 'dati_json']

def _google_sheets_configurato():
    try:
        return 'gcp_service_account' in st.secrets and 'season_sheet_id' in st.secrets
    except Exception:
        return False

def _diagnosi_google_sheets():
    """Restituisce una breve spiegazione di cosa manca nella configurazione, per aiutare il debug."""
    try:
        chiavi_presenti = list(st.secrets.keys())
    except Exception as e:
        return f"Secrets not readable at all ({e}). Are they saved in the app's Settings > Secrets?"
    if not chiavi_presenti:
        return "Secrets are empty. Nothing was saved in Settings > Secrets."
    mancanti = []
    if 'season_sheet_id' not in chiavi_presenti:
        mancanti.append('season_sheet_id')
    if 'gcp_service_account' not in chiavi_presenti:
        mancanti.append('[gcp_service_account]')
    if mancanti:
        return f"Found these keys: {chiavi_presenti}. Missing: {', '.join(mancanti)}."
    return "Configuration looks present but something else is failing (see error above, if any)."

@st.cache_resource
def _ottieni_worksheet_stagione():
    import gspread
    from google.oauth2.service_account import Credentials
    credenziali = Credentials.from_service_account_info(
        dict(st.secrets['gcp_service_account']), scopes=GOOGLE_SHEETS_SCOPES
    )
    client = gspread.authorize(credenziali)
    foglio = client.open_by_key(st.secrets['season_sheet_id'])
    try:
        worksheet = foglio.worksheet('SeasonData')
    except Exception:
        worksheet = foglio.add_worksheet(title='SeasonData', rows=2000, cols=4)
        worksheet.append_row(GOOGLE_SHEETS_HEADER)
    return worksheet

def _match_a_riga_sheet(match):
    return [match['nome'], str(match['data']), match['squadra'],
            match['dati'].to_json(orient='split', date_format='iso')]

def _riga_sheet_a_match(riga):
    from datetime import datetime as _dt
    nome, data_str, squadra, dati_json = riga[0], riga[1], riga[2], riga[3]
    df = pd.read_json(io.StringIO(dati_json), orient='split')
    if 'GPI_Tiro' in df.columns:
        df['GPI_Tiro'] = df['GPI_Tiro'].astype(float)
    if 'Is_Stress_Test' in df.columns:
        df['Is_Stress_Test'] = df['Is_Stress_Test'].astype(bool)
    try:
        data_valore = _dt.strptime(data_str, '%Y-%m-%d').date()
    except Exception:
        data_valore = data_str
    return {'nome': nome, 'data': data_valore, 'squadra': squadra, 'dati': df}

def carica_stagione_da_disco():
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_stagione()
            valori = worksheet.get_all_values()
            if len(valori) <= 1:
                return []
            return [_riga_sheet_a_match(riga) for riga in valori[1:] if riga and riga[0]]
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not load season from Google Sheets: {e}")
            return []
    if os.path.exists(SEASON_FILE):
        try:
            with open(SEASON_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return []
    return []

def salva_stagione_su_disco(db):
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_stagione()
            worksheet.clear()
            worksheet.append_row(GOOGLE_SHEETS_HEADER)
            righe = [_match_a_riga_sheet(m) for m in db]
            if righe:
                worksheet.append_rows(righe)
            return
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not save season to Google Sheets: {e}")
    with open(SEASON_FILE, 'wb') as f:
        pickle.dump(db, f)

if 'db' not in st.session_state:
    st.session_state['db'] = carica_stagione_da_disco()

st.sidebar.caption(f"📦 Matches in memory (season): {len(st.session_state['db'])}")
if _google_sheets_configurato():
    st.sidebar.caption("☁️ Storage: Google Sheets")
else:
    st.sidebar.caption("💻 Storage: local file")
    st.sidebar.caption(f"ℹ️ {_diagnosi_google_sheets()}")

tab1, tab2, tab3 = st.tabs(['📥 Upload Match Sheets', '📊 Single Game Analysis', '🏆 Seasonal Report'])

with tab1:
    st.header('Upload Game Data')

    if 'upload_authorized' not in st.session_state:
        st.session_state['upload_authorized'] = False

    if not st.session_state['upload_authorized']:
        st.info("🔒 This section is reserved for authorized staff. Everyone else can freely view the Single Game Analysis and Seasonal Report tabs.")
        codice_inserito = st.text_input("Access code", type="password", key="codice_upload")
        if st.button("Unlock"):
            if codice_inserito == UPLOAD_ACCESS_CODE:
                st.session_state['upload_authorized'] = True
                st.rerun()
            else:
                st.error("Incorrect code.")
    else:
        fc = st.file_uploader('Drag and drop Excel files here', type=['xlsx', 'xls'], accept_multiple_files=True)
    
        if fc:
            pe = []
            for idx, f in enumerate(fc):
                st.subheader(f"File Configuration: {f.name}")
                col1, col2, col3 = st.columns(3)
                with col1: nm = st.text_input(f'Game Name {idx+1}', value=f'Game {idx+1}', key=f'n_{idx}')
                with col2: dt = st.date_input(f'Event Date {idx+1}', value=datetime.now(), key=f"d_{idx}")
                with col3: sq = st.text_input(f'Analyzed Team {idx+1}', value=f'Team {idx+1}', key=f's_{idx}')
            
                try:
                    df = pd.read_excel(f)
                
                    # 📌 INDIVIDUAZIONE INTELLIGENTE DELLE COLONNE: Evita qualsiasi KeyError a prescindere dal testo maiuscolo/minuscolo
                    c_gk = [c for c in df.columns if 'gk' in str(c).lower() or 'portiere' in str(c).lower() or 'porter' in str(c).lower()][0]
                    c_tiro = [c for c in df.columns if 'tiro' in str(c).lower() or 'shot' in str(c).lower()][0]
                    c_res = [c for c in df.columns if 'result' in str(c).lower() or 'esito' in str(c).lower() or 'risultato' in str(c).lower()][0]
                    c_time = [c for c in df.columns if 'timeline' in str(c).lower() or 'tempo' in str(c).lower() or 'minut' in str(c).lower()][0]
                
                    df['PORTIERE_CLEAN'] = df[c_gk].astype(str).str.strip()
                    df['TIRO_CLEAN'] = df[c_tiro].astype(str).str.strip()
                    df['RESULT_CLEAN'] = df[c_res].astype(str).str.lower().str.strip()
                
                    minuti_list, tempo_list, scarti_list, punteggi_list = [], [], [], []
                    for val in df[c_time]:
                        m_tot, t_s, sc, pt = analizza_timeline(val)
                        minuti_list.append(m_tot)
                        tempo_list.append(t_s)
                        scarti_list.append(sc)
                        punteggi_list.append(pt)
                    
                    df['Minuti_Gara'] = minuti_list
                    df['Tempo_Visuale'] = tempo_list
                    df['Scarto_Punteggio'] = scarti_list
                    df['Punteggio_Live'] = punteggi_list
                
                    df['macro_settore'] = df['TIRO_CLEAN'].apply(mappa_macro_settore)
                
                    gpi_list, stress_list = [], []
                    for _, row in df.iterrows():
                        gp_val, str_bool = calcola_gpi_riga(row['macro_settore'], row['RESULT_CLEAN'], row['Minuti_Gara'], row['Scarto_Punteggio'])
                        gpi_list.append(gp_val)
                        stress_list.append(str_bool)
                    
                    df['GPI_Tiro'] = gpi_list
                    df['Is_Stress_Test'] = stress_list
                
                    def calcola_blocco_stringa(m):
                        if m < 10: return '0-10'
                        elif m < 20: return '10-20'
                        elif m < 30: return '20-30'
                        elif m < 40: return '30-40'
                        elif m < 50: return '40-50'
                        else: return '50-60'
                    df['Blocco_10m'] = df['Minuti_Gara'].apply(calcola_blocco_stringa)
                
                    pe.append({'nome': nm, 'data': dt, 'squadra': sq, 'dati': df})
                except Exception as e:
                    st.error(f'Error processing file {f.name}: {e}')
                
            if st.button('➕ Save & Process Matches (add to season)'):
                chiavi_esistenti = {(p['nome'], str(p['data']), p['squadra']) for p in st.session_state['db']}
                aggiunte, duplicati = 0, 0
                for match in pe:
                    chiave = (match['nome'], str(match['data']), match['squadra'])
                    if chiave in chiavi_esistenti:
                        duplicati += 1
                        continue
                    st.session_state['db'].append(match)
                    chiavi_esistenti.add(chiave)
                    aggiunte += 1

                salva_stagione_su_disco(st.session_state['db'])

                if aggiunte:
                    st.success(f'{aggiunte} match(es) added to the season. Total matches in memory: {len(st.session_state["db"])}.')
                if duplicati:
                    st.warning(f'{duplicati} match(es) skipped because already present (same name, date and team). Rename the "Game Name" if this is actually a different match.')
                if not aggiunte and not duplicati:
                    st.info('No matches to add.')

        st.markdown("---")
        st.subheader("💾 Season Backup")
        st.caption("Download a backup file of the whole season anytime and keep it on your computer. "
                   "If anything ever goes wrong with the online app, you can restore everything from this file.")

        col_backup1, col_backup2 = st.columns(2)
        with col_backup1:
            st.markdown("**Download backup**")
            if st.session_state['db']:
                backup_bytes = pickle.dumps(st.session_state['db'])
                nome_backup = f"goalkeeper_season_backup_{datetime.now().strftime('%Y-%m-%d_%H%M')}.pkl"
                st.download_button(
                    label="⬇️ Download Season Backup",
                    data=backup_bytes,
                    file_name=nome_backup,
                    mime="application/octet-stream"
                )
            else:
                st.caption("No data to back up yet.")

        with col_backup2:
            st.markdown("**Restore from backup**")
            file_backup = st.file_uploader("Upload a .pkl backup file", type=['pkl'], key="restore_backup")
            if file_backup is not None:
                if st.button("♻️ Restore backup (merge into current season)"):
                    try:
                        db_ripristinato = pickle.loads(file_backup.read())
                        chiavi_esistenti = {(p['nome'], str(p['data']), p['squadra']) for p in st.session_state['db']}
                        aggiunte_backup = 0
                        for match in db_ripristinato:
                            chiave = (match['nome'], str(match['data']), match['squadra'])
                            if chiave in chiavi_esistenti:
                                continue
                            st.session_state['db'].append(match)
                            chiavi_esistenti.add(chiave)
                            aggiunte_backup += 1
                        salva_stagione_su_disco(st.session_state['db'])
                        st.success(f"Restored {aggiunte_backup} match(es) from the backup file. "
                                  f"Total matches now in memory: {len(st.session_state['db'])}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not read this backup file: {e}")

        st.markdown("---")
        st.subheader("🗑️ Delete a Single Match")
        st.caption("Remove one specific match from the season (e.g. a friendly you only needed a one-off "
                   "report for) without touching any of the other matches.")
        if st.session_state['db']:
            opzioni_partite_elimina = [
                f"{p['nome']} ({p['data']}) - {p['squadra']}" for p in st.session_state['db']
            ]
            partita_da_eliminare = st.selectbox(
                "Select the match to delete:", opzioni_partite_elimina, key="elimina_partita_select"
            )
            idx_da_eliminare = opzioni_partite_elimina.index(partita_da_eliminare)
            conferma_elimina_singola = st.checkbox(
                "I confirm I want to delete this match only (this action is irreversible)",
                key="conferma_elimina_singola"
            )
            if st.button("🗑️ Delete This Match", disabled=not conferma_elimina_singola):
                st.session_state['db'].pop(idx_da_eliminare)
                salva_stagione_su_disco(st.session_state['db'])
                st.success(f"Match '{partita_da_eliminare}' deleted. Remaining matches: {len(st.session_state['db'])}.")
                st.rerun()
        else:
            st.caption("No matches to delete yet.")

        st.markdown("---")
        st.subheader("⚠️ Reset Season")
        st.caption(f"Matches currently saved in memory/season: **{len(st.session_state['db'])}**")
        conferma_reset = st.checkbox("I confirm I want to delete ALL season data (this action is irreversible)")
        if st.button("🔄 Reset Season", disabled=not conferma_reset):
            st.session_state['db'] = []
            salva_stagione_su_disco(st.session_state['db'])
            if os.path.exists(SEASON_FILE):
                os.remove(SEASON_FILE)
            st.success("Season reset. All data has been deleted.")
            st.rerun()

with tab2:
    if not st.session_state['db']:
        st.warning('Please upload and save data files first.')
    else:
        st.header("Single Match Statistical Analysis")
        opzioni_match = [f"{p['nome']} ({p['data'].strftime('%Y-%m-%d')}) - {p['squadra']}" for p in st.session_state['db']]
        scelta = st.selectbox('Select match:', opzioni_match)
        idx_match = opzioni_match.index(scelta)
        
        df_match = st.session_state['db'][idx_match]['dati'].copy()
        df_match = df_match.sort_values(by='Minuti_Gara').reset_index(drop=True)
        
        st.subheader("📊 Team Goalkeeping Totals")
        s_t, g_t, m_t, pct_t, eff_t = calcola_metriche_gruppo(df_match)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Saves", s_t)
        c2.metric("Total Goals Conceded", g_t)
        c3.metric("Team Save %", f"{pct_t:.1f}%")
        c4.metric("Team Efficiency %", f"{eff_t:.1f}%")
        
        st.markdown("---")
        st.subheader("📈 Goalkeeper Cumulative Match Performance Graph")
        
        gpi_progressivo = []
        storico_portieri_gpi = {}
        
        for idx, row in df_match.iterrows():
            gk_attuale = row['PORTIERE_CLEAN']
            punti_tiro = row['GPI_Tiro']
            
            if gk_attuale not in storico_portieri_gpi:
                nuovo_valore = punti_tiro
            else:
                nuovo_valore = storico_portieri_gpi[gk_attuale] + punti_tiro
                
            gpi_progressivo.append(nuovo_valore)
            storico_portieri_gpi[gk_attuale] = nuovo_valore
            
        df_match['GPI_Progressivo_Disegno'] = gpi_progressivo
        
        portieri_unici = list(df_match['PORTIERE_CLEAN'].dropna().unique())
        simboli_colore = ['🔵', '🔴', '🟢', '🟡', '🟣']
        mappa_colori_testo = {gk: simboli_colore[i % len(simboli_colore)] for i, gk in enumerate(portieri_unici)}
        
        def _costruisci_etichetta_asse_x(indice, gk, tempo_visuale):
            prefisso = f"{mappa_colori_testo[gk]} {gk}"
            if str(tempo_visuale).strip():
                return f"{prefisso} | {tempo_visuale}"
            return f"{prefisso} | Shot {indice + 1}"

        df_match['Label_Asse_X'] = [
            _costruisci_etichetta_asse_x(i, row['PORTIERE_CLEAN'], row['Tempo_Visuale'])
            for i, row in df_match.iterrows()
        ]
        
        colori_punti = []
        for _, row in df_match.iterrows():
            if row['Is_Stress_Test']:
                colori_punti.append('#ffcc00')
            elif row['GPI_Tiro'] >= 0:
                colori_punti.append('#2ca02c')
            else:
                colori_punti.append('#d62728')

        fig_linee = go.Figure()
        x_labels = df_match['Label_Asse_X'].values
        y_values = df_match['GPI_Progressivo_Disegno'].values
        
        fig_linee.add_trace(go.Scatter(
            x=x_labels, y=y_values, mode='lines', showlegend=False,
            line=dict(width=3, color='lightgray')
        ))
        
        for i in range(len(df_match)):
            fig_linee.add_trace(go.Scatter(
                x=[x_labels[i]], y=[y_values[i]], mode='markers', showlegend=False,
                marker=dict(
                    size=12, color=colori_punti[i],
                    symbol='square' if df_match['Is_Stress_Test'].values[i] else 'circle'
                )
            ))
            
        fig_linee.add_trace(go.Scatter(
            x=x_labels, y=y_values, mode='text', showlegend=False,
            text=df_match['GPI_Tiro'].apply(lambda x: f"+{x}" if x > 0 else str(x)),
            textposition="top center", textfont=dict(weight="bold", color="black")
        ))
            
        fig_linee.add_shape(
            type="line", x0=-0.5, y0=0, x1=len(df_match)-0.5, y1=0, line=dict(color="black", width=4)
        )
        
        fig_linee.update_layout(
            xaxis_title="Timeline / Live Score / Active Goalkeeper (Chronological Order)",
            yaxis_title="Progressive GPI Valuation Index",
            xaxis=dict(tickangle=90),
            height=600,
            margin=dict(b=140),
            plot_bgcolor='white'
        )

        st.plotly_chart(fig_linee, use_container_width=True)
        st.caption("🟢 Save/positive Miss   🔴 Goal conceded   🟨 square = Money Time (last 10 real match minutes, score margin between -5 and +5)")

        # ============================================================
        # SEZIONE: SEQUENZA CRONOLOGICA DEI TIRI
        # ============================================================
        st.markdown("---")
        st.subheader("📋 Chronological Shot Sequence")
        st.caption("Data from the Excel file, in chronological order, with the GPI calculated for each shot.")

        tabella_sequenza = pd.DataFrame({
            'Timeline': df_match['Tempo_Visuale'].values,
            'Goalkeeper': df_match['PORTIERE_CLEAN'].values,
            'Shot Type': df_match['TIRO_CLEAN'].values,
            'Outcome': df_match['RESULT_CLEAN'].values,
            'GPI': df_match['GPI_Tiro'].apply(lambda x: f"+{x}" if x > 0 else str(x)).values,
            'Money Time': df_match['Is_Stress_Test'].map({True: 'Yes', False: ''}).values
        })
        st.dataframe(tabella_sequenza, use_container_width=True, hide_index=True, height=450)

        # ============================================================
        # SEZIONE: GPI TOTALE PARTITA PER PORTIERE
        # ============================================================
        st.markdown("---")
        st.subheader("🥅 Total Match GPI per Goalkeeper")

        righe_gpi_totale = []
        for gk in portieri_unici:
            df_gk_tot = df_match[df_match['PORTIERE_CLEAN'] == gk]
            righe_gpi_totale.append({
                'Goalkeeper': f"{mappa_colori_testo[gk]} {gk}",
                'Total Match GPI': round(df_gk_tot['GPI_Tiro'].sum(), 1),
                'Shots Faced': len(df_gk_tot)
            })
        st.dataframe(pd.DataFrame(righe_gpi_totale), use_container_width=True, hide_index=True)

        # ============================================================
        # SEZIONE: STATISTICHE DETTAGLIATE PER PORTIERE
        # (settore specifico, macro-settore aggregato, money time)
        # ============================================================
        st.markdown("---")
        st.subheader("🧤 Detailed Statistics per Goalkeeper")

        dati_pdf_portieri = {}

        for gk in portieri_unici:
            df_gk = df_match[df_match['PORTIERE_CLEAN'] == gk]
            with st.expander(f"{mappa_colori_testo[gk]} {gk}", expanded=True):

                gpi_totale_gk = df_gk['GPI_Tiro'].sum()
                s_gk, g_gk, m_gk, pct_gk, eff_gk = calcola_metriche_gruppo(df_gk)

                cA, cB, cC, cD, cE = st.columns(5)
                cA.metric("Total GPI", f"{gpi_totale_gk:+.1f}")
                cB.metric("Saves", s_gk)
                cC.metric("Goals Conceded", g_gk)
                cD.metric("Save %", f"{pct_gk:.1f}%")
                cE.metric("Efficiency", f"{eff_gk:.1f}%")

                st.markdown("**Statistics by specific shot zone** (e.g. 6m1, lw2, 9m2.5 ...)")
                righe_settore = []
                for settore in sorted(df_gk['TIRO_CLEAN'].dropna().unique()):
                    df_s = df_gk[df_gk['TIRO_CLEAN'] == settore]
                    s, g, m, pct, eff = calcola_metriche_gruppo(df_s)
                    righe_settore.append({
                        'Zone': settore, 'Saves': s, 'Goals': g, 'Miss': m,
                        'Save %': round(pct, 1), 'Efficiency %': round(eff, 1),
                        'GPI': round(df_s['GPI_Tiro'].sum(), 1)
                    })
                st.dataframe(pd.DataFrame(righe_settore), use_container_width=True, hide_index=True)

                st.markdown("**Statistics by aggregated macro-zone** (all 6m, all bt, all 9m ...)")
                righe_macro = []
                for macro in sorted(df_gk['macro_settore'].dropna().unique()):
                    df_ma = df_gk[df_gk['macro_settore'] == macro]
                    s, g, m, pct, eff = calcola_metriche_gruppo(df_ma)
                    righe_macro.append({
                        'Macro-Zone': macro.upper(), 'Saves': s, 'Goals': g, 'Miss': m,
                        'Save %': round(pct, 1), 'Efficiency %': round(eff, 1),
                        'GPI': round(df_ma['GPI_Tiro'].sum(), 1)
                    })
                st.dataframe(pd.DataFrame(righe_macro), use_container_width=True, hide_index=True)

                st.markdown("**Money Time Performance** (from the 50th minute onward, score margin between -5 and +5)")
                df_stress_gk = df_gk[df_gk['Is_Stress_Test'] == True]
                pct_su_totale_gk = (len(df_stress_gk) / len(df_gk) * 100) if len(df_gk) > 0 else 0.0
                if not df_stress_gk.empty:
                    s_st, g_st, m_st, pct_st, eff_st = calcola_metriche_gruppo(df_stress_gk)
                    gpi_totale_st = df_stress_gk['GPI_Tiro'].sum()
                    cs1, cs2, cs3, cs4, cs5, cs6 = st.columns(6)
                    cs1.metric("Shots in Money Time", len(df_stress_gk))
                    cs2.metric("% of Total Shots", f"{pct_su_totale_gk:.1f}%")
                    cs3.metric("Saves", s_st)
                    cs4.metric("Goals Conceded", g_st)
                    cs5.metric("Save %", f"{pct_st:.1f}%")
                    cs6.metric("Total Match GPI", f"{gpi_totale_st:+.2f}")
                    money_time_riassunto = (
                        f"{len(df_stress_gk)} shots ({pct_su_totale_gk:.1f}% of total shots), "
                        f"{s_st} saves, {g_st} goals, Save % {pct_st:.1f}%, Total Match GPI {gpi_totale_st:+.2f}"
                    )
                else:
                    st.info("No shots faced in Money Time by this goalkeeper in this match.")
                    money_time_riassunto = "No shots in Money Time"

                dati_pdf_portieri[f"{mappa_colori_testo[gk]} {gk}"] = {
                    'gpi_totale': gpi_totale_gk, 'parate': s_gk, 'gol': g_gk,
                    'pct': pct_gk, 'eff': eff_gk,
                    'tabella_settore': pd.DataFrame(righe_settore),
                    'tabella_macro': pd.DataFrame(righe_macro),
                    'money_time_riassunto': money_time_riassunto
                }

        # ============================================================
        # SEZIONE: RENDIMENTO PER BLOCCHI DA 10 MINUTI
        # (% parate e GPI totale calcolati in modo indipendente per ogni blocco)
        # ============================================================
        st.markdown("---")
        st.subheader("⏱️ Performance by 10-Minute Blocks (full match)")
        st.caption("Each block is calculated independently of the others: this is not a cumulative value.")

        righe_blocchi = []
        for blocco in ORDINE_BLOCCHI:
            df_b = df_match[df_match['Blocco_10m'] == blocco]
            s_b, g_b, m_b, pct_b, eff_b = calcola_metriche_gruppo(df_b)
            gpi_b = df_b['GPI_Tiro'].sum() if not df_b.empty else 0.0
            righe_blocchi.append({
                'Block': blocco, 'Save %': round(pct_b, 1), 'Total GPI': round(gpi_b, 1),
                'Shots': len(df_b)
            })
        df_blocchi = pd.DataFrame(righe_blocchi)

        max_gpi_abs = max(df_blocchi['Total GPI'].abs().max(), 1)
        y_top_gpi = max_gpi_abs * 1.35
        y_bottom_gpi = -max_gpi_abs * 1.35
        y_bottom_pct = 6

        fig_blocchi = make_subplots(
            rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12,
            row_heights=[0.5, 0.5],
            subplot_titles=("Save % per block", "Total GPI per block")
        )
        # % line (no text attached to points)
        fig_blocchi.add_trace(
            go.Scatter(x=df_blocchi['Block'], y=df_blocchi['Save %'], name='Save %',
                       mode='lines+markers', line=dict(color='#1f77b4', width=3),
                       marker=dict(size=10, color='#1f77b4'), showlegend=False),
            row=1, col=1
        )
        # % labels ALWAYS at the bottom, fixed height (never overlapping the line)
        fig_blocchi.add_trace(
            go.Scatter(x=df_blocchi['Block'], y=[y_bottom_pct] * len(df_blocchi), mode='text',
                       text=df_blocchi['Save %'].apply(lambda x: f"{x:.0f}%"),
                       textfont=dict(color='#1f77b4', size=13), showlegend=False),
            row=1, col=1
        )
        # GPI bars (no text attached)
        fig_blocchi.add_trace(
            go.Bar(x=df_blocchi['Block'], y=df_blocchi['Total GPI'], name='Total GPI',
                   marker_color='#ff7f0e', width=0.5, showlegend=False),
            row=2, col=1
        )
        # GPI labels ALWAYS at the top, fixed height (never overlapping the bars)
        fig_blocchi.add_trace(
            go.Scatter(x=df_blocchi['Block'], y=[y_top_gpi] * len(df_blocchi), mode='text',
                       text=df_blocchi['Total GPI'].apply(lambda x: f"{x:+.1f}"),
                       textfont=dict(color='#ff7f0e', size=13), showlegend=False),
            row=2, col=1
        )
        fig_blocchi.update_layout(
            height=520, plot_bgcolor='white', margin=dict(t=50, b=40, l=40, r=40)
        )
        fig_blocchi.update_yaxes(title_text="Save %", range=[0, 115], row=1, col=1)
        fig_blocchi.update_yaxes(title_text="Total GPI", range=[y_bottom_gpi * 1.15, y_top_gpi * 1.15], row=2, col=1)
        fig_blocchi.update_xaxes(title_text="Game block (minutes)", row=2, col=1)

        st.plotly_chart(fig_blocchi, use_container_width=True)
        st.dataframe(df_blocchi, use_container_width=True, hide_index=True)

        # ============================================================
        # ESPORTAZIONE PDF DELL'INTERA PAGINA
        # ============================================================
        st.markdown("---")
        st.subheader("📄 Export Match Report to PDF")
        st.caption("Generate a PDF with every section of this page: totals, GPI chart, shot sequence, per-goalkeeper statistics, and 10-minute blocks.")

        if st.button("📄 Generate PDF for this match"):
            with st.spinner("Generating PDF..."):
                try:
                    pdf_bytes = genera_pdf_partita(
                        titolo_partita=scelta,
                        righe_gpi_totale=righe_gpi_totale,
                        tabella_sequenza=tabella_sequenza,
                        dati_portieri=dati_pdf_portieri,
                        df_blocchi=df_blocchi,
                        df_match=df_match,
                        fig_blocchi=fig_blocchi
                    )
                    nome_file_pdf = f"Report_{scelta}".replace(' ', '_').replace('/', '-') + ".pdf"
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=nome_file_pdf,
                        mime="application/pdf"
                    )
                    st.success("PDF generated! Click the button above to download it.")
                except Exception as e:
                    st.error(f"Error generating PDF: {e}")


with tab3:
    st.header("🏆 Seasonal Report")

    if not st.session_state['db']:
        st.warning("No matches in memory. Upload and process at least one match in the first tab to see the season report.")
    else:
        modalita = st.radio(
            "View season trends by:",
            ["Goalkeeper", "Team"],
            horizontal=True
        )

        portieri_stagione = sorted(set(
            gk for match in st.session_state['db'] for gk in match['dati']['PORTIERE_CLEAN'].dropna().unique()
        ))
        squadre_stagione = sorted(set(match['squadra'] for match in st.session_state['db']))

        df_stagione_totale = pd.DataFrame()
        dati_per_portiere = {}
        titolo_report = ""

        if modalita == "Goalkeeper":
            if not portieri_stagione:
                st.info("No goalkeepers found in the uploaded data.")
            else:
                portiere_scelto = st.selectbox("Select goalkeeper:", portieri_stagione)
                df_stagione_totale, lista_partite = raccogli_stagione_per_portiere(st.session_state['db'], portiere_scelto)
                dati_per_portiere = {portiere_scelto: lista_partite}
                titolo_report = f"Season — {portiere_scelto}"
        else:
            if not squadre_stagione:
                st.info("No teams found in the uploaded data.")
            else:
                squadra_scelta = st.selectbox("Select team:", squadre_stagione)
                df_stagione_totale, dati_per_portiere = raccogli_stagione_per_squadra(st.session_state['db'], squadra_scelta)
                titolo_report = f"Season — {squadra_scelta}"

        if titolo_report and df_stagione_totale.empty:
            st.info("No data available for the current selection: the selected goalkeeper/team has not yet faced any shots in the uploaded matches.")
        elif titolo_report:
            st.markdown("---")
            st.subheader(f"📊 Total Season Statistics — {titolo_report.replace('Season — ', '')}")
            s_tot, g_tot, m_tot, pct_tot, eff_tot = calcola_metriche_gruppo(df_stagione_totale)
            gpi_medio_tot = df_stagione_totale['GPI_Tiro'].mean() if not df_stagione_totale.empty else 0.0
            numero_partite_coinvolte = len(set(p['label'] for lista in dati_per_portiere.values() for p in lista))
            media_cumulativa_gpi = (df_stagione_totale['GPI_Tiro'].sum() / numero_partite_coinvolte) if numero_partite_coinvolte > 0 else 0.0
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Shots Faced", len(df_stagione_totale))
            c2.metric("Saves", s_tot)
            c3.metric("Goals Conceded", g_tot)
            c4.metric("Save %", f"{pct_tot:.1f}%")
            c5.metric("Average GPI (per shot)", f"{gpi_medio_tot:+.2f}")
            c6.metric("Cumulative Average GPI (per match)", f"{media_cumulativa_gpi:+.2f}")

            st.markdown("---")
            st.subheader("🥅 Total Season GPI per Goalkeeper")
            righe_gpi_stagione = []
            for gk, lista in dati_per_portiere.items():
                df_gk_tot = df_stagione_totale[df_stagione_totale['PORTIERE_CLEAN'] == gk]
                righe_gpi_stagione.append({
                    'Goalkeeper': gk,
                    'Total Season GPI': round(df_gk_tot['GPI_Tiro'].sum(), 1),
                    'Matches Played': len(lista),
                    'Shots Faced': len(df_gk_tot)
                })
            df_gpi_stagione = pd.DataFrame(righe_gpi_stagione)
            st.dataframe(df_gpi_stagione, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("📈 Season GPI Trend (per match + cumulative average)")
            st.caption("Matches in which a goalkeeper did not play are not counted.")
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_gpi_screen:
                generato = _disegna_grafico_stagione(dati_per_portiere, 'gpi_totale', 'Total Match GPI', tmp_gpi_screen.name)
                if generato:
                    st.image(tmp_gpi_screen.name, width=1000)

            st.markdown("---")
            st.subheader("📈 Season Save % Trend (per match + cumulative average)")
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_pct_screen:
                generato = _disegna_grafico_stagione(dati_per_portiere, 'pct', 'Match Save %', tmp_pct_screen.name)
                if generato:
                    st.image(tmp_pct_screen.name, width=1000)

            st.markdown("---")
            st.subheader("📋 Match History")
            righe_storico = []
            for gk, lista in dati_per_portiere.items():
                for p in lista:
                    righe_storico.append({
                        'Goalkeeper': gk, 'Match': p['label'],
                        'Total GPI': round(p['gpi_totale'], 1),
                        'Save %': round(p['pct'], 1),
                        'Shots Faced': p['tiri']
                    })
            df_storico = pd.DataFrame(righe_storico)
            st.dataframe(df_storico, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("🧤 Detailed Season Statistics per Goalkeeper")
            dati_pdf_portieri_stagione = {}
            for gk, lista in dati_per_portiere.items():
                df_gk_tot = df_stagione_totale[df_stagione_totale['PORTIERE_CLEAN'] == gk]
                if df_gk_tot.empty:
                    continue
                info = calcola_dettaglio_portiere(df_gk_tot, lista_partite=lista)
                dati_pdf_portieri_stagione[gk] = info
                with st.expander(f"{gk} — Total Season GPI: {info['gpi_totale']:+.1f}", expanded=True):
                    cA, cB, cC, cD, cE = st.columns(5)
                    cA.metric("Total GPI", f"{info['gpi_totale']:+.1f}")
                    cB.metric("Saves", info['parate'])
                    cC.metric("Goals Conceded", info['gol'])
                    cD.metric("Save %", f"{info['pct']:.1f}%")
                    cE.metric("Efficiency", f"{info['eff']:.1f}%")

                    st.markdown("**Statistics by specific shot zone**")
                    st.dataframe(info['tabella_settore'], use_container_width=True, hide_index=True)

                    st.markdown("**Statistics by aggregated macro-zone**")
                    st.dataframe(info['tabella_macro'], use_container_width=True, hide_index=True)

                    st.markdown(f"**Money Time Performance:** {info['money_time_riassunto']}")

            st.markdown("---")
            st.subheader("⏱️ Performance by 10-Minute Blocks (season cumulative)")
            df_blocchi_stagione, fig_blocchi_stagione = costruisci_grafico_blocchi(df_stagione_totale)
            st.plotly_chart(fig_blocchi_stagione, use_container_width=True)
            st.dataframe(df_blocchi_stagione, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("📄 Export Season Report to PDF")
            st.caption("Generate a PDF with every section of this page: totals, GPI and save % trends, match history, per-goalkeeper statistics, and 10-minute blocks.")

            if st.button("📄 Generate Season PDF"):
                with st.spinner("Generating PDF..."):
                    try:
                        pdf_bytes_stagione = genera_pdf_stagione(
                            titolo_report=titolo_report,
                            righe_gpi_stagione=righe_gpi_stagione,
                            df_storico=df_storico,
                            dati_portieri=dati_per_portiere,
                            df_blocchi=df_blocchi_stagione,
                            df_stagione_totale=df_stagione_totale,
                            fig_blocchi=fig_blocchi_stagione
                        )
                        nome_file_pdf_stagione = f"Report_{titolo_report}".replace(' ', '_').replace('/', '-').replace('—', '-') + ".pdf"
                        st.download_button(
                            label="⬇️ Download Season PDF",
                            data=pdf_bytes_stagione,
                            file_name=nome_file_pdf_stagione,
                            mime="application/pdf"
                        )
                        st.success("PDF generated! Click the button above to download it.")
                    except Exception as e:
                        st.error(f"Error generating PDF: {e}")
