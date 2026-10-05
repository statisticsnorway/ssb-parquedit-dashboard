# DESIGN.md – SSB Design Guidelines for Marimo Studio & Grid Views

> **Kontekst for AI:**  
> Du koder for interne analyseverktøy og dashboards i **Marimo** for Statistisk sentralbyrå (SSB).  
> Appene settes sammen i **Marimo Studio (Grid / View Editor)**.  
> 
> **Kjernearkitektur:**  
> 1. **Notebook-celler (Python):** Håndterer data, forretningslogikk og produserer rene UI-elementer, figurer, tabeller og nøkkeltall.  
> 2. **Marimo Studio (View):** Håndterer layout (rader, kolonner, grids) og overordnet struktur.  
> 3. **Tekst og dokumentasjon:** Titler, forklaringstekster og kilder legges i egne uavhengige celler/Markdown-blokker, slik at de kan flyttes og posisjoneres fritt i view-editoren.

---

## 1. Prinsipper for cellestruktur i Marimo

- **En oppgave per celle:** Unngå celler som returnerer tittel, forklaring, input og graf i en stor `mo.vstack()`. Del det opp:
  - Celle A: Filter/kontroller (`mo.ui.*`)
  - Celle B: Figur eller tabell
  - Celle C: Tittel/forklaring (ren Markdown)
- **Komponenter må være grid-vennlige:** Alle visuelle elementer (kort, tabeller, figurer) bør tilpasse seg containerbredden (`width: 100%`) slik at de ser bra ut uansett hvilken kolonnebredde de får i Studio-viewet.
- **Ikke hardkod app-layout i Python:** Bruk `mo.hstack` eller `mo.vstack` kun for tett koblede mikro-elementer (f.eks. et inputfelt ved siden av sin tilhørende knapp), aldri for hele dashboardets layout.

---

## 2. Visuell identitet og fargepalett (SSB)

Bruk disse fargene direkte i CSS, HTML og diagrammer:

| Fargenavn | Hex-kode | Bruksområde |
| :--- | :--- | :--- |
| **SSB Mørk 5** | `#274247` | Hovedfarge, overskrifter, mørk tekst, standardrammer |
| **SSB Grønn 4** | `#00824D` | Primæraksent, knapper, positive trender, primærserie i diagrammer |
| **SSB Mørk 1** | `#F0F8F9` | Bakgrunnsfarge for kort, dashboards og alternerende tabellrader |
| **SSB Mørk 2** | `#C3DCDC` | Tynne rammer, skillelinjer |
| **SSB Lilla 3** | `#7E5EE8` | Sekundæraksent (f.eks. avvik, prognoser eller serie 2 i diagrammer) |
| **SSB Hvit** | `#FFFFFF` | Ren bakgrunn for kort og visningsflater |

---

## 3. Typografi og formateringsregler

- **Titler & overskrifter:** `Roboto Condensed`, `Roboto` eller kraftig sans-serif i `#274247`.
- **Brødtekst:** `Open Sans` eller ren system-sans-serif.
- **Norsk tallkonvensjon:**
  - Bruk mellomrom som tusenskilletegn (f.eks. `1 500 000`, aldri komma).
  - Bruk komma som desimalskilletegn (f.eks. `4,2 %`).
  - Høyrestill alltid numeriske verdier i tabeller.

---

## 4. Basis-CSS for Marimo Studio

Inkluder denne styling-cellen i starten av notatboken for å gi komponentene riktig SSB-stil:

