import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import re
import inspect
import json
import uuid
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

try:
    from pypdf import PdfReader, PdfWriter
    _PYPDF_DISPONIBILE = True
except Exception:
    _PYPDF_DISPONIBILE = False

# Logo dell'associazione, incorporato direttamente nel codice (base64) cosicche' non
# serva gestire un file immagine separato: appare su ogni pagina dei PDF esportati.
LOGO_BASE64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/7QCEUGhvdG9zaG9wIDMuMAA4QklNBAQAAAAAAGgcAigAYkZCTUQwYTAwMGFiYzAxMDAwMDQ3"
    "MDMwMDAwYjIwNDAwMDA4ODA1MDAwMDQ5MDYwMDAwNzQwOTAwMDBmNDBjMDAwMDRkMGQwMDAwZmEwZDAwMDA1NDBlMDAwMDlhMTEw"
    "MDAwAP/bAIQABQYGCwgLCwsLCw0LCwsNDg4NDQ4ODw0ODg4NDxAQEBEREBAQEA8TEhMPEBETFBQTERMWFhYTFhUVFhkWGRYWEgEF"
    "BQUKBwoICQkICwgKCAsKCgkJCgoMCQoJCgkMDQsKCwsKCw0MCwsICwsMDAwNDQwMDQoLCg0MDQ0MExQTExOc/8IAEQgAlgCWAwEi"
    "AAIRAQMRAf/EAIcAAQABBQEBAAAAAAAAAAAAAAABAgMEBQcGCBAAAQMBBAYHAgkLBQAAAAAAAQACAxEEEiExEyJBUWFxBSAwMoGR"
    "saHRFCMzQlKCssHwEBVAQ1BgYnKSwuFTg6LS8REBAAEDAgUEAwADAQEAAAAAAREAITFBUWFxgZGhECCx8DDB0UBQ4fFg/9oADAMB"
    "AAIAAwAAAAHjaFSUCUSISQkQmAAAB2XjXZTjQAEpDaZkxoHq792z42PVba3c5822rpqoVUpEE9l4z2Y4yIJTLdbPGpzMXJ2FvZeg"
    "0U5tvCuYmRd0frNPtvMW5xZu6jT+l85p9tRExEuzcZ7NDjIJqprmPS2lvOxd7sNHt/Ree2ni/b8x1Wbn73zHscTPs6jNq2WHq/PZ"
    "+D5/dW4mKanZuM9mhxkE11exmPL+ssa2unYU4GTl4tnS+ts3KF3EpuU59FnT4eTl6HPwMa/RFVMVOzcZ7NDjMxJXXa2sxYzOnXzm"
    "+s68uUckv+r9Bdt8usdYU1eG1PXcOxd4/i/Rfz0Y8TCXZuM9mhxkFWy1ky9/Phcim5tdh5XZqtpjaWuun0dXmM6ivE9N5C4j13i4"
    "tTaiBDs3GezHGQJgVTTMxXVak9jc8VMx6/yVKJmIgQhIDs3Guyw4ymAACUJSgSgAACR2XjXZYcadlS407KONR2YcZdmHGXZhxqOz"
    "DjTso407KONOyjjXZQ//2gAIAQEAAQUC/b8dlkkXwQBCCFaONGzxKHom+prM6Ps7PG0gTEI1emtogEI099w2Z9ogEL33ZJVa4hFJ"
    "2Fn+RCYEGoBWybRMZK2zkC66zmsc/d6R+W7Cx4tagmoLpE/Gtla6V9qdaDgxr9ddIOrP2FgkDJnNMZa9MNUKNUz7zrPBpXYNDlZf"
    "lLpd2NxTNNoTTDGvziVNbnyLBRW5sbW2yNyeYig6MRlwd12tLkLG5jL7kKSufHoXgtWiYUbNGtDGEQxWeBkjjLi6Unrg0VVgm6FW"
    "i0tmAeU2Ry0zyi56LnIWyPRO0JTgOwskekltDnlNmNnfZYyyRsWjtXQoCkJba5J62qe0VtNuJ0fS76MMOkkeKHrWafQyTdKhwHTE"
    "1HWuWRo6RtDTJb5y5trmCk6RtDzJ0jPIpnOlfJ0k97R0s4PfSvXDiFpnq+axRPnWJNHLWrPE+FXzXSuRcT2gNELRHaV+b3p1qjgH"
    "7qf/2gAIAQMAAT8B7YzsGb2jxCDq5GvLr2iQtpTarROXfOPmrPGZ3hgw3ncPx7VK82IxsjYLrzS8TVzj7KJ1peJi2urVopzp1rS2"
    "8Ap4iF0NAW6R5yNAOO9WuZkd0kBzxW5wrt4eqsovvvHEk1PWIUlxubL3gD64IW+PLEeHuqnyxSYll6u2lPcVFE1uLRSvXdGHZiq+"
    "DM+iFoW/R67Lnzi7wA96Gjo7v1rq5d3DPjmnSRAnMCuGONKetVWL+LM+WNP7faho8e+MTTAHDZXHNGmzrkA5j9K//9oACAECAAE/"
    "Ae2Fneco3H6pTm3cxTnh17HC2St7GlFBC1mTQPBWqfQNveQ3lRgWwPfK81YMGgUDR+PFR2RjoA8jWo415V61ifdceI9FHKCulpQS"
    "xg2VJ8clY7M+WtDdZhfO/hx9FayIoi0YACg8UeqHUxGxRtfJk8N8SPTFO6Nlzwd9b30UcE8eAfc4Xq+wVCnme/Vc69Q7OtVMmLO6"
    "aL4ZJ9Mo2p5+cqqvVx2UWPBNieRgKohw3LHh2AcRkafpX//aAAgBAQAGPwL9v6rCRvyHmcFryxt4A3z/AMa+q/WycgIx7alfIPHK"
    "Wp9raLvyM/njqPNp+5O+MGG6oHtH3LI0GFaZEZg8ezke+pDAMAaVJNM1qNZHyF53m6q13OfzNfy/dtV1nxku4ZN/mP44qgc12eAz"
    "x54Zq8Hvabx25nbh5L4yOOTjTRu82+5PaMgcORx7G0f7f2urdHff9n/JWjAvGuu+u3cOAPmv5T9lfXd/aincm/Yb2Nobvir/AEOD"
    "uqabKDxAC0km+9QbT/6rkWo3G87hxO7kg1uQ9tdqDd5A81L/ADkeWHYsr3Tqu5P1fvTmHNhI8vy3nZD13IneqZAYuO4fjJUaKN3e"
    "/efyBxyiBkP1cvbRXuf+exxw9U2Zu1tJCSAA5uFfEUK133/4WZeJNFhGynI/eSuG6goOSx9iu3NU8TXDjgPYsWFvI19aeq+VHItP"
    "qKhPbpRekcKmjjRjdmW0oubgxmDRtxB/B69BiiXNaT9C9jTj7l8kyOgzcMuVcT7U0SSmlc7uA9PROY5uI31PuXcb5LuAefvW0eP+"
    "Ftd4+5d0I1FI4xWR1T5cytVoaNnzj5lZN5gAenY4v+9Y6R39Lf8AsmBsZBZgHXrxpuyWAWArRd3PgVi0+RWVEInRGgxJa+hcd51V"
    "hpG87rv+qwdXwp2EbDk5wB5VVobEyBscIIOGtS7sVjgYGgPa0vwxxzVrmjZeN+40DnrK18YS7zp96tAcbo0WJ3BWaMYQtA0dMiCM"
    "1E3TGSkp1bt25sz2qJun0lJu5cu3Nme3NWnSujI/VZXhj51yRo6Gha03afGY7k1vweMwPZUvoKg0RG4nrskpW6a0UtyAMMoo51ST"
    "im/FxlzRQPuayERNNYu3El2/zQfUVu6PIZBGrxV7bhwHdx4cUxodXQ4twBp7ELzx8WQ/ujA+XFazm6jg7ujMZJxPeJxorr4Yzq3b"
    "xabw8Uxxbg2PRubXvtRuig2DPsM13iq7VqkFzcbvzjy3riPBHit5OFM1rFt52bcyOexVriu8fNZ9pUYFUn1X7Jmj7Y2881V0kYi/"
    "1b2B5ba8Fds4x2zO731R831/dX//2gAIAQEBAT8h/wBfFR+caeDHwHlR3qjtkUJ9mbvxUtkG5dU8CKf9Ib6l+ULRCGBgZpJJMMLO"
    "EG4ytQRAkA8cQlmo/EdCqWkxMGDkV33flJ2ipsocbwxR4Acj0VY3cZLoVClJcYYtcFsxMGrRREZcitOiBTF1ds1PL0yQtF+EYXnD"
    "yqypJkfBR6qpy9YuwAno/hHSn6Vma3Hp6UYsZYyXzfe1yHel80BMF2YMbqZXYtGV1F5XPgq77v3FS7P4inPuefwQ05jl6wo09Gbg"
    "THAbVfZEUIYrTgnJ50lCa5bz1LHACZi9ZmZbtlK6NDY2L0VBpvVFA0wA5f8AKn8DDmvKlftWVgvVFTRx+83sFaAnfY60xWDPmHIM"
    "CqxoYvUnzKVki6zYvB1aa8haiD9rYbtMCJYyV3XkcaAU4H79aI/EX/lFSZWqmW6l4GWJvT7ypBKOZ+BeoQYhiZIrBzjNZAcYW770"
    "TUVthyHYeKsDG2NyBjo0KZkcP+mkALApesrogzo6ZeFPnkXhUZAdB5j2pqxxgjXALbwrpYpi2CnRcPGWV72AFOAzTpDEAcZQzOID"
    "vagRA2JxNsoSJbXaSoRSBDL1iRzikYM8XSGiRdJc0inanZ8V/chR2OkE8yp0rbMDrA+agRPyk8zNPjRksGgmblgohX5kQGky35BQ"
    "rIKQpEOg6xNPuTBip7tEotBgBh0seag+BB+1GUORL3rJDTbFYsqZgbUqXVGBYN2oQllglzl/yjxAnFiaxly4NR226xkQ8DStV5D4"
    "1eK0bzJfs8/gG8OZi7xVzzExpLDXMMZqzCLKne6NQ0GPBpdhiKlZg/vPg0oYVkGSZY4FH7mlKmefTzrSnmluJXAQNSdKazl28VwW"
    "7hSzIpEZhYIfsZqMllmF7P3o0KRgImpiyO2DXNGdcBPJj3sQGUlp60ONKVWrQKNYAQmBi81FATLTJVXVUHqIKzLN5N9ay/LxF1nU"
    "rlQYyt0aUFkl8NuxV2aIwwFsSeCkjBtguXSEucUdcuYNdYCpXe3BEQInJnnRyW6COJOGm2RVkZBoTaY/BhEcmgP7tSys7nlFT2JE"
    "8BpiIBiZ4U50DYiUztzrMtv6s/NSomPAXYgjpSpbVpA6BiDwmaBhRu50v/VWQTzfyOxEGRGETUa5M+Q5PgpD0CEuAv5A70oXOwb9"
    "9AcaKrLdcv8Agz6z/wDAf//aAAwDAQECAQMBAAAQsMIYw0YwwggA0UHJukEI+0njZfrQcq8/Vq4Zrw8o87FTSEHf0oq7sxF5c50o"
    "+Qh1DtQaeo8uxfaCDk8i2++M8s884CwAQwwQAAAg/9oACAEDAQE/EPyzTMKbJfuivAbqSp92nt1+VTQoG9nasrSXKFlTwYuKSnEu"
    "CO2CbaUb5YRoJe1rkp+am7T1+cVBKJXwKx4DBtM7UpYWEne7Gl0WpTzgcr9tKPaLZ1rU3MDnoVw76ThU1JxZ0c1gouTFhzH4ACt1"
    "qDwPfsvnvk1lJTSsNDp4lrl6GMhoXUF+D0qbB0/nnNjjxWrUsQXSOfSuIeZD+/fhBjf/ACv/2gAIAQIBAT8Q/MXIW5/CksR7CVR7"
    "0l44LqFc9N0wDpu5sPtROEootZ9jRr8fdKVCXldhLikvKK+rcOZ4e0DGD0ZHsHZRJYcKyL8CKENGSf4gQl9R93/0dK//2gAIAQEB"
    "AT8Q/wA2P8CKj1IqKj8sJNp1CvpHMK3mpso8f9RIGjFcLVDi7zJB2MqpBknHHVjJGfoQSn3lFxsFCluY5PS2nl0YPukoUf2UKmy/"
    "trkx3hjI96IpoANNCcRqnS12QyUeVAnSMMfxD7FBWdUXtGv5SVpdWKT3FFS8B0Lf2UaM3GiME7LvVwen8C9W3P8Ai6nh6A4BAVIT"
    "1B1GedphdqpiOf8A1Q8zzuUlPtKPQBFWAtx59N0SwURUoBP/APjknVrNgyFVm1Tns1m8BMkx3ejtqdkgd3uURfYJZrODxqjT9DMj"
    "9J9pRXQRIuTyOxXQpjlpdabcdEff/QVqqOjyYdpp6Zk4UBlBcLkSwKvQP/Mo5FpTVrMxoP8ASiawtJqHRkh5GdM4Irjj+/K12K/j"
    "Zo6SG5sBznxA9B9p6HlT/wBq7or+nJk0DCMKA2Q7sL20U8J/tLrW87OWRbCatvJsn7o81/KKlvCTuqANppfSz0K8rwfEHrprLpEV"
    "N3vAqxeyq1LKzSDT7VJlYSq/9GqXESWkDlOOOBRyH3cOSsxu4lHoPbNBsGoIId3/AGVF0g3+NW6cl5BeXossN+mReXX0WsKyfeKX"
    "JpYMpuGGXkKNADpFp7m61fQ+wpyUW5nvR0SMuKIgNw82pt29vmqJXkZ/TceVS1QGxLDNjFYcDtGGDi0SkpKY9lrhpAJRAZjha9RN"
    "AJh+StAWIZxxTlVXabyFAD2ijRp9hRQuQexYfv8ATWKukAXYC+k5kuWv5TFQaegSViysnm75rjXzmQAlVPnEteNN9P5X+CA0XlWT"
    "SFIAkUPPYul+qPOCSLrAaRWoFlMjhnpT7pEAwhHTZZsxX9qvrnasUFpZjY9LcK7uwZ5/2KJM+dkVQ9aORHRf9NQGUpy/kSIUF2iV"
    "NHyTS+e5WvjKAPa8/UocbpGrkxgU0tPMza4uHtSqGpI25GwtME0+0qa81QVgKJmTzT6FFmBcJlfcAFDWSJwG6YZ1VemlLnuOVCIP"
    "gBRu2UTRG2RjsFZqIUGbbO6slUeWoafwTQ1NDzEuwAFxN6IKsnMWxd6N1IxpEitEdIoVGVXKur6LS0/gmpqan02aek00n8k1NTU1"
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

APP_VERSION = "v31 - 2026-08-21 - Total Season Statistics: aggiunta Efficiency %, riquadro più grande in stile dashboard nel PDF, meno spazio vuoto in prima pagina"
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

# ============================================================
# HOME / AWAY: la prima squadra scritta nel nome del file è sempre "home",
# la seconda è sempre "away" (es. "Merano-Brixen 23-8-2026" -> Merano=home, Brixen=away).
# Usato sia per i portieri che per i tiratori.
# ============================================================
def estrai_home_away_da_nome_file(nome_file):
    """Ricava (squadra_home, squadra_away) dal nome del file. Restituisce (None, None)
    se il pattern 'Squadra1-Squadra2...' non viene riconosciuto."""
    base = os.path.splitext(str(nome_file))[0]
    m = re.match(r"^\s*([A-Za-zÀ-ÖØ-öø-ÿ'\.]+(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ'\.]+)*)\s*-\s*([A-Za-zÀ-ÖØ-öø-ÿ'\.]+(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ'\.]+)*)", base)
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()

def estrai_nome_e_data_da_nome_file(nome_file):
    """Ricava (nome_partita, data) dal nome del file: la prima parte (SquadraHome-SquadraAway)
    è il nome della partita, il resto è la data (giorno-mese-anno). Es. 'Merano-Brixen
    23-8-2026.xlsx' -> ('Merano-Brixen', date(2026, 8, 23)). Restituisce (None, None) per la
    parte che non riesce a riconoscere."""
    base = os.path.splitext(str(nome_file))[0]
    squadra_home, squadra_away = estrai_home_away_da_nome_file(nome_file)
    nome_partita = f"{squadra_home}-{squadra_away}" if squadra_home and squadra_away else None

    data = None
    m_data = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', base)
    if m_data:
        giorno, mese, anno = int(m_data.group(1)), int(m_data.group(2)), int(m_data.group(3))
        if anno < 100:
            anno += 2000
        try:
            data = datetime(anno, mese, giorno).date()
        except ValueError:
            data = None
    return nome_partita, data

def determina_casa_trasferta(squadra_analizzata, squadra_home, squadra_away):
    """Restituisce 'home', 'away' o None (se non determinabile), confrontando in modo
    tollerante (case-insensitive, contenimento) il nome della squadra analizzata con
    le due squadre estratte dal nome del file."""
    if not squadra_analizzata or not squadra_home or not squadra_away:
        return None
    sa = str(squadra_analizzata).strip().lower()
    sh = str(squadra_home).strip().lower()
    saw = str(squadra_away).strip().lower()
    if sa == sh or sa in sh or sh in sa:
        return 'home'
    if sa == saw or sa in saw or saw in sa:
        return 'away'
    return None

def calcola_split_casa_trasferta(righe_partite, chiave_valore_realizzati, chiave_valore_totali):
    """Dato un elenco di voci-partita (ciascuna con 'casa_trasferta', numeratore e denominatore),
    calcola il rendimento complessivo in casa e in trasferta e il gap assoluto in punti percentuali.
    righe_partite: lista di dict con chiavi 'casa_trasferta' ('home'/'away'/None), chiave_valore_realizzati, chiave_valore_totali."""
    home_num = sum(r[chiave_valore_realizzati] for r in righe_partite if r.get('casa_trasferta') == 'home')
    home_den = sum(r[chiave_valore_totali] for r in righe_partite if r.get('casa_trasferta') == 'home')
    away_num = sum(r[chiave_valore_realizzati] for r in righe_partite if r.get('casa_trasferta') == 'away')
    away_den = sum(r[chiave_valore_totali] for r in righe_partite if r.get('casa_trasferta') == 'away')
    home_pct = (home_num / home_den * 100) if home_den > 0 else None
    away_pct = (away_num / away_den * 100) if away_den > 0 else None
    gap = abs(home_pct - away_pct) if (home_pct is not None and away_pct is not None) else None
    return {
        'home_num': home_num, 'home_den': home_den, 'home_pct': home_pct,
        'away_num': away_num, 'away_den': away_den, 'away_pct': away_pct,
        'gap': gap
    }

def formatta_riga_casa_trasferta(split):
    """Formatta il dizionario di calcola_split_casa_trasferta in una stringa leggibile,
    con il gap evidenziato (in Markdown, rosso) se supera il 10%."""
    if split['home_pct'] is None and split['away_pct'] is None:
        return "No home/away data available (team names in the file names did not match)."
    parti = []
    if split['home_pct'] is not None:
        parti.append(f"Home {split['home_num']}/{split['home_den']} = {split['home_pct']:.1f}%")
    else:
        parti.append("Home: n/a")
    if split['away_pct'] is not None:
        parti.append(f"Away {split['away_num']}/{split['away_den']} = {split['away_pct']:.1f}%")
    else:
        parti.append("Away: n/a")
    if split['gap'] is not None:
        gap_testo = f"Gap {split['gap']:.1f}%"
        if split['gap'] > 10:
            parti.append(f":red[**{gap_testo}**]")
        else:
            parti.append(gap_testo)
    return "   |   ".join(parti)

# ============================================================
# MACRO-SETTORI PER I TIRATORI (diversi da quelli dei portieri: qui si raggruppa
# per "fascia" numerica orizzontale tra 6m/bt/9m, non per riga radiale)
# lw -> lw1+lw2 | rw -> rw1+rw2 | fb -> fb1+fb2+fb3
# settore 1 -> 6m1+bt1+9m1 | settore 1,5 -> 6m1,5+bt1,5+9m1,5 | ... | settore 3 -> 6m3+bt3+9m3
# 7m è sia macro che micro (singolo)
# ============================================================
ORDINE_MACRO_TIRATORI = ['7m', 'lw', 'rw', '1', '1,5', '2', '2,5', '3', 'fb']
ETICHETTA_MACRO_TIRATORI = {
    '7m': '7m', 'lw': 'LW', 'rw': 'RW', 'fb': 'FB',
    '1': 'Sector 1', '1,5': 'Sector 1.5', '2': 'Sector 2', '2,5': 'Sector 2.5', '3': 'Sector 3',
}

def mappa_macro_settore_tiratori(zona):
    z = _normalizza_zona(zona)
    if z == '7m':
        return z
    if z.startswith('lw'):
        return 'lw'
    if z.startswith('rw'):
        return 'rw'
    if z.startswith('fb'):
        return 'fb'
    m = re.match(r'^(6m|bt|9m)(1,5|2,5|1|2|3)$', z)
    if m:
        return m.group(2)
    return None

# Ordine "naturale" dei tasti della tastiera dei settori di campo (come da immagine allegata)
ORDINE_TASTIERA_TIRATORI = [
    ['7m'],
    ['lw1', 'lw2', 'rw2', 'rw1'],
    ['6m1', '6m1,5', '6m2', '6m2,5', '6m3'],
    ['bt1', 'bt1,5', 'bt2', 'bt2,5', 'bt3'],
    ['9m1', '9m1,5', '9m2', '9m2,5', '9m3'],
    ['fb1', 'fb2', 'fb3'],
]
TUTTI_I_TASTI_TIRATORI = [t for riga in ORDINE_TASTIERA_TIRATORI for t in riga]

# ============================================================
# PULSANTIERA INTERATTIVA (la tastiera dei settori di campo, come vera pulsantiera cliccabile,
# colorata con la stessa heat map a 4 colori usata nell'immagine statica/PDF)
# ============================================================
# ============================================================
# PULSANTIERA INTERATTIVA (la tastiera dei settori di campo, come vera pulsantiera cliccabile,
# colorata con la stessa heat map a 4 colori usata nell'immagine statica/PDF). Ogni pulsante
# viene colorato individualmente incapsulandolo in un st.container(key=...): dalla versione 1.32
# Streamlit aggiunge automaticamente la classe CSS "st-key-<key>" al contenitore, permettendo di
# colorare quel singolo pulsante in modo affidabile (molto più robusto del vecchio trucco a
# marcatore/fratello CSS). Se la versione di Streamlit è troppo vecchia per supportarlo, si
# ripiega automaticamente sulla vecchia tecnica.
# ============================================================
_CONTAINER_KEY_SUPPORTATO = 'key' in inspect.signature(st.container).parameters

# ============================================================
# IDENTITÀ GIOCATORE: ignora il numero di maglia (che può cambiare nel tempo, tra club e
# nazionale, ecc.) e il marcatore "[G]". "#15 - Muqolli A." e "#7 - Muqolli A." sono la stessa
# identità ("Muqolli A."); "Panitti [G]" diventa "Panitti". Questa identità è la chiave usata
# ovunque nell'app per raggruppare, filtrare, e agganciare foto/note ai giocatori.
# ============================================================
def estrai_numero_e_nome_base(nome_completo):
    """Da '#15 - Muqolli A.' o 'Panitti [G]' o 'Angiolini' estrae (numero_maglia_o_None,
    nome_base_senza_numero_e_senza_[G])."""
    testo = str(nome_completo).strip()
    testo_senza_gk = re.sub(r'\s*\[g\]\s*', '', testo, flags=re.IGNORECASE).strip()
    m = re.match(r'^#?\s*(\d+)\s*-\s*(.+)$', testo_senza_gk)
    if m:
        return m.group(1), m.group(2).strip()
    return None, testo_senza_gk

def identita_giocatore(nome_completo):
    """Chiave d'identità stabile per il giocatore, ignorando numero di maglia e '[G]'."""
    _, nome_base = estrai_numero_e_nome_base(nome_completo)
    return nome_base

def assicura_colonna_id(df, colonna_clean, colonna_id):
    """Rete di sicurezza: garantisce che 'df' abbia la colonna_id (PORTIERE_ID/TIRATORE_ID),
    calcolandola al volo da colonna_clean se manca (dati salvati prima che l'identità
    giocatore esistesse). Se manca anche colonna_clean, crea una colonna_id vuota per evitare
    KeyError altrove. Non modifica df in place."""
    if colonna_id in df.columns:
        return df
    df = df.copy()
    if colonna_clean in df.columns:
        df[colonna_id] = df[colonna_clean].apply(identita_giocatore)
    else:
        df[colonna_id] = pd.Series(dtype=object)
    return df

def numeri_maglia_visti(nomi_grezzi):
    """Dato un elenco di nomi grezzi (con numero) di uno stesso giocatore in un certo
    sottoinsieme di partite, restituisce una stringa con il/i numero/i di maglia usati:
    un solo numero se sempre lo stesso, più numeri separati da '/' se sono cambiati,
    stringa vuota se il giocatore non ha mai avuto un numero."""
    numeri = []
    for nome in nomi_grezzi:
        numero, _ = estrai_numero_e_nome_base(nome)
        if numero and numero not in numeri:
            numeri.append(numero)
    return '/'.join(f"#{n}" for n in numeri) if numeri else ''

def _chiave_css_sicura(testo):
    """Rende una stringa sicura da usare sia come key di Streamlit sia come classe CSS
    (niente virgole, spazi o altri caratteri che romperebbero il selettore)."""
    return re.sub(r'[^A-Za-z0-9_-]', '-', str(testo))

