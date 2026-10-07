# /// script
# dependencies = [
#     "faker>=37.0.0,<38.0.0",
#     "marimo>=0.25.0",
#     "polars>=1.38.1,<2.0.0",
#     "ssb-parquedit==0.1.0",
#     "marimo-studio==0.2.3"
# ]
# requires-python = ">=3.12,<3.15"
#
# [tool.marimo-studio]
# view_root = "views"
# runtime = "server"
# default = "parqueditor"
#
# [tool.marimo-studio.cells]
# cell-3 = {ref = "cell:v1:c235fd4e1fa29b1c5f6db78eb8c4cc42c411e837a797133ca23aded613536c16:c235fd4e1fa29b1c5f6db78eb8c4cc42c411e837a797133ca23aded613536c16:0"}
# cell-4 = {ref = "cell:v1:2fcf5cdad0a8acd7d89a19e43625ffecca6e262f4a68978156b9bcc89ed0eca4:71617b53de9d678661721042769b64dc8dd66c83479a31c93f07487aaea28008:0"}
# cell-5 = {ref = "cell:v1:41d40a75439a4362553173de980c511d10a47898a0ad5a0b57b763a126fe27ab:41d40a75439a4362553173de980c511d10a47898a0ad5a0b57b763a126fe27ab:0"}
# cell-6 = {ref = "cell:v1:63241cceeddf9e749da027930394574e7033d3f6fc0ea78a0d022288caa6142c:63241cceeddf9e749da027930394574e7033d3f6fc0ea78a0d022288caa6142c:0"}
# cell-7 = {ref = "cell:v1:285ff37a41ecc0df25ce346e7d44e51b615ae8da8e00c3442e76fba454dc1d32:285ff37a41ecc0df25ce346e7d44e51b615ae8da8e00c3442e76fba454dc1d32:0"}
# cell-8 = {ref = "cell:v1:beeae7895375de99a6b2acd9d160278385f6c80713a4bbf8bc0c2ba2b35a5a9c:beeae7895375de99a6b2acd9d160278385f6c80713a4bbf8bc0c2ba2b35a5a9c:0"}
# cell-9 = {ref = "cell:v1:4bef057d12093903213f106fd885736e0db41b04947ab3a0c73f15a53c47785c:4bef057d12093903213f106fd885736e0db41b04947ab3a0c73f15a53c47785c:0"}
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(width="full", app_title="Parqueditor")


@app.cell
def _():
    from ssb_parquedit import ParquEdit
    from faker import Faker
    import polars as pl

    MOCK_TABLES = ("local_mock_table_1", "local_mock_table_2")
    MOCK_ROW_COUNT = 10_000

    def make_mock_data(seed: int) -> pl.DataFrame:
        fake = Faker("no_NO")
        fake.seed_instance(seed)
        return pl.DataFrame(
            {
                "record_id": [fake.uuid4() for _ in range(MOCK_ROW_COUNT)],
                "organization_number": [
                    fake.numerify("#########") for _ in range(MOCK_ROW_COUNT)
                ],
                "organization_name": [fake.company() for _ in range(MOCK_ROW_COUNT)],
                "area_code": [fake.postcode() for _ in range(MOCK_ROW_COUNT)],
                "sector_code": [fake.numerify("##") for _ in range(MOCK_ROW_COUNT)],
                "sector": [fake.bs() for _ in range(MOCK_ROW_COUNT)],
                "period": [fake.date(pattern="%Y-%m") for _ in range(MOCK_ROW_COUNT)],
                "number_of_employees": [
                    fake.random_int(min=1, max=5000) for _ in range(MOCK_ROW_COUNT)
                ],
                "income": [
                    float(fake.pyfloat(left_digits=7, right_digits=2, positive=True))
                    for _ in range(MOCK_ROW_COUNT)
                ],
                "status": [fake.word() for _ in range(MOCK_ROW_COUNT)],
                "date": [
                    fake.date_between(start_date="-2y", end_date="today").isoformat()
                    for _ in range(MOCK_ROW_COUNT)
                ],
            }
        )

    class LocalParquEdit(ParquEdit):
        @classmethod
        def with_mock_tables(cls):
            con = cls.local()
            for index, table_name in enumerate(MOCK_TABLES):
                if not con.exists(table_name):
                    con.create_table(
                        table_name,
                        source=make_mock_data(seed=index),
                        product_name="local-mock-statistic",
                        user_defined_id=["record_id"],
                        fill=True,
                    )
            return con

    return LocalParquEdit, ParquEdit, pl