```python
import marimo as mo

ssb_theme = mo.Html("""
<style>
  :root {
    --ssb-dark: #274247;
    --ssb-green: #00824D;
    --ssb-bg: #F0F8F9;
    --ssb-border: #C3DCDC;
    --ssb-white: #FFFFFF;
    --ssb-purple: #7E5EE8;
    --font-heading: 'Roboto Condensed', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-body: 'Open Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  }

  /* SSB Kort for Studio-grid */
  .ssb-card {
    background: var(--ssb-white);
    border: 1px solid var(--ssb-border);
    border-radius: 6px;
    padding: 1rem 1.25rem;
    box-sizing: border-box;
    width: 100%;
    height: 100%;
  }

  /* Nøkkeltall / KPI */
  .ssb-kpi-value {
    font-family: var(--font-heading);
    font-size: 2.25rem;
    font-weight: 700;
    color: var(--ssb-dark);
    line-height: 1.1;
  }

  .ssb-kpi-label {
    font-family: var(--font-body);
    font-size: 0.875rem;
    color: #556B6F;
    margin-top: 0.35rem;
  }

  /* Status- og infoboks */
  .ssb-alert {
    padding: 0.75rem 1rem;
    border-radius: 0 4px 4px 0;
    font-family: var(--font-body);
    font-size: 0.9rem;
    color: var(--ssb-dark);
    box-sizing: border-box;
    width: 100%;
  }
  .ssb-alert-info {
    border-left: 4px solid var(--ssb-green);
    background-color: #ECFEED;
  }
  .ssb-alert-neutral {
    border-left: 4px solid var(--ssb-dark);
    background-color: var(--ssb-bg);
  }
  .ssb-alert-warning {
    border-left: 4px solid #D97706;
    background-color: #FFFBEB;
  }
</style>
""")
```

---

## 5. Komponentmaler for celler

### 5.1 Nøkkeltall (KPI-kort)
Generer som frittstående celle-outputs som kan slippes inn i grid-ruter:

```python
def ssb_kpi(label: str, value: str, subtitle: str = "") -> mo.Html:
    sub_html = f'<div style="font-size: 0.75rem; color: #76888B; margin-top: 4px;">{subtitle}</div>' if subtitle else ""
    return mo.Html(f"""
    <div class="ssb-card">
        <div class="ssb-kpi-value">{value}</div>
        <div class="ssb-kpi-label">{label}</div>
        {sub_html}
    </div>
    """)
```

### 5.2 Kontrollpanel / Filtre
Koble filtre logisk sammen, men la dem utgjøre en egen celle:

```python
# Eksempel på en kontroll-celle:
aar_velger = mo.ui.dropdown(options=["2024", "2025", "2026"], value="2026", label="Årgang:")
fylke_velger = mo.ui.dropdown(options=["Hele landet", "Oslo", "Vestland"], value="Hele landet", label="Område:")

# Returneres samlet for plassering i toppen eller sidemenyen i view'et:
mo.hstack([aar_velger, fylke_velger], gap=2)
```

### 5.3 Figurer og diagrammer
Bruk SSB-farger på dataserier og sørg for at diagrammer er responsive (`autosize` eller `width="container"`):

```python
SSB_PALETTE = [
    "#00824D",  # 1. serie (SSB Grønn)
    "#274247",  # 2. serie (SSB Mørk 5)
    "#7E5EE8",  # 3. serie (SSB Lilla 3)
    "#556B6F",  # 4. serie (Dempet mørk)
    "#B6E8B8",  # 5. serie (Lys grønn)
]

# Eksempel for Altair:
# chart = alt.Chart(df).mark_line().encode(
#     color=alt.Color('serie:N').scale(range=SSB_PALETTE)
# ).properties(width='container')
```

### 5.4 Tekst- og dokumentasjonsceller (for visning i View)
Tekst skal defineres i egne Markdown-celler, ikke pakkes inn i Python-beregningsceller:

```python
# Egen celle for ingress/forklaring som kan plasseres over en graf i Marimo Studio:
mo.md("""
### Sysselsatte etter næring
Diagrammet viser utviklingen over tid basert på kvartalsvise registerdata.
""")
```

---

## 6. Sjekkliste for AI

Før du genererer kode for en Marimo-løsning:
- [ ] Produserer cellen en modulær output som egner seg for plassering i Marimo Studio Grid View?
- [ ] Er overordnet tekst og overskrifter skilt ut i egne Markdown-celler fremfor å være låst inne i data-koden?
- [ ] Er diagrammer og kort satt til `width: 100%` / `container` så de tilpasser seg grid-kolonnene?
- [ ] Følger fargene SSB-paletten (`#274247`, `#00824D`, `#F0F8F9`, `#C3DCDC`)?
- [ ] Er tallformatene norske (mellomrom for tusen, komma for desimal)?