def _pulsante_colorato(etichetta, colore_sfondo, disabilitato, selezionato, key):
    """Renderizza un singolo pulsante Streamlit colorato in modo puntuale via CSS, con un look
    'a tessera' (bordi squadrati, nessuna ombra) che replica la grafica della heat map originale.
    Restituisce True se il pulsante è stato premuto in questo rerun."""
    colore_testo = '#1a1a1a' if colore_sfondo in ('#f2d24b', '#e9edf3') else 'white'
    bordo = '3px solid #111111' if selezionato else f'2px solid {colore_sfondo}'
    key_sicura = _chiave_css_sicura(key)
    regole_base = (
        f'background-color: {colore_sfondo} !important;'
        f'color: {colore_testo} !important;'
        f'border: {bordo} !important;'
        f'border-radius: 3px !important;'
        f'box-shadow: none !important;'
        f'font-weight: 700;'
        f'font-size: 0.78rem;'
        f'white-space: pre-line;'
        f'line-height: 1.15;'
        f'height: 38px;'
        f'min-height: 38px;'
        f'padding: 0px 2px;'
        f'margin: 0px;'
    )
    regole_disabled = (
        f'background-color: {colore_sfondo} !important;'
        f'color: {colore_testo} !important;'
        f'opacity: 0.55;'
        f'border: 1px solid {colore_sfondo} !important;'
    )
    if _CONTAINER_KEY_SUPPORTATO:
        container_key = f"btnbox-{key_sicura}"
        st.markdown(
            f'<style>'
            f'div.st-key-{container_key} button {{ {regole_base} }}'
            f'div.st-key-{container_key} button:disabled {{ {regole_disabled} }}'
            f'</style>',
            unsafe_allow_html=True
        )
        with st.container(key=container_key):
            return st.button(etichetta, key=key, disabled=disabilitato, use_container_width=True)
    else:
        marcatore = f"btnmark-{key_sicura}"
        st.markdown(
            f'<span class="{marcatore}"></span>'
            f'<style>'
            f'.{marcatore} + div button {{ {regole_base} }}'
            f'.{marcatore} + div button:disabled {{ {regole_disabled} }}'
            f'.{marcatore} + div {{ margin-bottom: -8px; }}'
            f'</style>',
            unsafe_allow_html=True
        )
        return st.button(etichetta, key=key, disabled=disabilitato, use_container_width=True)

def pulsantiera_settori_campo(conteggi_totali, conteggi_goal, tasto_selezionato, key_prefix):
    """Disegna l'intera tastiera dei settori di campo come griglia di pulsanti cliccabili veri
    (stesso layout piramidale e stessa heat map a 4 colori dell'immagine statica), pensata per
    stare affiancata alla porta in una colonna stretta. Restituisce il nome del tasto appena
    cliccato in questo rerun, o None."""
    st.markdown(
        "<style>div[data-testid='stHorizontalBlock']{gap:0.3rem;}"
        "div[data-testid='column']{padding:0px 1px;}</style>",
        unsafe_allow_html=True
    )
    colori_heat = _colori_heatmap_frequenza(conteggi_totali)
    n_col_max = max(len(r) for r in ORDINE_TASTIERA_TIRATORI)
    cliccato = None
    for r, riga in enumerate(ORDINE_TASTIERA_TIRATORI):
        spazio = (n_col_max - len(riga)) / 2
        larghezze = ([spazio] if spazio > 0 else []) + [1] * len(riga) + ([spazio] if spazio > 0 else [])
        colonne = st.columns(larghezze)
        colonne_tasti = colonne[1:-1] if spazio > 0 else colonne
        for col_tasto, tasto in zip(colonne_tasti, riga):
            tot = conteggi_totali.get(tasto, 0)
            goal = conteggi_goal.get(tasto, 0)
            pct_testo = f"{goal}/{tot}={goal/tot*100:.0f}%" if tot > 0 else "0/0"
            etichetta = f"{tasto}\n{pct_testo}"
            colore = colori_heat.get(tasto, '#e9edf3')
            with col_tasto:
                premuto = _pulsante_colorato(
                    etichetta, colore, disabilitato=(tot == 0),
                    selezionato=(tasto == tasto_selezionato), key=f"{key_prefix}_{tasto}"
                )
            if premuto:
                cliccato = tasto
    return cliccato

# ============================================================
# EXPECTED SAVES % (efficacia attesa per settore specifico) — "S.P. Value"
# Valore di riferimento di base: il lavoro storico di video-analisi di Sergio Palazzi.
# Questo valore resta SEMPRE disponibile in memoria, qualunque sia il profilo attivo
# selezionato altrove nell'app (vedi 'profili_expected_stato' in session_state).
# ============================================================
SP_VALUE_DEFAULT = {
    'lw1': 46, 'lw2': 39,
    'rw1': 48, 'rw2': 36,
    '6m1': 30, '6m1,5': 30, '6m2': 29, '6m2,5': 24, '6m3': 24,
    'bt1': 34, 'bt1,5': 34, 'bt2': 25, 'bt2,5': 34, 'bt3': 34,
    '9m1': 60, '9m1,5': 60, '9m2': 52, '9m2,5': 55, '9m3': 55,
    '7m': 25,
    'fb1': 22, 'fb2': 22, 'fb3': 22,
}

def _normalizza_zona(zona):
    """Normalizza la stringa del settore per il confronto (rimuove spazi e suffissi non numerici
    come '-'/'+' che a volte compaiono nei file Excel, es. '9m 2' o '6m3-')."""
    z = str(zona).strip().lower().replace(' ', '')
    z = z.rstrip('-+')
    return z

def ottieni_expected_pct(zona):
    """Restituisce il valore di Expected Saves % per un settore specifico, secondo il profilo
    attualmente attivo (S.P. Value di default, oppure un profilo calcolato dai dati). Se il
    profilo attivo non copre quel settore, ripiega su S.P. Value. Restituisce None se anche
    S.P. Value non lo copre."""
    z = _normalizza_zona(zona)
    stato = st.session_state.get('profili_expected_stato')
    if not stato:
        return SP_VALUE_DEFAULT.get(z)
    profilo_attivo = stato['profili'].get(stato['attivo'], {})
    if z in profilo_attivo:
        return profilo_attivo[z]
    return stato['profili'].get('S.P. Value', SP_VALUE_DEFAULT).get(z)

def ottieni_expected_goal_pct(zona):
    """Expected Goal % per i TIRATORI: è semplicemente il ribaltamento dell'Expected Save %
    dei portieri (100 - Expected Save %). Es. 7m: Expected Save % portiere = 25% -> Expected
    Goal % tiratore = 75%. Restituisce None se il settore non è mappato."""
    save_pct = ottieni_expected_pct(zona)
    return (100 - save_pct) if save_pct is not None else None

def calcola_profilo_expected_da_dati(elenco_partite_gk):
    """Calcola un profilo di Expected Save % settore per settore a partire dai dati REALI di un
    insieme di partite portieri: per ciascun settore, Expected Save % = salvataggi reali /
    (salvataggi + gol) in quel settore, su tutte le partite fornite. I settori senza tiri
    registrati vengono omessi (chi legge il profilo ripiega su S.P. Value per quelli)."""
    if not elenco_partite_gk:
        return {}
    frammenti = [m['dati'] for m in elenco_partite_gk]
    df_tot = pd.concat(frammenti, ignore_index=True)
    profilo = {}
    for zona in SP_VALUE_DEFAULT.keys():
        df_z = df_tot[df_tot['TIRO_CLEAN'].apply(_normalizza_zona) == zona]
        s = len(df_z[df_z['RESULT_CLEAN'].isin(['save', 's'])])
        g = len(df_z[df_z['RESULT_CLEAN'].isin(['goal', 'g'])])
        if s + g > 0:
            profilo[zona] = round(s / (s + g) * 100, 1)
    return profilo

def applica_colori_expected(df_settore):
    """Restituisce una versione 'stilizzata' della tabella per settore specifico, con lo sfondo
    di ogni riga colorato in base al confronto tra Efficiency % reale ed Expected Efficiency %:
    verde = sopra media, giallo = esattamente in media, rosso = sotto media.
    Le righe senza un valore Expected Efficiency % mappato restano senza colore."""
    def _colora_riga(row):
        expected = row.get('Expected Efficiency %', '')
        if expected == '' or expected is None:
            return [''] * len(row)
        valore_reale = row['Efficiency %']
        differenza = valore_reale - expected
        if abs(differenza) < 0.05:
            colore = 'background-color: #ffeb9c'
        elif differenza > 0:
            colore = 'background-color: #c6efce'
        else:
            colore = 'background-color: #ffc7ce'
        return [colore] * len(row)

    formattatori_disponibili = {
        'Save %': lambda x: f"{x:.1f}%",
        'Efficiency %': lambda x: f"{x:.1f}%",
        'Expected Efficiency %': lambda x: f"{x:.0f}%" if x != '' else '',
        'GPI': lambda x: f"{x:+.1f}",
    }
    formattatori_da_usare = {c: f for c, f in formattatori_disponibili.items() if c in df_settore.columns}
    return df_settore.style.apply(_colora_riga, axis=1).format(formattatori_da_usare)

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
def raccogli_stagione_per_portiere(elenco_partite, identita_portiere):
    """Scorre l'elenco di partite (in ordine cronologico) e raccoglie, per il portiere indicato
    (per identità, ignorando eventuali numeri di maglia diversi), solo le partite in cui ha
    effettivamente affrontato almeno un tiro. Le partite in cui non è sceso in campo vengono
    escluse (non contano come 0)."""
    partite_ordinate = sorted(elenco_partite, key=lambda p: p['data'])
    frammenti = []
    lista_partite = []
    for match in partite_ordinate:
        df_m = match['dati']
        df_gk = df_m[df_m['PORTIERE_ID'] == identita_portiere].copy()
        if df_gk.empty:
            continue
        df_gk['Match_Label'] = f"{match['nome']} ({match['data']})"
        s, g, m_, pct, eff = calcola_metriche_gruppo(df_gk)
        df_gk_stress = df_gk[df_gk['Is_Stress_Test'] == True]
        gpi_money_time = df_gk_stress['GPI_Tiro'].sum() if not df_gk_stress.empty else None
        s_mt, g_mt, m_mt, pct_mt, eff_mt = calcola_metriche_gruppo(df_gk_stress)
        frammenti.append(df_gk)
        lista_partite.append({
            'label': f"{match['nome']} ({match['data']})",
            'data': match['data'],
            'gpi_totale': df_gk['GPI_Tiro'].sum(),
            'pct': pct,
            'eff': eff,
            'tiri': len(df_gk),
            'saves': s,
            'money_time_gpi': gpi_money_time,
            'money_time_tiri': len(df_gk_stress),
            'money_time_saves': s_mt,
            'money_time_pct': pct_mt,
            'casa_trasferta': determina_casa_trasferta(match['squadra'], match.get('squadra_home'), match.get('squadra_away')),
            'numero_maglia': numeri_maglia_visti(df_gk['PORTIERE_CLEAN'].unique()),
        })
    df_aggregato = pd.concat(frammenti, ignore_index=True) if frammenti else pd.DataFrame()
    return df_aggregato, lista_partite

def raccogli_stagione_per_squadra(elenco_partite, nome_squadra):
    """Filtra le partite della squadra indicata e raccoglie, per ciascuna identità di portiere
    che vi ha giocato, il proprio storico stagionale (stessa logica di raccogli_stagione_per_portiere)."""
    partite_squadra = sorted([p for p in elenco_partite if p['squadra'] == nome_squadra], key=lambda p: p['data'])
    frammenti = [m['dati'] for m in partite_squadra]
    df_aggregato = pd.concat(frammenti, ignore_index=True) if frammenti else pd.DataFrame()

    portieri_unici = sorted(set(
        gk for m in partite_squadra for gk in m['dati']['PORTIERE_ID'].dropna().unique()
    ))
    dati_per_portiere = {}
    for gk in portieri_unici:
        _, lista_partite_gk = raccogli_stagione_per_portiere(partite_squadra, gk)
        dati_per_portiere[gk] = lista_partite_gk
    return df_aggregato, dati_per_portiere