@app.cell
def _(ParquEdit):
    import html
    import numbers
    import marimo as mo
    import os

    reasons = [
        "OTHER_SOURCE",
        "REVIEW",
        "OWNER",
        "MARGINAL_UNIT",
        "DUPLICATE",
        "OTHER",
    ]
    get_refresh, set_refresh = mo.state(0)

    is_dapla_prod = os.environ.get("DAPLA_ENVIRONMENT", "").lower() == "prod"
    if not is_dapla_prod:
        os.environ["DAPLA_USER"] = "local-mock-user@ssb.no"
    DAPLA_TEAM = os.environ["DAPLA_TEAM"] if is_dapla_prod else "local-mock-team"
    con = ParquEdit() if is_dapla_prod else LocalParquEdit().with_mock_tables()
    return DAPLA_TEAM, con, get_refresh, html, mo, numbers, reasons, set_refresh


@app.cell
def status_banner(con, DAPLA_TEAM, mo):
    try:
        tables = con.list_tables()
        connection_error = None
    except Exception as error:
        tables = []
        connection_error = error

    if connection_error:
        status = mo.md(
            f"## Kunne ikke koble til Parquedit\n\n"
            f"Team: *{DAPLA_TEAM}*\n\n"
            "Sjekk:\n\n"
            "- At du har startet tjenesten med riktig team\n"
            "- At Parquedit er skrudd på for teamet i Dapla Ctrl"
        )
    elif not tables:
        status = mo.md(
            f"## Fant ingen Parquedit-tabeller\n\n"
            f"Team: *{DAPLA_TEAM}*\n\n"
            "Sjekk at du har startet tjenesten med riktig team"
        )
    else:
        status = None
    status
    return connection_error, tables


@app.cell
def intro_panel(connection_error, mo, tables):
    mo.stop(connection_error is not None or not tables, mo.md(""))
    mo.md(
        """
    # Brukerveiledning

    Velg en Parquedit-tabell, finn riktig rad i tabellen, og lagre manuelle endringer
    med årsaken til endringen.

    ### Slik bruker du siden
    1. Velg tabellen du vil jobbe med.
    2. Søk, filtrer og velg raden som skal redigeres.
    3. Bruk skjemaet under tabellen til å oppdatere en eller flere verdier.
    4. Oppgi årsaken til endringen, og legg eventuelt til en kommentar.
    """
    )
    return


@app.cell
def table_selector_panel(connection_error, mo, tables):

    mo.stop(connection_error is not None or not tables, mo.md(""))
    table_selector = mo.ui.dropdown(
        options=tables,
        value=tables[0],
        label="Velg Parquedit-tabell",
        full_width=True,
    )
    mo.vstack(
        [
            mo.md("### 1. Velg tabell"),
            mo.md(
                "Velg tabellen du vil jobbe med før du søker etter raden som skal redigeres."
            ),
            table_selector,
        ]
    )
    return (table_selector,)


@app.cell(hide_code=True)
def table_metadata_panel(con, DAPLA_TEAM, get_refresh, html, mo, table_selector):

    _ = get_refresh()
    product_history = con.get_edits(table_name=table_selector.value)
    product_name_value = None
    user_defined_id_text = None
    row_change_count = 0
    value_change_count = 0
    if product_history is not None and not product_history.empty:
        row_change_count = len(product_history)
        if "new_values" in product_history.columns:
            value_change_count = sum(
                len(change_dict)
                for change_dict in product_history["new_values"].dropna()
                if isinstance(change_dict, dict)
            )
        if "product_name" in product_history.columns:
            non_null_product_names = product_history["product_name"].dropna()
            if not non_null_product_names.empty:
                product_name_value = str(non_null_product_names.iloc[0])
        if "user_defined_id" in product_history.columns:
            non_null_user_defined_ids = product_history["user_defined_id"].dropna()
            if not non_null_user_defined_ids.empty:
                first_user_defined_id = non_null_user_defined_ids.iloc[0]
                if isinstance(first_user_defined_id, dict):
                    user_defined_id_text = ", ".join(first_user_defined_id.keys())
                else:
                    user_defined_id_text = str(first_user_defined_id)

    product_text = product_name_value or "Ikke tilgjengelig"
    unique_id_text = user_defined_id_text or "Ikke tilgjengelig"
    metadata_items = [
        (
            "Team",
            DAPLA_TEAM,
            "Teamet som eier denne Parquedit-tabellen.",
        ),
        (
            "Dataprodukt",
            product_text,
            "Navnet på dataproduktet som denne Parquedit-tabellen tilhører.",
        ),
        (
            "Unik rad-id",
            unique_id_text,
            "Kolonnene som sammen identifiserer en rad unikt i tabellen.",
        ),
        (
            "Antall radendringer",
            str(row_change_count),
            "Antall registrerte radendringer i endringshistorikken for valgt tabell.",
        ),
        (
            "Antall verdiendringer",
            str(value_change_count),
            "Summen av felter som er endret i endringshistorikken for valgt tabell.",
        ),
    ]

    def render_metadata_row(label: str, value: str, help_text: str) -> str:
        return f"""
        <div style='display:grid; grid-template-columns:minmax(12rem, 15rem) minmax(0, 1fr); gap:0.75rem; align-items:start; padding:0.35rem 0;'>
          <div style='display:inline-flex; align-items:center; gap:0.2rem; color:#556b6f; font-weight:600;'>
            <span>{html.escape(label)}</span>
            <details data-auto-close style='position:relative; display:inline-block;'>
              <summary
                style='display:inline-flex; align-items:center; justify-content:center; width:1rem; height:1rem; border:1px solid #c3dcdc; border-radius:999px; background:#f0f8f9; color:#274247; font-size:0.72rem; font-weight:700; cursor:pointer; list-style:none; user-select:none;'
                aria-label='{html.escape(help_text, quote=True)}'
              >?</summary>
              <div style='position:absolute; top:1.35rem; left:0; z-index:20; min-width:16rem; max-width:24rem; padding:0.65rem 0.75rem; border:1px solid #c3dcdc; border-radius:0.5rem; background:#ffffff; color:#274247; box-shadow:0 8px 24px rgb(39 66 71 / 0.12); line-height:1.35; font-weight:400;'>
                {html.escape(help_text)}
              </div>
            </details>
            <span>:</span>
          </div>
          <div style='color:#274247;'>{html.escape(value)}</div>
        </div>
        """

    metadata_rows_html = "".join(
        render_metadata_row(label, value, help_text)
        for label, value, help_text in metadata_items
    )
    metadata_panel = mo.Html(
        f"""
        <div style='display:grid; gap:0.1rem;'>
          {metadata_rows_html}
        </div>
        """
    )
    metadata_panel
    return


@app.cell
def column_selector_panel(con, get_refresh, pl, table_selector):

    _ = get_refresh()
    data: pl.DataFrame = con.view(
        table_name=table_selector.value,
        output_format="polars",
    )
    return (data,)


@app.cell(hide_code=True)
def table_panel(data: "pl.DataFrame", mo):

    table_view = mo.ui.table(
        data=data,
        selection="single",
        pagination=True,
        page_size=10,
        label="### 2. Finn og velg raden som skal redigeres",
        freeze_columns_left=["rowid"],
        show_download=False,
    )
    mo.vstack(
        [
            mo.md(
                "Bruk søk og filtrering i tabellen for å finne riktig rad. "
                "Du må velge en rad før skjemaet under kan brukes."
            ),
            table_view,
        ]
    )
    return (table_view,)