def combina_numeri_maglia(lista_partite):
    """Combina i numeri di maglia visti su più partite (ciascuna con il proprio campo
    'numero_maglia' già calcolato) in un'unica stringa, senza duplicati."""
    numeri = []
    for p in (lista_partite or []):
        nm = p.get('numero_maglia', '')
        if nm:
            for singolo in nm.split('/'):
                if singolo not in numeri:
                    numeri.append(singolo)
    return '/'.join(numeri)

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
        expected = ottieni_expected_pct(settore)
        righe_settore.append({
            'Zone': settore, 'Saves': s2, 'Goals': g2, 'Miss': m2,
            'Save %': round(pct2, 1), 'Efficiency %': round(eff2, 1),
            'Expected Efficiency %': expected if expected is not None else '',
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
        'tabella_settore': pd.DataFrame(righe_settore) if righe_settore else pd.DataFrame({
            'Zone': [], 'Saves': [], 'Goals': [], 'Miss': [],
            'Save %': [], 'Efficiency %': [], 'Expected Efficiency %': [], 'GPI': []
        }),
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

def _disegna_grafico_blocchi_pdf(df_blocchi, output_path):
    """Disegna il grafico a blocchi da 10 minuti (linea % sopra, barre GPI sotto) con Matplotlib,
    per il PDF — evita del tutto la dipendenza da Kaleido/Chrome, non sempre disponibile
    negli ambienti di hosting online come Streamlit Cloud."""
    blocchi = df_blocchi['Block'].tolist()
    percentuali = df_blocchi['Save %'].tolist()
    gpi_totali = df_blocchi['Total GPI'].tolist()
    x = list(range(len(blocchi)))

    fig, (ax_pct, ax_gpi) = plt.subplots(2, 1, figsize=(10, 6.5), dpi=150, sharex=True)

    ax_pct.plot(x, percentuali, marker='o', color='#1f77b4', linewidth=3, markersize=9)
    for xi, v in zip(x, percentuali):
        ax_pct.annotate(f"{v:.0f}%", (xi, v), textcoords='offset points', xytext=(0, 10),
                        ha='center', fontsize=10, fontweight='bold', color='#1f77b4')
    ax_pct.set_ylabel('Save %')
    ax_pct.set_ylim(0, max(110, max(percentuali, default=0) * 1.2))
    ax_pct.set_title('Save % per block', fontsize=11)
    ax_pct.grid(axis='y', linestyle='--', alpha=0.3)
    ax_pct.spines['top'].set_visible(False)
    ax_pct.spines['right'].set_visible(False)

    colori_barre = ['#ff7f0e'] * len(gpi_totali)
    ax_gpi.bar(x, gpi_totali, color=colori_barre, width=0.5)
    max_abs_gpi = max(1, max((abs(v) for v in gpi_totali), default=1))
    for xi, v in zip(x, gpi_totali):
        offset = max_abs_gpi * 0.06
        va = 'bottom' if v >= 0 else 'top'
        ax_gpi.annotate(f"{v:+.1f}", (xi, v + (offset if v >= 0 else -offset)),
                        ha='center', va=va, fontsize=10, fontweight='bold', color='#ff7f0e')
    ax_gpi.axhline(0, color='black', linewidth=1)
    ax_gpi.set_ylabel('Total GPI')
    ax_gpi.set_xlabel('Game block (minutes)')
    ax_gpi.set_xticks(x)
    ax_gpi.set_xticklabels(blocchi)
    ax_gpi.set_ylim(-max_abs_gpi * 1.35, max_abs_gpi * 1.35)
    ax_gpi.set_title('Total GPI per block', fontsize=11)
    ax_gpi.grid(axis='y', linestyle='--', alpha=0.3)
    ax_gpi.spines['top'].set_visible(False)
    ax_gpi.spines['right'].set_visible(False)

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close(fig)

# ============================================================
# DISEGNO PORTA (9 settori T1-T9) E TASTIERA (settori di campo) PER I TIRATORI
# Condivisi tra schermata (st.pyplot) e PDF (RLImage), stesso stile grafico del resto dell'app.
# ============================================================
ORDINE_PORTA = [['T1', 'T2', 'T3'], ['T4', 'T5', 'T6'], ['T7', 'T8', 'T9']]

def _colore_expected(reale_pct, expected_pct):
    """Verde se il tiratore è sopra la media attesa, giallo se coincide, rosso se sotto."""
    if reale_pct is None or expected_pct is None:
        return '#2c4a6e'  # colore neutro (nessun confronto disponibile)
    diff = reale_pct - expected_pct
    if abs(diff) < 0.05:
        return '#c9a600'
    elif diff > 0:
        return '#1e7d34'
    else:
        return '#b5231a'

def _colori_heatmap_porta(conteggi):
    """Heat map a 4 toni di blu per i 9 settori della porta, in base alla frequenza dei tiri:
    blu scuro = settori più frequentati, blu medio = un po' meno, azzurro = ancora meno,
    colore di sfondo = nessun tiro. Stessa logica quantile di _colori_heatmap_frequenza."""
    valori = sorted(set(v for v in conteggi.values() if v > 0), reverse=True)
    colori = {}
    if not valori:
        return {k: '#e9edf3' for k in conteggi}
    for k, v in conteggi.items():
        if v <= 0:
            colori[k] = '#e9edf3'
        else:
            rank_pct = 1 - (sorted(valori, reverse=True).index(v) / max(1, len(valori) - 1)) if len(valori) > 1 else 1
            if rank_pct >= 0.66:
                colori[k] = '#0b3d68'
            elif rank_pct >= 0.33:
                colori[k] = '#2f6fa8'
            else:
                colori[k] = '#7fb8e0'
    return colori

def disegna_porta(conteggi_totali, conteggi_goal, colore_cornice=None, titolo=None):
    """Disegna la porta con i 9 settori (T1-T9): sotto ogni settore, 'goal/totale = pct%'.
    Ogni settore è colorato con una heat map a 4 toni di blu in base alla frequenza dei tiri.
    colore_cornice: se fornito ('#rrggbb'), colora il bordo esterno (usato quando è selezionato
    un settore di campo specifico, in base al confronto con l'Expected Goal %)."""
    fig, ax = plt.subplots(figsize=(2.9, 2.5), dpi=150)
    margine_cornice = 0.22
    ax.set_xlim(-margine_cornice, 3 + margine_cornice)
    ax.set_ylim(-margine_cornice, 3 + margine_cornice)
    ax.set_aspect('equal')
    ax.axis('off')

    bordo = colore_cornice if colore_cornice else '#2c4a6e'
    fig.patch.set_facecolor('white')
    ax.add_patch(plt.Rectangle((-margine_cornice, -margine_cornice), 3 + 2 * margine_cornice, 3 + 2 * margine_cornice,
                                facecolor=bordo, edgecolor='none', zorder=0))

    colori_heat = _colori_heatmap_porta(conteggi_totali)
    for r, riga in enumerate(ORDINE_PORTA):
        for c, sett in enumerate(riga):
            x0 = c
            y0 = 2 - r
            tot = conteggi_totali.get(sett, 0)
            goal = conteggi_goal.get(sett, 0)
            pct = (goal / tot * 100) if tot > 0 else None
            colore_cella = colori_heat.get(sett, '#e9edf3')
            testo_colore = '#1a1a1a' if colore_cella in ('#7fb8e0', '#e9edf3') else 'white'
            ax.add_patch(plt.Rectangle((x0, y0), 1, 1, facecolor=colore_cella, edgecolor='white', linewidth=1.5, zorder=1))
            ax.text(x0 + 0.5, y0 + 0.62, sett, ha='center', va='center', fontsize=8.5,
                    color=testo_colore, fontweight='bold', zorder=2)
            testo_val = f"{goal}/{tot}={pct:.0f}%" if tot > 0 else "0/0"
            ax.text(x0 + 0.5, y0 + 0.30, testo_val, ha='center', va='center', fontsize=7.3,
                    color=testo_colore, zorder=2)
    if titolo:
        ax.set_title(titolo, fontsize=11, color='#15304f', pad=10)
    fig.tight_layout()
    return fig

def _colori_heatmap_frequenza(conteggi):
    """Assegna a ciascun settore uno dei 4 livelli della heat map in base alla frequenza dei tiri
    (quartili sui settori con almeno un tiro): rosso = più ricorrenti, arancio, giallo, sfondo = nessun tiro."""
    valori = sorted(set(v for v in conteggi.values() if v > 0), reverse=True)
    colori = {}
    if not valori:
        return {k: '#e9edf3' for k in conteggi}
    soglie = valori[max(0, len(valori)//3 - 1)] if len(valori) >= 3 else valori[0]
    soglia_alta = valori[0]
    soglia_media = valori[len(valori)//3] if len(valori) > 3 else (valori[1] if len(valori) > 1 else valori[0])
    soglia_bassa = valori[-1]
    for k, v in conteggi.items():
        if v <= 0:
            colori[k] = '#e9edf3'
        else:
            rank_pct = 1 - (sorted(valori, reverse=True).index(v) / max(1, len(valori) - 1)) if len(valori) > 1 else 1
            if rank_pct >= 0.66 or v == soglia_alta:
                colori[k] = '#d13b2e'
            elif rank_pct >= 0.33:
                colori[k] = '#f0872b'
            else:
                colori[k] = '#f2d24b'
    return colori

def disegna_tastiera(conteggi_totali, conteggi_goal, tasto_selezionato=None):
    """Disegna la tastiera dei settori di campo per i PDF, con lo stesso stile 'a barre larghe'
    della pulsantiera interattiva a schermo (una riga per fascia, celle rettangolari a piena
    larghezza): più leggibile della vecchia griglia quadrata, che non aveva spazio per le
    percentuali più lunghe. Heat map a 4 colori (frequenza tiri); il tasto eventualmente
    selezionato viene evidenziato con un bordo nero spesso."""
    colori_heat = _colori_heatmap_frequenza(conteggi_totali)
    n_righe = len(ORDINE_TASTIERA_TIRATORI)
    larghezza_totale = 10  # unità arbitrarie: ogni riga occupa sempre l'intera larghezza
    altezza_cella = 0.62
    spazio_riga = 1.0

    fig, ax = plt.subplots(figsize=(9.5, 5.6), dpi=150)
    ax.set_xlim(0, larghezza_totale)
    ax.set_ylim(0, n_righe * spazio_riga)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    for r, riga in enumerate(ORDINE_TASTIERA_TIRATORI):
        larghezza_cella = larghezza_totale / len(riga)
        y0 = (n_righe - 1 - r) * spazio_riga + (spazio_riga - altezza_cella) / 2
        for c, tasto in enumerate(riga):
            x0 = c * larghezza_cella
            tot = conteggi_totali.get(tasto, 0)
            goal = conteggi_goal.get(tasto, 0)
            pct = (goal / tot * 100) if tot > 0 else None
            colore = colori_heat.get(tasto, '#e9edf3')
            bordo_larghezza = 2.6 if tasto == tasto_selezionato else 1.2
            colore_bordo = 'black' if tasto == tasto_selezionato else 'white'
            margine = larghezza_cella * 0.04
            ax.add_patch(plt.Rectangle((x0 + margine, y0), larghezza_cella - 2 * margine, altezza_cella,
                                        facecolor=colore, edgecolor=colore_bordo, linewidth=bordo_larghezza, zorder=1))
            testo_colore = '#222222' if colore in ('#f2d24b', '#e9edf3') else 'white'
            centro_x = x0 + larghezza_cella / 2
            testo_val = f"{goal}/{tot}={pct:.0f}%" if tot > 0 else "0/0"
            ax.text(centro_x, y0 + altezza_cella * 0.66, tasto, ha='center', va='center', fontsize=10,
                    color=testo_colore, fontweight='bold', zorder=2)
            ax.text(centro_x, y0 + altezza_cella * 0.27, testo_val, ha='center', va='center', fontsize=9,
                    color=testo_colore, zorder=2)
    fig.tight_layout()
    return fig

# ============================================================
# PORTIERI: PARSING FILE (stessa identica logica prima incorporata nel loop di upload,
# ora estratta in una funzione riusabile anche dal nuovo file unificato)
# ============================================================
def elabora_file_portieri(df_raw):
    """Prende il DataFrame grezzo (colonne tipo PORTIERE/GK, TIRO, RESULT, TIMELINE) e
    restituisce il DataFrame arricchito con tutte le colonne calcolate (GPI, Money Time, ecc.).
    Solleva ValueError se manca una colonna essenziale."""
    def _trova_colonna(parole_chiave):
        for c in df_raw.columns:
            c_low = str(c).lower()
            if any(p in c_low for p in parole_chiave):
                return c
        return None

    c_gk = _trova_colonna(['gk', 'portiere', 'porter'])
    c_tiro = _trova_colonna(['tiro', 'shot'])
    c_res = _trova_colonna(['result', 'esito', 'risultato'])
    c_time = _trova_colonna(['timeline', 'tempo', 'minut'])

    mancanti = [nome for nome, val in [('PORTIERE/GK', c_gk), ('TIRO', c_tiro),
                ('RESULT', c_res), ('TIMELINE', c_time)] if val is None]
    if mancanti:
        raise ValueError(f"Missing required column(s): {', '.join(mancanti)}")

    df = df_raw.copy()
    df['PORTIERE_CLEAN'] = df[c_gk].astype(str).str.strip()
    df['PORTIERE_ID'] = df['PORTIERE_CLEAN'].apply(identita_giocatore)
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

    def _calcola_blocco_stringa(m):
        if m < 10: return '0-10'
        elif m < 20: return '10-20'
        elif m < 30: return '20-30'
        elif m < 40: return '30-40'
        elif m < 50: return '40-50'
        else: return '50-60'
    df['Blocco_10m'] = df['Minuti_Gara'].apply(_calcola_blocco_stringa)
    return df

# ============================================================
# TIRATORI: PARSING FILE, METRICHE, TOP SCORERS, MACRO-SETTORI
# ============================================================
def calcola_money_time_flag(minuti, scarto):
    return (minuti >= 50) and (-5 <= scarto <= 5)

def elabora_file_tiratori(df_raw):
    """Prende il DataFrame grezzo letto da un file Excel dei tiratori (TIRATORE, TIRO,
    GOAL SECTOR, RESULT, TIMELINE) e restituisce il DataFrame arricchito con tutte le colonne
    calcolate necessarie al resto dell'app. Solleva ValueError se manca una colonna essenziale."""
    def _trova_colonna(parole_chiave):
        for c in df_raw.columns:
            c_low = str(c).lower()
            if any(p in c_low for p in parole_chiave):
                return c
        return None

    c_tiratore = _trova_colonna(['tiratore', 'shooter', 'giocatore', 'player'])
    c_tiro = _trova_colonna(['tiro', 'shot'])
    c_goalsector = _trova_colonna(['goal sector', 'goal_sector', 'settore porta', 'net sector'])
    c_result = _trova_colonna(['result', 'esito', 'risultato'])
    c_time = _trova_colonna(['timeline', 'tempo', 'minut'])

    mancanti = [nome for nome, val in [('TIRATORE', c_tiratore), ('TIRO', c_tiro),
                ('GOAL SECTOR', c_goalsector), ('RESULT', c_result), ('TIMELINE', c_time)] if val is None]
    if mancanti:
        raise ValueError(f"Missing required column(s): {', '.join(mancanti)}")

    df = df_raw.copy()
    df['TIRATORE_CLEAN'] = df[c_tiratore].astype(str).str.strip()
    df['TIRATORE_ID'] = df['TIRATORE_CLEAN'].apply(identita_giocatore)
    df['TIRO_CLEAN'] = df[c_tiro].astype(str).str.strip()
    df['GOAL_SECTOR_CLEAN'] = df[c_goalsector].astype(str).str.strip()
    df['RESULT_CLEAN'] = df[c_result].astype(str).str.lower().str.strip()

    minuti_list, tempo_list, scarti_list, punteggi_list = [], [], [], []
    for val in df[c_time]:
        m_tot, t_s, sc, pt = analizza_timeline(val)
        minuti_list.append(m_tot); tempo_list.append(t_s); scarti_list.append(sc); punteggi_list.append(pt)
    df['Minuti_Gara'] = minuti_list
    df['Tempo_Visuale'] = tempo_list
    df['Scarto_Punteggio'] = scarti_list
    df['Punteggio_Live'] = punteggi_list

    df['macro_settore_tir'] = df['TIRO_CLEAN'].apply(mappa_macro_settore_tiratori)
    df['Is_Money_Time'] = df.apply(lambda r: calcola_money_time_flag(r['Minuti_Gara'], r['Scarto_Punteggio']), axis=1)
    return df

# ============================================================
# FILE UNIFICATO (formato unico HOME/AWAY): una sola tabella per l'intera gara, con il portiere
# che difende marcato con "[G]" in una delle due colonne squadra, e l'avversario che tira
# nell'altra. Da qui si ricavano SEPARATAMENTE i 4 dataframe "storici" (portiere-casa,
# portiere-trasferta, tiratori-casa, tiratori-trasferta, riusando le stesse identiche funzioni di
# elaborazione già in uso) più il dataframe "testa a testa" per l'analisi incrociata.
# ============================================================
def _e_portiere(valore):
    return isinstance(valore, str) and '[g]' in valore.lower()

def elabora_file_unificato(df_raw, squadra_home, squadra_away):
    """Restituisce (df_gk_home, df_gk_away, df_tir_home, df_tir_away, df_h2h). Ognuno dei 4
    dataframe principali è già nello stesso formato prodotto da elabora_file_portieri /
    elabora_file_tiratori (stesse colonne calcolate), pronto per essere salvato come al solito.
    df_h2h porta anche il nome reale delle due squadre, necessario per il filtro squadra
    dell'analisi testa a testa."""
    def _trova_colonna(parole_chiave):
        for c in df_raw.columns:
            c_low = str(c).lower()
            if any(p in c_low for p in parole_chiave):
                return c
        return None

    c_home = _trova_colonna(['home'])
    c_away = _trova_colonna(['away'])
    c_tiro = _trova_colonna(['tiro', 'shot'])
    c_result = _trova_colonna(['result', 'esito', 'risultato'])
    c_goalsector = _trova_colonna(['goal sector', 'goal_sector', 'settore porta', 'net sector'])
    c_time = _trova_colonna(['timeline', 'tempo', 'minut'])

    mancanti = [nome for nome, val in [('HOME', c_home), ('AWAY', c_away), ('TIRO', c_tiro),
                ('RESULT', c_result), ('TIMELINE', c_time)] if val is None]
    if mancanti:
        raise ValueError(f"Missing required column(s): {', '.join(mancanti)}")

    righe_gk_home, righe_gk_away = [], []
    righe_tir_home, righe_tir_away = [], []
    righe_h2h = []

    for _, r in df_raw.iterrows():
        val_home = str(r[c_home]).strip() if pd.notna(r[c_home]) else ''
        val_away = str(r[c_away]).strip() if pd.notna(r[c_away]) else ''
        home_ha_nome = bool(val_home)
        away_ha_nome = bool(val_away)
        if not home_ha_nome and not away_ha_nome:
            continue  # riga vuota: niente da registrare

        home_e_gk = home_ha_nome and _e_portiere(val_home)
        away_e_gk = away_ha_nome and _e_portiere(val_away)

        # Regola generale: chi ha "[G]" è il portiere, chi non ce l'ha è il tiratore — vale sia
        # quando sono compilate entrambe le colonne (coppia portiere-vs-tiratore sulla stessa
        # riga, utile anche per il testa a testa) sia quando ne è compilata solo una (tagging
        # "di una sola squadra": in quel caso manca il nome dell'altro attore, ma la riga resta
        # comunque valida per chi È stato taggato).
        if home_ha_nome and away_ha_nome and (home_e_gk == away_e_gk):
            continue  # entrambe compilate ma ambigue (nessuna o entrambe con "[G]"): scartata

        portiere = tiratore = None
        squadra_portiere = squadra_tiratore = None
        if home_ha_nome:
            if home_e_gk:
                portiere, squadra_portiere = val_home, 'home'
            else:
                tiratore, squadra_tiratore = val_home, 'home'
        if away_ha_nome:
            if away_e_gk:
                portiere, squadra_portiere = val_away, 'away'
            else:
                tiratore, squadra_tiratore = val_away, 'away'

        tiro = r[c_tiro]
        result = r[c_result]
        timeline = r[c_time]
        goal_sector = r[c_goalsector] if c_goalsector is not None else None

        if portiere:
            riga_gk = {'PORTIERE': portiere, 'TIRO': tiro, 'RESULT': result, 'TIMELINE': timeline}
            (righe_gk_home if squadra_portiere == 'home' else righe_gk_away).append(riga_gk)

        if tiratore:
            riga_tir = {'TIRATORE': tiratore, 'TIRO': tiro, 'GOAL SECTOR': goal_sector,
                        'RESULT': result, 'TIMELINE': timeline}
            (righe_tir_home if squadra_tiratore == 'home' else righe_tir_away).append(riga_tir)

        if portiere and tiratore:
            righe_h2h.append({
                'PORTIERE': portiere, 'TIRATORE': tiratore, 'TIRO': tiro, 'RESULT': result, 'TIMELINE': timeline,
                'Squadra_Portiere': squadra_home if squadra_portiere == 'home' else squadra_away,
                'Squadra_Tiratore': squadra_home if squadra_tiratore == 'home' else squadra_away,
            })

    def _elabora_o_vuoto_gk(righe):
        if not righe:
            return pd.DataFrame()
        return elabora_file_portieri(pd.DataFrame(righe))

    def _elabora_o_vuoto_tir(righe):
        if not righe:
            return pd.DataFrame()
        return elabora_file_tiratori(pd.DataFrame(righe))

    df_gk_home = _elabora_o_vuoto_gk(righe_gk_home)
    df_gk_away = _elabora_o_vuoto_gk(righe_gk_away)
    df_tir_home = _elabora_o_vuoto_tir(righe_tir_home)
    df_tir_away = _elabora_o_vuoto_tir(righe_tir_away)

    if righe_h2h:
        df_h2h = pd.DataFrame(righe_h2h)
        df_h2h['PORTIERE_CLEAN'] = df_h2h['PORTIERE'].astype(str).str.strip()
        df_h2h['TIRATORE_CLEAN'] = df_h2h['TIRATORE'].astype(str).str.strip()
        df_h2h['PORTIERE_ID'] = df_h2h['PORTIERE_CLEAN'].apply(identita_giocatore)
        df_h2h['TIRATORE_ID'] = df_h2h['TIRATORE_CLEAN'].apply(identita_giocatore)
        df_h2h['TIRO_CLEAN'] = df_h2h['TIRO'].astype(str).str.strip()
        df_h2h['RESULT_CLEAN'] = df_h2h['RESULT'].astype(str).str.lower().str.strip()
        minuti_list, scarti_list = [], []
        for val in df_h2h['TIMELINE']:
            m_tot, _, sc, _ = analizza_timeline(val)
            minuti_list.append(m_tot)
            scarti_list.append(sc)
        df_h2h['Minuti_Gara'] = minuti_list
        df_h2h['Scarto_Punteggio'] = scarti_list
        df_h2h['Is_Money_Time'] = df_h2h.apply(lambda r: calcola_money_time_flag(r['Minuti_Gara'], r['Scarto_Punteggio']), axis=1)
        df_h2h = df_h2h[['PORTIERE_CLEAN', 'TIRATORE_CLEAN', 'PORTIERE_ID', 'TIRATORE_ID', 'Squadra_Portiere', 'Squadra_Tiratore',
                          'TIRO_CLEAN', 'RESULT_CLEAN', 'Minuti_Gara', 'Scarto_Punteggio', 'Is_Money_Time']]
    else:
        df_h2h = pd.DataFrame(columns=['PORTIERE_CLEAN', 'TIRATORE_CLEAN', 'PORTIERE_ID', 'TIRATORE_ID', 'Squadra_Portiere', 'Squadra_Tiratore',
                                        'TIRO_CLEAN', 'RESULT_CLEAN', 'Minuti_Gara', 'Scarto_Punteggio', 'Is_Money_Time'])

    return df_gk_home, df_gk_away, df_tir_home, df_tir_away, df_h2h

def calcola_metriche_tiratori_gruppo(df):
    """(goal, totale, pct realizzazione) per un qualsiasi sottoinsieme di tiri di tiratori."""
    if df.empty:
        return 0, 0, 0.0
    tot = len(df)
    goal = len(df[df['RESULT_CLEAN'].isin(['goal', 'g'])])
    pct = (goal / tot * 100) if tot > 0 else 0.0
    return goal, tot, pct

def costruisci_conteggi_porta(df):
    """dict settore-porta(T1..T9) -> totale tiri, dict -> goal segnati."""
    tot, goal = {}, {}
    for sett in [t for riga in ORDINE_PORTA for t in riga]:
        df_s = df[df['GOAL_SECTOR_CLEAN'] == sett]
        tot[sett] = len(df_s)
        goal[sett] = len(df_s[df_s['RESULT_CLEAN'].isin(['goal', 'g'])])
    return tot, goal

def costruisci_conteggi_tastiera(df):
    """dict settore-campo -> totale tiri, dict -> goal segnati (sui tasti standard della tastiera)."""
    tot, goal = {}, {}
    for tasto in TUTTI_I_TASTI_TIRATORI:
        df_s = df[df['TIRO_CLEAN'].apply(lambda z: _normalizza_zona(z)) == tasto]
        tot[tasto] = len(df_s)
        goal[tasto] = len(df_s[df_s['RESULT_CLEAN'].isin(['goal', 'g'])])
    return tot, goal

def classifica_tiratori_per_volume(df, solo_money_time=False, n=None):
    """Restituisce TUTTI i giocatori (o i primi n se specificato) ordinati per NUMERO di tiri
    presi (non per %), in ordine decrescente di volume, con relativa % di realizzazione."""
    d = df[df['Is_Money_Time'] == True] if solo_money_time else df
    if d.empty:
        return pd.DataFrame({'Player': [], 'Shots': [], 'Goals': [], 'Goal %': []})
    righe = []
    for giocatore, df_g in d.groupby('TIRATORE_ID'):
        goal, tot, pct = calcola_metriche_tiratori_gruppo(df_g)
        righe.append({'Player': giocatore, 'Shots': tot, 'Goals': goal, 'Goal %': round(pct, 1)})
    df_classifica = pd.DataFrame(righe).sort_values('Shots', ascending=False).reset_index(drop=True)
    return df_classifica.head(n) if n else df_classifica

def tabella_macro_tiratori(df):
    """Tabella con il totale per ciascun macro-settore (LW, RW, FB, Sector 1...3, 7m, EG)."""
    righe = []
    for macro in ORDINE_MACRO_TIRATORI:
        df_m = df[df['macro_settore_tir'] == macro]
        if df_m.empty:
            continue
        goal, tot, pct = calcola_metriche_tiratori_gruppo(df_m)
        righe.append({'Macro-Zone': ETICHETTA_MACRO_TIRATORI[macro], 'Goals': goal, 'Shots': tot, 'Goal %': round(pct, 1)})
    return pd.DataFrame(righe) if righe else pd.DataFrame({'Macro-Zone': [], 'Goals': [], 'Shots': [], 'Goal %': []})

def tabella_micro_di_un_macro(df, macro):
    """Ripartizione nei micro-settori di uno specifico macro-settore selezionato."""
    df_m = df[df['macro_settore_tir'] == macro]
    righe = []
    for zona in sorted(df_m['TIRO_CLEAN'].apply(_normalizza_zona).unique()):
        df_z = df_m[df_m['TIRO_CLEAN'].apply(_normalizza_zona) == zona]
        goal, tot, pct = calcola_metriche_tiratori_gruppo(df_z)
        righe.append({'Zone': zona, 'Goals': goal, 'Shots': tot, 'Goal %': round(pct, 1)})
    return pd.DataFrame(righe) if righe else pd.DataFrame({'Zone': [], 'Goals': [], 'Shots': [], 'Goal %': []})

# ============================================================
# TESTA A TESTA (H2H): "chi soffre chi" — per un portiere, quali tiratori segnano di più contro
# di lui (ordinati dal più al meno "sofferto"); per un tiratore, contro quali portieri segna di
# meno (ordinati dal portiere più "sofferto" al meno).
# ============================================================
def classifica_h2h(df_h2h, giocatore, e_portiere):
    """df_h2h: dataframe con colonne PORTIERE_ID/TIRATORE_ID/RESULT_CLEAN/Squadra_*.
    giocatore è un'identità (nome senza numero di maglia). Restituisce una tabella con un
    avversario per riga, ordinata dal più al meno sofferto, con Goals/Shots/Goal % di quel
    confronto diretto e la squadra dell'avversario."""
    if e_portiere:
        df_g = df_h2h[df_h2h['PORTIERE_ID'] == giocatore]
        colonna_avversario, colonna_squadra_avv = 'TIRATORE_ID', 'Squadra_Tiratore'
    else:
        df_g = df_h2h[df_h2h['TIRATORE_ID'] == giocatore]
        colonna_avversario, colonna_squadra_avv = 'PORTIERE_ID', 'Squadra_Portiere'

    if df_g.empty:
        return pd.DataFrame({'Opponent': [], 'Team': [], 'Goals': [], 'Shots': [], 'Goal %': []})

    righe = []
    for avversario, df_a in df_g.groupby(colonna_avversario):
        tot = len(df_a)
        goal = len(df_a[df_a['RESULT_CLEAN'] == 'goal'])
        pct = (goal / tot * 100) if tot > 0 else 0.0
        squadra_avv = df_a[colonna_squadra_avv].iloc[0]
        righe.append({'Opponent': avversario, 'Team': squadra_avv, 'Goals': goal, 'Shots': tot, 'Goal %': round(pct, 1)})
    df_classifica = pd.DataFrame(righe)
    # Portiere: più sofferto = tiratore che gli segna più spesso (Goal % decrescente)
    # Tiratore: più sofferto = portiere contro cui segna meno spesso (Goal % crescente)
    # A parità di Goal %: più tiri prima (campione più solido); a parità anche di tiri: alfabetico.
    return df_classifica.sort_values(
        ['Goal %', 'Shots', 'Opponent'],
        ascending=[not e_portiere, False, True]
    ).reset_index(drop=True)

COLORE_ACCENTO = colors.HexColor('#15304f')
COLORE_TESTATA_TABELLE = colors.HexColor('#1b3a63')

def _tabella_metriche_pdf(voci, stili, larghezza_totale_cm=25.5):
    """Costruisce una riga di 'schede' in stile dashboard (etichetta piccola sopra, valore grande
    e in evidenza sotto) — usata per rendere le statistiche totali più prominenti nel PDF,
    invece di un'unica riga di testo compressa."""
    stile_etichetta = ParagraphStyle('EtichettaMetrica', parent=stili['Normal'], fontSize=8,
                                      textColor=colors.HexColor('#666666'), alignment=1, leading=10)
    stile_valore = ParagraphStyle('ValoreMetrica', parent=stili['Normal'], fontSize=18,
                                   textColor=COLORE_ACCENTO, alignment=1, fontName='Helvetica-Bold',
                                   spaceBefore=4)
    riga_etichette = [Paragraph(etichetta, stile_etichetta) for etichetta, _ in voci]
    riga_valori = [Paragraph(valore, stile_valore) for _, valore in voci]
    larghezza_colonna = larghezza_totale_cm / len(voci)
    t = Table([riga_etichette, riga_valori], colWidths=[larghezza_colonna * cm] * len(voci))
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#dddddd')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7f9fc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
    ]))
    return t

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

COLORE_EXPECTED_SOPRA = colors.HexColor('#c6efce')
COLORE_EXPECTED_UGUALE = colors.HexColor('#ffeb9c')
COLORE_EXPECTED_SOTTO = colors.HexColor('#ffc7ce')

def _tabella_settore_reportlab(df_settore, col_widths=None, font_size=7):
    """Come _df_to_reportlab_table, ma colora lo sfondo di ogni riga in base al confronto
    Efficiency % vs Expected Efficiency %: verde = sopra media, giallo = esattamente in media, rosso = sotto."""
    formattatori_disponibili = {
        'Save %': lambda x: f"{x:.1f}%",
        'Efficiency %': lambda x: f"{x:.1f}%",
        'Expected Efficiency %': lambda x: f"{x:.0f}%" if x != '' else '',
        'GPI': lambda x: f"{x:+.1f}",
    }
    df_formattato = df_settore.copy()
    for colonna, formattatore in formattatori_disponibili.items():
        if colonna in df_formattato.columns:
            df_formattato[colonna] = df_formattato[colonna].apply(formattatore)

    dati = [list(df_formattato.columns)] + df_formattato.astype(str).values.tolist()
    t = Table(dati, colWidths=col_widths, repeatRows=1)
    comandi_stile = [
        ('BACKGROUND', (0, 0), (-1, 0), COLORE_TESTATA_TABELLE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), font_size),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]
    for i, (_, row) in enumerate(df_settore.iterrows(), start=1):
        expected = row.get('Expected Efficiency %', '')
        if expected == '' or expected is None:
            colore_riga = colors.white if i % 2 == 1 else colors.HexColor('#f2f2f2')
        else:
            differenza = row['Efficiency %'] - expected
            if abs(differenza) < 0.05:
                colore_riga = COLORE_EXPECTED_UGUALE
            elif differenza > 0:
                colore_riga = COLORE_EXPECTED_SOPRA
            else:
                colore_riga = COLORE_EXPECTED_SOTTO
        comandi_stile.append(('BACKGROUND', (0, i), (-1, i), colore_riga))
    t.setStyle(TableStyle(comandi_stile))
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
        foto_gk_b64 = st.session_state.get('foto_giocatori', {}).get(identita_giocatore(gk))
        if foto_gk_b64:
            intestazione_gk = Table(
                [[RLImage(io.BytesIO(foto_base64_a_bytes(foto_gk_b64)), width=1.8 * cm, height=1.8 * cm),
                  Paragraph(f"Detailed Statistics — {gk}", sezione_stile)]],
                colWidths=[2.1 * cm, None]
            )
            intestazione_gk.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
        else:
            intestazione_gk = Paragraph(f"Detailed Statistics — {gk}", sezione_stile)
        elementi.append(KeepTogether([
            intestazione_gk,
            Paragraph(
                f"Total GPI: {info['gpi_totale']:+.1f}   |   Saves: {info['parate']}   |   "
                f"Goals Conceded: {info['gol']}   |   Save %: {info['pct']:.1f}%   |   Efficiency: {info['eff']:.1f}%",
                stili['Normal']
            ),
            Spacer(1, 0.2*cm),
            Paragraph("By specific shot zone", stili['Heading4']),
        ]))
        elementi.append(_tabella_settore_reportlab(info['tabella_settore'], font_size=7))
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
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_blocchi:
        _disegna_grafico_blocchi_pdf(df_blocchi, tmp_blocchi.name)
        larghezza_px, altezza_px = PILImage.open(tmp_blocchi.name).size
        larghezza_blocchi_cm, altezza_blocchi_cm = _dimensioni_adattate(larghezza_px, altezza_px, 16, 9)
        elementi.append(KeepTogether([
            Paragraph("Performance by 10-Minute Blocks", sezione_stile),
            RLImage(tmp_blocchi.name, width=larghezza_blocchi_cm*cm, height=altezza_blocchi_cm*cm)
        ]))
    elementi.append(Spacer(1, 0.3*cm))
    elementi.append(_df_to_reportlab_table(df_blocchi))

    doc.build(elementi, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buffer.seek(0)
    return buffer.getvalue()

def genera_pdf_stagione(titolo_report, righe_gpi_stagione, df_storico, dati_portieri, df_blocchi, df_stagione_totale, fig_blocchi, logo_squadra_b64=None):
    """Costruisce il PDF del report stagionale (portiere singolo o squadra) e lo restituisce come bytes.
    Stessa identità grafica (logo, colori, footer) del report di partita singola.
    logo_squadra_b64: se fornito, il logo della squadra compare in copertina accanto al logo
    dell'associazione (solo quando il report è per squadra)."""
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
           Paragraph(titolo_report, sottotitolo_stile)],
          (RLImage(io.BytesIO(foto_base64_a_bytes(logo_squadra_b64)), width=dimensione_logo_copertina, height=dimensione_logo_copertina)
           if logo_squadra_b64 else '')]],
        colWidths=[dimensione_logo_copertina + 0.4*cm, None, dimensione_logo_copertina + 0.2*cm]
    )
    blocco_titolo.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'CENTER'),
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
        Spacer(1, 0.2*cm),
        _tabella_metriche_pdf([
            ("Shots Faced", str(len(df_stagione_totale))),
            ("Saves", str(s_tot)),
            ("Goals Conceded", str(g_tot)),
            ("Save %", f"{pct_tot:.1f}%"),
            ("Efficiency %", f"{eff_tot:.1f}%"),
            ("Avg GPI (per shot)", f"{gpi_medio_tot:+.2f}"),
            ("Avg GPI (per match)", f"{media_cumulativa_gpi:+.2f}"),
        ], stili)
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
        larghezza_pdf_cm, altezza_pdf_cm = _dimensioni_adattate(larghezza_px, altezza_px, 25.5, 6.0)
        elementi.append(KeepTogether([
            Paragraph("Season GPI Trend (per match + cumulative average)", sezione_stile),
            RLImage(tmp_gpi.name, width=larghezza_pdf_cm*cm, height=altezza_pdf_cm*cm)
        ]))
    elementi.append(_separatore())

    # Season save % trend chart
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_pct:
        _disegna_grafico_stagione(dati_portieri, 'pct', 'Match Save %', tmp_pct.name)
        larghezza_px, altezza_px = PILImage.open(tmp_pct.name).size
        larghezza_pdf_cm, altezza_pdf_cm = _dimensioni_adattate(larghezza_px, altezza_px, 25.5, 6.0)
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
        df_gk_tot = df_stagione_totale[df_stagione_totale['PORTIERE_ID'] == gk]
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
        elementi.append(_tabella_settore_reportlab(info['tabella_settore'], font_size=7))
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
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_blocchi:
        _disegna_grafico_blocchi_pdf(df_blocchi, tmp_blocchi.name)
        larghezza_px, altezza_px = PILImage.open(tmp_blocchi.name).size
        larghezza_blocchi_cm, altezza_blocchi_cm = _dimensioni_adattate(larghezza_px, altezza_px, 16, 9)
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
GOOGLE_SHEETS_HEADER = ['nome', 'data', 'squadra', 'squadra_home', 'squadra_away', 'dati_json']

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
        worksheet = foglio.add_worksheet(title='SeasonData', rows=2000, cols=6)
        worksheet.append_row(GOOGLE_SHEETS_HEADER)
    return worksheet

def _match_a_riga_sheet(match):
    return [match['nome'], str(match['data']), match['squadra'],
            match.get('squadra_home') or '', match.get('squadra_away') or '',
            match['dati'].to_json(orient='split', date_format='iso')]

def _riga_sheet_a_match(riga):
    from datetime import datetime as _dt
    nome, data_str, squadra = riga[0], riga[1], riga[2]
    if len(riga) >= 6:
        squadra_home = riga[3] or None
        squadra_away = riga[4] or None
        dati_json = riga[5]
    else:
        # Formato vecchio (senza colonne home/away), per compatibilità con righe già salvate
        squadra_home = None
        squadra_away = None
        dati_json = riga[3]
    df = pd.read_json(io.StringIO(dati_json), orient='split')
    if 'GPI_Tiro' in df.columns:
        df['GPI_Tiro'] = df['GPI_Tiro'].astype(float)
    if 'Is_Stress_Test' in df.columns:
        df['Is_Stress_Test'] = df['Is_Stress_Test'].astype(bool)
    if 'PORTIERE_ID' not in df.columns and 'PORTIERE_CLEAN' in df.columns:
        df['PORTIERE_ID'] = df['PORTIERE_CLEAN'].apply(identita_giocatore)
    try:
        data_valore = _dt.strptime(data_str, '%Y-%m-%d').date()
    except Exception:
        data_valore = data_str
    return {'nome': nome, 'data': data_valore, 'squadra': squadra,
            'squadra_home': squadra_home, 'squadra_away': squadra_away, 'dati': df}

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
                db = pickle.load(f)
            for m in db:
                if 'PORTIERE_ID' not in m['dati'].columns and 'PORTIERE_CLEAN' in m['dati'].columns:
                    m['dati']['PORTIERE_ID'] = m['dati']['PORTIERE_CLEAN'].apply(identita_giocatore)
            return db
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