@app.cell
def editor_panel(
    data: "pl.DataFrame",
    html,
    mo,
    numbers,
    pl,
    reasons,
    table_view,
):

    selected: pl.DataFrame = table_view.value
    selected_row = selected.row(0, named=True) if selected.height else None
    field_columns = [col for col in data.columns if col != "rowid"]

    field_elements = {}
    row_blocks = []
    for col in field_columns:
        value = None if selected_row is None else selected_row[col]
        series = data.get_column(col)
        non_null = series.drop_nulls()
        sample_value = non_null[0] if len(non_null) else None

        if isinstance(value, numbers.Integral) and not isinstance(value, bool):
            input_element = mo.ui.number(value=int(value), label="")
        elif isinstance(value, numbers.Real) and not isinstance(value, bool):
            input_element = mo.ui.number(value=float(value), label="")
        elif isinstance(sample_value, numbers.Integral) and not isinstance(
            sample_value, bool
        ):
            input_element = mo.ui.number(value=None, label="")
        elif isinstance(sample_value, numbers.Real) and not isinstance(
            sample_value, bool
        ):
            input_element = mo.ui.number(value=None, label="")
        else:
            input_element = mo.ui.text(
                value="" if value is None else str(value),
                label="",
                full_width=True,
            )

        field_elements[col] = input_element
        current_display = (
            "-" if value is None else f"<code>{html.escape(str(value))}</code>"
        )
        row_blocks.append(
            f"""
    <div style="display:grid; grid-template-columns: minmax(12rem, 1.1fr) minmax(12rem, 1.1fr) minmax(16rem, 1.6fr); gap:1rem; align-items:center; padding:0.6rem 0; border-bottom:1px solid var(--mo-border-color);">
      <div><strong>{html.escape(col)}</strong></div>
      <div>{current_display}</div>
      <div>{{{col}}}</div>
    </div>
    """
        )

    field_elements["_reason"] = mo.ui.dropdown(
        options=reasons,
        value="REVIEW",
        label="",
        full_width=True,
    )
    field_elements["_comment"] = mo.ui.text_area(label="", full_width=True)

    if selected_row is None:
        selected_header = """
    ### 3. Rediger valgt rad

    Ingen rad valgt ennå.
    """
        selected_message = "Velg en rad i tabellen over for å forhåndsutfylle skjemaet og aktivere lagring."
    else:
        selected_header = f"""
    ### 3. Rediger valgt rad

    Du redigerer `rowid={selected_row["rowid"]}`.
    """
        selected_message = (
            "Sammenlign eksisterende og nye verdier før du lagrer endringen."
        )

    editor_template = f"""
    {selected_header}

    {selected_message}

    <div style="display:grid; grid-template-columns: minmax(12rem, 1.1fr) minmax(12rem, 1.1fr) minmax(16rem, 1.6fr); gap:1rem; align-items:end; padding-bottom:0.6rem; border-bottom:2px solid var(--mo-border-color); margin-top:1rem;">
      <div><strong>Felt</strong></div>
      <div><strong>Nåværende verdi</strong></div>
      <div><strong>Ny verdi</strong></div>
    </div>
    {"".join(row_blocks)}

    <div style="border:1px solid var(--mo-border-color); border-radius:0.75rem; padding:1rem; margin-top:1rem;">
      <div><strong>Endringsinformasjon</strong></div>
      <div style="display:grid; grid-template-columns: minmax(10rem, 1fr) minmax(16rem, 2fr); gap:1rem; align-items:center; margin-top:0.75rem;">
        <div><strong>Årsak</strong></div>
        <div>{{_reason}}</div>
      </div>
      <div style="margin-top:0.75rem;">
        <div><strong>Kommentar</strong></div>
        <div style="margin-top:0.5rem;">{{_comment}}</div>
      </div>
    </div>
    """

    edit_form = (
        mo.md(editor_template)
        .batch(**field_elements)
        .form(
            submit_button_label="Lagre endringer i Parquedit",
            submit_button_disabled=selected_row is None,
            submit_button_tooltip=(
                "Velg en rad i tabellen for å kunne lagre endringer."
                if selected_row is None
                else None
            ),
        )
    )

    edit_form
    return edit_form, selected_row