# ============================================================
# STORAGE STAGIONALE SEPARATO PER I TIRATORI (seconda "app" nella app)
# Stessa identica logica di persistenza dei portieri (Google Sheets se configurato,
# altrimenti file locale), ma su un worksheet/file dedicato, cosicché le due stagioni
# (portieri e tiratori) restino indipendenti pur condividendo lo stesso "Reset Season".
# ============================================================
SHOOTER_SEASON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "season_data_shooters.pkl")
SHOOTER_NOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shooter_notes.pkl")
STAFF_ACCESS_CODE = "GigiGiamba2026"

@st.cache_resource
def _ottieni_worksheet_tiratori():
    import gspread
    from google.oauth2.service_account import Credentials
    credenziali = Credentials.from_service_account_info(
        dict(st.secrets['gcp_service_account']), scopes=GOOGLE_SHEETS_SCOPES
    )
    client = gspread.authorize(credenziali)
    foglio = client.open_by_key(st.secrets['season_sheet_id'])
    try:
        worksheet = foglio.worksheet('ShooterSeasonData')
    except Exception:
        worksheet = foglio.add_worksheet(title='ShooterSeasonData', rows=2000, cols=6)
        worksheet.append_row(['nome', 'data', 'squadra', 'squadra_home', 'squadra_away', 'dati_json'])
    return worksheet

def _match_a_riga_sheet_tiratori(match):
    return [match['nome'], str(match['data']), match['squadra'],
            match.get('squadra_home') or '', match.get('squadra_away') or '',
            match['dati'].to_json(orient='split', date_format='iso')]

def _riga_sheet_a_match_tiratori(riga):
    from datetime import datetime as _dt
    nome, data_str, squadra = riga[0], riga[1], riga[2]
    squadra_home = riga[3] if len(riga) > 3 and riga[3] else None
    squadra_away = riga[4] if len(riga) > 4 and riga[4] else None
    dati_json = riga[5] if len(riga) > 5 else riga[3]
    df = pd.read_json(io.StringIO(dati_json), orient='split')
    if 'Is_Money_Time' in df.columns:
        df['Is_Money_Time'] = df['Is_Money_Time'].astype(bool)
    if 'TIRATORE_ID' not in df.columns and 'TIRATORE_CLEAN' in df.columns:
        df['TIRATORE_ID'] = df['TIRATORE_CLEAN'].apply(identita_giocatore)
    if 'macro_settore_tir' in df.columns and 'TIRO_CLEAN' in df.columns:
        df['macro_settore_tir'] = df['TIRO_CLEAN'].apply(mappa_macro_settore_tiratori)
    try:
        data_valore = _dt.strptime(data_str, '%Y-%m-%d').date()
    except Exception:
        data_valore = data_str
    return {'nome': nome, 'data': data_valore, 'squadra': squadra,
            'squadra_home': squadra_home, 'squadra_away': squadra_away, 'dati': df}

def carica_stagione_tiratori_da_disco():
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_tiratori()
            valori = worksheet.get_all_values()
            if len(valori) <= 1:
                return []
            return [_riga_sheet_a_match_tiratori(riga) for riga in valori[1:] if riga and riga[0]]
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not load shooter season from Google Sheets: {e}")
            return []
    if os.path.exists(SHOOTER_SEASON_FILE):
        try:
            with open(SHOOTER_SEASON_FILE, 'rb') as f:
                db = pickle.load(f)
            for m in db:
                if 'TIRATORE_ID' not in m['dati'].columns and 'TIRATORE_CLEAN' in m['dati'].columns:
                    m['dati']['TIRATORE_ID'] = m['dati']['TIRATORE_CLEAN'].apply(identita_giocatore)
                if 'macro_settore_tir' in m['dati'].columns and 'TIRO_CLEAN' in m['dati'].columns:
                    m['dati']['macro_settore_tir'] = m['dati']['TIRO_CLEAN'].apply(mappa_macro_settore_tiratori)
            return db
        except Exception:
            return []
    return []

def salva_stagione_tiratori_su_disco(db):
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_tiratori()
            worksheet.clear()
            worksheet.append_row(['nome', 'data', 'squadra', 'squadra_home', 'squadra_away', 'dati_json'])
            righe = [_match_a_riga_sheet_tiratori(m) for m in db]
            if righe:
                worksheet.append_rows(righe)
            return
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not save shooter season to Google Sheets: {e}")
    with open(SHOOTER_SEASON_FILE, 'wb') as f:
        pickle.dump(db, f)

@st.cache_resource
def _ottieni_worksheet_note():
    import gspread
    from google.oauth2.service_account import Credentials
    credenziali = Credentials.from_service_account_info(
        dict(st.secrets['gcp_service_account']), scopes=GOOGLE_SHEETS_SCOPES
    )
    client = gspread.authorize(credenziali)
    foglio = client.open_by_key(st.secrets['season_sheet_id'])
    try:
        worksheet = foglio.worksheet('ShooterNotes')
    except Exception:
        worksheet = foglio.add_worksheet(title='ShooterNotes', rows=500, cols=2)
        worksheet.append_row(['giocatore', 'nota'])
    return worksheet

def carica_note_da_disco():
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_note()
            valori = worksheet.get_all_values()
            grezzo = {r[0]: r[1] for r in valori[1:] if r and r[0]}
            migrato = _migra_chiavi_a_identita(grezzo)
            if migrato != grezzo:
                salva_note_su_disco(migrato)
            return migrato
        except Exception:
            return {}
    if os.path.exists(SHOOTER_NOTES_FILE):
        try:
            with open(SHOOTER_NOTES_FILE, 'rb') as f:
                grezzo = pickle.load(f)
            migrato = _migra_chiavi_a_identita(grezzo)
            if migrato != grezzo:
                salva_note_su_disco(migrato)
            return migrato
        except Exception:
            return {}
    return {}

def salva_note_su_disco(note_dict):
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_note()
            worksheet.clear()
            worksheet.append_row(['giocatore', 'nota'])
            righe = [[g, n] for g, n in note_dict.items()]
            if righe:
                worksheet.append_rows(righe)
            return
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not save notes to Google Sheets: {e}")
    with open(SHOOTER_NOTES_FILE, 'wb') as f:
        pickle.dump(note_dict, f)

# ============================================================
# FOTO GIOCATORI (mezzo busto, jpg/png) — condivise tra portieri e tiratori, indicizzate per
# nome. Ogni foto viene ridimensionata e compressa PRIMA di essere salvata, così pesa pochi KB
# indipendentemente da quanto è pesante il file originale caricato dall'utente.
# ============================================================
PLAYER_PHOTOS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "player_photos.pkl")

def elabora_foto_giocatore(file_caricato, lato_max=220, qualita_jpeg=78):
    """Ridimensiona (mantenendo le proporzioni, lato massimo lato_max px) e comprime in JPEG
    la foto caricata, poi la restituisce codificata in base64 (stringa), pronta da salvare."""
    immagine = PILImage.open(file_caricato)
    immagine = immagine.convert('RGB')
    immagine.thumbnail((lato_max, lato_max))
    buffer_foto = io.BytesIO()
    immagine.save(buffer_foto, format='JPEG', quality=qualita_jpeg, optimize=True)
    return base64.b64encode(buffer_foto.getvalue()).decode('utf-8')

def foto_base64_a_bytes(foto_b64):
    return base64.b64decode(foto_b64)

@st.cache_resource
def _ottieni_worksheet_foto():
    import gspread
    from google.oauth2.service_account import Credentials
    credenziali = Credentials.from_service_account_info(
        dict(st.secrets['gcp_service_account']), scopes=GOOGLE_SHEETS_SCOPES
    )
    client = gspread.authorize(credenziali)
    foglio = client.open_by_key(st.secrets['season_sheet_id'])
    try:
        worksheet = foglio.worksheet('PlayerPhotos')
    except Exception:
        worksheet = foglio.add_worksheet(title='PlayerPhotos', rows=500, cols=2)
        worksheet.append_row(['giocatore', 'foto_base64'])
    return worksheet

def _migra_chiavi_a_identita(diz):
    """Rimappa le chiavi di un dizionario (foto o note) all'identità del giocatore (senza
    numero di maglia né '[G]'), unendo eventuali doppioni derivanti da numeri diversi dello
    stesso giocatore (in caso di collisione vince l'ultimo valore incontrato)."""
    migrato = {}
    for chiave, valore in diz.items():
        migrato[identita_giocatore(chiave)] = valore
    return migrato

def carica_foto_da_disco():
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_foto()
            valori = worksheet.get_all_values()
            grezzo = {r[0]: r[1] for r in valori[1:] if r and r[0] and len(r) > 1}
            migrato = _migra_chiavi_a_identita(grezzo)
            if migrato != grezzo:
                salva_foto_su_disco(migrato)
            return migrato
        except Exception:
            return {}
    if os.path.exists(PLAYER_PHOTOS_FILE):
        try:
            with open(PLAYER_PHOTOS_FILE, 'rb') as f:
                grezzo = pickle.load(f)
            migrato = _migra_chiavi_a_identita(grezzo)
            if migrato != grezzo:
                salva_foto_su_disco(migrato)
            return migrato
        except Exception:
            return {}
    return {}

def salva_foto_su_disco(foto_dict):
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_foto()
            worksheet.clear()
            worksheet.append_row(['giocatore', 'foto_base64'])
            righe = [[g, f] for g, f in foto_dict.items()]
            if righe:
                worksheet.append_rows(righe)
            return
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not save player photos to Google Sheets: {e}")
    with open(PLAYER_PHOTOS_FILE, 'wb') as f:
        pickle.dump(foto_dict, f)

# ============================================================
# TESTA A TESTA (H2H): eventi tiratore-vs-portiere raccolti dal file unificato, usati per
# l'analisi "chi soffre chi". Salvati per partita, come per portieri/tiratori.
# ============================================================
H2H_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "season_data_h2h.pkl")

@st.cache_resource
def _ottieni_worksheet_h2h():
    import gspread
    from google.oauth2.service_account import Credentials
    credenziali = Credentials.from_service_account_info(
        dict(st.secrets['gcp_service_account']), scopes=GOOGLE_SHEETS_SCOPES
    )
    client = gspread.authorize(credenziali)
    foglio = client.open_by_key(st.secrets['season_sheet_id'])
    try:
        worksheet = foglio.worksheet('H2HData')
    except Exception:
        worksheet = foglio.add_worksheet(title='H2HData', rows=2000, cols=4)
        worksheet.append_row(['nome', 'data', 'dati_json'])
    return worksheet

def _backfill_id_h2h(df):
    if 'PORTIERE_ID' not in df.columns and 'PORTIERE_CLEAN' in df.columns:
        df['PORTIERE_ID'] = df['PORTIERE_CLEAN'].apply(identita_giocatore)
    if 'TIRATORE_ID' not in df.columns and 'TIRATORE_CLEAN' in df.columns:
        df['TIRATORE_ID'] = df['TIRATORE_CLEAN'].apply(identita_giocatore)
    return df

def carica_h2h_da_disco():
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_h2h()
            valori = worksheet.get_all_values()
            partite = []
            for riga in valori[1:]:
                if not riga or not riga[0]:
                    continue
                df = pd.read_json(io.StringIO(riga[2]), orient='split')
                if 'Is_Money_Time' in df.columns:
                    df['Is_Money_Time'] = df['Is_Money_Time'].astype(bool)
                df = _backfill_id_h2h(df)
                partite.append({'nome': riga[0], 'data': riga[1], 'dati': df})
            return partite
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not load head-to-head data from Google Sheets: {e}")
            return []
    if os.path.exists(H2H_FILE):
        try:
            with open(H2H_FILE, 'rb') as f:
                partite = pickle.load(f)
            for m in partite:
                m['dati'] = _backfill_id_h2h(m['dati'])
            return partite
        except Exception:
            return []
    return []

def salva_h2h_su_disco(db):
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_h2h()
            worksheet.clear()
            worksheet.append_row(['nome', 'data', 'dati_json'])
            righe = [[m['nome'], str(m['data']), m['dati'].to_json(orient='split', date_format='iso')] for m in db]
            if righe:
                worksheet.append_rows(righe)
            return
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not save head-to-head data to Google Sheets: {e}")
    with open(H2H_FILE, 'wb') as f:
        pickle.dump(db, f)

# ============================================================
# CAMPIONATI: raggruppamenti di partite salvati con un nome, filtrabili per squadra e per
# intervallo di date (con "Sine Die" = senza data di fine, si aggiornano da sole man mano che
# carichi nuove partite). Disponibili sia nel Seasonal Report (portieri) sia in Shooting Trend
# Analysis (tiratori/H2H), oltre al raggruppamento libero già esistente (multiselect partite).
# ============================================================
CHAMPIONSHIPS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "championships.pkl")

@st.cache_resource
def _ottieni_worksheet_campionati():
    import gspread
    from google.oauth2.service_account import Credentials
    credenziali = Credentials.from_service_account_info(
        dict(st.secrets['gcp_service_account']), scopes=GOOGLE_SHEETS_SCOPES
    )
    client = gspread.authorize(credenziali)
    foglio = client.open_by_key(st.secrets['season_sheet_id'])
    try:
        worksheet = foglio.worksheet('Championships')
    except Exception:
        worksheet = foglio.add_worksheet(title='Championships', rows=200, cols=4)
        worksheet.append_row(['nome', 'squadre_json', 'data_inizio', 'data_fine'])
    return worksheet

def carica_campionati_da_disco():
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_campionati()
            valori = worksheet.get_all_values()
            campionati = []
            for riga in valori[1:]:
                if not riga or not riga[0]:
                    continue
                squadre = json.loads(riga[1]) if riga[1] else None
                data_inizio = datetime.strptime(riga[2], '%Y-%m-%d').date()
                data_fine = datetime.strptime(riga[3], '%Y-%m-%d').date() if len(riga) > 3 and riga[3] else None
                campionati.append({'nome': riga[0], 'squadre': squadre, 'data_inizio': data_inizio, 'data_fine': data_fine})
            return campionati
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not load championships from Google Sheets: {e}")
            return []
    if os.path.exists(CHAMPIONSHIPS_FILE):
        try:
            with open(CHAMPIONSHIPS_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return []
    return []

def salva_campionati_su_disco(lista_campionati):
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_campionati()
            worksheet.clear()
            worksheet.append_row(['nome', 'squadre_json', 'data_inizio', 'data_fine'])
            righe = [[
                c['nome'],
                json.dumps(c['squadre']) if c['squadre'] else '',
                str(c['data_inizio']),
                str(c['data_fine']) if c['data_fine'] else ''
            ] for c in lista_campionati]
            if righe:
                worksheet.append_rows(righe)
            return
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not save championships to Google Sheets: {e}")
    with open(CHAMPIONSHIPS_FILE, 'wb') as f:
        pickle.dump(lista_campionati, f)

def partite_in_campionato(elenco_partite, campionato):
    """Filtra elenco_partite (lista di match-dict con 'squadra' e 'data') secondo i criteri del
    campionato indicato: squadre (None = tutte), data_inizio, data_fine (None = Sine Die)."""
    risultato = []
    for m in elenco_partite:
        if campionato['squadre'] and m['squadra'] not in campionato['squadre']:
            continue
        if m['data'] < campionato['data_inizio']:
            continue
        if campionato['data_fine'] and m['data'] > campionato['data_fine']:
            continue
        risultato.append(m)
    return risultato

def partite_h2h_in_campionato(elenco_partite_h2h, campionato):
    """Come partite_in_campionato, ma per l'H2H: le voci non hanno un singolo campo 'squadra'
    (coinvolgono sempre due squadre), quindi il filtro squadra passa se almeno una delle due
    compare nelle righe della partita."""
    risultato = []
    for m in elenco_partite_h2h:
        if m['data'] < campionato['data_inizio']:
            continue
        if campionato['data_fine'] and m['data'] > campionato['data_fine']:
            continue
        if campionato['squadre']:
            squadre_partita = set(m['dati']['Squadra_Portiere'].unique()) | set(m['dati']['Squadra_Tiratore'].unique())
            if not (squadre_partita & set(campionato['squadre'])):
                continue
        risultato.append(m)
    return risultato

# ============================================================
# PROFILI EXPECTED VALUES: "S.P. Value" (baseline di Sergio Palazzi, sempre presente e
# modificabile a mano) più eventuali profili calcolati dai dati (GPIA general data, campionati,
# intervalli di date, o gruppi di partite ad hoc). Un solo profilo alla volta è "attivo" e
# determina i valori usati in tutta l'app; S.P. Value non viene mai sovrascritto dal cambio
# di profilo attivo, resta sempre disponibile.
# ============================================================
EXPECTED_PROFILES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expected_profiles.pkl")

@st.cache_resource
def _ottieni_worksheet_expected():
    import gspread
    from google.oauth2.service_account import Credentials
    credenziali = Credentials.from_service_account_info(
        dict(st.secrets['gcp_service_account']), scopes=GOOGLE_SHEETS_SCOPES
    )
    client = gspread.authorize(credenziali)
    foglio = client.open_by_key(st.secrets['season_sheet_id'])
    try:
        worksheet = foglio.worksheet('ExpectedProfiles')
    except Exception:
        worksheet = foglio.add_worksheet(title='ExpectedProfiles', rows=10, cols=1)
        worksheet.append_row(['dati_json'])
    return worksheet

def carica_profili_expected_da_disco():
    default = {'profili': {'S.P. Value': dict(SP_VALUE_DEFAULT)}, 'attivo': 'S.P. Value'}
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_expected()
            valori = worksheet.get_all_values()
            if len(valori) <= 1 or not valori[1] or not valori[1][0]:
                salva_profili_expected_su_disco(default)
                return default
            dati = json.loads(valori[1][0])
            if 'S.P. Value' not in dati.get('profili', {}):
                dati['profili']['S.P. Value'] = dict(SP_VALUE_DEFAULT)
            return dati
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not load Expected Values profiles from Google Sheets: {e}")
            return default
    if os.path.exists(EXPECTED_PROFILES_FILE):
        try:
            with open(EXPECTED_PROFILES_FILE, 'rb') as f:
                dati = pickle.load(f)
            if 'S.P. Value' not in dati.get('profili', {}):
                dati['profili']['S.P. Value'] = dict(SP_VALUE_DEFAULT)
            return dati
        except Exception:
            return default
    return default

def salva_profili_expected_su_disco(dati):
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_expected()
            worksheet.clear()
            worksheet.append_row(['dati_json'])
            worksheet.append_row([json.dumps(dati)])
            return
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not save Expected Values profiles to Google Sheets: {e}")
    with open(EXPECTED_PROFILES_FILE, 'wb') as f:
        pickle.dump(dati, f)

# ============================================================
# TRAINING SESSIONS: sezione riservata separata (stessa password di Shooting Trend, ma da
# sbloccare a sé) per gestire squadre allenate (con logo), una libreria di sessioni PDF
# (esportate da OneNote, caricate in blocco) con link ed etichette persistenti, e l'esportazione
# in un PDF finale (copertina con logo associazione + dati sessione, seguita dalle pagine
# originali del PDF caricato).
# ============================================================
TRAINING_ACCESS_CODE = "GigiGiamba2026"
TRAINING_TEAMS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "training_teams.pkl")
TRAINING_SESSIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "training_sessions.pkl")
DIMENSIONE_CHUNK_PDF = 40000  # caratteri base64 per riga: resta sotto il limite di una cella di Google Sheets

@st.cache_resource
def _ottieni_worksheet_training_teams():
    import gspread
    from google.oauth2.service_account import Credentials
    credenziali = Credentials.from_service_account_info(
        dict(st.secrets['gcp_service_account']), scopes=GOOGLE_SHEETS_SCOPES
    )
    client = gspread.authorize(credenziali)
    foglio = client.open_by_key(st.secrets['season_sheet_id'])
    try:
        worksheet = foglio.worksheet('TrainingTeams')
    except Exception:
        worksheet = foglio.add_worksheet(title='TrainingTeams', rows=200, cols=2)
        worksheet.append_row(['nome', 'logo_base64'])
    return worksheet

def carica_squadre_allenate_da_disco():
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_training_teams()
            valori = worksheet.get_all_values()
            return [{'nome': r[0], 'logo_b64': r[1] if len(r) > 1 and r[1] else None} for r in valori[1:] if r and r[0]]
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not load training teams from Google Sheets: {e}")
            return []
    if os.path.exists(TRAINING_TEAMS_FILE):
        try:
            with open(TRAINING_TEAMS_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return []
    return []

def salva_squadre_allenate_su_disco(lista_squadre):
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_training_teams()
            worksheet.clear()
            worksheet.append_row(['nome', 'logo_base64'])
            righe = [[s['nome'], s.get('logo_b64') or ''] for s in lista_squadre]
            if righe:
                worksheet.append_rows(righe)
            return
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not save training teams to Google Sheets: {e}")
    with open(TRAINING_TEAMS_FILE, 'wb') as f:
        pickle.dump(lista_squadre, f)

@st.cache_resource
def _ottieni_worksheet_training_meta():
    import gspread
    from google.oauth2.service_account import Credentials
    credenziali = Credentials.from_service_account_info(
        dict(st.secrets['gcp_service_account']), scopes=GOOGLE_SHEETS_SCOPES
    )
    client = gspread.authorize(credenziali)
    foglio = client.open_by_key(st.secrets['season_sheet_id'])
    try:
        worksheet = foglio.worksheet('TrainingSessionsMeta')
    except Exception:
        worksheet = foglio.add_worksheet(title='TrainingSessionsMeta', rows=500, cols=3)
        worksheet.append_row(['id', 'nome_sessione', 'dati_json'])
    return worksheet

@st.cache_resource
def _ottieni_worksheet_training_pdf():
    import gspread
    from google.oauth2.service_account import Credentials
    credenziali = Credentials.from_service_account_info(
        dict(st.secrets['gcp_service_account']), scopes=GOOGLE_SHEETS_SCOPES
    )
    client = gspread.authorize(credenziali)
    foglio = client.open_by_key(st.secrets['season_sheet_id'])
    try:
        worksheet = foglio.worksheet('TrainingSessionsPDF')
    except Exception:
        worksheet = foglio.add_worksheet(title='TrainingSessionsPDF', rows=5000, cols=3)
        worksheet.append_row(['id', 'indice_chunk', 'chunk_base64'])
    return worksheet

def carica_sessioni_allenamento_da_disco():
    if _google_sheets_configurato():
        try:
            worksheet_meta = _ottieni_worksheet_training_meta()
            valori_meta = worksheet_meta.get_all_values()
            if len(valori_meta) <= 1:
                return []
            worksheet_pdf = _ottieni_worksheet_training_pdf()
            valori_pdf = worksheet_pdf.get_all_values()
            chunk_per_id = {}
            for riga in valori_pdf[1:]:
                if not riga or not riga[0]:
                    continue
                chunk_per_id.setdefault(riga[0], []).append((int(riga[1]), riga[2]))
            sessioni = []
            for riga in valori_meta[1:]:
                if not riga or not riga[0]:
                    continue
                id_sessione, nome_sessione, dati_json = riga[0], riga[1], riga[2]
                dati = json.loads(dati_json)
                pdf_bytes = None
                if id_sessione in chunk_per_id:
                    chunk_ordinati = sorted(chunk_per_id[id_sessione], key=lambda c: c[0])
                    b64_completo = ''.join(c[1] for c in chunk_ordinati)
                    pdf_bytes = base64.b64decode(b64_completo)
                sessioni.append({
                    'id': id_sessione, 'nome_sessione': nome_sessione, 'pdf_bytes': pdf_bytes,
                    'link_list': dati.get('link_list', []), 'note_generali': dati.get('note_generali', ''),
                    'assegnazioni': dati.get('assegnazioni', []),
                })
            return sessioni
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not load training sessions from Google Sheets: {e}")
            return []
    if os.path.exists(TRAINING_SESSIONS_FILE):
        try:
            with open(TRAINING_SESSIONS_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return []
    return []

def salva_sessioni_allenamento_su_disco(lista_sessioni):
    if _google_sheets_configurato():
        try:
            worksheet_meta = _ottieni_worksheet_training_meta()
            worksheet_meta.clear()
            worksheet_meta.append_row(['id', 'nome_sessione', 'dati_json'])
            righe_meta = [[
                s['id'], s['nome_sessione'],
                json.dumps({'link_list': s['link_list'], 'note_generali': s['note_generali'], 'assegnazioni': s['assegnazioni']})
            ] for s in lista_sessioni]
            if righe_meta:
                worksheet_meta.append_rows(righe_meta)

            worksheet_pdf = _ottieni_worksheet_training_pdf()
            worksheet_pdf.clear()
            worksheet_pdf.append_row(['id', 'indice_chunk', 'chunk_base64'])
            righe_pdf = []
            for s in lista_sessioni:
                if not s.get('pdf_bytes'):
                    continue
                b64_completo = base64.b64encode(s['pdf_bytes']).decode('utf-8')
                for indice, inizio in enumerate(range(0, len(b64_completo), DIMENSIONE_CHUNK_PDF)):
                    righe_pdf.append([s['id'], indice, b64_completo[inizio:inizio + DIMENSIONE_CHUNK_PDF]])
            if righe_pdf:
                worksheet_pdf.append_rows(righe_pdf)
            return
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not save training sessions to Google Sheets: {e}")
    with open(TRAINING_SESSIONS_FILE, 'wb') as f:
        pickle.dump(lista_sessioni, f)

# ============================================================
# LOGHI SQUADRA: magazzino condiviso in tutta l'app, indicizzato per nome squadra (esattamente
# come le foto giocatori sono indicizzate per identità). Non importa in quale sezione carichi il
# logo la prima volta (Training Sessions, Seasonal Report, Shooting Trend...): una volta agganciato
# a un nome, viene riconosciuto ovunque quel nome compaia, comprese le esportazioni PDF cumulative
# di squadra.
# ============================================================
TEAM_LOGOS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "team_logos.pkl")

@st.cache_resource
def _ottieni_worksheet_loghi_squadra():
    import gspread
    from google.oauth2.service_account import Credentials
    credenziali = Credentials.from_service_account_info(
        dict(st.secrets['gcp_service_account']), scopes=GOOGLE_SHEETS_SCOPES
    )
    client = gspread.authorize(credenziali)
    foglio = client.open_by_key(st.secrets['season_sheet_id'])
    try:
        worksheet = foglio.worksheet('TeamLogos')
    except Exception:
        worksheet = foglio.add_worksheet(title='TeamLogos', rows=500, cols=2)
        worksheet.append_row(['squadra', 'logo_base64'])
    return worksheet

def carica_loghi_squadra_da_disco():
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_loghi_squadra()
            valori = worksheet.get_all_values()
            return {r[0]: r[1] for r in valori[1:] if r and r[0] and len(r) > 1}
        except Exception:
            return {}
    if os.path.exists(TEAM_LOGOS_FILE):
        try:
            with open(TEAM_LOGOS_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return {}
    return {}

def salva_loghi_squadra_su_disco(loghi_dict):
    if _google_sheets_configurato():
        try:
            worksheet = _ottieni_worksheet_loghi_squadra()
            worksheet.clear()
            worksheet.append_row(['squadra', 'logo_base64'])
            righe = [[nome, logo] for nome, logo in loghi_dict.items()]
            if righe:
                worksheet.append_rows(righe)
            return
        except Exception as e:
            st.sidebar.error(f"⚠️ Could not save team logos to Google Sheets: {e}")
    with open(TEAM_LOGOS_FILE, 'wb') as f:
        pickle.dump(loghi_dict, f)

def gestisci_logo_squadra(nome_squadra, key_prefix):
    """Widget riusabile: mostra il logo attuale della squadra (se presente) e un uploader per
    caricarne/sostituirne uno. Riconosciuto ovunque nell'app in base al nome squadra."""
    chiave_sicura = _chiave_css_sicura(nome_squadra)
    key_uploader = f"{key_prefix}_logo_{chiave_sicura}"
    key_marcatore = f"_processato_{key_uploader}"
    col_logo, col_upload = st.columns([1, 4])
    with col_upload:
        nuovo_file = st.file_uploader(f"Logo for {nome_squadra} (optional, jpg/png)", type=['jpg', 'jpeg', 'png'],
                                       key=key_uploader, label_visibility="collapsed")
        if nuovo_file is not None:
            marcatore_attuale = f"{nuovo_file.name}-{nuovo_file.size}"
            if st.session_state.get(key_marcatore) != marcatore_attuale:
                st.session_state['loghi_squadre'][nome_squadra] = elabora_foto_giocatore(nuovo_file)
                salva_loghi_squadra_su_disco(st.session_state['loghi_squadre'])
                st.session_state[key_marcatore] = marcatore_attuale
                st.rerun()
    with col_logo:
        logo_b64 = st.session_state['loghi_squadre'].get(nome_squadra)
        if logo_b64:
            st.image(foto_base64_a_bytes(logo_b64), width=80)
            if st.button("🗑️", key=f"rimuovi_{key_uploader}", help="Remove team logo"):
                del st.session_state['loghi_squadre'][nome_squadra]
                salva_loghi_squadra_su_disco(st.session_state['loghi_squadre'])
                st.rerun()

def gestisci_foto_giocatore(nome_giocatore, key_prefix):
    """Widget riusabile: mostra la foto attuale (se presente) e un uploader per caricarne/
    sostituirne una. Ridimensiona e salva automaticamente al volo."""
    chiave_sicura = _chiave_css_sicura(nome_giocatore)
    key_uploader = f"{key_prefix}_foto_{chiave_sicura}"
    key_marcatore = f"_processata_{key_uploader}"
    col_foto, col_upload = st.columns([1, 4])
    with col_upload:
        nuovo_file = st.file_uploader("Photo (optional, jpg/png)", type=['jpg', 'jpeg', 'png'],
                                       key=key_uploader, label_visibility="collapsed")
        if nuovo_file is not None:
            marcatore_attuale = f"{nuovo_file.name}-{nuovo_file.size}"
            if st.session_state.get(key_marcatore) != marcatore_attuale:
                st.session_state['foto_giocatori'][nome_giocatore] = elabora_foto_giocatore(nuovo_file)
                salva_foto_su_disco(st.session_state['foto_giocatori'])
                st.session_state[key_marcatore] = marcatore_attuale
                st.rerun()
    with col_foto:
        foto_b64 = st.session_state['foto_giocatori'].get(nome_giocatore)
        if foto_b64:
            st.image(foto_base64_a_bytes(foto_b64), width=80)
            if st.button("🗑️", key=f"rimuovi_{key_uploader}", help="Remove photo"):
                del st.session_state['foto_giocatori'][nome_giocatore]
                salva_foto_su_disco(st.session_state['foto_giocatori'])
                st.rerun()

if 'db' not in st.session_state:
    st.session_state['db'] = carica_stagione_da_disco()
    for _m in st.session_state['db']:
        _m['dati'] = assicura_colonna_id(_m['dati'], 'PORTIERE_CLEAN', 'PORTIERE_ID')
if 'db_tiratori' not in st.session_state:
    st.session_state['db_tiratori'] = carica_stagione_tiratori_da_disco()
    for _m in st.session_state['db_tiratori']:
        _m['dati'] = assicura_colonna_id(_m['dati'], 'TIRATORE_CLEAN', 'TIRATORE_ID')
if 'note_tiratori' not in st.session_state:
    st.session_state['note_tiratori'] = carica_note_da_disco()
if 'foto_giocatori' not in st.session_state:
    st.session_state['foto_giocatori'] = carica_foto_da_disco()
if 'db_h2h' not in st.session_state:
    st.session_state['db_h2h'] = carica_h2h_da_disco()
    for _m in st.session_state['db_h2h']:
        _m['dati'] = assicura_colonna_id(_m['dati'], 'PORTIERE_CLEAN', 'PORTIERE_ID')
        _m['dati'] = assicura_colonna_id(_m['dati'], 'TIRATORE_CLEAN', 'TIRATORE_ID')
if 'campionati' not in st.session_state:
    st.session_state['campionati'] = carica_campionati_da_disco()
if 'profili_expected_stato' not in st.session_state:
    st.session_state['profili_expected_stato'] = carica_profili_expected_da_disco()
if 'squadre_allenate' not in st.session_state:
    st.session_state['squadre_allenate'] = carica_squadre_allenate_da_disco()
if 'sessioni_allenamento' not in st.session_state:
    st.session_state['sessioni_allenamento'] = carica_sessioni_allenamento_da_disco()
if 'loghi_squadre' not in st.session_state:
    st.session_state['loghi_squadre'] = carica_loghi_squadra_da_disco()
    # Migrazione: i loghi caricati finora dentro "Training Sessions" (per squadra) confluiscono
    # nel magazzino condiviso, così sono riconosciuti subito ovunque nell'app.
    _migrazione_avvenuta = False
    for _squadra in st.session_state['squadre_allenate']:
        if _squadra.get('logo_b64') and _squadra['nome'] not in st.session_state['loghi_squadre']:
            st.session_state['loghi_squadre'][_squadra['nome']] = _squadra['logo_b64']
            _migrazione_avvenuta = True
    if _migrazione_avvenuta:
        salva_loghi_squadra_su_disco(st.session_state['loghi_squadre'])

# ============================================================
# NOTE DEL COACH: markup semplice **grassetto**, __sottolineato__, ==evidenziato==
# ============================================================
def note_markup_a_html_streamlit(testo):
    t = str(testo or '')
    t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'__(.+?)__', r'<u>\1</u>', t)
    t = re.sub(r'==(.+?)==', r'<mark style="background-color:#ffef7a">\1</mark>', t)
    return t.replace('\n', '<br>')

def note_markup_a_reportlab(testo):
    t = str(testo or '')
    t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'__(.+?)__', r'<u>\1</u>', t)
    t = re.sub(r'==(.+?)==', r'<span backColor="#ffef7a">\1</span>', t)
    return t.replace('\n', '<br/>')

# ============================================================
# GENERAZIONE PDF PER I TIRATORI (singolo giocatore / squadra / Trend Summary)
# Stessa identità grafica (logo, colori, footer) del resto dell'app.
# ============================================================
def _immagine_da_figura_matplotlib(fig, max_larghezza_cm, max_altezza_cm):
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        fig.savefig(tmp.name, bbox_inches='tight', dpi=150)
        plt.close(fig)
        larghezza_px, altezza_px = PILImage.open(tmp.name).size
        w_cm, h_cm = _dimensioni_adattate(larghezza_px, altezza_px, max_larghezza_cm, max_altezza_cm)
        return RLImage(tmp.name, width=w_cm * cm, height=h_cm * cm)

def _blocco_giocatore_pdf(nome_giocatore, df_giocatore, stili, sezione_stile, nota_html=None):
    """Costruisce gli elementi ReportLab (porta, tastiera, tabella macro-zone, note) per UN
    giocatore, a partire dal suo sottoinsieme di tiri già filtrato (per partite/money-time/macro
    a monte). Porta, tastiera e tabella macro-zone stanno tutte sulla stessa riga."""
    elementi = []
    goal, tot, pct = calcola_metriche_tiratori_gruppo(df_giocatore)
    foto_b64 = st.session_state.get('foto_giocatori', {}).get(nome_giocatore)
    if foto_b64:
        intestazione = Table(
            [[RLImage(io.BytesIO(foto_base64_a_bytes(foto_b64)), width=1.8 * cm, height=1.8 * cm),
              [Paragraph(f"{nome_giocatore}", sezione_stile), Paragraph(f"Total: {goal}/{tot} = {pct:.1f}%", stili['Normal'])]]],
            colWidths=[2.1 * cm, None]
        )
        intestazione.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        elementi.append(intestazione)
    else:
        elementi.append(Paragraph(f"{nome_giocatore}", sezione_stile))
        elementi.append(Paragraph(f"Total: {goal}/{tot} = {pct:.1f}%", stili['Normal']))
    elementi.append(Spacer(1, 0.2 * cm))

    tot_porta, goal_porta = costruisci_conteggi_porta(df_giocatore)
    fig_porta = disegna_porta(tot_porta, goal_porta)
    tot_tast, goal_tast = costruisci_conteggi_tastiera(df_giocatore)
    fig_tast = disegna_tastiera(tot_tast, goal_tast)

    img_porta = _immagine_da_figura_matplotlib(fig_porta, 7.5, 6.5)
    img_tast = _immagine_da_figura_matplotlib(fig_tast, 11, 7.5)

    df_macro = tabella_macro_tiratori(df_giocatore)
    stile_intestazione_macro = ParagraphStyle('IntestazioneMacroPdf', parent=stili['Heading4'], fontSize=9, spaceAfter=4)
    if not df_macro.empty:
        blocco_macro = [
            Paragraph("By macro-zone", stile_intestazione_macro),
            _df_to_reportlab_table(df_macro, col_widths=[2.7 * cm, 1.5 * cm, 1.5 * cm, 2.3 * cm], font_size=7)
        ]
    else:
        blocco_macro = [Paragraph("By macro-zone", stile_intestazione_macro), Paragraph("No shots recorded.", stili['Normal'])]

    riga_layout = Table([[img_porta, img_tast, blocco_macro]], colWidths=[8 * cm, 11.5 * cm, 8 * cm])
    riga_layout.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elementi.append(riga_layout)
    elementi.append(Spacer(1, 0.3 * cm))

    if nota_html:
        elementi.append(Paragraph("Coach notes", stili['Heading4']))
        elementi.append(Paragraph(nota_html, stili['Normal']))

    return elementi