@app.cell
def _(
    con,
    data: "pl.DataFrame",
    edit_form,
    get_refresh,
    mo,
    selected_row,
    set_refresh,
    table_selector,
):

    if (
        selected_row is not None
        and edit_form is not None
        and edit_form.value is not None
    ):
        form_data = edit_form.value
        changes = {
            col: form_data[col]
            for col in data.columns
            if col != "rowid" and str(form_data[col]) != str(selected_row[col])
        }
        if changes:
            con.edit(
                table_name=table_selector.value,
                rowid=selected_row["rowid"],
                changes=changes,
                change_event_reason=form_data["_reason"],
                change_comment=form_data["_comment"],
            )
            set_refresh(get_refresh() + 1)
            mo.status.toast("Endringen ble lagret i Parquedit.")
    return


@app.cell(hide_code=True)
def history_panel(con, get_refresh, mo, table_selector):

    import json

    _ = get_refresh()
    history = con.get_edits(table_name=table_selector.value)
    mo.stop(history is None or history.empty, mo.md(""))

    history = history.sort_values("snapshot_time", ascending=False).reset_index(
        drop=True
    )
    row_index_lookup = {str(index): index for index in history.index}
    preferred_columns = [
        "snapshot_time",
        "change_event_reason",
        "changed_by",
        "change_comment",
        "rowid",
        "old_values",
        "new_values",
    ]
    history_columns = preferred_columns + [
        column for column in history.columns if column not in preferred_columns
    ]
    history = history[history_columns]

    def format_hover_value(column_name, value):
        if value is None:
            return f"{column_name}: -"
        if isinstance(value, dict):
            formatted = json.dumps(value, ensure_ascii=False, indent=2)
            separator = """
    """
            return column_name + ":" + separator + formatted
        return f"{column_name}: {value}"

    def style_history_cell(row_id, column_name, value):
        row_index = row_index_lookup.get(str(row_id), 0)
        styles = {
            "backgroundColor": "#f0f8f9" if row_index % 2 else "#ffffff",
        }
        if column_name == "snapshot_time":
            styles["fontWeight"] = "600"
        if column_name in {"old_values", "new_values"}:
            styles["fontFamily"] = "ui-monospace, SFMono-Regular, Menlo, monospace"
            styles["fontSize"] = "0.85rem"
        if column_name == "change_comment" and value:
            styles["fontStyle"] = "italic"
        return styles

    history_view = mo.ui.table(
        history,
        selection=None,
        label="### 4. Endringshistorikk",
        show_download=False,
        show_data_types=False,
        visible_columns=preferred_columns,
        format_mapping={
            "snapshot_time": lambda value: value.strftime("%d.%m.%Y %H:%M")
        },
        wrapped_columns=["old_values", "new_values", "change_comment"],
        column_widths={
            "rowid": 90,
            "snapshot_time": 150,
            "old_values": 300,
            "new_values": 300,
            "changed_by": 190,
            "change_event_reason": 160,
            "change_comment": 260,
        },
        max_height=420,
        header_tooltip={
            "rowid": "Den unike identifikatoren til raden som ble endret.",
            "snapshot_time": "Tidspunktet da endringen ble registrert.",
            "old_values": "Verdiene før endringen ble lagret.",
            "new_values": "Verdiene etter endringen ble lagret.",
            "changed_by": "Brukeren som utførte endringen.",
            "change_event_reason": "Oppgitt årsak til endringen.",
            "change_comment": "Valgfri kommentar knyttet til endringen.",
        },
        style_cell=style_history_cell,
        hover_template=lambda row_id, column_name, value: format_hover_value(
            column_name, value
        ),
    )
    mo.vstack(
        [
            mo.md("Se tidligere endringer for valgt tabell nederst i viewen."),
            history_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