def genera_pdf_tiratori(titolo_report, dati_per_giocatore, note_dict=None, df_squadra_riepilogo=None, logo_squadra_b64=None):
    """dati_per_giocatore: dict {nome_giocatore: df_filtrato}. Genera un PDF con UNA PAGINA per
    ciascun giocatore (porta, tastiera e tabella macro-zone sulla stessa riga, note sotto).
    Se df_squadra_riepilogo è fornito (dataframe aggregato dell'intera selezione), il PDF apre
    con due pagine di riepilogo squadra: 1) mappa generale (porta + tastiera con heat map),
    2) tabelle tiratori per volume di tiro (totale e Money Time) e statistiche per macro-zona.
    logo_squadra_b64: se fornito, il logo della squadra compare in copertina accanto al logo
    dell'associazione."""
    note_dict = note_dict or {}
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=1.6 * cm, bottomMargin=1.4 * cm,
                             leftMargin=1.2 * cm, rightMargin=1.2 * cm)
    stili = getSampleStyleSheet()
    titolo_stile = ParagraphStyle('TitoloReportTir', parent=stili['Title'], fontSize=20,
                                   textColor=COLORE_ACCENTO, spaceAfter=2)
    sottotitolo_stile = ParagraphStyle('SottotitoloTir', parent=stili['Heading3'], fontSize=13,
                                        textColor=colors.HexColor('#555555'))
    sezione_stile = ParagraphStyle('SezioneTir', parent=stili['Heading2'], spaceBefore=4, spaceAfter=6,
                                    textColor=COLORE_ACCENTO)
    intestazione_tabella_stile = ParagraphStyle('IntestazioneTabellaTir', parent=stili['Heading4'], fontSize=9, spaceAfter=4)
    sezione_compatta_stile = ParagraphStyle('SezioneCompattaTir', parent=stili['Heading2'], fontSize=13,
                                             spaceBefore=0, spaceAfter=4, textColor=COLORE_ACCENTO)

    dimensione_logo_copertina = 2.6 * cm
    blocco_titolo = Table(
        [[RLImage(io.BytesIO(LOGO_BYTES), width=dimensione_logo_copertina, height=dimensione_logo_copertina),
          [Paragraph("SHOOTING TREND ANALYSIS", titolo_stile), Paragraph(titolo_report, sottotitolo_stile)],
          (RLImage(io.BytesIO(foto_base64_a_bytes(logo_squadra_b64)), width=dimensione_logo_copertina, height=dimensione_logo_copertina)
           if logo_squadra_b64 else '')]],
        colWidths=[dimensione_logo_copertina + 0.4 * cm, None, dimensione_logo_copertina + 0.2 * cm]
    )
    blocco_titolo.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0, 0), (0, 0), 'CENTER'), ('ALIGN', (2, 0), (2, 0), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    blocchi_pagine = []

    if df_squadra_riepilogo is not None and not df_squadra_riepilogo.empty:
        # Pagina 1: mappa generale di squadra (porta + tastiera con heat map)
        pagina1 = [Paragraph("General Shot Map", sezione_stile), Spacer(1, 0.2 * cm)]
        tot_p_sq, goal_p_sq = costruisci_conteggi_porta(df_squadra_riepilogo)
        fig_p_sq = disegna_porta(tot_p_sq, goal_p_sq)
        tot_t_sq, goal_t_sq = costruisci_conteggi_tastiera(df_squadra_riepilogo)
        fig_t_sq = disegna_tastiera(tot_t_sq, goal_t_sq)
        img_p_sq = _immagine_da_figura_matplotlib(fig_p_sq, 11, 10)
        img_t_sq = _immagine_da_figura_matplotlib(fig_t_sq, 16, 10.5)
        riga_mappa = Table([[img_p_sq, img_t_sq]], colWidths=[11.5 * cm, 16.5 * cm])
        riga_mappa.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        pagina1.append(riga_mappa)
        blocchi_pagine.append(pagina1)

        # Pagina 2: tiratori per volume di tiro (tabelle affiancate) + statistiche per macro-zona
        intest_volume_tot = Paragraph("By total shot volume", intestazione_tabella_stile)
        tabella_volume_tot = _df_to_reportlab_table(
            classifica_tiratori_per_volume(df_squadra_riepilogo), col_widths=[7*cm, 2*cm, 2*cm, 2*cm], font_size=7
        )
        intest_volume_mt = Paragraph("By Money Time shot volume", intestazione_tabella_stile)
        tabella_volume_mt = _df_to_reportlab_table(
            classifica_tiratori_per_volume(df_squadra_riepilogo, solo_money_time=True),
            col_widths=[7 * cm, 2 * cm, 2 * cm, 2 * cm], font_size=7
        )
        riga_volume = Table(
            [[[intest_volume_tot, tabella_volume_tot], [intest_volume_mt, tabella_volume_mt]]],
            colWidths=[13.5 * cm, 13.5 * cm]
        )
        riga_volume.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        pagina2 = [
            Paragraph("Shooters by Shot Volume", sezione_compatta_stile), Spacer(1, 0.1 * cm),
            riga_volume,
            Spacer(1, 0.2 * cm),
            Paragraph("By Macro-Zone (team total)", sezione_compatta_stile), Spacer(1, 0.1 * cm),
            _df_to_reportlab_table(tabella_macro_tiratori(df_squadra_riepilogo),
                                    col_widths=[5 * cm, 3 * cm, 3 * cm, 3 * cm], font_size=7),
        ]
        blocchi_pagine.append(pagina2)

    giocatori_validi = [(g, df_g) for g, df_g in dati_per_giocatore.items() if not df_g.empty]
    for nome_giocatore, df_g in giocatori_validi:
        nota_html = note_markup_a_reportlab(note_dict.get(nome_giocatore, '')) if note_dict.get(nome_giocatore) else None
        blocchi_pagine.append(_blocco_giocatore_pdf(nome_giocatore, df_g, stili, sezione_stile, nota_html))

    elementi = [blocco_titolo, Spacer(1, 0.5 * cm)]
    if blocchi_pagine:
        elementi.extend(blocchi_pagine[0])
        for blocco in blocchi_pagine[1:]:
            elementi.append(PageBreak())
            elementi.extend(blocco)

    doc.build(elementi, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buffer.seek(0)
    return buffer.getvalue()

def genera_pdf_trend_summary(titolo_report, note_dict):
    """PDF riassuntivo con l'elenco dei giocatori selezionati e, accanto, le note scritte dal coach."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=1.6 * cm, bottomMargin=1.4 * cm,
                             leftMargin=1.2 * cm, rightMargin=1.2 * cm)
    stili = getSampleStyleSheet()
    titolo_stile = ParagraphStyle('TitoloTrendSummary', parent=stili['Title'], fontSize=20,
                                   textColor=COLORE_ACCENTO, spaceAfter=2)
    sottotitolo_stile = ParagraphStyle('SottotitoloTrendSummary', parent=stili['Heading3'], fontSize=13,
                                        textColor=colors.HexColor('#555555'))
    elementi = []
    dimensione_logo_copertina = 2.6 * cm
    blocco_titolo = Table(
        [[RLImage(io.BytesIO(LOGO_BYTES), width=dimensione_logo_copertina, height=dimensione_logo_copertina),
          [Paragraph("TREND SUMMARY", titolo_stile), Paragraph(titolo_report, sottotitolo_stile)]]],
        colWidths=[dimensione_logo_copertina + 0.4 * cm, None]
    )
    blocco_titolo.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elementi.append(blocco_titolo)
    elementi.append(Spacer(1, 0.5 * cm))

    righe = [['Player', 'Coach Notes']]
    for nome_giocatore, nota in note_dict.items():
        righe.append([Paragraph(nome_giocatore, stili['Normal']),
                      Paragraph(note_markup_a_reportlab(nota) if nota else '—', stili['Normal'])])
    t = Table(righe, colWidths=[6 * cm, 19 * cm], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORE_TESTATA_TABELLE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
    ]))
    elementi.append(t)

    doc.build(elementi, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buffer.seek(0)
    return buffer.getvalue()

def genera_pdf_sessione_allenamento(sessione, assegnazione, squadre_allenate):
    """Genera il PDF finale di una sessione di allenamento: una pagina di copertina (logo
    dell'associazione, eventuale logo/nome squadra, data, nome sessione, note generali + note
    specifiche dell'assegnazione come 'cartellini' colorati, link come pulsanti in griglia)
    seguita dalle pagine del PDF originale caricato (esportato da OneNote), se presente e se
    pypdf è disponibile. Copertina in orizzontale a due colonne, come le tipiche pagine OneNote
    esportate, per un documento finale visivamente coerente e senza spazio bianco sprecato."""
    # Rileva la dimensione esatta della prima pagina del PDF originale (a volte molto più grande
    # di un normale foglio, es. formati "widescreen" o pagine OneNote esportate a canvas ampio),
    # e calcola un fattore di scala così che loghi, testi e margini crescano/si riducano in
    # proporzione, restando sempre leggibili e ben distribuiti qualunque sia la dimensione reale.
    dimensione_pagina = landscape(A4)
    if sessione.get('pdf_bytes') and _PYPDF_DISPONIBILE:
        try:
            prima_pagina_originale = PdfReader(io.BytesIO(sessione['pdf_bytes'])).pages[0]
            larghezza_punti = float(prima_pagina_originale.mediabox.width)
            altezza_punti = float(prima_pagina_originale.mediabox.height)
            if larghezza_punti > 0 and altezza_punti > 0:
                dimensione_pagina = (larghezza_punti, altezza_punti)
        except Exception:
            pass
    fattore_scala = dimensione_pagina[0] / landscape(A4)[0]

    stili = getSampleStyleSheet()
    titolo_stile = ParagraphStyle('TitoloSessione', parent=stili['Title'], fontSize=22 * fattore_scala,
                                   leading=26 * fattore_scala, textColor=COLORE_ACCENTO, spaceAfter=2 * fattore_scala)
    sottotitolo_stile = ParagraphStyle('SottotitoloSessione', parent=stili['Heading3'], fontSize=14 * fattore_scala,
                                        leading=17 * fattore_scala, textColor=colors.HexColor('#555555'))
    sezione_stile = ParagraphStyle('SezioneSessione', parent=stili['Heading2'], fontSize=13 * fattore_scala,
                                    leading=16 * fattore_scala, spaceBefore=0, spaceAfter=4 * fattore_scala,
                                    textColor=COLORE_ACCENTO)
    corpo_scheda_stile = ParagraphStyle('CorpoScheda', parent=stili['Normal'], fontSize=10 * fattore_scala,
                                         leading=14 * fattore_scala)
    link_pulsante_stile = ParagraphStyle('LinkPulsante', parent=stili['Normal'], fontSize=10.5 * fattore_scala,
                                          leading=13 * fattore_scala, textColor=COLORE_ACCENTO)
    COLORE_SFONDO_NOTA = colors.HexColor('#f3f5f7')
    COLORE_SFONDO_LINK = colors.HexColor('#eaf0f7')
    COLORE_BORDO_LINK = colors.HexColor('#c3d3e3')

    def _scheda_nota(titolo, testo_html, larghezza):
        t = Table([[Paragraph(titolo, sezione_stile)], [Paragraph(testo_html, corpo_scheda_stile)]], colWidths=[larghezza])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLORE_SFONDO_NOTA),
            ('LEFTPADDING', (0, 0), (-1, -1), 12 * fattore_scala), ('RIGHTPADDING', (0, 0), (-1, -1), 12 * fattore_scala),
            ('TOPPADDING', (0, 0), (0, 0), 10 * fattore_scala), ('BOTTOMPADDING', (0, 0), (0, 0), 2 * fattore_scala),
            ('TOPPADDING', (0, 1), (0, 1), 0), ('BOTTOMPADDING', (0, 1), (0, 1), 10 * fattore_scala),
        ]))
        return t

    def _pulsante_link(nome, url, larghezza):
        p = Paragraph(f'<link href="{url}" color="#15304f"><b>• {nome}</b></link>', link_pulsante_stile)
        t = Table([[p]], colWidths=[larghezza])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLORE_SFONDO_LINK),
            ('BOX', (0, 0), (-1, -1), 0.7, COLORE_BORDO_LINK),
            ('LEFTPADDING', (0, 0), (-1, -1), 10 * fattore_scala), ('RIGHTPADDING', (0, 0), (-1, -1), 10 * fattore_scala),
            ('TOPPADDING', (0, 0), (-1, -1), 9 * fattore_scala), ('BOTTOMPADDING', (0, 0), (-1, -1), 9 * fattore_scala),
        ]))
        return t

    buffer_copertina = io.BytesIO()
    margine_orizzontale = 1.8 * cm * fattore_scala
    doc = SimpleDocTemplate(buffer_copertina, pagesize=dimensione_pagina,
                             topMargin=1.6 * cm * fattore_scala, bottomMargin=1.4 * cm * fattore_scala,
                             leftMargin=margine_orizzontale, rightMargin=margine_orizzontale)
    larghezza_pagina = dimensione_pagina[0] - 2 * margine_orizzontale
    elementi = []

    dimensione_logo = 2.8 * cm * fattore_scala
    squadra_nome = assegnazione.get('squadra') if assegnazione else None
    logo_squadra_b64 = st.session_state['loghi_squadre'].get(squadra_nome) if squadra_nome else None

    blocco_titolo = Table(
        [[RLImage(io.BytesIO(LOGO_BYTES), width=dimensione_logo, height=dimensione_logo),
          [Paragraph("TRAINING SESSION", titolo_stile), Paragraph(sessione['nome_sessione'], sottotitolo_stile)],
          (RLImage(io.BytesIO(foto_base64_a_bytes(logo_squadra_b64)), width=dimensione_logo, height=dimensione_logo)
           if logo_squadra_b64 else '')]],
        colWidths=[dimensione_logo + 0.5 * cm * fattore_scala, None, dimensione_logo + 0.3 * cm * fattore_scala]
    )
    blocco_titolo.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0, 0), (0, 0), 'CENTER'), ('ALIGN', (2, 0), (2, 0), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elementi.append(blocco_titolo)
    elementi.append(Spacer(1, 0.3 * cm * fattore_scala))

    fascia_colorata = Table([['']], colWidths=[larghezza_pagina], rowHeights=[0.22 * cm * fattore_scala])
    fascia_colorata.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), COLORE_ACCENTO)]))
    elementi.append(fascia_colorata)
    elementi.append(Spacer(1, 0.45 * cm * fattore_scala))

    if squadra_nome or (assegnazione and assegnazione.get('data')):
        info_riga = []
        if squadra_nome:
            info_riga.append(f"<b>Team:</b> {squadra_nome}")
        if assegnazione and assegnazione.get('data'):
            info_riga.append(f"<b>Date:</b> {assegnazione['data']}")
        elementi.append(Paragraph("   |   ".join(info_riga), corpo_scheda_stile))
        elementi.append(Spacer(1, 0.4 * cm * fattore_scala))

    larghezza_colonna = (larghezza_pagina - 1.0 * cm * fattore_scala) / 2

    colonna_sinistra = []
    if sessione.get('note_generali'):
        colonna_sinistra.append(_scheda_nota("Session notes", note_markup_a_reportlab(sessione['note_generali']), larghezza_colonna))
        colonna_sinistra.append(Spacer(1, 0.35 * cm * fattore_scala))
    if assegnazione and assegnazione.get('nota'):
        colonna_sinistra.append(_scheda_nota(f"Notes for {squadra_nome or 'this session'}",
                                              note_markup_a_reportlab(assegnazione['nota']), larghezza_colonna))
        colonna_sinistra.append(Spacer(1, 0.35 * cm * fattore_scala))

    colonna_destra = []
    if sessione.get('link_list'):
        colonna_destra.append(Paragraph("Exercise videos", sezione_stile))
        colonna_destra.append(Spacer(1, 0.15 * cm * fattore_scala))
        for link in sessione['link_list']:
            colonna_destra.append(_pulsante_link(link['nome'], link['url'], larghezza_colonna))
            colonna_destra.append(Spacer(1, 0.2 * cm * fattore_scala))

    if colonna_sinistra or colonna_destra:
        tabella_colonne = Table([[colonna_sinistra or '', colonna_destra or '']], colWidths=[larghezza_colonna, larghezza_colonna])
        tabella_colonne.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (1, 0), (1, 0), 1.0 * cm * fattore_scala), ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0), ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        elementi.append(tabella_colonne)

    doc.build(elementi, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buffer_copertina.seek(0)

    if not sessione.get('pdf_bytes') or not _PYPDF_DISPONIBILE:
        return buffer_copertina.getvalue()

    try:
        writer = PdfWriter()
        for pagina in PdfReader(buffer_copertina).pages:
            writer.add_page(pagina)
        for pagina in PdfReader(io.BytesIO(sessione['pdf_bytes'])).pages:
            writer.add_page(pagina)
        buffer_finale = io.BytesIO()
        writer.write(buffer_finale)
        buffer_finale.seek(0)
        return buffer_finale.getvalue()
    except Exception:
        return buffer_copertina.getvalue()

st.sidebar.caption(f"📦 Matches in memory (season): {len(st.session_state['db'])}")
if _google_sheets_configurato():
    st.sidebar.caption("☁️ Storage: Google Sheets")
else:
    st.sidebar.caption("💻 Storage: local file")
    st.sidebar.caption(f"ℹ️ {_diagnosi_google_sheets()}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(['📥 Upload Match Sheets', '📊 Single Game Analysis', '🏆 Seasonal Report', '🎯 Shooting Trend Analysis', '🏋️ Training Sessions'])

with tab1:
    st.header('Upload Game Data')

    if 'upload_authorized' not in st.session_state:
        st.session_state['upload_authorized'] = False

    if not st.session_state['upload_authorized']:
        st.info("🔒 This section is reserved for authorized staff. Everyone else can freely view the Single Game Analysis and Seasonal Report tabs.")
        with st.form(key="form_upload_access", clear_on_submit=True):
            codice_inserito = st.text_input("Access code", type="password", key="codice_upload")
            sbloccato = st.form_submit_button("Unlock")
        if sbloccato:
            if codice_inserito == UPLOAD_ACCESS_CODE:
                st.session_state['upload_authorized'] = True
                st.rerun()
            else:
                st.error("Incorrect code.")
    else:
        # ============================================================
        # UPLOAD FILE UNIFICATO (formato unico HOME/AWAY, un solo file per l'intera gara)
        # ============================================================
        st.subheader("📥 Upload Match (unified format — recommended)")
        st.caption("A single Excel file for the whole match — see the file format rules below.")

        with st.expander("📋 File format rules (read this if you're tagging matches for the team)"):
            st.markdown("""
**File name**

Format: `Home-Away Date (day-month-year).xlsx`

Concrete example: `Merano-Brixen 23-8-2026.xlsx` → home team **Merano**, away team **Brixen**, played on **23 August 2026**.

- The **first** name (before the dash) is always the home team, the **second** (after the dash) is always the away team.
- The date after that is read as **day-month-year** (not month-day-year).
- The Game Name and Event Date fields are filled in automatically from this — you shouldn't need to type them by hand.

**Columns** (any order, any capitalization — the app finds them by name)

| Column | What goes in it |
|---|---|
| `HOME` | Whoever is involved on the home team's side of that shot: either the home goalkeeper (if the home team is defending) or the home shooter (if the home team is attacking) |
| `AWAY` | Same, for the away team |
| `TIRO` | The shot zone: `7m`, `6m1`, `6m1,5`, `6m2`, `6m2,5`, `6m3`, `bt1`...`bt3`, `9m1`...`9m3`, `lw1`, `lw2`, `rw1`, `rw2`, `fb1`, `fb2`, `fb3` |
| `GOAL SECTOR` | Which of the 9 net zones (`T1`...`T9`) the shot went to — only relevant if a shooter is tagged on that row |
| `RESULT` | `goal`, `save`, or `miss` |
| `TIMELINE` | Match clock and score, e.g. `23'45'' - 6-4`. For friendlies you're not timing, just leave it blank or use a simple sequence |

**The `[G]` rule** — this is the key thing to get right:
- Whichever of `HOME`/`AWAY` has **`[G]`** in the name (e.g. `Panitti [G]`, `#1 - Kabashi [G]`) is read as the **goalkeeper** defending that shot.
- The other cell, if filled, is the **shooter** facing him.
- A cell **without** `[G]` is always treated as a shooter — never as a goalkeeper.

**Tagging only part of a match is fine** — leave a cell empty for whatever you're not tracking:
- Only tracking your own goalkeeper's saves? Tag the `[G]` cell, leave the shooter's cell empty.
- Only tracking your own shooters, don't care who the opposing goalkeeper is? Tag the shooter's cell, leave the other cell empty (no `[G]` needed anywhere on that row).
- Tagging both (goalkeeper *and* shooter on the same row)? That's what feeds the Head-to-Head "who suffers whom" analysis — worth doing whenever you can.
- A row with **both** cells empty, or with `[G]` on **both** sides, doesn't make sense and gets skipped automatically.
            """)

        fc_uni = st.file_uploader('Drag and drop the unified match file(s) here', type=['xlsx', 'xls'],
                                   accept_multiple_files=True, key="upload_unificato")

        if fc_uni:
            pe_gk_uni, pe_tir_uni, pe_h2h_uni = [], [], []
            for idx, f in enumerate(fc_uni):
                st.markdown(f"**File Configuration: {f.name}**")
                nome_da_file, data_da_file = estrai_nome_e_data_da_nome_file(f.name)
                col1, col2 = st.columns(2)
                with col1:
                    nm_u = st.text_input(f'Game Name {idx+1}', value=nome_da_file or f'Game {idx+1}', key=f'un_{idx}')
                with col2:
                    dt_u = st.date_input(f'Event Date {idx+1}', value=data_da_file or datetime.now(), key=f"ud_{idx}")
                sq_home_u, sq_away_u = estrai_home_away_da_nome_file(f.name)
                if not sq_home_u or not sq_away_u:
                    st.error(f"Could not read the two team names from the file name '{f.name}'. "
                             f"Rename it as \"TeamHome-TeamAway date.xlsx\" and re-upload.")
                    continue
                if not data_da_file:
                    st.warning("Could not read the date from the file name — check/set 'Event Date' above.")
                st.caption(f"Home: **{sq_home_u}**  |  Away: **{sq_away_u}**")
                try:
                    df_raw_u = pd.read_excel(f)
                    df_gk_h, df_gk_a, df_tir_h, df_tir_a, df_h2h_u = elabora_file_unificato(df_raw_u, sq_home_u, sq_away_u)
                    if not df_gk_h.empty:
                        pe_gk_uni.append({'nome': nm_u, 'data': dt_u, 'squadra': sq_home_u, 'dati': df_gk_h,
                                           'squadra_home': sq_home_u, 'squadra_away': sq_away_u})
                    if not df_gk_a.empty:
                        pe_gk_uni.append({'nome': nm_u, 'data': dt_u, 'squadra': sq_away_u, 'dati': df_gk_a,
                                           'squadra_home': sq_home_u, 'squadra_away': sq_away_u})
                    if not df_tir_h.empty:
                        pe_tir_uni.append({'nome': nm_u, 'data': dt_u, 'squadra': sq_home_u, 'dati': df_tir_h,
                                            'squadra_home': sq_home_u, 'squadra_away': sq_away_u})
                    if not df_tir_a.empty:
                        pe_tir_uni.append({'nome': nm_u, 'data': dt_u, 'squadra': sq_away_u, 'dati': df_tir_a,
                                            'squadra_home': sq_home_u, 'squadra_away': sq_away_u})
                    if not df_h2h_u.empty:
                        pe_h2h_uni.append({'nome': nm_u, 'data': dt_u, 'dati': df_h2h_u})
                    st.caption(f"Parsed: {len(df_gk_h)} GK-home rows, {len(df_gk_a)} GK-away rows, "
                               f"{len(df_tir_h)} shooter-home rows, {len(df_tir_a)} shooter-away rows, "
                               f"{len(df_h2h_u)} head-to-head events.")
                except Exception as e:
                    st.error(f'Error processing file {f.name}: {e}')

            if st.button('➕ Save & Process Match (unified)'):
                chiavi_gk = {(p['nome'], str(p['data']), p['squadra']) for p in st.session_state['db']}
                chiavi_tir = {(p['nome'], str(p['data']), p['squadra']) for p in st.session_state['db_tiratori']}
                chiavi_h2h = {(p['nome'], str(p['data'])) for p in st.session_state['db_h2h']}
                agg_gk = agg_tir = agg_h2h = 0
                for match in pe_gk_uni:
                    chiave = (match['nome'], str(match['data']), match['squadra'])
                    if chiave not in chiavi_gk:
                        st.session_state['db'].append(match)
                        chiavi_gk.add(chiave)
                        agg_gk += 1
                for match in pe_tir_uni:
                    chiave = (match['nome'], str(match['data']), match['squadra'])
                    if chiave not in chiavi_tir:
                        st.session_state['db_tiratori'].append(match)
                        chiavi_tir.add(chiave)
                        agg_tir += 1
                for match in pe_h2h_uni:
                    chiave = (match['nome'], str(match['data']))
                    if chiave not in chiavi_h2h:
                        st.session_state['db_h2h'].append(match)
                        chiavi_h2h.add(chiave)
                        agg_h2h += 1
                salva_stagione_su_disco(st.session_state['db'])
                salva_stagione_tiratori_su_disco(st.session_state['db_tiratori'])
                salva_h2h_su_disco(st.session_state['db_h2h'])
                st.success(f"Saved: {agg_gk} goalkeeper record(s), {agg_tir} shooter record(s), "
                           f"{agg_h2h} head-to-head match(es) added.")

        st.markdown("---")

        with st.expander("Old 4-file format (deprecated — only for legacy one-off files)"):
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
                        df_raw = pd.read_excel(f)
                        df = elabora_file_portieri(df_raw)
                        sq_home, sq_away = estrai_home_away_da_nome_file(f.name)
                        pe.append({'nome': nm, 'data': dt, 'squadra': sq, 'dati': df,
                                   'squadra_home': sq_home, 'squadra_away': sq_away})
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
        st.subheader("🏆 Championships")
        st.caption("Save a named group of matches, filtered by team and by date range. Use "
                   "'Sine Die' (no end date) to keep adding new matches automatically as you "
                   "upload them, until you close it with a specific end date. Once created, a "
                   "championship becomes selectable in Seasonal Report and Shooting Trend Analysis.")

        with st.expander("➕ Create a new championship"):
            nome_camp = st.text_input("Championship name (e.g. 'Serie A Gold 2026-27')", key="nuovo_camp_nome")
            tutte_le_squadre_camp = sorted(set(
                [m['squadra'] for m in st.session_state['db']] +
                [m['squadra'] for m in st.session_state['db_tiratori']]
            ))
            squadre_camp = st.multiselect("Teams (leave empty to include all teams found)",
                                           tutte_le_squadre_camp, key="nuovo_camp_squadre")
            col_ci1, col_ci2 = st.columns(2)
            with col_ci1:
                data_inizio_camp = st.date_input("Start date", value=datetime.now(), key="nuovo_camp_inizio")
            with col_ci2:
                sine_die_camp = st.checkbox("Sine Die (no end date yet)", value=True, key="nuovo_camp_sine_die")
                data_fine_camp = None if sine_die_camp else st.date_input("End date", value=datetime.now(), key="nuovo_camp_fine")
            if st.button("➕ Create Championship"):
                nome_pulito = nome_camp.strip()
                if not nome_pulito:
                    st.error("Give the championship a name.")
                elif any(c['nome'] == nome_pulito for c in st.session_state['campionati']):
                    st.error("A championship with this name already exists.")
                else:
                    st.session_state['campionati'].append({
                        'nome': nome_pulito,
                        'squadre': squadre_camp if squadre_camp else None,
                        'data_inizio': data_inizio_camp,
                        'data_fine': data_fine_camp,
                    })
                    salva_campionati_su_disco(st.session_state['campionati'])
                    st.success(f"Championship '{nome_pulito}' created.")
                    st.rerun()

        if st.session_state['campionati']:
            st.markdown("**Existing championships**")
            for i, camp in enumerate(st.session_state['campionati']):
                squadre_testo = ', '.join(camp['squadre']) if camp['squadre'] else 'All teams'
                fine_testo = str(camp['data_fine']) if camp['data_fine'] else 'Sine Die (still open)'
                with st.expander(f"🏆 {camp['nome']} — {squadre_testo} — {camp['data_inizio']} → {fine_testo}"):
                    if camp['data_fine'] is None:
                        nuova_fine_camp = st.date_input("Set an end date to close this championship",
                                                         value=datetime.now(), key=f"fine_camp_{i}")
                        if st.button("🔒 Close championship (set end date)", key=f"chiudi_camp_{i}"):
                            st.session_state['campionati'][i]['data_fine'] = nuova_fine_camp
                            salva_campionati_su_disco(st.session_state['campionati'])
                            st.rerun()
                    else:
                        if st.button("🔓 Reopen (remove end date — back to Sine Die)", key=f"riapri_camp_{i}"):
                            st.session_state['campionati'][i]['data_fine'] = None
                            salva_campionati_su_disco(st.session_state['campionati'])
                            st.rerun()
                    if st.button("🗑️ Delete this championship", key=f"del_camp_{i}"):
                        st.session_state['campionati'].pop(i)
                        salva_campionati_su_disco(st.session_state['campionati'])
                        st.success(f"Championship '{camp['nome']}' deleted (matches themselves are untouched).")
                        st.rerun()
        else:
            st.caption("No championships created yet.")

        st.markdown("---")
        st.subheader("🎯 Expected Values (S.P. Value)")
        st.caption("'S.P. Value' is the baseline reference — Sergio Palazzi's video-analysis "
                   "work — and it always stays available, no matter which profile you switch to "
                   "below. You can also compute Expected Save % / Expected Goal % straight from "
                   "the data stored in this app: from everything ('GPIA general data'), from a "
                   "specific championship, a date range, or an ad-hoc group of matches.")

        stato_expected = st.session_state['profili_expected_stato']
        nomi_profili_expected = list(stato_expected['profili'].keys())
        if 'S.P. Value' in nomi_profili_expected:
            nomi_profili_expected.remove('S.P. Value')
        nomi_profili_expected = ['S.P. Value'] + nomi_profili_expected

        indice_attivo = nomi_profili_expected.index(stato_expected['attivo']) if stato_expected['attivo'] in nomi_profili_expected else 0
        profilo_scelto_attivo = st.selectbox(
            "Active profile (used everywhere in the app for Expected Save % / Expected Goal % comparisons):",
            nomi_profili_expected, index=indice_attivo, key="selettore_profilo_expected"
        )
        if profilo_scelto_attivo != stato_expected['attivo']:
            st.session_state['profili_expected_stato']['attivo'] = profilo_scelto_attivo
            salva_profili_expected_su_disco(st.session_state['profili_expected_stato'])
            st.rerun()

        with st.expander("✏️ Edit S.P. Value manually"):
            st.caption("Change these only if Sergio Palazzi communicates updated reference values.")
            valori_sp_attuali = stato_expected['profili']['S.P. Value']
            nuovi_valori_sp = {}
            colonne_sp = st.columns(3)
            for i, zona in enumerate(SP_VALUE_DEFAULT.keys()):
                with colonne_sp[i % 3]:
                    nuovi_valori_sp[zona] = st.number_input(
                        zona, min_value=0, max_value=100,
                        value=int(round(valori_sp_attuali.get(zona, SP_VALUE_DEFAULT[zona]))),
                        key=f"sp_val_{zona}"
                    )
            if st.button("💾 Save S.P. Value changes"):
                st.session_state['profili_expected_stato']['profili']['S.P. Value'] = nuovi_valori_sp
                salva_profili_expected_su_disco(st.session_state['profili_expected_stato'])
                st.success("S.P. Value updated.")
                st.rerun()

        if st.button("🔄 Update to GPIA general data"):
            nuovo_profilo_gpia = calcola_profilo_expected_da_dati(st.session_state['db'])
            if nuovo_profilo_gpia:
                st.session_state['profili_expected_stato']['profili']['GPIA General Data'] = nuovo_profilo_gpia
                salva_profili_expected_su_disco(st.session_state['profili_expected_stato'])
                st.success(f"'GPIA General Data' computed from {len(st.session_state['db'])} goalkeeper match record(s) and saved. "
                           f"Select it above to make it the active profile.")
                st.rerun()
            else:
                st.warning("No goalkeeper data available yet to compute this from.")

        with st.expander("➕ Create a custom Expected Values profile"):
            nome_profilo_custom = st.text_input("Profile name", key="nuovo_profilo_expected_nome")
            origine_profilo = st.radio("Compute it from:", ["A championship", "A date range", "Specific matches"],
                                        key="origine_profilo_expected", horizontal=True)
            partite_sorgente_expected = []
            if origine_profilo == "A championship":
                if st.session_state['campionati']:
                    camp_scelto_expected = st.selectbox(
                        "Championship:", [c['nome'] for c in st.session_state['campionati']], key="camp_per_expected")
                    camp_obj_expected = next(c for c in st.session_state['campionati'] if c['nome'] == camp_scelto_expected)
                    partite_sorgente_expected = partite_in_campionato(st.session_state['db'], camp_obj_expected)
                else:
                    st.caption("No championships created yet — create one above first, or pick a different source.")
            elif origine_profilo == "A date range":
                col_ed1, col_ed2 = st.columns(2)
                with col_ed1:
                    data_i_expected = st.date_input("From:", value=datetime.now(), key="expected_data_i")
                with col_ed2:
                    data_f_expected = st.date_input("To:", value=datetime.now(), key="expected_data_f")
                partite_sorgente_expected = [m for m in st.session_state['db'] if data_i_expected <= m['data'] <= data_f_expected]
            else:
                opzioni_match_expected = [f"{m['nome']} ({m['data']}) - {m['squadra']}" for m in st.session_state['db']]
                scelte_match_expected = st.multiselect("Select matches:", opzioni_match_expected, key="match_per_expected")
                partite_sorgente_expected = [m for m, lbl in zip(st.session_state['db'], opzioni_match_expected) if lbl in scelte_match_expected]

            if st.button("➕ Compute and save this profile"):
                nome_pulito_expected = nome_profilo_custom.strip()
                if not nome_pulito_expected:
                    st.error("Give the profile a name.")
                elif nome_pulito_expected == 'S.P. Value':
                    st.error("This name is reserved for the baseline profile.")
                elif not partite_sorgente_expected:
                    st.error("No matches match this selection.")
                else:
                    nuovo_profilo_custom = calcola_profilo_expected_da_dati(partite_sorgente_expected)
                    st.session_state['profili_expected_stato']['profili'][nome_pulito_expected] = nuovo_profilo_custom
                    salva_profili_expected_su_disco(st.session_state['profili_expected_stato'])
                    st.success(f"Profile '{nome_pulito_expected}' computed from {len(partite_sorgente_expected)} match record(s) and saved.")
                    st.rerun()

        profili_cancellabili_expected = [n for n in nomi_profili_expected if n != 'S.P. Value']
        if profili_cancellabili_expected:
            with st.expander("🗑️ Delete a computed profile"):
                profilo_da_cancellare_expected = st.selectbox(
                    "Profile to delete:", profili_cancellabili_expected, key="profilo_da_cancellare_expected")
                if st.button("🗑️ Delete this profile"):
                    del st.session_state['profili_expected_stato']['profili'][profilo_da_cancellare_expected]
                    if st.session_state['profili_expected_stato']['attivo'] == profilo_da_cancellare_expected:
                        st.session_state['profili_expected_stato']['attivo'] = 'S.P. Value'
                    salva_profili_expected_su_disco(st.session_state['profili_expected_stato'])
                    st.success(f"Profile '{profilo_da_cancellare_expected}' deleted. S.P. Value is unaffected.")
                    st.rerun()

        st.markdown("---")
        st.subheader("💾 Full Backup")
        st.caption("Download a backup file of everything in this app — matches (goalkeepers + "
                   "shooters + head-to-head), player photos, coach notes, championships, and "
                   "Expected Values profiles — anytime, and keep it on your computer. If anything "
                   "ever goes wrong with the online app, or before a Reset Season, you can restore "
                   "everything from this file.")

        col_backup1, col_backup2 = st.columns(2)
        with col_backup1:
            st.markdown("**Download backup**")
            esiste_qualcosa_da_salvare = (
                st.session_state['db'] or st.session_state['db_tiratori'] or st.session_state['db_h2h']
                or st.session_state['foto_giocatori'] or st.session_state['note_tiratori']
            )
            if esiste_qualcosa_da_salvare:
                backup_bytes = pickle.dumps({
                    'db': st.session_state['db'],
                    'db_tiratori': st.session_state['db_tiratori'],
                    'db_h2h': st.session_state['db_h2h'],
                    'foto_giocatori': st.session_state['foto_giocatori'],
                    'note_tiratori': st.session_state['note_tiratori'],
                    'campionati': st.session_state['campionati'],
                    'profili_expected_stato': st.session_state['profili_expected_stato'],
                })
                nome_backup = f"full_backup_{datetime.now().strftime('%Y-%m-%d_%H%M')}.pkl"
                st.download_button(
                    label="⬇️ Download Full Backup",
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
                if st.button("♻️ Restore backup (merge into current data)"):
                    try:
                        contenuto_backup = pickle.loads(file_backup.read())
                        # Retrocompatibilità: i backup vecchi erano una semplice lista (solo portieri)
                        if isinstance(contenuto_backup, dict):
                            db_gk_ripristinato = contenuto_backup.get('db', [])
                            db_tir_ripristinato = contenuto_backup.get('db_tiratori', [])
                            db_h2h_ripristinato = contenuto_backup.get('db_h2h', [])
                            foto_ripristinate = contenuto_backup.get('foto_giocatori', {})
                            note_ripristinate = contenuto_backup.get('note_tiratori', {})
                            campionati_ripristinati = contenuto_backup.get('campionati', [])
                            profili_expected_ripristinati = contenuto_backup.get('profili_expected_stato', None)
                        else:
                            db_gk_ripristinato = contenuto_backup
                            db_tir_ripristinato = []
                            db_h2h_ripristinato = []
                            foto_ripristinate = {}
                            note_ripristinate = {}
                            campionati_ripristinati = []
                            profili_expected_ripristinati = None

                        chiavi_gk = {(p['nome'], str(p['data']), p['squadra']) for p in st.session_state['db']}
                        agg_gk = 0
                        for match in db_gk_ripristinato:
                            chiave = (match['nome'], str(match['data']), match['squadra'])
                            if chiave in chiavi_gk:
                                continue
                            st.session_state['db'].append(match)
                            chiavi_gk.add(chiave)
                            agg_gk += 1

                        chiavi_tir = {(p['nome'], str(p['data']), p['squadra']) for p in st.session_state['db_tiratori']}
                        agg_tir = 0
                        for match in db_tir_ripristinato:
                            chiave = (match['nome'], str(match['data']), match['squadra'])
                            if chiave in chiavi_tir:
                                continue
                            st.session_state['db_tiratori'].append(match)
                            chiavi_tir.add(chiave)
                            agg_tir += 1

                        chiavi_h2h = {(p['nome'], str(p['data'])) for p in st.session_state['db_h2h']}
                        agg_h2h = 0
                        for match in db_h2h_ripristinato:
                            chiave = (match['nome'], str(match['data']))
                            if chiave in chiavi_h2h:
                                continue
                            st.session_state['db_h2h'].append(match)
                            chiavi_h2h.add(chiave)
                            agg_h2h += 1

                        agg_foto = 0
                        for nome_g, foto_b64 in foto_ripristinate.items():
                            if nome_g not in st.session_state['foto_giocatori']:
                                st.session_state['foto_giocatori'][nome_g] = foto_b64
                                agg_foto += 1

                        agg_note = 0
                        for nome_g, nota in note_ripristinate.items():
                            if nome_g not in st.session_state['note_tiratori']:
                                st.session_state['note_tiratori'][nome_g] = nota
                                agg_note += 1

                        nomi_campionati_esistenti = {c['nome'] for c in st.session_state['campionati']}
                        agg_camp = 0
                        for camp in campionati_ripristinati:
                            if camp['nome'] not in nomi_campionati_esistenti:
                                st.session_state['campionati'].append(camp)
                                nomi_campionati_esistenti.add(camp['nome'])
                                agg_camp += 1

                        agg_profili = 0
                        if profili_expected_ripristinati:
                            for nome_p, valori_p in profili_expected_ripristinati.get('profili', {}).items():
                                if nome_p not in st.session_state['profili_expected_stato']['profili']:
                                    st.session_state['profili_expected_stato']['profili'][nome_p] = valori_p
                                    agg_profili += 1
                                elif nome_p == 'S.P. Value':
                                    # S.P. Value: il backup non sovrascrive mai la versione attuale automaticamente
                                    pass

                        salva_stagione_su_disco(st.session_state['db'])
                        salva_stagione_tiratori_su_disco(st.session_state['db_tiratori'])
                        salva_h2h_su_disco(st.session_state['db_h2h'])
                        salva_foto_su_disco(st.session_state['foto_giocatori'])
                        salva_note_su_disco(st.session_state['note_tiratori'])
                        salva_campionati_su_disco(st.session_state['campionati'])
                        salva_profili_expected_su_disco(st.session_state['profili_expected_stato'])
                        st.success(f"Restored {agg_gk} goalkeeper record(s), {agg_tir} shooter record(s), "
                                   f"{agg_h2h} head-to-head match(es), {agg_foto} photo(s), {agg_note} note(s), "
                                   f"{agg_camp} championship(s), {agg_profili} Expected Values profile(s) from the backup file.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not read this backup file: {e}")

        st.markdown("---")
        st.subheader("🗑️ Delete a Single Match")
        st.caption("Remove one specific match from the season — goalkeeper data, shooter data and "
                   "head-to-head data all at once, since a single unified file feeds all three.")
        chiavi_match = sorted(set(
            [(p['nome'], str(p['data'])) for p in st.session_state['db']] +
            [(p['nome'], str(p['data'])) for p in st.session_state['db_tiratori']] +
            [(p['nome'], str(p['data'])) for p in st.session_state.get('db_h2h', [])]
        ), key=lambda k: k[1])
        if chiavi_match:
            etichette_match_elimina = [f"{nome} ({data})" for nome, data in chiavi_match]
            match_da_eliminare = st.selectbox(
                "Select the match to delete:", etichette_match_elimina, key="elimina_partita_select"
            )
            nome_sel, data_sel = chiavi_match[etichette_match_elimina.index(match_da_eliminare)]
            n_gk = sum(1 for p in st.session_state['db'] if p['nome'] == nome_sel and str(p['data']) == data_sel)
            n_tir = sum(1 for p in st.session_state['db_tiratori'] if p['nome'] == nome_sel and str(p['data']) == data_sel)
            n_h2h = sum(1 for p in st.session_state.get('db_h2h', []) if p['nome'] == nome_sel and str(p['data']) == data_sel)
            st.caption(f"Will remove: {n_gk} goalkeeper record(s), {n_tir} shooter record(s), {n_h2h} head-to-head match(es).")
            conferma_elimina_singola = st.checkbox(
                "I confirm I want to delete this match only (this action is irreversible)",
                key="conferma_elimina_singola"
            )
            if st.button("🗑️ Delete This Match", disabled=not conferma_elimina_singola):
                st.session_state['db'] = [p for p in st.session_state['db']
                                           if not (p['nome'] == nome_sel and str(p['data']) == data_sel)]
                st.session_state['db_tiratori'] = [p for p in st.session_state['db_tiratori']
                                                    if not (p['nome'] == nome_sel and str(p['data']) == data_sel)]
                st.session_state['db_h2h'] = [p for p in st.session_state.get('db_h2h', [])
                                               if not (p['nome'] == nome_sel and str(p['data']) == data_sel)]
                salva_stagione_su_disco(st.session_state['db'])
                salva_stagione_tiratori_su_disco(st.session_state['db_tiratori'])
                salva_h2h_su_disco(st.session_state['db_h2h'])
                st.success(f"Match '{match_da_eliminare}' deleted (all data). "
                           f"Remaining: {len(st.session_state['db'])} goalkeeper record(s), "
                           f"{len(st.session_state['db_tiratori'])} shooter record(s), "
                           f"{len(st.session_state['db_h2h'])} head-to-head match(es).")
                st.rerun()
        else:
            st.caption("No matches to delete yet.")

        st.markdown("---")
        st.subheader("⚠️ Reset Season")
        st.caption("This resets the ENTIRE app season: goalkeepers AND shooters (Shooting Trend "
                   "Analysis), including player notes. Use this only at the start of a new season.")
        st.caption(f"Goalkeeper matches currently saved: **{len(st.session_state['db'])}**  |  "
                   f"Shooter matches currently saved: **{len(st.session_state.get('db_tiratori', []))}**")
        conferma_reset = st.checkbox("I confirm I want to delete ALL season data — goalkeepers and shooters — (this action is irreversible)")
        if st.button("🔄 Reset Season (goalkeepers + shooters)", disabled=not conferma_reset):
            st.session_state['db'] = []
            salva_stagione_su_disco(st.session_state['db'])
            if os.path.exists(SEASON_FILE):
                os.remove(SEASON_FILE)
            st.session_state['db_tiratori'] = []
            salva_stagione_tiratori_su_disco(st.session_state['db_tiratori'])
            if os.path.exists(SHOOTER_SEASON_FILE):
                os.remove(SHOOTER_SEASON_FILE)
            st.session_state['note_tiratori'] = {}
            salva_note_su_disco(st.session_state['note_tiratori'])
            if os.path.exists(SHOOTER_NOTES_FILE):
                os.remove(SHOOTER_NOTES_FILE)
            st.session_state['db_h2h'] = []
            salva_h2h_su_disco(st.session_state['db_h2h'])
            if os.path.exists(H2H_FILE):
                os.remove(H2H_FILE)
            st.success("Season reset. All data (goalkeepers and shooters) has been deleted.")
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
        gpi_totale_squadra = df_match['GPI_Tiro'].sum()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Saves", s_t)
        c2.metric("Total Goals Conceded", g_t)
        c3.metric("Team Save %", f"{pct_t:.1f}%")
        c4.metric("Team Efficiency %", f"{eff_t:.1f}%")
        c5.metric("Team GPI (Total)", f"{gpi_totale_squadra:+.1f}")
        
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

        st.plotly_chart(fig_linee, use_container_width=True, key="fig_linee_single_match")
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
                gestisci_foto_giocatore(identita_giocatore(gk), key_prefix="single_match")

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
                    expected = ottieni_expected_pct(settore)
                    righe_settore.append({
                        'Zone': settore, 'Saves': s, 'Goals': g, 'Miss': m,
                        'Save %': round(pct, 1), 'Efficiency %': round(eff, 1),
                        'Expected Efficiency %': expected if expected is not None else '',
                        'GPI': round(df_s['GPI_Tiro'].sum(), 1)
                    })
                st.dataframe(applica_colori_expected(pd.DataFrame(righe_settore)), use_container_width=True, hide_index=True)

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

        st.plotly_chart(fig_blocchi, use_container_width=True, key="fig_blocchi_single_match")
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

        opzioni_campionato_gk = ["All Data & All Time"] + [c['nome'] for c in st.session_state['campionati']]
        campionato_scelto_gk = st.selectbox("🏆 Championship:", opzioni_campionato_gk, key="campionato_gk")
        if campionato_scelto_gk != "All Data & All Time":
            campionato_obj_gk = next(c for c in st.session_state['campionati'] if c['nome'] == campionato_scelto_gk)
            db_gk_filtrato = partite_in_campionato(st.session_state['db'], campionato_obj_gk)
        else:
            db_gk_filtrato = st.session_state['db']

        portieri_stagione = sorted(set(
            gk for match in db_gk_filtrato for gk in match['dati']['PORTIERE_ID'].dropna().unique()
        ))
        squadre_stagione = sorted(set(match['squadra'] for match in db_gk_filtrato))

        df_stagione_totale = pd.DataFrame()
        dati_per_portiere = {}
        titolo_report = ""

        if not db_gk_filtrato:
            st.info("No matches fall within this championship's team/date filters.")
        elif modalita == "Goalkeeper":
            if not portieri_stagione:
                st.info("No goalkeepers found in the uploaded data.")
            else:
                portiere_scelto = st.selectbox("Select goalkeeper:", portieri_stagione)
                df_stagione_totale, lista_partite = raccogli_stagione_per_portiere(db_gk_filtrato, portiere_scelto)
                dati_per_portiere = {portiere_scelto: lista_partite}
                titolo_report = f"{campionato_scelto_gk} — {portiere_scelto}"
        else:
            if not squadre_stagione:
                st.info("No teams found in the uploaded data.")
            else:
                squadra_scelta = st.selectbox("Select team:", squadre_stagione)
                with st.expander(f"🖼️ {squadra_scelta} logo"):
                    gestisci_logo_squadra(squadra_scelta, key_prefix="gk_seasonal")
                df_stagione_totale, dati_per_portiere = raccogli_stagione_per_squadra(db_gk_filtrato, squadra_scelta)
                titolo_report = f"{campionato_scelto_gk} — {squadra_scelta}"

        # ------------------------------------------------------------
        # SELETTORE GRUPPO PARTITE: tutta la stagione (default), una singola
        # partita, oppure un gruppo a scelta (es. solo le partite in casa).
        # ------------------------------------------------------------
        if titolo_report and not df_stagione_totale.empty:
            etichette_disponibili = sorted(
                set(p['label'] for lista in dati_per_portiere.values() for p in lista),
                key=lambda lbl: next(p['data'] for lista in dati_per_portiere.values() for p in lista if p['label'] == lbl)
            )
            selezione_match = st.multiselect(
                "Filter matches (leave empty to use the whole season):",
                etichette_disponibili, default=[]
            )
            if selezione_match:
                df_stagione_totale = df_stagione_totale[df_stagione_totale['Match_Label'].isin(selezione_match)]
                dati_per_portiere = {
                    gk: [p for p in lista if p['label'] in selezione_match]
                    for gk, lista in dati_per_portiere.items()
                }
                dati_per_portiere = {gk: lista for gk, lista in dati_per_portiere.items() if lista}
                titolo_report = titolo_report + f" ({len(selezione_match)} selected match(es))"

        if titolo_report and df_stagione_totale.empty:
            st.info("No data available for the current selection: the selected goalkeeper/team has not yet faced any shots in the uploaded matches.")
        elif titolo_report:
            st.markdown("---")
            st.subheader(f"📊 Total Season Statistics — {titolo_report.replace('Season — ', '')}")
            s_tot, g_tot, m_tot, pct_tot, eff_tot = calcola_metriche_gruppo(df_stagione_totale)
            gpi_medio_tot = df_stagione_totale['GPI_Tiro'].mean() if not df_stagione_totale.empty else 0.0
            numero_partite_coinvolte = len(set(p['label'] for lista in dati_per_portiere.values() for p in lista))
            media_cumulativa_gpi = (df_stagione_totale['GPI_Tiro'].sum() / numero_partite_coinvolte) if numero_partite_coinvolte > 0 else 0.0
            c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
            c1.metric("Shots Faced", len(df_stagione_totale))
            c2.metric("Saves", s_tot)
            c3.metric("Goals Conceded", g_tot)
            c4.metric("Save %", f"{pct_tot:.1f}%")
            c5.metric("Efficiency %", f"{eff_tot:.1f}%")
            c6.metric("Average GPI (per shot)", f"{gpi_medio_tot:+.2f}")
            c7.metric("Cumulative Average GPI (per match)", f"{media_cumulativa_gpi:+.2f}")

            st.markdown("---")
            st.subheader("🥅 Total Season GPI per Goalkeeper")
            righe_gpi_stagione = []
            for gk, lista in dati_per_portiere.items():
                df_gk_tot = df_stagione_totale[df_stagione_totale['PORTIERE_ID'] == gk]
                righe_gpi_stagione.append({
                    'Goalkeeper': gk,
                    'Number': combina_numeri_maglia(lista),
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
                df_gk_tot = df_stagione_totale[df_stagione_totale['PORTIERE_ID'] == gk]
                if df_gk_tot.empty:
                    continue
                info = calcola_dettaglio_portiere(df_gk_tot, lista_partite=lista)
                dati_pdf_portieri_stagione[gk] = info
                numero_gk = combina_numeri_maglia(lista)
                etichetta_numero = f" ({numero_gk})" if numero_gk else ""
                with st.expander(f"{gk}{etichetta_numero} — Total Season GPI: {info['gpi_totale']:+.1f}", expanded=True):
                    gestisci_foto_giocatore(gk, key_prefix="gk")
                    cA, cB, cC, cD, cE = st.columns(5)
                    cA.metric("Total GPI", f"{info['gpi_totale']:+.1f}")
                    cB.metric("Saves", info['parate'])
                    cC.metric("Goals Conceded", info['gol'])
                    cD.metric("Save %", f"{info['pct']:.1f}%")
                    cE.metric("Efficiency", f"{info['eff']:.1f}%")

                    st.markdown("**Statistics by specific shot zone**")
                    st.dataframe(applica_colori_expected(info['tabella_settore']), use_container_width=True, hide_index=True)

                    st.markdown("**Statistics by aggregated macro-zone**")
                    st.dataframe(info['tabella_macro'], use_container_width=True, hide_index=True)

                    st.markdown(f"**Money Time Performance:** {info['money_time_riassunto']}")

                    split_casa = calcola_split_casa_trasferta(dati_per_portiere.get(gk, []), 'saves', 'tiri')
                    st.markdown(f"**Home/Away Save %:** {formatta_riga_casa_trasferta(split_casa)}")

            st.markdown("---")
            st.subheader("⏱️ Performance by 10-Minute Blocks (season cumulative)")
            df_blocchi_stagione, fig_blocchi_stagione = costruisci_grafico_blocchi(df_stagione_totale)
            st.plotly_chart(fig_blocchi_stagione, use_container_width=True, key="fig_blocchi_seasonal")
            st.dataframe(df_blocchi_stagione, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("📄 Export Season Report to PDF")
            st.caption("Generate a PDF with every section of this page: totals, GPI and save % trends, match history, per-goalkeeper statistics, and 10-minute blocks.")

            if st.button("📄 Generate Season PDF"):
                with st.spinner("Generating PDF..."):
                    try:
                        logo_squadra_gk = st.session_state['loghi_squadre'].get(squadra_scelta) if modalita == "Team" else None
                        pdf_bytes_stagione = genera_pdf_stagione(
                            titolo_report=titolo_report,
                            righe_gpi_stagione=righe_gpi_stagione,
                            df_storico=df_storico,
                            dati_portieri=dati_per_portiere,
                            df_blocchi=df_blocchi_stagione,
                            df_stagione_totale=df_stagione_totale,
                            fig_blocchi=fig_blocchi_stagione,
                            logo_squadra_b64=logo_squadra_gk
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


with tab4:
    st.header("🎯 Shooting Trend Analysis")
    st.caption("Reserved staff section — shooter shot maps, expected goals, money time and home/away trends.")

    if 'staff_authorized' not in st.session_state:
        st.session_state['staff_authorized'] = False

    if not st.session_state['staff_authorized']:
        st.info("🔒 This section is reserved for authorized staff.")
        with st.form(key="form_staff_access", clear_on_submit=True):
            codice_staff = st.text_input("Access code", type="password", key="codice_staff")
            sbloccato_staff = st.form_submit_button("Unlock")
        if sbloccato_staff:
            if codice_staff == STAFF_ACCESS_CODE:
                st.session_state['staff_authorized'] = True
                st.rerun()
            else:
                st.error("Incorrect code.")
    else:
        st.caption("To delete a specific match (goalkeeper + shooter + head-to-head data together) "
                   "or to wipe the whole season, use 📥 Upload Match Sheets.")

        # ============================================================
        # DASHBOARD
        # ============================================================
        st.markdown("---")
        st.header("📊 Shooting Trend Dashboard")

        if not st.session_state['db_tiratori']:
            st.warning("No shooter matches uploaded yet.")
        else:
            opzioni_campionato_tir = ["All Data & All Time"] + [c['nome'] for c in st.session_state['campionati']]
            campionato_scelto_tir = st.selectbox("🏆 Championship:", opzioni_campionato_tir, key="campionato_tir")
            if campionato_scelto_tir != "All Data & All Time":
                campionato_obj_tir = next(c for c in st.session_state['campionati'] if c['nome'] == campionato_scelto_tir)
                db_tir = partite_in_campionato(st.session_state['db_tiratori'], campionato_obj_tir)
            else:
                db_tir = st.session_state['db_tiratori']

            if not db_tir:
                st.warning("No matches fall within this championship's team/date filters — showing All Data & All Time instead.")
                db_tir = st.session_state['db_tiratori']

            squadre_tir = sorted(set(m['squadra'] for m in db_tir))
            giocatori_tir = sorted(set(
                g for m in db_tir for g in m['dati']['TIRATORE_ID'].dropna().unique()
            ))

            with st.expander(f"🌍 League Totals — {campionato_scelto_tir} (all teams, all shots)"):
                df_lega_totale = pd.concat([m['dati'] for m in db_tir], ignore_index=True)
                goal_lega, tot_lega, pct_lega = calcola_metriche_tiratori_gruppo(df_lega_totale)
                st.caption(f"Overall: {goal_lega}/{tot_lega} = {pct_lega:.1f}%  —  "
                           f"{len(squadre_tir)} team(s), {len(giocatori_tir)} player(s), {len(db_tir)} match record(s).")
                st.markdown("**By macro-zone**")
                st.dataframe(tabella_macro_tiratori(df_lega_totale), use_container_width=True, hide_index=True)
                macro_lega_scelto = st.selectbox(
                    "Break down a macro-zone into micro-zones (optional):",
                    ["(none)"] + [ETICHETTA_MACRO_TIRATORI[m] for m in ORDINE_MACRO_TIRATORI],
                    key="macro_lega_tir"
                )
                if macro_lega_scelto != "(none)":
                    macro_lega_key = next(k for k, v in ETICHETTA_MACRO_TIRATORI.items() if v == macro_lega_scelto)
                    st.dataframe(tabella_micro_di_un_macro(df_lega_totale, macro_lega_key), use_container_width=True, hide_index=True)

            modalita_tir = st.radio("View by:", ["Team", "Player"], horizontal=True, key="modalita_tir")

            if modalita_tir == "Team":
                squadra_scelta_tir = st.selectbox("Select team:", squadre_tir, key="squadra_scelta_tir")
                with st.expander(f"🖼️ {squadra_scelta_tir} logo"):
                    gestisci_logo_squadra(squadra_scelta_tir, key_prefix="tir_dashboard")
                match_squadra = [m for m in db_tir if m['squadra'] == squadra_scelta_tir]
                giocatori_da_mostrare = sorted(set(
                    g for m in match_squadra for g in m['dati']['TIRATORE_ID'].dropna().unique()
                ))
                match_rilevanti = match_squadra
                titolo_dashboard = squadra_scelta_tir
            else:
                giocatore_scelto_tir = st.selectbox("Select player:", giocatori_tir, key="giocatore_scelto_tir")
                giocatori_da_mostrare = [giocatore_scelto_tir]
                match_rilevanti = [m for m in db_tir if giocatore_scelto_tir in m['dati']['TIRATORE_ID'].values]
                titolo_dashboard = giocatore_scelto_tir

            # ---- Match group selector ----
            match_rilevanti_ord = sorted(match_rilevanti, key=lambda m: m['data'])
            etichette_match = [f"{m['nome']} ({m['data']})" for m in match_rilevanti_ord]
            selezione_match_tir = st.multiselect(
                "Filter matches (leave empty to use the whole season):",
                etichette_match, default=[], key="selezione_match_tir"
            )
            match_filtrati = (
                [m for m, lbl in zip(match_rilevanti_ord, etichette_match) if lbl in selezione_match_tir]
                if selezione_match_tir else match_rilevanti_ord
            )

            col_a, col_b = st.columns(2)
            with col_a:
                solo_money_time = st.checkbox("Money Time only (from 50', score margin ±5)", key="mt_toggle_tir")
            with col_b:
                macro_scelto = st.selectbox(
                    "Focus on a macro-zone (optional):",
                    ["(All zones)"] + [ETICHETTA_MACRO_TIRATORI[m] for m in ORDINE_MACRO_TIRATORI],
                    key="macro_scelto_tir"
                )
            macro_key = None
            if macro_scelto != "(All zones)":
                macro_key = next(k for k, v in ETICHETTA_MACRO_TIRATORI.items() if v == macro_scelto)

            if not match_filtrati:
                st.info("No matches match the current selection.")
            else:
                # ---- Aggregato dell'attuale selezione (squadra o giocatore singolo, filtrata) ----
                frammenti_sel = []
                for m in match_filtrati:
                    d = m['dati'][m['dati']['TIRATORE_ID'].isin(giocatori_da_mostrare)]
                    if not d.empty:
                        frammenti_sel.append(d)
                df_selezione = pd.concat(frammenti_sel, ignore_index=True) if frammenti_sel else m['dati'].iloc[0:0]
                if solo_money_time and not df_selezione.empty:
                    df_selezione = df_selezione[df_selezione['Is_Money_Time'] == True]

                # ---- Shooters ranked by shot volume (team view only) ----
                if modalita_tir == "Team":
                    st.markdown("---")
                    st.subheader(f"🔝 Shooters by Shot Volume — {titolo_dashboard}")
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        st.markdown("**By total shot volume**")
                        st.dataframe(classifica_tiratori_per_volume(df_selezione), use_container_width=True, hide_index=True)
                    with cc2:
                        st.markdown("**By Money Time shot volume**")
                        st.dataframe(classifica_tiratori_per_volume(df_selezione, solo_money_time=True), use_container_width=True, hide_index=True)

                # ---- Shot Map: porta e pulsantiera affiancate ----
                st.markdown("---")
                st.subheader(f"🥅 Shot Map — {titolo_dashboard}")
                if 'tasto_focus_shared' not in st.session_state:
                    st.session_state['tasto_focus_shared'] = None
                tot_tast_sel, goal_tast_sel = costruisci_conteggi_tastiera(df_selezione)
                if st.session_state['tasto_focus_shared'] not in TUTTI_I_TASTI_TIRATORI:
                    st.session_state['tasto_focus_shared'] = None
                tasto_scelto = st.session_state['tasto_focus_shared']

                if tasto_scelto:
                    df_porta_sel = df_selezione[df_selezione['TIRO_CLEAN'].apply(_normalizza_zona) == tasto_scelto]
                    if macro_key:
                        df_porta_sel = df_porta_sel[df_porta_sel['macro_settore_tir'] == macro_key]
                    g_sel, t_sel, pct_sel = calcola_metriche_tiratori_gruppo(df_porta_sel)
                    expected_sel = ottieni_expected_goal_pct(tasto_scelto)
                    colore_cornice_sel = _colore_expected(pct_sel if t_sel > 0 else None, expected_sel)
                else:
                    df_porta_sel = df_selezione if not macro_key else df_selezione[df_selezione['macro_settore_tir'] == macro_key]
                    colore_cornice_sel = None
                tot_p_sel, goal_p_sel = costruisci_conteggi_porta(df_porta_sel)
                fig_p_sel = disegna_porta(tot_p_sel, goal_p_sel, colore_cornice=colore_cornice_sel)

                col_porta_sel, col_tast_sel = st.columns([1, 2])
                with col_porta_sel:
                    st.pyplot(fig_p_sel)
                    if tasto_scelto:
                        expected_testo_sel = f"{expected_sel:.0f}%" if expected_sel is not None else "n/a"
                        if t_sel > 0:
                            st.caption(f"Expected Goal % for {tasto_scelto}: **{expected_testo_sel}**  |  Real: **{pct_sel:.1f}%** ({g_sel}/{t_sel})")
                        else:
                            st.caption(f"Expected Goal % for {tasto_scelto}: **{expected_testo_sel}**  |  No shots from this sector.")
                with col_tast_sel:
                    tasto_cliccato = pulsantiera_settori_campo(
                        tot_tast_sel, goal_tast_sel, tasto_scelto, key_prefix="pulsantiera"
                    )
                    if tasto_cliccato:
                        st.session_state['tasto_focus_shared'] = (
                            None if tasto_cliccato == st.session_state['tasto_focus_shared'] else tasto_cliccato
                        )
                        st.rerun()
                    if tasto_scelto:
                        if st.button("↺ Reset — show all sectors", key="reset_tasto_focus"):
                            st.session_state['tasto_focus_shared'] = None
                            st.rerun()

                if modalita_tir == "Team":
                    if macro_key:
                        st.markdown(f"**Breakdown of macro-zone {ETICHETTA_MACRO_TIRATORI[macro_key]}**")
                        g_msq, t_msq, pct_msq = calcola_metriche_tiratori_gruppo(df_selezione[df_selezione['macro_settore_tir'] == macro_key])
                        st.caption(f"Macro-zone total: {g_msq}/{t_msq} = {pct_msq:.1f}%")
                        st.dataframe(tabella_micro_di_un_macro(df_selezione, macro_key), use_container_width=True, hide_index=True)
                    else:
                        st.markdown("**By macro-zone**")
                        st.dataframe(tabella_macro_tiratori(df_selezione), use_container_width=True, hide_index=True)

                st.markdown("---")
                dati_pdf_giocatori = {}
                for nome_giocatore in giocatori_da_mostrare:
                    frammenti_g = []
                    lista_partite_g = []
                    for m in match_filtrati:
                        df_g_match = m['dati'][m['dati']['TIRATORE_ID'] == nome_giocatore]
                        if df_g_match.empty:
                            continue
                        frammenti_g.append(df_g_match)
                        g_, tot_, pct_ = calcola_metriche_tiratori_gruppo(df_g_match)
                        df_g_mt = df_g_match[df_g_match['Is_Money_Time'] == True]
                        g_mt, tot_mt, pct_mt = calcola_metriche_tiratori_gruppo(df_g_mt)
                        lista_partite_g.append({
                            'label': f"{m['nome']} ({m['data']})", 'goals': g_, 'shots': tot_,
                            'money_time_goals': g_mt, 'money_time_shots': tot_mt,
                            'casa_trasferta': determina_casa_trasferta(m['squadra'], m.get('squadra_home'), m.get('squadra_away')),
                        })
                    if not frammenti_g:
                        continue
                    df_giocatore = pd.concat(frammenti_g, ignore_index=True)
                    if solo_money_time:
                        df_giocatore = df_giocatore[df_giocatore['Is_Money_Time'] == True]
                    if macro_key:
                        df_giocatore_vista = df_giocatore[df_giocatore['macro_settore_tir'] == macro_key]
                    else:
                        df_giocatore_vista = df_giocatore

                    with st.expander(f"🤾 {nome_giocatore}", expanded=(modalita_tir == "Player")):
                        gestisci_foto_giocatore(nome_giocatore, key_prefix="tir")
                        goal_tot, shots_tot, pct_tot = calcola_metriche_tiratori_gruppo(df_giocatore_vista)
                        cA, cB, cC = st.columns(3)
                        cA.metric("Shots", shots_tot)
                        cB.metric("Goals", goal_tot)
                        cC.metric("Goal %", f"{pct_tot:.1f}%")

                        # ---- Porta e tastiera individuali (stessa identica grafica e funzionalità
                        # della pulsantiera condivisa qui sopra; solo in vista Team — in vista Player
                        # sono già mostrate, identiche, nella Shot Map in cima alla pagina) ----
                        if modalita_tir == "Team":
                            if tasto_scelto:
                                df_per_porta = df_giocatore[df_giocatore['TIRO_CLEAN'].apply(_normalizza_zona) == tasto_scelto]
                                if macro_key:
                                    df_per_porta = df_per_porta[df_per_porta['macro_settore_tir'] == macro_key]
                                g_sel, t_sel, pct_sel = calcola_metriche_tiratori_gruppo(df_per_porta)
                                expected_sel = ottieni_expected_goal_pct(tasto_scelto)
                                colore_cornice = _colore_expected(pct_sel if t_sel > 0 else None, expected_sel)
                                tot_porta, goal_porta = costruisci_conteggi_porta(df_per_porta)
                            else:
                                tot_porta, goal_porta = costruisci_conteggi_porta(df_giocatore_vista)
                                colore_cornice = None
                            fig_p = disegna_porta(tot_porta, goal_porta, colore_cornice=colore_cornice)
                            tot_tast, goal_tast = costruisci_conteggi_tastiera(df_giocatore)

                            chiave_giocatore = _chiave_css_sicura(nome_giocatore)
                            col_porta, col_tast = st.columns([1, 2])
                            with col_porta:
                                st.pyplot(fig_p)
                                if tasto_scelto:
                                    expected_testo = f"{expected_sel:.0f}%" if expected_sel is not None else "n/a"
                                    if t_sel > 0:
                                        st.caption(f"Expected Goal % for {tasto_scelto}: **{expected_testo}**  |  Real: **{pct_sel:.1f}%** ({g_sel}/{t_sel})")
                                    else:
                                        st.caption(f"Expected Goal % for {tasto_scelto}: **{expected_testo}**  |  No shots from this sector.")
                            with col_tast:
                                tasto_cliccato_p = pulsantiera_settori_campo(
                                    tot_tast, goal_tast, tasto_scelto, key_prefix=f"pulsantiera_{chiave_giocatore}"
                                )
                                if tasto_cliccato_p:
                                    st.session_state['tasto_focus_shared'] = (
                                        None if tasto_cliccato_p == tasto_scelto else tasto_cliccato_p
                                    )
                                    st.rerun()
                                if tasto_scelto:
                                    if st.button("↺ Reset — show all sectors", key=f"reset_tasto_focus_{chiave_giocatore}"):
                                        st.session_state['tasto_focus_shared'] = None
                                        st.rerun()

                        # ---- Macro breakdown ----
                        if macro_key:
                            st.markdown(f"**Breakdown of macro-zone {ETICHETTA_MACRO_TIRATORI[macro_key]}**")
                            df_macro_view = df_giocatore[df_giocatore['macro_settore_tir'] == macro_key]
                            g_m, t_m, pct_m = calcola_metriche_tiratori_gruppo(df_macro_view)
                            st.caption(f"Macro-zone total: {g_m}/{t_m} = {pct_m:.1f}%")
                            st.dataframe(tabella_micro_di_un_macro(df_giocatore, macro_key), use_container_width=True, hide_index=True)
                        else:
                            st.markdown("**By macro-zone**")
                            st.dataframe(tabella_macro_tiratori(df_giocatore), use_container_width=True, hide_index=True)

                        # ---- Home/Away & Money Time summary ----
                        split_casa_tir = calcola_split_casa_trasferta(lista_partite_g, 'goals', 'shots')
                        st.markdown(f"**Home/Away Goal %:** {formatta_riga_casa_trasferta(split_casa_tir)}")

                        tot_mt_g = sum(p['money_time_goals'] for p in lista_partite_g)
                        tot_mt_s = sum(p['money_time_shots'] for p in lista_partite_g)
                        if tot_mt_s > 0:
                            st.markdown(f"**Money Time Performance:** {tot_mt_g}/{tot_mt_s} = {tot_mt_g/tot_mt_s*100:.1f}%")
                        else:
                            st.markdown("**Money Time Performance:** No shots in Money Time.")

                        # ---- Coach notes ----
                        st.markdown("**Coach notes** (use `**bold**`, `__underline__`, `==highlight==` — max 1000 characters)")
                        nota_attuale = st.session_state['note_tiratori'].get(nome_giocatore, '')
                        nota_nuova = st.text_area("Notes", value=nota_attuale, max_chars=1000,
                                                   key=f"nota_{nome_giocatore}", label_visibility="collapsed")
                        if nota_nuova != nota_attuale:
                            st.session_state['note_tiratori'][nome_giocatore] = nota_nuova
                            salva_note_su_disco(st.session_state['note_tiratori'])
                        if nota_nuova.strip():
                            st.markdown(note_markup_a_html_streamlit(nota_nuova), unsafe_allow_html=True)

                        # ---- Single-player PDF ----
                        if st.button(f"📄 Generate PDF — {nome_giocatore}", key=f"pdf_{nome_giocatore}"):
                            with st.spinner("Generating PDF..."):
                                try:
                                    pdf_bytes_g = genera_pdf_tiratori(
                                        f"{titolo_dashboard} — {nome_giocatore}",
                                        {nome_giocatore: df_giocatore_vista},
                                        {nome_giocatore: nota_nuova}
                                    )
                                    st.download_button(
                                        label="⬇️ Download PDF", data=pdf_bytes_g,
                                        file_name=f"Shooting_Report_{nome_giocatore}".replace(' ', '_') + ".pdf",
                                        mime="application/pdf", key=f"dl_{nome_giocatore}"
                                    )
                                except Exception as e:
                                    st.error(f"Error generating PDF: {e}")

                        dati_pdf_giocatori[nome_giocatore] = df_giocatore_vista

                # ---- Team / full-selection PDF ----
                st.markdown("---")
                st.subheader("📄 Export to PDF")
                col_pdf1, col_pdf2 = st.columns(2)
                with col_pdf1:
                    if st.button("📄 Generate PDF for this selection"):
                        with st.spinner("Generating PDF..."):
                            try:
                                note_selezione = {g: st.session_state['note_tiratori'].get(g, '') for g in dati_pdf_giocatori}
                                logo_squadra_tir = st.session_state['loghi_squadre'].get(titolo_dashboard) if modalita_tir == "Team" else None
                                pdf_bytes_sel = genera_pdf_tiratori(
                                    titolo_dashboard, dati_pdf_giocatori, note_selezione,
                                    df_squadra_riepilogo=(df_selezione if modalita_tir == "Team" else None),
                                    logo_squadra_b64=logo_squadra_tir
                                )
                                st.download_button(
                                    label="⬇️ Download PDF", data=pdf_bytes_sel,
                                    file_name=f"Shooting_Report_{titolo_dashboard}".replace(' ', '_') + ".pdf",
                                    mime="application/pdf", key="dl_selection"
                                )
                            except Exception as e:
                                st.error(f"Error generating PDF: {e}")
                with col_pdf2:
                    if st.button("📄 Generate Trend Summary PDF (notes only)"):
                        with st.spinner("Generating PDF..."):
                            try:
                                note_selezione = {g: st.session_state['note_tiratori'].get(g, '') for g in dati_pdf_giocatori}
                                pdf_bytes_summary = genera_pdf_trend_summary(titolo_dashboard, note_selezione)
                                st.download_button(
                                    label="⬇️ Download Trend Summary", data=pdf_bytes_summary,
                                    file_name=f"Trend_Summary_{titolo_dashboard}".replace(' ', '_') + ".pdf",
                                    mime="application/pdf", key="dl_summary"
                                )
                            except Exception as e:
                                st.error(f"Error generating PDF: {e}")

        # ============================================================
        # TESTA A TESTA: "chi soffre chi"
        # ============================================================
        st.markdown("---")
        st.header("🥊 Head-to-Head — Who Suffers Whom")
        st.caption("Available only for matches uploaded with the unified format (HOME/AWAY, single file).")

        if not st.session_state['db_h2h']:
            st.info("No head-to-head data yet — upload at least one match using the unified format above.")
        else:
            opzioni_campionato_h2h = ["All Data & All Time"] + [c['nome'] for c in st.session_state['campionati']]
            campionato_scelto_h2h = st.selectbox("🏆 Championship:", opzioni_campionato_h2h, key="campionato_h2h")
            if campionato_scelto_h2h != "All Data & All Time":
                campionato_obj_h2h = next(c for c in st.session_state['campionati'] if c['nome'] == campionato_scelto_h2h)
                db_h2h_filtrato = partite_h2h_in_campionato(st.session_state['db_h2h'], campionato_obj_h2h)
            else:
                db_h2h_filtrato = st.session_state['db_h2h']

            if not db_h2h_filtrato:
                st.warning("No head-to-head matches fall within this championship's team/date filters — showing All Data & All Time instead.")
                db_h2h_filtrato = st.session_state['db_h2h']

            df_h2h_tot = pd.concat([m['dati'] for m in db_h2h_filtrato], ignore_index=True)
            portieri_h2h = sorted(df_h2h_tot['PORTIERE_ID'].unique())
            tiratori_h2h = sorted(df_h2h_tot['TIRATORE_ID'].unique())
            tutti_giocatori_h2h = sorted(set(portieri_h2h) | set(tiratori_h2h))

            giocatore_h2h = st.selectbox("Select player (goalkeeper or shooter):", tutti_giocatori_h2h, key="giocatore_h2h")
            e_portiere_h2h = giocatore_h2h in portieri_h2h

            classifica_completa = classifica_h2h(df_h2h_tot, giocatore_h2h, e_portiere_h2h)
            squadre_avversarie_disponibili = sorted(classifica_completa['Team'].dropna().unique())
            squadre_scelte_h2h = st.multiselect(
                "Filter by opponent team (leave empty to include all teams faced):",
                squadre_avversarie_disponibili, default=[], key="squadre_h2h"
            )
            if squadre_scelte_h2h:
                classifica_finale = classifica_completa[classifica_completa['Team'].isin(squadre_scelte_h2h)].reset_index(drop=True)
            else:
                classifica_finale = classifica_completa

            etichetta_ruolo = "Goalkeeper" if e_portiere_h2h else "Shooter"
            etichetta_avv = "Shooters" if e_portiere_h2h else "Goalkeepers"
            st.markdown(f"**{giocatore_h2h}** ({etichetta_ruolo}) — {etichetta_avv} ranked from most to least suffered:")
            classifica_finale_vis = classifica_finale.rename(columns={'Opponent': etichetta_avv[:-1] if etichetta_avv.endswith('s') else etichetta_avv})
            st.dataframe(classifica_finale_vis, use_container_width=True, hide_index=True)

with tab5:
    st.header("🏋️ Training Sessions")
    st.caption("Reserved staff section — training session library (PDFs exported from OneNote), "
               "exercise video links, and export as a branded PDF ready to share with a team.")

    if 'training_authorized' not in st.session_state:
        st.session_state['training_authorized'] = False

    if not st.session_state['training_authorized']:
        st.info("🔒 This section is reserved for authorized staff.")
        with st.form(key="form_training_access", clear_on_submit=True):
            codice_training = st.text_input("Access code", type="password", key="codice_training")
            sbloccato_training = st.form_submit_button("Unlock")
        if sbloccato_training:
            if codice_training == TRAINING_ACCESS_CODE:
                st.session_state['training_authorized'] = True
                st.rerun()
            else:
                st.error("Incorrect code.")
    else:
        # ============================================================
        # SQUADRE ALLENATE
        # ============================================================
        st.subheader("👥 Teams you coach")
        with st.expander("➕ Add a team"):
            nome_squadra_nuova = st.text_input("Team name", key="nuova_squadra_training_nome")
            if st.button("➕ Add team"):
                nome_pulito_squadra = nome_squadra_nuova.strip()
                if not nome_pulito_squadra:
                    st.error("Give the team a name.")
                elif any(s['nome'] == nome_pulito_squadra for s in st.session_state['squadre_allenate']):
                    st.error("A team with this name already exists.")
                else:
                    st.session_state['squadre_allenate'].append({'nome': nome_pulito_squadra})
                    salva_squadre_allenate_su_disco(st.session_state['squadre_allenate'])
                    st.success(f"Team '{nome_pulito_squadra}' added. You can attach a logo below.")
                    st.rerun()

        if st.session_state['squadre_allenate']:
            indici_ordinati = sorted(range(len(st.session_state['squadre_allenate'])),
                                      key=lambda i: st.session_state['squadre_allenate'][i]['nome'].lower())
            colonne_squadre = st.columns(min(len(st.session_state['squadre_allenate']), 5))
            for posizione, i in enumerate(indici_ordinati):
                squadra = st.session_state['squadre_allenate'][i]
                with colonne_squadre[posizione % len(colonne_squadre)]:
                    logo_b64 = st.session_state['loghi_squadre'].get(squadra['nome'])
                    if logo_b64:
                        st.image(foto_base64_a_bytes(logo_b64), width=60)
                    st.caption(squadra['nome'])

                    key_mostra_uploader = f"_mostra_uploader_logo_{i}"
                    if logo_b64 and not st.session_state.get(key_mostra_uploader):
                        if st.button("✏️ Change logo", key=f"change_logo_{i}"):
                            st.session_state[key_mostra_uploader] = True
                            st.rerun()
                    else:
                        nuovo_logo_file = st.file_uploader("Logo", type=['jpg', 'jpeg', 'png'], key=f"logo_compatto_{i}",
                                                            label_visibility="collapsed")
                        if nuovo_logo_file is not None:
                            marcatore_logo = f"{nuovo_logo_file.name}-{nuovo_logo_file.size}"
                            if st.session_state.get(f"_processato_logo_compatto_{i}") != marcatore_logo:
                                st.session_state['loghi_squadre'][squadra['nome']] = elabora_foto_giocatore(nuovo_logo_file)
                                salva_loghi_squadra_su_disco(st.session_state['loghi_squadre'])
                                st.session_state[f"_processato_logo_compatto_{i}"] = marcatore_logo
                                st.session_state[key_mostra_uploader] = False
                                st.rerun()
                    if st.button("🗑️", key=f"del_squadra_training_{i}", help=f"Remove {squadra['nome']}"):
                        st.session_state['squadre_allenate'].pop(i)
                        salva_squadre_allenate_su_disco(st.session_state['squadre_allenate'])
                        st.rerun()
        else:
            st.caption("No teams added yet.")

        st.markdown("---")

        # ============================================================
        # LIBRERIA SESSIONI: upload in blocco
        # ============================================================
        st.subheader("📥 Session library")
        st.caption("Export your OneNote pages as PDF (File → Export → PDF), then drop as many as "
                   "you like here at once — e.g. all the sessions you write during the off-season. "
                   "Each becomes a reusable session: attach links and notes once, then reuse it for "
                   "as many teams and dates as you want, without retyping anything.")

        fc_sessioni = st.file_uploader("Drag and drop session PDF(s) here", type=['pdf'],
                                        accept_multiple_files=True, key="upload_sessioni_bulk")
        if fc_sessioni:
            if st.button("➕ Create Session(s) from these PDFs"):
                nomi_esistenti = {s['nome_sessione'] for s in st.session_state['sessioni_allenamento']}
                aggiunte_sessioni = 0
                for f in fc_sessioni:
                    nome_base = os.path.splitext(f.name)[0]
                    nome_finale = nome_base
                    contatore = 2
                    while nome_finale in nomi_esistenti:
                        nome_finale = f"{nome_base} ({contatore})"
                        contatore += 1
                    st.session_state['sessioni_allenamento'].append({
                        'id': uuid.uuid4().hex,
                        'nome_sessione': nome_finale,
                        'pdf_bytes': f.read(),
                        'link_list': [],
                        'note_generali': '',
                        'assegnazioni': [],
                    })
                    nomi_esistenti.add(nome_finale)
                    aggiunte_sessioni += 1
                salva_sessioni_allenamento_su_disco(st.session_state['sessioni_allenamento'])
                st.success(f"{aggiunte_sessioni} session(s) created.")
                st.rerun()

        if not _PYPDF_DISPONIBILE:
            st.warning("⚠️ The `pypdf` package isn't available — sessions will still work, but the "
                       "exported PDF will only include the cover page, not the original OneNote pages. "
                       "Add `pypdf` to requirements.txt to enable full merging.")

        st.markdown("---")
        st.subheader("📚 Your sessions")
        if not st.session_state['sessioni_allenamento']:
            st.info("No sessions yet — upload some PDFs above to get started.")
        else:
            nomi_squadre_disponibili = sorted(s['nome'] for s in st.session_state['squadre_allenate'])
            for idx_sessione, sessione in enumerate(st.session_state['sessioni_allenamento']):
                chiave_sess = sessione['id']
                with st.expander(f"📄 {sessione['nome_sessione']}"):
                    nuovo_nome_sessione = st.text_input("Session name", value=sessione['nome_sessione'], key=f"nome_sess_{chiave_sess}")
                    if nuovo_nome_sessione.strip() and nuovo_nome_sessione.strip() != sessione['nome_sessione']:
                        st.session_state['sessioni_allenamento'][idx_sessione]['nome_sessione'] = nuovo_nome_sessione.strip()
                        salva_sessioni_allenamento_su_disco(st.session_state['sessioni_allenamento'])
                        st.rerun()

                    col_pdf1, col_pdf2 = st.columns(2)
                    with col_pdf1:
                        if sessione.get('pdf_bytes'):
                            st.download_button("⬇️ View original PDF", data=sessione['pdf_bytes'],
                                                file_name=f"{sessione['nome_sessione']}.pdf", mime="application/pdf",
                                                key=f"dl_orig_{chiave_sess}")
                        else:
                            st.caption("No PDF attached.")
                    with col_pdf2:
                        nuovo_pdf = st.file_uploader("Replace PDF", type=['pdf'], key=f"replace_pdf_{chiave_sess}")
                        if nuovo_pdf is not None:
                            st.session_state['sessioni_allenamento'][idx_sessione]['pdf_bytes'] = nuovo_pdf.read()
                            salva_sessioni_allenamento_su_disco(st.session_state['sessioni_allenamento'])
                            st.success("PDF replaced.")
                            st.rerun()

                    st.markdown("**Exercise video links**")
                    for i_link, link in enumerate(sessione['link_list']):
                        col_l1, col_l2, col_l3 = st.columns([2, 4, 1])
                        col_l1.caption(link['nome'])
                        col_l2.caption(link['url'])
                        if col_l3.button("🗑️", key=f"del_link_{chiave_sess}_{i_link}"):
                            st.session_state['sessioni_allenamento'][idx_sessione]['link_list'].pop(i_link)
                            salva_sessioni_allenamento_su_disco(st.session_state['sessioni_allenamento'])
                            st.rerun()
                    col_nl1, col_nl2, col_nl3 = st.columns([2, 4, 1])
                    nome_link_nuovo = col_nl1.text_input("Label", key=f"nuovo_link_nome_{chiave_sess}", label_visibility="collapsed", placeholder="Exercise 1")
                    url_link_nuovo = col_nl2.text_input("URL", key=f"nuovo_link_url_{chiave_sess}", label_visibility="collapsed", placeholder="https://...")
                    if col_nl3.button("➕", key=f"add_link_{chiave_sess}"):
                        if nome_link_nuovo.strip() and url_link_nuovo.strip():
                            st.session_state['sessioni_allenamento'][idx_sessione]['link_list'].append(
                                {'nome': nome_link_nuovo.strip(), 'url': url_link_nuovo.strip()})
                            salva_sessioni_allenamento_su_disco(st.session_state['sessioni_allenamento'])
                            st.rerun()

                    nota_generale_nuova = st.text_area("Session notes (max 1000 characters)", value=sessione['note_generali'],
                                                        max_chars=1000, key=f"nota_gen_{chiave_sess}")
                    if nota_generale_nuova != sessione['note_generali']:
                        st.session_state['sessioni_allenamento'][idx_sessione]['note_generali'] = nota_generale_nuova
                        salva_sessioni_allenamento_su_disco(st.session_state['sessioni_allenamento'])

                    st.markdown("**Assign to a team & date (optional, repeatable)**")
                    for i_ass, assegnazione in enumerate(sessione['assegnazioni']):
                        col_a1, col_a2, col_a3 = st.columns([3, 1, 1])
                        etichetta_ass = f"{assegnazione.get('squadra') or '(no team)'} — {assegnazione.get('data') or '(no date)'}"
                        col_a1.caption(etichetta_ass)
                        if col_a2.button("📄 Export", key=f"export_ass_{chiave_sess}_{i_ass}"):
                            pdf_finale = genera_pdf_sessione_allenamento(sessione, assegnazione, st.session_state['squadre_allenate'])
                            st.download_button("⬇️ Download", data=pdf_finale,
                                                file_name=f"{sessione['nome_sessione']}_{assegnazione.get('squadra') or 'session'}.pdf",
                                                mime="application/pdf", key=f"dl_ass_{chiave_sess}_{i_ass}")
                        if col_a3.button("🗑️", key=f"del_ass_{chiave_sess}_{i_ass}"):
                            st.session_state['sessioni_allenamento'][idx_sessione]['assegnazioni'].pop(i_ass)
                            salva_sessioni_allenamento_su_disco(st.session_state['sessioni_allenamento'])
                            st.rerun()

                    st.markdown("**Add a new assignment**")
                    squadra_ass = st.selectbox("Team (optional)", ["(none)"] + nomi_squadre_disponibili, key=f"squadra_ass_{chiave_sess}")
                    specifica_data = st.checkbox("Specify a date", key=f"specifica_data_{chiave_sess}")
                    data_ass = st.date_input("Date", value=datetime.now(), key=f"data_ass_{chiave_sess}") if specifica_data else None
                    nota_ass = st.text_area("Notes for this team/date (max 1000 characters)", max_chars=1000, key=f"nota_ass_{chiave_sess}")
                    if st.button("➕ Add assignment", key=f"add_ass_btn_{chiave_sess}"):
                        st.session_state['sessioni_allenamento'][idx_sessione]['assegnazioni'].append({
                            'squadra': None if squadra_ass == "(none)" else squadra_ass,
                            'data': str(data_ass) if data_ass else None,
                            'nota': nota_ass,
                        })
                        salva_sessioni_allenamento_su_disco(st.session_state['sessioni_allenamento'])
                        for _chiave_da_svuotare in (f"squadra_ass_{chiave_sess}", f"specifica_data_{chiave_sess}",
                                                     f"data_ass_{chiave_sess}", f"nota_ass_{chiave_sess}"):
                            st.session_state.pop(_chiave_da_svuotare, None)
                        st.rerun()

                    st.markdown("---")
                    if st.button("📄 Export session (no team/date)", key=f"export_plain_{chiave_sess}"):
                        pdf_semplice = genera_pdf_sessione_allenamento(sessione, None, st.session_state['squadre_allenate'])
                        st.download_button("⬇️ Download", data=pdf_semplice,
                                            file_name=f"{sessione['nome_sessione']}.pdf", mime="application/pdf",
                                            key=f"dl_plain_{chiave_sess}")

                    conferma_del_sessione = st.checkbox("I confirm I want to delete this session (irreversible)", key=f"conferma_del_sess_{chiave_sess}")
                    if st.button("🗑️ Delete this session", key=f"del_sess_{chiave_sess}", disabled=not conferma_del_sessione):
                        st.session_state['sessioni_allenamento'].pop(idx_sessione)
                        salva_sessioni_allenamento_su_disco(st.session_state['sessioni_allenamento'])
                        st.success(f"Session '{sessione['nome_sessione']}' deleted.")
                        st.rerun()
