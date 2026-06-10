import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Labometric",
    page_icon="🧬",
    layout="wide"
)

# ── Load data ─────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("ingredients.csv")

df = load_data()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧬 LABOMETRIC")
    st.caption("ANALYSER V0.1")
    st.divider()
    st.markdown("**NAVIGATION**")
    page = st.radio(
        "",
        ["Overview", "Ingredients", "Formulation Builder", "Analysis", "Datasets", "Quick Profiler", "Risk Heatmap", "Reaction Predictor", "Lab Workflow", "Stock Manager", "Solubility Calculator", "Dilution Calculator", "Buffer Calculator"],
        label_visibility="collapsed"
    )
    st.divider()
    st.markdown("**QUICK ACTIONS**")
    if st.button("＋ Add ingredient"):
        st.info("Feature coming soon.")
    st.divider()
    st.caption("STATUS  🟢 ONLINE")
    st.caption("NODE    BIO-01")


# PAGE 1 — OVERVIEW:

if page == "Overview":

    st.markdown("## Labometric")

    if "hazard_filter" not in st.session_state:
        st.session_state.hazard_filter = "ALL"

    col_search, col_all, col_danger, col_warn, col_safe, col_info, col_unk = st.columns([3,1,1,1,1,1,1])
    with col_search:
        search = st.text_input("", placeholder="🔍 Search name, formula, CAS...", label_visibility="collapsed")
    with col_all:
        if st.button("ALL"):     st.session_state.hazard_filter = "ALL"
    with col_danger:
        if st.button("DANGER"):  st.session_state.hazard_filter = "DANGER"
    with col_warn:
        if st.button("WARNING"): st.session_state.hazard_filter = "WARNING"
    with col_safe:
        if st.button("SAFE"):    st.session_state.hazard_filter = "SAFE"
    with col_info:
        if st.button("INFO"):    st.session_state.hazard_filter = "INFO"
    with col_unk:
        if st.button("UNKNOWN"): st.session_state.hazard_filter = "UNKNOWN"

    filtered = df.copy()
    if st.session_state.hazard_filter != "ALL":
        filtered = filtered[filtered["hazard"] == st.session_state.hazard_filter]
    if search:
        filtered = filtered[
            filtered["name"].str.contains(search, case=False, na=False) |
            filtered["formula"].str.contains(search, case=False, na=False) |
            filtered["cas"].astype(str).str.contains(search, case=False, na=False)
        ]

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("TOTAL INGREDIENTS", len(filtered),                              help="Registered in library")
    m2.metric("AVG MOL. WEIGHT",   f"{filtered['mw'].mean():,.0f} g/mol")
    m3.metric("AVG pH",            f"{filtered['ph'].mean():.2f}",             help="Across dataset")
    m4.metric("DANGER RATIO",      f"{(filtered['hazard']=='DANGER').mean()*100:.1f}%", help="High-hazard entries")
    st.divider()

    color_map = {
        "DANGER":  "#e74c3c",
        "WARNING": "#f39c12",
        "SAFE":    "#27ae60",
        "INFO":    "#3498db",
        "UNKNOWN": "#95a5a6"
    }

    c1, c2, c3 = st.columns(3)

    with c1:
        st.caption("DISTRIBUTION")
        st.markdown("**Hazard Classification**")
        haz = filtered["hazard"].value_counts().reset_index()
        haz.columns = ["hazard", "count"]
        fig1 = px.bar(haz, x="hazard", y="count", color="hazard",
                      color_discrete_map=color_map, text="count")
        fig1.update_layout(showlegend=False, height=300, margin=dict(t=10,b=10))
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.caption("ACIDITY PROFILE")
        st.markdown("**pH Distribution**")
        fig2 = px.histogram(filtered, x="ph", nbins=7,
                            color_discrete_sequence=["#2c4a8c"])
        fig2.update_layout(height=300, margin=dict(t=10,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    with c3:
        st.caption("MASS PROFILE")
        st.markdown("**Mol. Weight Distribution**")
        bins   = [0, 100, 250, 500, 1000, float("inf")]
        labels = ["<100", "100-250", "250-500", "500-1k", "1k+"]
        temp = filtered.copy()
        temp["mw_bin"] = pd.cut(temp["mw"], bins=bins, labels=labels)
        mw_counts = temp["mw_bin"].value_counts().sort_index().reset_index()
        mw_counts.columns = ["range", "count"]
        fig3 = px.bar(mw_counts, x="range", y="count",
                      color_discrete_sequence=["#1a2f5e"])
        fig3.update_layout(height=300, margin=dict(t=10,b=10))
        st.plotly_chart(fig3, use_container_width=True)

    st.divider()
    st.caption("LIBRARY")
    st.markdown(f"**Ingredients** — {len(filtered)} rows")

    def color_hazard(val):
        colors = {
            "DANGER":  "background-color:#fde8e8; color:#c0392b;",
            "WARNING": "background-color:#fef9e7; color:#d35400;",
            "SAFE":    "background-color:#eafaf1; color:#1e8449;",
            "INFO":    "background-color:#ebf5fb; color:#1a5276;",
            "UNKNOWN": "background-color:#f2f3f4; color:#717d7e;"
        }
        return colors.get(val, "")

    st.dataframe(
        filtered.style.map(color_hazard, subset=["hazard"]),
        use_container_width=True,
        height=400
    )



# PAGE 2 — INGREDIENT DETAIL:

elif page == "Ingredients":

    st.markdown("## Ingredient Detail")
    st.caption("Select any ingredient to view its full safety profile.")
    st.divider()

    search_detail = st.text_input("Search ingredient", placeholder="Type a name or CAS number...")
    filtered_detail = df.copy()
    if search_detail:
        filtered_detail = filtered_detail[
            filtered_detail["name"].str.contains(search_detail, case=False, na=False) |
            filtered_detail["cas"].astype(str).str.contains(search_detail, case=False, na=False)
        ]

    if filtered_detail.empty:
        st.warning("No ingredients found. Try a different search term.")
    else:
        selected = st.selectbox("Select ingredient", filtered_detail["name"].tolist())

        if selected:
            row = df[df["name"] == selected].iloc[0]

            hazard_colors = {
                "DANGER":  ("🔴", "#fde8e8", "#c0392b"),
                "WARNING": ("🟡", "#fef9e7", "#d35400"),
                "SAFE":    ("🟢", "#eafaf1", "#1e8449"),
                "INFO":    ("🔵", "#ebf5fb", "#1a5276"),
                "UNKNOWN": ("⚪", "#f2f3f4", "#717d7e")
            }
            icon, bg, fg = hazard_colors.get(row["hazard"], ("⚪", "#f2f3f4", "#717d7e"))

            st.divider()
            col_name, col_badge = st.columns([3, 1])
            with col_name:
                st.markdown(f"### {row['name']}")
                st.code(row["formula"])
            with col_badge:
                st.markdown(
                    f"<div style='background:{bg};color:{fg};padding:12px 18px;"
                    f"border-radius:8px;text-align:center;font-weight:bold;"
                    f"font-size:18px;margin-top:10px'>{icon} {row['hazard']}</div>",
                    unsafe_allow_html=True
                )

            st.divider()
            p1, p2, p3, p4, p5 = st.columns(5)
            p1.metric("Mol. Weight", f"{row['mw']:,} g/mol")
            p2.metric("pH",          row["ph"])
            p3.metric("Quantity",    row["qty"])
            p4.metric("Purity",      f"{row['purity']}%")
            p5.metric("CAS Number",  row["cas"])

            st.divider()
            st.markdown("#### Safety Notes")
            safety_notes = {
                "DANGER": [
                    "⚠️ Requires full PPE — gloves, goggles, lab coat mandatory",
                    "⚠️ Store in designated hazardous chemical cabinet",
                    "⚠️ Refer to SDS before handling",
                    "⚠️ Dispose as hazardous waste — do not pour down drain"
                ],
                "WARNING": [
                    "🔶 Use gloves and eye protection when handling",
                    "🔶 Avoid prolonged skin or inhalation exposure",
                    "🔶 Store away from incompatible substances",
                    "🔶 Check SDS for specific precautions"
                ],
                "SAFE": [
                    "✅ Generally safe under normal lab conditions",
                    "✅ Standard PPE recommended as good practice",
                    "✅ Store at room temperature unless noted",
                    "✅ Dispose according to institutional guidelines"
                ],
                "INFO": [
                    "ℹ️ Controlled or monitored substance",
                    "ℹ️ Follow institutional protocols for use",
                    "ℹ️ Document usage in lab notebook",
                    "ℹ️ Check local regulations before ordering"
                ],
                "UNKNOWN": [
                    "❓ Insufficient data available for this substance",
                    "❓ Treat as potentially hazardous until confirmed",
                    "❓ Consult supervisor before use"
                ]
            }
            for note in safety_notes.get(row["hazard"], ["No specific notes available."]):
                st.markdown(note)

            st.divider()
            st.caption(f"Data source: BioSpec internal database · CAS: {row['cas']}")



# PAGE 3 — FORMULATION BUILDER:

elif page == "Formulation Builder":

    st.markdown("## Formulation Builder")
    st.caption("Add ingredients to build a formulation and get an overall safety profile.")
    st.divider()

    if "formulation" not in st.session_state:
        st.session_state.formulation = []

    col_a, col_b, col_c = st.columns([3, 1, 1])
    with col_a:
        ingredient_choice = st.selectbox("Select ingredient", df["name"].tolist(), key="form_select")
    with col_b:
        amount = st.number_input("Amount", min_value=0.1, value=1.0, step=0.1, key="form_amount")
    with col_c:
        unit = st.selectbox("Unit", ["g", "mg", "ml", "µl", "%w/v"], key="form_unit")

    if st.button("➕ Add to formulation"):
        row = df[df["name"] == ingredient_choice].iloc[0]
        st.session_state.formulation.append({
            "name":    ingredient_choice,
            "formula": row["formula"],
            "amount":  amount,
            "unit":    unit,
            "mw":      row["mw"],
            "ph":      row["ph"],
            "purity":  row["purity"],
            "hazard":  row["hazard"],
            "cas":     row["cas"]
        })
        st.success(f"Added {ingredient_choice}")

    if st.session_state.formulation:
        form_df = pd.DataFrame(st.session_state.formulation)

        st.divider()
        st.markdown("### Formulation Summary")
        fm1, fm2, fm3, fm4 = st.columns(4)
        avg_ph       = form_df["ph"].mean()
        avg_mw       = form_df["mw"].mean()
        danger_count = int((form_df["hazard"] == "DANGER").sum())
        fm1.metric("Total Ingredients", len(form_df))
        fm2.metric("Avg pH",            f"{avg_ph:.2f}")
        fm3.metric("Avg Mol. Weight",   f"{avg_mw:,.0f} g/mol")
        fm4.metric("Danger Count",      danger_count,
                   delta="High risk" if danger_count > 2 else "Acceptable",
                   delta_color="inverse")

        st.divider()
        if danger_count == 0:
            st.success("✅ Overall Formulation Risk: LOW — No dangerous ingredients detected")
        elif danger_count <= 2:
            st.warning(f"⚠️ Overall Formulation Risk: MEDIUM — {danger_count} dangerous ingredient(s) present")
        else:
            st.error(f"🔴 Overall Formulation Risk: HIGH — {danger_count} dangerous ingredients detected")

        st.divider()
        st.markdown("### Ingredient List")

        def color_hazard_form(val):
            colors = {
                "DANGER":  "background-color:#fde8e8;color:#c0392b;",
                "WARNING": "background-color:#fef9e7;color:#d35400;",
                "SAFE":    "background-color:#eafaf1;color:#1e8449;",
                "INFO":    "background-color:#ebf5fb;color:#1a5276;",
            }
            return colors.get(val, "")

        st.dataframe(
            form_df.style.map(color_hazard_form, subset=["hazard"]),
            use_container_width=True
        )

        st.divider()
        st.markdown("### Hazard Breakdown")
        color_map = {
            "DANGER":"#e74c3c","WARNING":"#f39c12",
            "SAFE":"#27ae60","INFO":"#3498db"
        }
        haz_chart = form_df["hazard"].value_counts().reset_index()
        haz_chart.columns = ["hazard", "count"]
        fig = px.bar(haz_chart, x="hazard", y="count", color="hazard",
                     color_discrete_map=color_map, text="count")
        fig.update_layout(showlegend=False, height=250, margin=dict(t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        if st.button("🗑️ Clear formulation"):
            st.session_state.formulation = []
            st.rerun()
    else:
        st.info("No ingredients added yet. Use the selector above to build your formulation.")



# PAGE 4 — SAFETY REPORT EXPORT:

elif page == "Analysis":

    st.markdown("## Safety Report Export")
    st.caption("Generate and download a safety report for any set of ingredients.")
    st.divider()

    st.markdown("### Select ingredients to include")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        hazard_select = st.multiselect(
            "Filter by hazard",
            ["DANGER", "WARNING", "SAFE", "INFO", "UNKNOWN"],
            default=["DANGER", "WARNING", "SAFE", "INFO", "UNKNOWN"]
        )
    with col_f2:
        name_select = st.multiselect("Or pick specific ingredients", df["name"].tolist())

    report_df = df[df["name"].isin(name_select)] if name_select else df[df["hazard"].isin(hazard_select)]

    st.divider()
    st.markdown(f"**{len(report_df)} ingredients** will be included in the report.")

    def color_hazard_rep(val):
        colors = {
            "DANGER":  "background-color:#fde8e8;color:#c0392b;",
            "WARNING": "background-color:#fef9e7;color:#d35400;",
            "SAFE":    "background-color:#eafaf1;color:#1e8449;",
            "INFO":    "background-color:#ebf5fb;color:#1a5276;",
        }
        return colors.get(val, "")

    st.dataframe(
        report_df.style.map(color_hazard_rep, subset=["hazard"]),
        use_container_width=True
    )

    st.divider()
    st.markdown("### Report Summary")
    rs1, rs2, rs3 = st.columns(3)
    rs1.metric("Total",          len(report_df))
    rs2.metric("Danger entries", int((report_df["hazard"] == "DANGER").sum()))
    rs3.metric("Avg purity",     f"{report_df['purity'].mean():.1f}%")

    st.divider()
    st.markdown("### Download Report")

    st.download_button(
        label="⬇️ Download as CSV",
        data=report_df.to_csv(index=False).encode("utf-8"),
        file_name="biospec_safety_report.csv",
        mime="text/csv"
    )

    summary_lines = [
        "BIOSPEC ANALYSER — SAFETY REPORT",
        "=" * 40,
        f"Total ingredients : {len(report_df)}",
        f"Danger entries    : {int((report_df['hazard']=='DANGER').sum())}",
        f"Warning entries   : {int((report_df['hazard']=='WARNING').sum())}",
        f"Safe entries      : {int((report_df['hazard']=='SAFE').sum())}",
        f"Average purity    : {report_df['purity'].mean():.1f}%",
        f"Average mol. wt   : {report_df['mw'].mean():,.0f} g/mol",
        "=" * 40,
        "",
        "INGREDIENT LIST",
        ""
    ]
    for _, r in report_df.iterrows():
        summary_lines.append(
            f"{r['name']} | {r['formula']} | MW: {r['mw']} | "
            f"pH: {r['ph']} | Hazard: {r['hazard']} | CAS: {r['cas']}"
        )

    st.download_button(
        label="⬇️ Download as TXT",
        data="\n".join(summary_lines).encode("utf-8"),
        file_name="biospec_safety_report.txt",
        mime="text/plain"
    )



# PAGE 5 — BATCH UPLOAD:

elif page == "Datasets":

    st.markdown("## Batch Ingredient Upload")
    st.caption("Upload your own CSV file to analyse a custom ingredient list.")
    st.divider()

    st.markdown("### Required CSV format")
    st.code("name, formula, mw, ph, qty, purity, cas, hazard")
    st.markdown("Hazard must be one of: **DANGER, WARNING, SAFE, INFO, UNKNOWN**")

    st.divider()
    template_df = pd.DataFrame([{
        "name": "Example Compound", "formula": "C2H5OH",
        "mw": 46.07, "ph": 7.0, "qty": "100ml",
        "purity": 99.5, "cas": "64-17-5", "hazard": "SAFE"
    }])
    st.download_button(
        label="⬇️ Download template CSV",
        data=template_df.to_csv(index=False).encode("utf-8"),
        file_name="biospec_template.csv",
        mime="text/csv"
    )

    st.divider()
    st.markdown("### Upload your file")
    batch_file = st.file_uploader("Upload CSV", type="csv", key="batch_upload")

    if batch_file:
        try:
            batch_df = pd.read_csv(batch_file)
            required_cols = {"name", "formula", "mw", "ph", "qty", "purity", "cas", "hazard"}
            missing = required_cols - set(batch_df.columns)

            if missing:
                st.error(f"Missing columns: {', '.join(missing)}")
            else:
                st.success(f"✅ File loaded — {len(batch_df)} ingredients found")
                st.divider()

                b1, b2, b3, b4 = st.columns(4)
                b1.metric("Total",  len(batch_df))
                b2.metric("Danger", int((batch_df["hazard"] == "DANGER").sum()))
                b3.metric("Avg MW", f"{batch_df['mw'].mean():,.0f} g/mol")
                b4.metric("Avg pH", f"{batch_df['ph'].mean():.2f}")

                st.divider()
                color_map = {
                    "DANGER":"#e74c3c","WARNING":"#f39c12",
                    "SAFE":"#27ae60","INFO":"#3498db","UNKNOWN":"#95a5a6"
                }
                haz = batch_df["hazard"].value_counts().reset_index()
                haz.columns = ["hazard", "count"]
                fig = px.bar(haz, x="hazard", y="count", color="hazard",
                             color_discrete_map=color_map, text="count")
                fig.update_layout(showlegend=False, height=250, margin=dict(t=10,b=10))
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### Uploaded Ingredients")

                def color_hazard_batch(val):
                    colors = {
                        "DANGER":  "background-color:#fde8e8;color:#c0392b;",
                        "WARNING": "background-color:#fef9e7;color:#d35400;",
                        "SAFE":    "background-color:#eafaf1;color:#1e8449;",
                        "INFO":    "background-color:#ebf5fb;color:#1a5276;"
                    }
                    return colors.get(val, "")

                st.dataframe(
                    batch_df.style.map(color_hazard_batch, subset=["hazard"]),
                    use_container_width=True
                )

                st.divider()
                if st.button("➕ Merge into main database"):
                    combined = pd.concat([df, batch_df], ignore_index=True)
                    combined = combined.drop_duplicates(subset=["name"])
                    combined.to_csv("ingredients.csv", index=False)
                    st.success(f"✅ Merged — database now has {len(combined)} ingredients. Restart the app to see changes.")

        except Exception as e:
            st.error(f"Error reading file: {e}")



# PAGE 6 — QUICK PROFILER:

elif page == "Quick Profiler":

    st.markdown("## 🔬 What Am I Working With?")
    st.caption("Type any ingredient name and get an instant safety profile.")
    st.divider()

    query = st.text_input(
        "",
        placeholder="e.g. Ethanol, Sodium Azide, Chloroform...",
        label_visibility="collapsed"
    )

    hazard_config = {
        "DANGER":  {"icon": "🔴", "color": "#e74c3c", "bg": "#fde8e8", "label": "DANGER"},
        "WARNING": {"icon": "🟡", "color": "#d35400", "bg": "#fef9e7", "label": "WARNING"},
        "SAFE":    {"icon": "🟢", "color": "#1e8449", "bg": "#eafaf1", "label": "SAFE"},
        "INFO":    {"icon": "🔵", "color": "#1a5276", "bg": "#ebf5fb", "label": "INFO"},
        "UNKNOWN": {"icon": "⚪", "color": "#717d7e", "bg": "#f2f3f4", "label": "UNKNOWN"},
    }

    usage_map = {
        "bovine serum albumin":     "Used as a protein standard and blocking agent in biochemical assays such as ELISA and western blotting.",
        "sodium azide":             "Used as a preservative in biological buffers and reagents; also used in organic synthesis.",
        "polysorbate 80":           "A nonionic surfactant used as an emulsifier in pharmaceutical formulations and food products.",
        "formaldehyde":             "Used as a fixative in histology and as a disinfectant; also used in protein crosslinking.",
        "ethanol":                  "Common laboratory solvent and disinfectant; used in DNA precipitation and surface sterilisation.",
        "triton x-100":             "A nonionic detergent used to solubilise membrane proteins and permeabilise cells.",
        "glycerol":                 "Used as a cryoprotectant, humectant, and component of electrophoresis loading buffers.",
        "ethidium bromide":         "A fluorescent dye that intercalates into DNA; used for visualising nucleic acids in gel electrophoresis.",
        "edta":                     "A chelating agent used to bind divalent metal ions; used in buffers to inhibit nucleases.",
        "tris buffer":              "A common biological buffer used to maintain pH in biochemical experiments.",
        "peg-400":                  "Polyethylene glycol used as a solubiliser, plasticiser, and excipient in drug formulations.",
        "mannitol":                 "A sugar alcohol used as an osmotic agent and cryoprotectant in pharmaceutical formulations.",
        "histidine":                "An essential amino acid used as a buffering agent in protein formulations and drug products.",
        "polysorbate 20":           "A mild nonionic surfactant used to prevent protein aggregation in biopharmaceutical formulations.",
        "mercury chloride":         "A highly toxic inorganic compound used historically as a disinfectant and fixative.",
        "acetic acid":              "Used in buffer preparation (e.g. acetate buffer) and as a mild fixative in histology.",
        "acetone":                  "A polar aprotic solvent used for dehydration, precipitation, and equipment cleaning.",
        "acetonitrile":             "A solvent widely used in HPLC mobile phases and organic synthesis.",
        "acrylamide":               "Monomer used to prepare polyacrylamide gels for electrophoresis; neurotoxic in monomer form.",
        "agar":                     "A polysaccharide used to solidify microbiological culture media.",
        "agarose":                  "Used to prepare gels for nucleic acid electrophoresis; derived from seaweed.",
        "ammonium acetate":         "Used as a volatile buffer in mass spectrometry and HPLC applications.",
        "ammonium bicarbonate":     "Used as a volatile buffer in proteomics sample preparation and LC-MS workflows.",
        "ammonium chloride":        "Used in cell biology to inhibit lysosomal acidification and block viral entry.",
        "ammonium persulfate":      "Initiator used in polymerisation of acrylamide gels for PAGE electrophoresis.",
        "ammonium sulfate":         "Used for protein precipitation and purification via salting-out methods.",
        "ampicillin":               "A beta-lactam antibiotic used for selection of transformed bacteria in molecular biology.",
        "ascorbic acid":            "An antioxidant vitamin used to prevent oxidation of sensitive compounds in solution.",
        "boric acid":               "Used in TBE buffer for nucleic acid electrophoresis; also a mild antiseptic.",
        "bromophenol blue":         "A pH indicator and tracking dye used in gel electrophoresis loading buffers.",
        "calcium chloride":         "Used to prepare competent cells for bacterial transformation and in cell culture media.",
        "calcium phosphate":        "Used in transfection protocols and as a calcium source in cell culture.",
        "chloroform":               "A halogenated solvent used in nucleic acid extraction (e.g. phenol-chloroform method).",
        "citric acid":              "Used in buffer preparation (citrate buffer) and as a chelating and preservative agent.",
        "copper sulfate":           "Used in the Bradford and Biuret protein assays and as a histological stain component.",
        "dmso":                     "A polar aprotic solvent used to dissolve compounds and as a cryoprotectant for cell storage.",
        "dextrose":                 "A simple sugar (glucose) used as a carbon source in microbial culture media.",
        "dimethylformamide":        "An aprotic polar solvent used in organic synthesis and peptide chemistry.",
        "dithiothreitol":           "A reducing agent used to break disulfide bonds in proteins during sample preparation.",
        "dopamine hcl":             "A catecholamine neurotransmitter used in cell biology and surface coating experiments.",
        "ethylene glycol":          "Used as a cryoprotectant and antifreeze agent; also used in protein crystallisation.",
        "ferric chloride":          "Used as a Lewis acid catalyst and as a reagent for phenol detection.",
        "folic acid":               "A B vitamin used as a supplement in cell culture media; essential for nucleotide synthesis.",
        "glucose":                  "The primary energy source for cells; used extensively in culture media formulations.",
        "glutaraldehyde":           "A crosslinking fixative used in electron microscopy and for surface immobilisation of proteins.",
        "guanidine hcl":            "A strong protein denaturant used in protein unfolding and nucleic acid extraction.",
        "hepes":                    "A zwitterionic buffer commonly used in cell culture to maintain physiological pH.",
        "hydrochloric acid":        "A strong acid used for pH adjustment, protein hydrolysis, and cleaning glassware.",
        "hydrogen peroxide":        "An oxidising agent used as a disinfectant, bleach, and in chemiluminescence assays.",
        "imidazole":                "Used to elute His-tagged proteins from nickel affinity chromatography columns.",
        "isopropanol":              "A common solvent used for DNA precipitation, surface disinfection, and protein precipitation.",
        "kanamycin":                "An aminoglycoside antibiotic used for selection of kanamycin-resistant bacterial transformants.",
        "l-arginine":               "An amino acid used to improve protein solubility and stability in formulations.",
        "l-cysteine":               "A sulfur-containing amino acid used as a reducing agent and in protein structure studies.",
        "l-glutamine":              "An essential amino acid supplement added to cell culture media for cell growth.",
        "l-proline":                "An amino acid used as a stabiliser in protein formulations and cryoprotective solutions.",
        "lactic acid":              "Used in buffer systems and as a pH regulator in pharmaceutical formulations.",
        "lithium chloride":         "Used to precipitate RNA selectively from complex mixtures in extraction protocols.",
        "magnesium chloride":       "A cofactor for DNA polymerases; essential in PCR and restriction enzyme reactions.",
        "magnesium sulfate":        "Used as a magnesium source in culture media and enzyme reaction buffers.",
        "maleic acid":              "Used in buffer preparation and as a crosslinking reagent in biochemical applications.",
        "methanol":                 "A polar solvent used in HPLC, protein precipitation, and fixing cells for flow cytometry.",
        "methylene blue":           "A redox indicator and biological stain used to visualise cells and assess cell viability.",
        "nonidet p-40":             "A nonionic detergent used to lyse cells and solubilise membrane-associated proteins.",
        "pbs buffer":               "Phosphate-buffered saline; a standard isotonic buffer used in cell biology and washing steps.",
        "phenol":                   "Used in phenol-chloroform nucleic acid extraction; highly corrosive and toxic.",
        "phenol red":               "A pH indicator used in cell culture media to visually monitor pH changes.",
        "phosphoric acid":          "Used for pH adjustment and buffer preparation in analytical and biochemical applications.",
        "potassium chloride":       "Used in electrophysiology experiments and as a component of physiological saline solutions.",
        "potassium hydroxide":      "A strong base used for pH adjustment, saponification, and tissue digestion.",
        "potassium iodide":         "Used as a source of iodide ions and in thyroid research and staining applications.",
        "propidium iodide":         "A membrane-impermeant fluorescent dye used to stain dead cells in flow cytometry.",
        "proteinase k":             "A broad-spectrum serine protease used to digest proteins in nucleic acid extraction.",
        "pyridine":                 "A basic heterocyclic solvent used in organic synthesis and derivatisation reactions.",
        "saponin":                  "A natural detergent used to permeabilise cell membranes for intracellular staining.",
        "silver nitrate":           "Used in silver staining of gels and as an antimicrobial and analytical reagent.",
        "sodium bicarbonate":       "Used as a pH buffer in cell culture CO2 incubators and in electrophoresis buffers.",
        "sodium carbonate":         "A strong base used in colorimetric assays such as the Lowry protein assay.",
        "sodium chloride":          "The primary salt used to maintain osmolarity in physiological buffers and culture media.",
        "sodium dodecyl sulfate":   "An anionic detergent used to denature and impart negative charge to proteins in SDS-PAGE.",
        "sodium hydroxide":         "A strong base used for pH adjustment, cleaning, and decontaminating laboratory equipment.",
        "sodium hypochlorite":      "The active ingredient in bleach; used for surface decontamination and biohazard inactivation.",
        "sodium phosphate":         "Used as a buffer component and to adjust pH in biological and analytical applications.",
        "streptomycin":             "An aminoglycoside antibiotic added to cell culture media to prevent bacterial contamination.",
        "sucrose":                  "Used as a cryoprotectant, density gradient medium, and osmotic agent in cell biology.",
        "sulfuric acid":            "A strong mineral acid used for pH adjustment, digestion, and analytical chemistry.",
        "temed":                    "An accelerator used alongside ammonium persulfate to polymerise acrylamide gels.",
        "tetracycline":             "A broad-spectrum antibiotic used for bacterial selection and inducible gene expression systems.",
        "toluene":                  "An aromatic solvent used in organic synthesis, histology, and scintillation counting.",
        "trichloroacetic acid":     "Used to precipitate proteins, remove nucleic acids, and fix cells in biochemical assays.",
        "triethanolamine":          "Used as a pH adjusting agent and emulsifier in pharmaceutical and cosmetic formulations.",
        "urea":                     "A strong denaturant used to unfold proteins and solubilise inclusion bodies.",
        "xylene cyanol":            "A blue tracking dye used alongside bromophenol blue in gel electrophoresis loading buffers.",
        "zinc chloride":            "Used as a Lewis acid catalyst and as a zinc source in enzymatic and cell biology studies.",
        "zinc sulfate":             "Used as a zinc supplement in culture media and for protein precipitation applications.",
        "beta-mercaptoethanol":     "A strong reducing agent used to break disulfide bonds; highly toxic with a strong odour.",
    }

    handling_tips = {
        "DANGER":  "Use full PPE. Work in a fume hood. Refer to SDS before any handling.",
        "WARNING": "Wear gloves and eye protection. Avoid inhalation and prolonged skin contact.",
        "SAFE":    "Standard lab PPE is sufficient. Follow institutional disposal guidelines.",
        "INFO":    "Controlled substance — follow institutional protocols and document usage.",
        "UNKNOWN": "Treat as potentially hazardous. Consult supervisor before use.",
    }

    if query:
        match = df[df["name"].str.lower().str.contains(query.strip().lower(), na=False)]

        if match.empty:
            st.error(f"❌ No ingredient found matching **'{query}'**. Try a different name or check spelling.")
            st.caption("Tip: Try searching part of the name, e.g. 'sodium' instead of 'Sodium Chloride'")
        else:
            for _, row in match.iterrows():
                haz   = row["hazard"]
                cfg   = hazard_config.get(haz, hazard_config["UNKNOWN"])
                usage = usage_map.get(row["name"].lower(), "No usage description available for this compound.")
                tip   = handling_tips.get(haz, "No handling tip available.")
                cas   = str(row["cas"]).strip()
                image_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/PNG"

                st.markdown(
                    f"""
                    <div style='
                        background:{cfg["bg"]};
                        border-left:5px solid {cfg["color"]};
                        border-radius:10px;
                        padding:20px 24px;
                        margin-bottom:16px;
                    '>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div style='flex:1'>
                                <span style='font-size:22px;font-weight:700;color:#1a1a1a'>{row["name"]}</span>
                                <span style='font-size:14px;color:#555;margin-left:12px;font-family:monospace'>{row["formula"]}</span>
                            </div>
                            <div style='margin:0 24px;'>
                                <img src='{image_url}'
                                     style='width:120px;height:120px;object-fit:contain;background:white;
                                            border-radius:8px;border:1px solid {cfg["color"]}44;padding:6px;'
                                     onerror="this.style.display='none'"
                                />
                            </div>
                            <div style='
                                background:{cfg["color"]};
                                color:white;
                                padding:6px 16px;
                                border-radius:20px;
                                font-weight:700;
                                font-size:13px;
                                letter-spacing:0.05em;
                                align-self:flex-start;
                            '>{cfg["icon"]} {cfg["label"]}</div>
                        </div>
                        <hr style='border:none;border-top:1px solid {cfg["color"]}33;margin:14px 0'/>
                        <table style='width:100%;font-size:13px;color:#333;'>
                            <tr>
                                <td style='padding:4px 0;width:25%'>🧪 <b>Mol. Weight</b></td>
                                <td>{row["mw"]:,} g/mol</td>
                                <td style='padding:4px 0;width:25%'>⚗️ <b>pH</b></td>
                                <td>{row["ph"]}</td>
                            </tr>
                            <tr>
                                <td style='padding:4px 0'>📦 <b>Purity</b></td>
                                <td>{row["purity"]}%</td>
                                <td style='padding:4px 0'>🔖 <b>CAS</b></td>
                                <td>{row["cas"]}</td>
                            </tr>
                            <tr>
                                <td style='padding:4px 0'>🔬 <b>Used for</b></td>
                                <td colspan='3'>{usage}</td>
                            </tr>
                            <tr>
                                <td style='padding:4px 0'>🛡️ <b>Handling</b></td>
                                <td colspan='3'>{tip}</td>
                            </tr>
                        </table>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.markdown(
            """
            <div style='text-align:center;padding:60px 20px;color:#888;'>
                <div style='font-size:48px;margin-bottom:16px'>🔬</div>
                <div style='font-size:18px;font-weight:600;margin-bottom:8px'>Type an ingredient above</div>
                <div style='font-size:13px'>Get an instant profile — what it is, what it does,
                hazard level, pH, mol. weight, structure image, and a handling tip.</div>
            </div>
            """,
            unsafe_allow_html=True
        )



# PAGE 7 — RISK HEATMAP:

elif page == "Risk Heatmap":
    import plotly.graph_objects as go

    st.markdown("## 🌡️ Risk Heatmap")
    st.caption("Visual risk matrix of all ingredients across multiple hazard dimensions.")
    st.divider()

    def compute_scores(row):
        tox = {"DANGER": 95, "WARNING": 55, "SAFE": 10, "INFO": 30, "UNKNOWN": 50}.get(row["hazard"], 50)
        ph_risk     = min(abs(row["ph"] - 7.0) * 14, 100)
        purity_risk = max(0, 100 - row["purity"])
        mw = row["mw"]
        if mw < 100:       mw_risk = 20
        elif mw < 500:     mw_risk = 40
        elif mw < 1000:    mw_risk = 60
        elif mw < 10000:   mw_risk = 75
        else:              mw_risk = 90
        overall = round((tox * 0.5) + (ph_risk * 0.2) + (purity_risk * 0.1) + (mw_risk * 0.2), 1)
        return pd.Series({
            "Toxicity":      tox,
            "pH Risk":       round(ph_risk, 1),
            "Purity Risk":   round(purity_risk, 1),
            "MW Complexity": mw_risk,
            "Overall Risk":  overall
        })

    scores_df  = df.apply(compute_scores, axis=1)
    heatmap_df = pd.concat([df[["name", "hazard"]], scores_df], axis=1)

    # ── Tab layout ────────────────────────────────────────
    tab1, tab2 = st.tabs(["📊 Full Heatmap", "🔍 Ingredient Lookup"])

    # ── TAB 1: Full heatmap ───────────────────────────────
    with tab1:
        col_ctrl1, col_ctrl2 = st.columns([2, 1])
        with col_ctrl1:
            selected_hazards = st.multiselect(
                "Filter by hazard",
                ["DANGER", "WARNING", "SAFE", "INFO", "UNKNOWN"],
                default=["DANGER", "WARNING", "SAFE", "INFO", "UNKNOWN"],
                key="hm_hazard"
            )
        with col_ctrl2:
            top_n = st.slider("Show top N by overall risk", 5, len(df), 30, key="hm_topn")

        filtered_hm = heatmap_df[heatmap_df["hazard"].isin(selected_hazards)]
        filtered_hm = filtered_hm.nlargest(top_n, "Overall Risk")

        if filtered_hm.empty:
            st.warning("No data to display. Adjust filters.")
        else:
            dims   = ["Toxicity", "pH Risk", "Purity Risk", "MW Complexity", "Overall Risk"]
            z_data = filtered_hm[dims].values.tolist()
            y_labels = filtered_hm["name"].tolist()

            fig_hm = go.Figure(data=go.Heatmap(
                z=z_data,
                x=dims,
                y=y_labels,
                colorscale=[
                    [0.0, "#1a9e56"],
                    [0.4, "#f5c518"],
                    [0.7, "#f39c12"],
                    [1.0, "#e74c3c"]
                ],
                zmin=0, zmax=100,
                text=[[f"{v:.0f}" for v in row] for row in z_data],
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False,
                colorbar=dict(
                    title="Risk Score",
                    tickvals=[0, 25, 50, 75, 100],
                    ticktext=["0 Safe", "25", "50", "75", "100 Max"]
                )
            ))
            fig_hm.update_layout(
                height=max(400, len(y_labels) * 22),
                margin=dict(t=20, b=20, l=200),
                xaxis=dict(side="top"),
                yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig_hm, use_container_width=True)

            st.divider()
            st.markdown("### Risk Score Table")

            def color_overall(val):
                if val >= 75:   return "background-color:#fde8e8;color:#c0392b;"
                elif val >= 50: return "background-color:#fef9e7;color:#d35400;"
                elif val >= 25: return "background-color:#fffde7;color:#b7950b;"
                else:           return "background-color:#eafaf1;color:#1e8449;"

            st.dataframe(
                filtered_hm.style.map(color_overall, subset=["Overall Risk"]),
                use_container_width=True,
                height=400
            )

            st.download_button(
                label="⬇️ Download risk scores CSV",
                data=filtered_hm.to_csv(index=False).encode("utf-8"),
                file_name="biospec_risk_heatmap.csv",
                mime="text/csv"
            )

    # ── TAB 2: Ingredient lookup ──────────────────────────
    with tab2:
        st.markdown("### 🔍 Search a specific ingredient")
        lookup_query = st.text_input(
            "",
            placeholder="Type ingredient name...",
            label_visibility="collapsed",
            key="hm_lookup"
        )

        if lookup_query:
            match = heatmap_df[heatmap_df["name"].str.lower().str.contains(
                lookup_query.strip().lower(), na=False
            )]

            if match.empty:
                st.error(f"No ingredient found matching '{lookup_query}'.")
            else:
                for _, row in match.iterrows():
                    haz = row["hazard"]
                    haz_colors = {
                        "DANGER":  ("#fde8e8", "#c0392b", "🔴"),
                        "WARNING": ("#fef9e7", "#d35400", "🟡"),
                        "SAFE":    ("#eafaf1", "#1e8449", "🟢"),
                        "INFO":    ("#ebf5fb", "#1a5276", "🔵"),
                        "UNKNOWN": ("#f2f3f4", "#717d7e", "⚪"),
                    }
                    bg, fg, icon = haz_colors.get(haz, ("#f2f3f4","#717d7e","⚪"))

                    st.markdown(
                        f"<div style='background:{bg};border-left:5px solid {fg};"
                        f"border-radius:10px;padding:16px 22px;margin-bottom:12px;'>"
                        f"<div style='font-size:18px;font-weight:700;color:#1a1a1a;"
                        f"margin-bottom:12px'>{row['name']} "
                        f"<span style='font-size:13px;background:{fg};color:white;"
                        f"padding:3px 12px;border-radius:20px;margin-left:8px'>"
                        f"{icon} {haz}</span></div>",
                        unsafe_allow_html=True
                    )

                    # Score bars
                    dims = ["Toxicity", "pH Risk", "Purity Risk", "MW Complexity", "Overall Risk"]
                    for dim in dims:
                        score = row[dim]
                        bar_color = "#e74c3c" if score >= 75 else "#f39c12" if score >= 50 else "#f5c518" if score >= 25 else "#27ae60"
                        st.markdown(
                            f"<div style='display:flex;align-items:center;gap:12px;"
                            f"margin-bottom:8px;'>"
                            f"<span style='width:140px;font-size:13px;color:#555;'>{dim}</span>"
                            f"<div style='flex:1;background:#eee;border-radius:6px;height:18px;'>"
                            f"<div style='width:{score}%;background:{bar_color};"
                            f"height:18px;border-radius:6px;transition:width 0.3s;'></div></div>"
                            f"<span style='width:40px;font-size:13px;font-weight:600;"
                            f"color:{bar_color};text-align:right'>{score:.0f}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                    # Risk interpretation
                    overall = row["Overall Risk"]
                    if overall >= 75:
                        interp = "🔴 High risk ingredient — strict handling protocols required"
                    elif overall >= 50:
                        interp = "🟡 Moderate risk — standard precautions and PPE required"
                    elif overall >= 25:
                        interp = "🟠 Low-moderate risk — general lab safety sufficient"
                    else:
                        interp = "🟢 Low risk — safe under normal laboratory conditions"

                    st.markdown(
                        f"<div style='margin-top:10px;padding:10px 14px;"
                        f"background:white;border-radius:8px;border:1px solid {fg}44;"
                        f"font-size:13px;color:#333;'>{interp}</div></div>",
                        unsafe_allow_html=True
                    )
        else:
            st.markdown(
                "<div style='text-align:center;padding:40px;color:#aaa;'>"
                "<div style='font-size:36px;margin-bottom:10px'>🔍</div>"
                "Type an ingredient name above to see its full risk breakdown."
                "</div>",
                unsafe_allow_html=True
            )



# PAGE 8 — REACTION PREDICTOR:

elif page == "Reaction Predictor":
    import itertools

    st.markdown("## ⚗️ Reaction & Condition Predictor")
    st.caption("Select 2 or more ingredients to predict interactions, required conditions, and combined hazard.")
    st.divider()

    reaction_db = {
        frozenset(["hydrochloric acid", "sodium hydroxide"]): {
            "type":        "Acid-Base Neutralisation",
            "equation":    "HCl + NaOH → NaCl + H₂O",
            "conditions":  "Room temperature, aqueous solution",
            "outcome":     "Produces sodium chloride and water. Highly exothermic — add acid to base slowly.",
            "hazard_rise": "HIGH → MEDIUM after reaction (neutralised product is safe)",
            "temp":        "Exothermic — can reach 80°C if concentrated",
            "warning":     "⚠️ Never add water to concentrated acid. Always add acid to base."
        },
        frozenset(["hydrogen peroxide", "sodium hydroxide"]): {
            "type":        "Oxidiser-Base Decomposition",
            "equation":    "H₂O₂ + NaOH → NaHO₂ + H₂O",
            "conditions":  "Alkaline conditions, room temperature",
            "outcome":     "Hydrogen peroxide decomposes rapidly in alkaline conditions releasing oxygen gas.",
            "hazard_rise": "DANGER — oxygen evolution can cause pressure buildup in sealed containers",
            "temp":        "Exothermic decomposition",
            "warning":     "⚠️ Do not seal container. Perform in open vessel with ventilation."
        },
        frozenset(["ethanol", "hydrogen peroxide"]): {
            "type":        "Oxidation Reaction",
            "equation":    "C₂H₅OH + H₂O₂ → CH₃CHO + 2H₂O",
            "conditions":  "Ambient temperature, may require catalyst",
            "outcome":     "Ethanol is oxidised to acetaldehyde. Mixture is flammable and volatile.",
            "hazard_rise": "WARNING → DANGER (flammable mixture, toxic acetaldehyde produced)",
            "temp":        "Exothermic if concentrated",
            "warning":     "⚠️ Keep away from ignition sources. Work in fume hood."
        },
        frozenset(["formaldehyde", "sodium hydroxide"]): {
            "type":        "Cannizzaro Reaction",
            "equation":    "2HCHO + NaOH → HCOONa + CH₃OH",
            "conditions":  "Concentrated NaOH, room temperature",
            "outcome":     "Formaldehyde disproportionates into methanol and sodium formate.",
            "hazard_rise": "DANGER — formaldehyde vapour and methanol generation",
            "temp":        "Mild exotherm",
            "warning":     "⚠️ Carcinogenic vapours. Fume hood mandatory. Full PPE required."
        },
        frozenset(["acetic acid", "sodium hydroxide"]): {
            "type":        "Acid-Base Neutralisation",
            "equation":    "CH₃COOH + NaOH → CH₃COONa + H₂O",
            "conditions":  "Aqueous solution, room temperature",
            "outcome":     "Produces sodium acetate buffer. Mildly exothermic.",
            "hazard_rise": "WARNING → SAFE (acetate buffer is non-hazardous)",
            "temp":        "Mildly exothermic",
            "warning":     "✅ Relatively safe — standard acetate buffer preparation."
        },
        frozenset(["chloroform", "sodium hydroxide"]): {
            "type":        "Haloform Hydrolysis",
            "equation":    "CHCl₃ + 4NaOH → HCOONa + 3NaCl + 2H₂O",
            "conditions":  "Strong alkaline conditions, elevated temperature",
            "outcome":     "Chloroform slowly hydrolyses. May produce toxic phosgene as intermediate.",
            "hazard_rise": "DANGER — phosgene (COCl₂) possible toxic byproduct",
            "temp":        "Requires heating >50°C",
            "warning":     "⚠️ SEVERE — potential phosgene generation. Fume hood and gas monitoring required."
        },
        frozenset(["ethanol", "acetic acid"]): {
            "type":        "Fischer Esterification",
            "equation":    "C₂H₅OH + CH₃COOH ⇌ CH₃COOC₂H₅ + H₂O",
            "conditions":  "Acid catalyst (H₂SO₄), heat 60–80°C, reflux",
            "outcome":     "Produces ethyl acetate (common solvent). Reversible equilibrium.",
            "hazard_rise": "WARNING (flammable vapours during heating)",
            "temp":        "60–80°C under reflux",
            "warning":     "⚠️ Flammable vapours — no open flames. Use heating mantle."
        },
        frozenset(["glucose", "sodium hydroxide"]): {
            "type":        "Alkaline Degradation",
            "equation":    "C₆H₁₂O₆ + NaOH → lactic acid + formic acid + other degradation products",
            "conditions":  "Concentrated NaOH, elevated temperature",
            "outcome":     "Glucose undergoes retro-aldol and isomerisation producing organic acids.",
            "hazard_rise": "WARNING (strongly alkaline solution)",
            "temp":        "Accelerated above 50°C",
            "warning":     "🔶 Monitor pH. Caramelisation may occur at high temperatures."
        },
        frozenset(["hydrogen peroxide", "potassium iodide"]): {
            "type":        "Catalytic Decomposition (Elephant Toothpaste)",
            "equation":    "2H₂O₂ → 2H₂O + O₂↑ (KI as catalyst)",
            "conditions":  "Aqueous, room temperature, KI as catalyst",
            "outcome":     "Rapid violent oxygen evolution. Highly exothermic foaming reaction.",
            "hazard_rise": "DANGER — rapid gas evolution, severe exotherm",
            "temp":        "Highly exothermic — solution reaches 60°C+",
            "warning":     "⚠️ Do not seal. Violent foaming. Use open large container only."
        },
        frozenset(["sodium hydroxide", "ammonium chloride"]): {
            "type":        "Base-Salt Reaction / Ammonia Generation",
            "equation":    "NaOH + NH₄Cl → NaCl + H₂O + NH₃↑",
            "conditions":  "Aqueous, room temperature or gentle heating",
            "outcome":     "Releases toxic ammonia gas. Used in lab preparation of ammonia.",
            "hazard_rise": "DANGER — toxic NH₃ gas released",
            "temp":        "Accelerated with heating",
            "warning":     "⚠️ Toxic gas — fume hood mandatory. Do not inhale ammonia."
        },
        frozenset(["citric acid", "sodium bicarbonate"]): {
            "type":        "Acid-Carbonate Effervescence",
            "equation":    "C₆H₈O₇ + 3NaHCO₃ → Na₃C₆H₅O₇ + 3H₂O + 3CO₂↑",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "CO₂ gas released. Produces sodium citrate buffer solution.",
            "hazard_rise": "SAFE — no significant hazard increase",
            "temp":        "Room temperature, slightly endothermic",
            "warning":     "✅ Safe. Common in pharmaceutical and food effervescent formulations."
        },
        frozenset(["copper sulfate", "sodium hydroxide"]): {
            "type":        "Precipitation Reaction",
            "equation":    "CuSO₄ + 2NaOH → Cu(OH)₂↓ + Na₂SO₄",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Blue copper hydroxide precipitate forms. Basis of Biuret protein assay.",
            "hazard_rise": "WARNING (copper compounds are toxic to aquatic organisms)",
            "temp":        "Room temperature",
            "warning":     "🔶 Dispose of copper waste properly — do not pour down drain."
        },
        frozenset(["ethanol", "sodium hydroxide"]): {
            "type":        "Alkoxide Formation",
            "equation":    "C₂H₅OH + NaOH → C₂H₅ONa + H₂O",
            "conditions":  "Concentrated NaOH, elevated temperature",
            "outcome":     "Forms sodium ethoxide — a strong nucleophile used in organic synthesis.",
            "hazard_rise": "DANGER — sodium ethoxide reacts violently with moisture",
            "temp":        "Requires elevated temperature",
            "warning":     "⚠️ Highly reactive product. Keep away from moisture and water."
        },
        frozenset(["phenol", "sodium hydroxide"]): {
            "type":        "Acid-Base / Phenoxide Formation",
            "equation":    "C₆H₅OH + NaOH → C₆H₅ONa + H₂O",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Forms sodium phenoxide. Used in phenol-chloroform RNA/DNA extraction.",
            "hazard_rise": "DANGER — phenol absorbed rapidly through skin",
            "temp":        "Room temperature",
            "warning":     "⚠️ Phenol causes severe burns. Face shield and fume hood mandatory."
        },
        frozenset(["urea", "hydrochloric acid"]): {
            "type":        "Protonation / Salt Formation",
            "equation":    "CO(NH₂)₂ + HCl → [CO(NH₃)₂]Cl",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Urea hydrochloride formed. Used in protein denaturation buffers.",
            "hazard_rise": "WARNING → DANGER (corrosive acidic denaturing solution)",
            "temp":        "Room temperature",
            "warning":     "⚠️ Corrosive mixture. Gloves and eye protection required."
        },
        frozenset(["sulfuric acid", "sodium hydroxide"]): {
            "type":        "Strong Acid-Base Neutralisation",
            "equation":    "H₂SO₄ + 2NaOH → Na₂SO₄ + 2H₂O",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Produces sodium sulfate and water. Violently exothermic if concentrated.",
            "hazard_rise": "EXTREME DANGER during mixing → SAFE after full neutralisation",
            "temp":        "Can boil if concentrated — use ice bath",
            "warning":     "⚠️ Add acid to base VERY slowly. Ice bath recommended. Full PPE mandatory."
        },
        frozenset(["isopropanol", "hydrogen peroxide"]): {
            "type":        "Oxidation Reaction",
            "equation":    "C₃H₇OH + H₂O₂ → CH₃COCH₃ + 2H₂O",
            "conditions":  "Room temperature, may require acid catalyst",
            "outcome":     "Isopropanol oxidised to acetone. Flammable peroxide mixture.",
            "hazard_rise": "WARNING → DANGER (flammable, unstable peroxide mixture)",
            "temp":        "Mild exotherm",
            "warning":     "⚠️ Flammable vapours. No ignition sources. Fume hood required."
        },
        frozenset(["sodium azide", "hydrochloric acid"]): {
            "type":        "Extremely Dangerous Acid-Azide Reaction",
            "equation":    "NaN₃ + HCl → NaCl + HN₃↑",
            "conditions":  "Any acidic condition, room temperature",
            "outcome":     "Releases hydrazoic acid (HN₃) — extremely toxic and shock-sensitive explosive.",
            "hazard_rise": "EXTREME DANGER — lethal toxic explosive gas",
            "temp":        "Room temperature — no heating needed",
            "warning":     "🚨 NEVER combine. HN₃ is lethal and explosive. Evacuate immediately if accidental mixing occurs."
        },
        frozenset(["boric acid", "glycerol"]): {
            "type":        "Complexation / Ester Formation",
            "equation":    "B(OH)₃ + C₃H₈O₃ → glyceroborate complex + H₂O",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Forms glyceroborate complex. Used in gel electrophoresis TBE/TBG buffers.",
            "hazard_rise": "SAFE — no hazard increase",
            "temp":        "Room temperature",
            "warning":     "✅ Safe combination. Basis of standard gel electrophoresis buffer."
        },
        frozenset(["tris buffer", "hydrochloric acid"]): {
            "type":        "Buffer Preparation",
            "equation":    "Tris-base + HCl → Tris-HCl (buffered solution)",
            "conditions":  "Aqueous, room temperature, pH adjustment monitored",
            "outcome":     "Standard Tris-HCl buffer preparation used widely in molecular biology.",
            "hazard_rise": "WARNING (corrosive acid involved in preparation)",
            "temp":        "Room temperature",
            "warning":     "🔶 Add HCl slowly while monitoring pH with pH meter."
        },
        frozenset(["sodium azide", "sulfuric acid"]): {
            "type":        "Extremely Dangerous Acid-Azide Reaction",
            "equation":    "2NaN₃ + H₂SO₄ → Na₂SO₄ + 2HN₃↑",
            "conditions":  "Any acidic condition",
            "outcome":     "Releases hydrazoic acid — explosive and lethal in small concentrations.",
            "hazard_rise": "EXTREME DANGER — do not combine under any circumstances",
            "temp":        "Room temperature — spontaneous",
            "warning":     "🚨 NEVER combine. Immediately evacuate and contact hazmat if accidental contact."
        },
        frozenset(["phenol", "chloroform"]): {
            "type":        "Nucleic Acid Extraction Mixture",
            "equation":    "Physical partitioning — no covalent reaction",
            "conditions":  "Aqueous, room temperature, pH determines DNA vs RNA extraction",
            "outcome":     "Biphasic mixture used for DNA/RNA extraction. Nucleic acids partition to aqueous phase.",
            "hazard_rise": "DANGER — both compounds are toxic; combined exposure increases risk",
            "temp":        "Room temperature — use chilled if possible",
            "warning":     "⚠️ Both phenol and chloroform are highly toxic. Fume hood, face shield, double gloves mandatory."
        },
        frozenset(["acrylamide", "ammonium persulfate"]): {
            "type":        "Free Radical Polymerisation",
            "equation":    "n(CH₂=CHCONH₂) → [-CH₂-CH(CONH₂)-]ₙ (polyacrylamide)",
            "conditions":  "Aqueous, room temperature, TEMED as accelerator",
            "outcome":     "Forms polyacrylamide gel used in PAGE electrophoresis. Monomer is neurotoxic.",
            "hazard_rise": "DANGER (monomer) → WARNING (polymer — less toxic once polymerised)",
            "temp":        "Room temperature, exothermic polymerisation",
            "warning":     "⚠️ Acrylamide monomer is a neurotoxin and carcinogen. Avoid skin contact. Gloves mandatory."
        },
        frozenset(["acrylamide", "temed"]): {
            "type":        "Polymerisation Initiation",
            "equation":    "TEMED accelerates free radical generation from APS to polymerise acrylamide",
            "conditions":  "Aqueous, room temperature, requires ammonium persulfate",
            "outcome":     "TEMED accelerates polymerisation of acrylamide to polyacrylamide.",
            "hazard_rise": "DANGER — acrylamide monomer neurotoxic before polymerisation",
            "temp":        "Room temperature",
            "warning":     "⚠️ Handle acrylamide monomer with extreme caution. Double gloves recommended."
        },
        frozenset(["ammonium persulfate", "temed"]): {
            "type":        "Radical Initiation System",
            "equation":    "APS + TEMED → free radicals → initiates acrylamide polymerisation",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "APS/TEMED system generates free radicals that initiate polyacrylamide gel formation.",
            "hazard_rise": "WARNING — oxidant/amine mixture; avoid direct skin contact",
            "temp":        "Room temperature",
            "warning":     "🔶 Mix just before use — polymerisation begins immediately. Avoid inhaling APS dust."
        },
        frozenset(["hydrogen peroxide", "iron sulfate"]): {
            "type":        "Fenton Reaction",
            "equation":    "Fe²⁺ + H₂O₂ → Fe³⁺ + OH• + OH⁻",
            "conditions":  "Acidic aqueous solution (pH 3–4), room temperature",
            "outcome":     "Generates highly reactive hydroxyl radicals. Used in oxidative stress research.",
            "hazard_rise": "DANGER — hydroxyl radicals damage DNA, proteins, and lipids",
            "temp":        "Room temperature, exothermic",
            "warning":     "⚠️ Extremely reactive radicals generated. Perform in small volumes. Antioxidants nearby."
        },
        frozenset(["methanol", "sodium hydroxide"]): {
            "type":        "Methoxide Formation",
            "equation":    "CH₃OH + NaOH → CH₃ONa + H₂O",
            "conditions":  "Anhydrous conditions, elevated temperature",
            "outcome":     "Forms sodium methoxide — a very strong base and nucleophile.",
            "hazard_rise": "DANGER — sodium methoxide is highly flammable and reactive with water",
            "temp":        "Elevated temperature required",
            "warning":     "⚠️ Sodium methoxide reacts violently with water. Fire risk. Fume hood mandatory."
        },
        frozenset(["toluene", "sodium hydroxide"]): {
            "type":        "Limited Reaction / Physical Extraction",
            "equation":    "Minimal reaction — biphasic system",
            "conditions":  "Room temperature, two immiscible phases",
            "outcome":     "Toluene and NaOH form a biphasic system. Used in liquid-liquid extraction.",
            "hazard_rise": "DANGER — toluene is flammable and toxic",
            "temp":        "Room temperature",
            "warning":     "⚠️ Toluene vapours are flammable and neurotoxic. Fume hood mandatory."
        },
        frozenset(["ascorbic acid", "hydrogen peroxide"]): {
            "type":        "Antioxidant Oxidation",
            "equation":    "C₆H₈O₆ + H₂O₂ → C₆H₆O₆ + 2H₂O",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Ascorbic acid reduces hydrogen peroxide to water. Ascorbic acid is oxidised to dehydroascorbic acid.",
            "hazard_rise": "SAFE → WARNING (ascorbic acid quenches H₂O₂ activity)",
            "temp":        "Room temperature",
            "warning":     "✅ Ascorbic acid can be used to safely quench dilute H₂O₂ solutions."
        },
        frozenset(["dithiothreitol", "iodoacetamide"]): {
            "type":        "Thiol Alkylation — Proteomics Sample Prep",
            "equation":    "DTT-SH + ICH₂CONH₂ → DTT-S-CH₂CONH₂ + HI",
            "conditions":  "Aqueous, room temperature, pH 8.0, dark conditions",
            "outcome":     "DTT reduces disulfide bonds; iodoacetamide alkylates free thiols to prevent re-oxidation.",
            "hazard_rise": "WARNING — iodoacetamide is a known alkylating agent; avoid skin contact",
            "temp":        "Room temperature, protect from light",
            "warning":     "⚠️ Iodoacetamide is toxic and a potential carcinogen. Perform in dark, wear gloves."
        },
        frozenset(["edta", "calcium chloride"]): {
            "type":        "Metal Ion Chelation",
            "equation":    "EDTA⁴⁻ + Ca²⁺ → [Ca-EDTA]²⁻",
            "conditions":  "Aqueous, physiological pH, room temperature",
            "outcome":     "EDTA chelates calcium ions, removing them from solution. Used to inhibit calcium-dependent enzymes.",
            "hazard_rise": "SAFE — both compounds are low hazard individually and in combination",
            "temp":        "Room temperature",
            "warning":     "✅ Safe combination. EDTA is used routinely to chelate divalent cations in biological buffers."
        },
        frozenset(["edta", "magnesium chloride"]): {
            "type":        "Magnesium Ion Chelation",
            "equation":    "EDTA⁴⁻ + Mg²⁺ → [Mg-EDTA]²⁻",
            "conditions":  "Aqueous, neutral pH, room temperature",
            "outcome":     "EDTA chelates Mg²⁺, inhibiting Mg-dependent enzymes including DNA polymerases.",
            "hazard_rise": "SAFE — routine chelation in molecular biology",
            "temp":        "Room temperature",
            "warning":     "✅ Commonly used to stop enzymatic reactions in molecular biology (e.g. stop PCR, DNase)."
        },
        frozenset(["sodium dodecyl sulfate", "potassium chloride"]): {
            "type":        "SDS Precipitation",
            "equation":    "SDS⁻ + K⁺ → KDS precipitate↓",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Potassium dodecyl sulfate precipitates out of solution. Causes SDS-PAGE buffer to fail.",
            "hazard_rise": "WARNING — precipitation causes assay failure; not a toxic reaction",
            "temp":        "Room temperature; worsens at low temperature",
            "warning":     "🔶 Do not use KCl-based buffers with SDS. Substitute NaCl to avoid precipitation."
        },
        frozenset(["sodium dodecyl sulfate", "dithiothreitol"]): {
            "type":        "Protein Denaturation — SDS-PAGE Prep",
            "equation":    "DTT reduces disulfide bonds; SDS denatures and coats protein with negative charge",
            "conditions":  "Aqueous, 95–100°C heating (5 min), pH ~6.8",
            "outcome":     "Proteins fully denatured and separated by molecular weight in SDS-PAGE.",
            "hazard_rise": "WARNING — heated DTT releases volatile sulfur compounds",
            "temp":        "95–100°C for 5 minutes",
            "warning":     "⚠️ Heat in a closed tube. Open cap carefully after heating. DTT odour is strong."
        },
        frozenset(["urea", "dithiothreitol"]): {
            "type":        "Protein Denaturation for 2D Electrophoresis",
            "equation":    "Urea unfolds protein; DTT reduces disulfide bonds",
            "conditions":  "8M urea, 65mM DTT, room temperature",
            "outcome":     "Complete protein unfolding used in 2D-PAGE and proteomics sample preparation.",
            "hazard_rise": "WARNING — high urea concentrations irritating to skin/eyes",
            "temp":        "Room temperature — do not heat urea above 37°C (produces cyanate)",
            "warning":     "⚠️ Never heat urea solutions above 37°C — cyanate forms and carbamylates proteins."
        },
        frozenset(["urea", "heat"]): {
            "type":        "Urea Decomposition / Carbamylation Risk",
            "equation":    "H₂NCONH₂ → NH₃ + HNCO (isocyanic acid) at >37°C",
            "conditions":  "Aqueous, temperature >37°C",
            "outcome":     "Urea decomposes to ammonia and isocyanic acid which carbamylates proteins.",
            "hazard_rise": "WARNING — isocyanic acid modifies lysine residues on proteins irreversibly",
            "temp":        "Decomposition begins above 37°C",
            "warning":     "⚠️ Always prepare urea solutions fresh and use at room temperature only."
        },
        frozenset(["phenol", "chloroform", "isoamyl alcohol"]): {
            "type":        "PCI Nucleic Acid Extraction",
            "equation":    "Physical biphasic partitioning (25:24:1 ratio)",
            "conditions":  "Aqueous, room temperature, centrifugation required",
            "outcome":     "Standard PCI extraction separates nucleic acids (aqueous) from proteins (organic phase).",
            "hazard_rise": "DANGER — all three components are toxic; combined inhalation and skin exposure risk is high",
            "temp":        "Room temperature or 4°C",
            "warning":     "⚠️ Triple hazard combination. Fume hood, face shield, double gloves, and chemical-resistant apron required."
        },
        frozenset(["chloroform", "isoamyl alcohol"]): {
            "type":        "CIA Mixture — Protein Removal",
            "equation":    "Physical mixture — 24:1 chloroform:isoamyl alcohol",
            "conditions":  "Room temperature, used after phenol extraction",
            "outcome":     "Removes residual phenol from nucleic acid preparations. Isoamyl alcohol reduces foaming.",
            "hazard_rise": "DANGER — both are volatile and toxic",
            "temp":        "Room temperature, keep on ice",
            "warning":     "⚠️ Handle only in fume hood. Chloroform is a suspected carcinogen."
        },
        frozenset(["guanidine hcl", "beta-mercaptoethanol"]): {
            "type":        "Protein Denaturation / Reduction",
            "equation":    "GuHCl unfolds protein; BME reduces disulfide bonds",
            "conditions":  "6M GuHCl, 0.1M BME, pH 8.0, room temperature",
            "outcome":     "Complete protein denaturation and reduction. Used in protein refolding and purification.",
            "hazard_rise": "DANGER — beta-mercaptoethanol is highly toxic and has strong noxious odour",
            "temp":        "Room temperature",
            "warning":     "⚠️ BME is toxic by inhalation and skin absorption. Fume hood and double gloves mandatory."
        },
        frozenset(["sodium dodecyl sulfate", "ethanol"]): {
            "type":        "Detergent Precipitation",
            "equation":    "SDS precipitates in high ethanol concentrations",
            "conditions":  "High ethanol concentration (>70%), room temperature",
            "outcome":     "SDS precipitates out of solution. Causes assay interference and membrane disruption.",
            "hazard_rise": "WARNING — ethanol is flammable; SDS precipitation causes experimental failure",
            "temp":        "Room temperature; worse at low temperatures",
            "warning":     "🔶 Avoid mixing high concentrations of SDS with ethanol. SDS will precipitate and block pipettes."
        },
        frozenset(["trichloroacetic acid", "sodium hydroxide"]): {
            "type":        "Acid-Base Neutralisation",
            "equation":    "CCl₃COOH + NaOH → CCl₃COONa + H₂O",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Neutralisation of TCA. Used to adjust pH after TCA protein precipitation.",
            "hazard_rise": "DANGER during mixing — TCA is highly corrosive",
            "temp":        "Exothermic — add slowly",
            "warning":     "⚠️ TCA causes severe burns. Add NaOH very slowly. Ice bath recommended."
        },
        frozenset(["acetic acid", "hydrogen peroxide"]): {
            "type":        "Peracetic Acid Formation",
            "equation":    "CH₃COOH + H₂O₂ ⇌ CH₃COOOH + H₂O",
            "conditions":  "Room temperature, equilibrium reaction",
            "outcome":     "Produces peracetic acid — a potent disinfectant and oxidising agent.",
            "hazard_rise": "DANGER — peracetic acid is corrosive, oxidising, and explosive at high concentrations",
            "temp":        "Room temperature — spontaneous equilibrium",
            "warning":     "⚠️ Peracetic acid is highly corrosive and a strong oxidiser. Store and use in small volumes only."
        },
        frozenset(["sodium hypochlorite", "hydrochloric acid"]): {
            "type":        "Extremely Dangerous Chlorine Gas Generation",
            "equation":    "NaOCl + 2HCl → NaCl + H₂O + Cl₂↑",
            "conditions":  "Any acidic condition, room temperature",
            "outcome":     "Produces chlorine gas — toxic, corrosive, and potentially lethal.",
            "hazard_rise": "EXTREME DANGER — chlorine gas is a chemical warfare agent",
            "temp":        "Room temperature — spontaneous and immediate",
            "warning":     "🚨 NEVER combine bleach with any acid. Evacuate immediately if accidental mixing occurs. Call emergency services."
        },
        frozenset(["sodium hypochlorite", "ammonia"]): {
            "type":        "Extremely Dangerous Chloramine Formation",
            "equation":    "NaOCl + NH₃ → NH₂Cl + NaOH (chloramine)",
            "conditions":  "Room temperature, any concentration",
            "outcome":     "Forms toxic chloramine gases including monochloramine, dichloramine, and nitrogen trichloride.",
            "hazard_rise": "EXTREME DANGER — chloramines are toxic and cause respiratory damage",
            "temp":        "Room temperature — immediate reaction",
            "warning":     "🚨 NEVER combine bleach with ammonia or ammonium compounds. Evacuate area immediately."
        },
        frozenset(["sodium hypochlorite", "hydrogen peroxide"]): {
            "type":        "Oxidiser-Oxidiser Reaction",
            "equation":    "NaOCl + H₂O₂ → NaCl + H₂O + O₂↑",
            "conditions":  "Room temperature, aqueous",
            "outcome":     "Both are strong oxidisers. Oxygen gas evolves rapidly. Exothermic.",
            "hazard_rise": "DANGER — oxygen evolution, violent decomposition possible",
            "temp":        "Exothermic — can get hot rapidly",
            "warning":     "⚠️ Do not combine oxidisers. Violent oxygen evolution in sealed containers is explosive."
        },
        frozenset(["potassium hydroxide", "hydrochloric acid"]): {
            "type":        "Strong Acid-Base Neutralisation",
            "equation":    "KOH + HCl → KCl + H₂O",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Produces potassium chloride and water. Highly exothermic.",
            "hazard_rise": "EXTREME DANGER during mixing → SAFE after neutralisation",
            "temp":        "Highly exothermic — can splatter if concentrated",
            "warning":     "⚠️ Add acid to base slowly with stirring. Use ice bath if concentrated. Full PPE required."
        },
        frozenset(["methanol", "hydrogen peroxide"]): {
            "type":        "Oxidation Reaction",
            "equation":    "CH₃OH + H₂O₂ → HCHO + 2H₂O",
            "conditions":  "Room temperature, may require catalyst",
            "outcome":     "Methanol oxidised to formaldehyde — a carcinogen and respiratory irritant.",
            "hazard_rise": "DANGER — formaldehyde vapour produced; both reactants are toxic",
            "temp":        "Room temperature",
            "warning":     "⚠️ Formaldehyde generation. Fume hood mandatory. Do not inhale."
        },
        frozenset(["dimethylformamide", "sodium hydroxide"]): {
            "type":        "Hydrolysis",
            "equation":    "HCON(CH₃)₂ + NaOH + H₂O → HCOONa + (CH₃)₂NH",
            "conditions":  "Aqueous alkaline conditions, elevated temperature",
            "outcome":     "DMF hydrolyses to sodium formate and dimethylamine.",
            "hazard_rise": "DANGER — dimethylamine is toxic and flammable; DMF itself is a reproductive toxin",
            "temp":        "Accelerated at elevated temperature",
            "warning":     "⚠️ DMF is a reproductive toxin. Fume hood mandatory. Pregnant individuals must not handle."
        },
        frozenset(["phosphoric acid", "sodium hydroxide"]): {
            "type":        "Phosphate Buffer Preparation",
            "equation":    "H₃PO₄ + NaOH → NaH₂PO₄ / Na₂HPO₄ / Na₃PO₄ (depending on ratio)",
            "conditions":  "Aqueous, room temperature, pH monitored",
            "outcome":     "Produces phosphate buffer. Ratio of acid to base determines pH of resulting buffer.",
            "hazard_rise": "WARNING during preparation — corrosive acid involved",
            "temp":        "Mildly exothermic",
            "warning":     "🔶 Add NaOH slowly to acid while monitoring pH. Standard phosphate buffer preparation."
        },
        frozenset(["lactic acid", "sodium hydroxide"]): {
            "type":        "Lactate Buffer Preparation",
            "equation":    "CH₃CH(OH)COOH + NaOH → CH₃CH(OH)COONa + H₂O",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Produces sodium lactate buffer. Used in pharmaceutical and cell culture applications.",
            "hazard_rise": "SAFE — both compounds are low hazard",
            "temp":        "Room temperature",
            "warning":     "✅ Safe buffer preparation. Standard procedure in pharmaceutical formulation."
        },
        frozenset(["imidazole", "hydrochloric acid"]): {
            "type":        "Imidazole Buffer Preparation",
            "equation":    "C₃H₄N₂ + HCl → C₃H₅N₂⁺Cl⁻ (imidazolium chloride)",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Produces imidazole-HCl buffer used in His-tag protein elution from Ni-NTA columns.",
            "hazard_rise": "WARNING — corrosive acid involved",
            "temp":        "Room temperature",
            "warning":     "🔶 Add HCl carefully. Imidazole buffer is standard in protein purification workflows."
        },
        frozenset(["hepes", "sodium hydroxide"]): {
            "type":        "HEPES Buffer Preparation",
            "equation":    "HEPES (free acid) + NaOH → HEPES-Na buffer at pH 7.0–7.6",
            "conditions":  "Aqueous, room temperature, pH 7.0–7.6",
            "outcome":     "Standard HEPES buffer used in cell culture. pH adjusted with NaOH.",
            "hazard_rise": "SAFE — routine buffer preparation",
            "temp":        "Room temperature",
            "warning":     "✅ Very common cell culture buffer preparation. Safe under standard conditions."
        },
        frozenset(["tris buffer", "acetic acid"]): {
            "type":        "TAE Buffer Preparation",
            "equation":    "Tris + acetic acid + EDTA → TAE buffer",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Produces Tris-Acetate-EDTA (TAE) buffer — the most common buffer for agarose gel electrophoresis.",
            "hazard_rise": "SAFE — standard electrophoresis buffer",
            "temp":        "Room temperature",
            "warning":     "✅ TAE is a standard molecular biology buffer. Safe routine preparation."
        },
        frozenset(["tris buffer", "boric acid"]): {
            "type":        "TBE Buffer Preparation",
            "equation":    "Tris + boric acid + EDTA → TBE buffer",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Produces Tris-Borate-EDTA (TBE) buffer used in gel electrophoresis for small DNA fragments.",
            "hazard_rise": "SAFE — standard electrophoresis buffer",
            "temp":        "Room temperature",
            "warning":     "✅ TBE is widely used in molecular biology. Boric acid is mildly toxic — avoid ingestion."
        },
        frozenset(["silver nitrate", "sodium chloride"]): {
            "type":        "Precipitation Reaction",
            "equation":    "AgNO₃ + NaCl → AgCl↓ + NaNO₃",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "White silver chloride precipitate forms immediately. Used in chloride detection assays.",
            "hazard_rise": "WARNING — silver nitrate stains skin and surfaces permanently",
            "temp":        "Room temperature — immediate precipitation",
            "warning":     "🔶 Silver nitrate stains skin black. Wear gloves. AgCl precipitate is light-sensitive."
        },
        frozenset(["copper sulfate", "ammonium hydroxide"]): {
            "type":        "Complex Formation — Biuret Assay",
            "equation":    "CuSO₄ + 4NH₃ → [Cu(NH₃)₄]SO₄ (tetraamminecopper complex)",
            "conditions":  "Alkaline aqueous conditions, room temperature",
            "outcome":     "Deep blue tetraamminecopper(II) complex forms. Basis of protein detection assays.",
            "hazard_rise": "WARNING — ammonia vapours released",
            "temp":        "Room temperature",
            "warning":     "🔶 Ammonia vapours are irritating. Work in fume hood. Classic Biuret protein assay reaction."
        },
        frozenset(["glucose", "copper sulfate"]): {
            "type":        "Benedict's / Fehling's Test",
            "equation":    "glucose + 2Cu²⁺ + 5OH⁻ → Cu₂O↓ + gluconate + 3H₂O",
            "conditions":  "Alkaline aqueous (pH ~10), heated to 100°C",
            "outcome":     "Glucose reduces Cu²⁺ to Cu⁺ forming brick-red Cu₂O precipitate. Classic reducing sugar test.",
            "hazard_rise": "WARNING — hot alkaline solution, copper waste",
            "temp":        "100°C (boiling water bath, 5 minutes)",
            "warning":     "🔶 Handle hot solution carefully. Dispose of copper precipitate as hazardous waste."
        },
        frozenset(["potassium iodide", "sodium hypochlorite"]): {
            "type":        "Oxidation of Iodide to Iodine",
            "equation":    "2KI + NaOCl + H₂O → I₂ + 2KOH + NaCl",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Iodine is liberated from iodide. Brown-yellow colour develops. Used in iodometric titrations.",
            "hazard_rise": "WARNING — iodine vapours are irritating; hypochlorite is corrosive",
            "temp":        "Room temperature",
            "warning":     "🔶 Iodine stains. Perform in fume hood. Neutralise with sodium thiosulfate."
        },
        frozenset(["ascorbic acid", "iron sulfate"]): {
            "type":        "Iron Reduction / Antioxidant Assay",
            "equation":    "Fe³⁺ + ascorbic acid → Fe²⁺ + dehydroascorbic acid",
            "conditions":  "Acidic aqueous, room temperature",
            "outcome":     "Ascorbic acid reduces Fe³⁺ to Fe²⁺. Basis of FRAP antioxidant assay.",
            "hazard_rise": "SAFE — both are low hazard at typical lab concentrations",
            "temp":        "Room temperature",
            "warning":     "✅ Safe antioxidant assay reaction. Standard in food and pharmaceutical analysis."
        },
        frozenset(["sodium bicarbonate", "hydrochloric acid"]): {
            "type":        "Acid-Carbonate Effervescence",
            "equation":    "NaHCO₃ + HCl → NaCl + H₂O + CO₂↑",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Vigorous CO₂ evolution. Used to neutralise acid spills and in buffer preparation.",
            "hazard_rise": "WARNING during mixing (corrosive acid) → SAFE after neutralisation",
            "temp":        "Room temperature — rapid effervescence",
            "warning":     "🔶 Add slowly to avoid violent foaming. Useful for neutralising acid spills in lab."
        },
        frozenset(["sodium carbonate", "hydrochloric acid"]): {
            "type":        "Acid-Carbonate Effervescence",
            "equation":    "Na₂CO₃ + 2HCl → 2NaCl + H₂O + CO₂↑",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "CO₂ evolution and salt formation. Used in pH adjustment and titrations.",
            "hazard_rise": "WARNING — corrosive acid; neutralised product is safe",
            "temp":        "Room temperature",
            "warning":     "🔶 Add acid to carbonate slowly to control CO₂ evolution rate."
        },
        frozenset(["lithium chloride", "ethanol"]): {
            "type":        "RNA Precipitation",
            "equation":    "LiCl + RNA → LiCl-RNA precipitate (physical interaction)",
            "conditions":  "Cold temperature (−20°C), aqueous/ethanol mixture",
            "outcome":     "LiCl selectively precipitates RNA without co-precipitating DNA or proteins.",
            "hazard_rise": "WARNING — ethanol is flammable",
            "temp":        "−20°C overnight for best yield",
            "warning":     "🔶 Flammable ethanol. Keep away from ignition. Standard RNA precipitation procedure."
        },
        frozenset(["isopropanol", "sodium chloride"]): {
            "type":        "Nucleic Acid Precipitation",
            "equation":    "DNA/RNA + NaCl + isopropanol → nucleic acid pellet (physical process)",
            "conditions":  "Cold temperature, centrifugation required",
            "outcome":     "NaCl neutralises phosphate backbone charge; isopropanol precipitates nucleic acids.",
            "hazard_rise": "WARNING — isopropanol is flammable",
            "temp":        "−20°C or room temperature (isopropanol precipitates faster than ethanol)",
            "warning":     "🔶 Flammable solvent. Standard molecular biology nucleic acid precipitation."
        },
        frozenset(["glutaraldehyde", "sodium hydroxide"]): {
            "type":        "Aldol Condensation / Polymerisation",
            "equation":    "OHC-(CH₂)₃-CHO + NaOH → aldol condensation polymers",
            "conditions":  "Alkaline conditions, room temperature",
            "outcome":     "Glutaraldehyde polymerises rapidly in alkaline conditions. Used in crosslinking chemistry.",
            "hazard_rise": "DANGER — glutaraldehyde is a potent sensitiser and respiratory hazard",
            "temp":        "Room temperature — polymerisation is rapid",
            "warning":     "⚠️ Glutaraldehyde vapours cause asthma and sensitisation. Fume hood and gloves mandatory."
        },
        frozenset(["propidium iodide", "ethanol"]): {
            "type":        "Cell Permeabilisation for Flow Cytometry",
            "equation":    "Physical process — ethanol permeabilises cell membranes allowing PI entry",
            "conditions":  "70% ethanol fixation, then PI staining in aqueous buffer",
            "outcome":     "Fixed and permeabilised cells stain with PI for DNA content analysis by flow cytometry.",
            "hazard_rise": "DANGER — propidium iodide is mutagenic; ethanol is flammable",
            "temp":        "4°C for ethanol fixation; room temperature for PI staining",
            "warning":     "⚠️ PI is a mutagen. Avoid skin contact. Dispose as biohazardous waste."
        },
        frozenset(["ethidium bromide", "agarose"]): {
            "type":        "DNA Staining in Gel Electrophoresis",
            "equation":    "EtBr intercalates between DNA base pairs by π-stacking",
            "conditions":  "Dissolved in molten agarose (~50°C) or in running buffer",
            "outcome":     "DNA bands fluoresce orange-red under UV light. Standard DNA visualisation method.",
            "hazard_rise": "DANGER — ethidium bromide is a potent mutagen and intercalating agent",
            "temp":        "Added to agarose at ~50°C or post-gel staining",
            "warning":     "⚠️ EtBr is mutagenic. Wear gloves at all times. Dispose as hazardous waste. Consider SYBR Safe as safer alternative."
        },
        frozenset(["sodium azide", "water"]): {
            "type":        "Dissolution / Hydrolysis",
            "equation":    "NaN₃ (s) + H₂O → Na⁺ + N₃⁻ (aq)",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Sodium azide dissolves completely. The azide anion (N₃⁻) is highly toxic.",
            "hazard_rise": "DANGER — aqueous azide solutions are acutely toxic",
            "temp":        "Room temperature",
            "warning":     "⚠️ Even dilute azide solutions are toxic. Do not pipette by mouth. Dispose as chemical waste — never pour down metal drains (explosive metal azides may form)."
        },
        frozenset(["beta-mercaptoethanol", "sodium hydroxide"]): {
            "type":        "Thiolate Formation",
            "equation":    "HOCH₂CH₂SH + NaOH → HOCH₂CH₂S⁻Na⁺ + H₂O",
            "conditions":  "Aqueous alkaline conditions, room temperature",
            "outcome":     "Beta-mercaptoethanol deprotonated to thiolate — a stronger nucleophile and reducing agent.",
            "hazard_rise": "DANGER — BME is toxic and extremely malodorous; thiolate is more reactive",
            "temp":        "Room temperature",
            "warning":     "⚠️ BME is toxic by inhalation and absorbed through skin. Fume hood is non-negotiable."
        },
        frozenset(["saponin", "cholesterol"]): {
            "type":        "Membrane Permeabilisation",
            "equation":    "Saponin + membrane cholesterol → membrane pores (physical interaction)",
            "conditions":  "Aqueous buffer, room temperature, 0.1–1% saponin",
            "outcome":     "Saponin complexes with cholesterol in cell membranes creating pores for intracellular staining.",
            "hazard_rise": "WARNING — saponin is haemolytic at high concentrations",
            "temp":        "Room temperature",
            "warning":     "🔶 Use at low concentrations. Saponin is reversible unlike detergents. Rinse cells after staining."
        },
        frozenset(["magnesium chloride", "sodium hydroxide"]): {
            "type":        "Precipitation Reaction",
            "equation":    "MgCl₂ + 2NaOH → Mg(OH)₂↓ + 2NaCl",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "White magnesium hydroxide precipitate forms. Interferes with Mg-dependent enzyme assays.",
            "hazard_rise": "WARNING — concentrated NaOH is corrosive",
            "temp":        "Room temperature",
            "warning":     "🔶 Avoid in enzyme assay buffers. Mg(OH)₂ precipitate can be redissolved by acidification."
        },
        frozenset(["calcium chloride", "sodium phosphate"]): {
            "type":        "Calcium Phosphate Precipitation / Transfection",
            "equation":    "3CaCl₂ + 2Na₃PO₄ → Ca₃(PO₄)₂↓ + 6NaCl",
            "conditions":  "Aqueous, physiological pH, slow mixing",
            "outcome":     "Calcium phosphate precipitate forms co-precipitating DNA. Basis of calcium phosphate transfection.",
            "hazard_rise": "SAFE — routine transfection procedure",
            "temp":        "Room temperature — mix gently and slowly for best precipitate",
            "warning":     "✅ Standard calcium phosphate transfection method. Safe for routine cell biology use."
        },
        frozenset(["mannitol", "heat"]): {
            "type":        "Thermal Crystallisation / Polymorphic Transition",
            "equation":    "Mannitol (amorphous) → Mannitol (crystalline) upon heating",
            "conditions":  "Lyophilisation or spray drying, 60–100°C",
            "outcome":     "Mannitol undergoes polymorphic transitions during freeze-drying. Can cause vial cracking if uncontrolled.",
            "hazard_rise": "INFO — not a safety hazard but critical for formulation stability",
            "temp":        "Crystallisation onset ~60°C; avoid >100°C",
            "warning":     "🔶 Control cooling rate during lyophilisation. Use annealing step to ensure consistent polymorph."
        },
        frozenset(["sucrose", "heat"]): {
            "type":        "Caramelisation / Maillard Degradation",
            "equation":    "C₁₂H₂₂O₁₁ → caramel polymers + HMF + CO₂ (>160°C)",
            "conditions":  "Dry heat or aqueous above 160°C",
            "outcome":     "Sucrose decomposes to fructose and glucose, then further to caramel. In biologics, causes protein glycation.",
            "hazard_rise": "WARNING — HMF (hydroxymethylfurfural) formed is a potential carcinogen",
            "temp":        "160°C dry; lower in acidic aqueous conditions",
            "warning":     "⚠️ Avoid autoclaving sucrose solutions with proteins — causes glycation. Filter-sterilise instead."
        },
        frozenset(["polysorbate 80", "heat"]): {
            "type":        "Oxidative Degradation / Peroxide Formation",
            "equation":    "Polysorbate 80 + O₂ → fatty acid peroxides + aldehydes",
            "conditions":  "Elevated temperature, light exposure, trace metal catalysis",
            "outcome":     "Peroxides form and degrade protein therapeutics. Major concern in biopharmaceutical formulations.",
            "hazard_rise": "DANGER — peroxides oxidise methionine and tryptophan residues in proteins",
            "temp":        "Accelerated above 40°C; occurs at room temperature over time",
            "warning":     "⚠️ Store polysorbate solutions cold and dark. Use antioxidants (methionine, EDTA) in formulations."
        },
        frozenset(["polysorbate 80", "bovine serum albumin"]): {
            "type":        "Protein-Surfactant Interaction",
            "equation":    "BSA + Polysorbate 80 → BSA-surfactant complex (hydrophobic interaction)",
            "conditions":  "Aqueous, physiological pH, room temperature",
            "outcome":     "Polysorbate 80 binds hydrophobic patches on BSA preventing aggregation at interfaces.",
            "hazard_rise": "SAFE — protective interaction used in biopharmaceutical formulations",
            "temp":        "Room temperature",
            "warning":     "✅ Used intentionally to stabilise protein formulations. Concentration must be optimised."
        },
        frozenset(["bovine serum albumin", "heat"]): {
            "type":        "Protein Thermal Denaturation / Aggregation",
            "equation":    "BSA (native) → BSA (unfolded) → BSA aggregates (>65°C)",
            "conditions":  "Aqueous, temperature >65°C, depends on pH and ionic strength",
            "outcome":     "BSA denatures and aggregates irreversibly above 65°C. Used as model protein in aggregation studies.",
            "hazard_rise": "INFO — not a direct safety hazard but ruins experimental samples",
            "temp":        "Tm ~65°C; aggregation accelerates above 70°C",
            "warning":     "🔶 Never autoclave BSA solutions. Heat inactivation at 56°C for 30 min is safe for virus inactivation."
        },
        frozenset(["ascorbic acid", "sodium bicarbonate"]): {
            "type":        "Acid-Carbonate Effervescence",
            "equation":    "C₆H₈O₆ + NaHCO₃ → NaC₆H₇O₆ + H₂O + CO₂↑",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "CO₂ evolution and sodium ascorbate formation. Basis of effervescent vitamin C tablets.",
            "hazard_rise": "SAFE — common pharmaceutical formulation reaction",
            "temp":        "Room temperature",
            "warning":     "✅ Safe effervescent reaction. Sodium ascorbate is a mild antioxidant buffer."
        },
        frozenset(["glycerol", "sodium hydroxide"]): {
            "type":        "Glycerate Formation / Saponification",
            "equation":    "C₃H₈O₃ + NaOH → sodium glycerate + H₂O",
            "conditions":  "Concentrated NaOH, elevated temperature",
            "outcome":     "Glycerol reacts slowly with NaOH at high concentrations and temperature.",
            "hazard_rise": "WARNING — concentrated NaOH is corrosive",
            "temp":        "Slow at room temperature; accelerated above 60°C",
            "warning":     "🔶 Dilute glycerol solutions are safe with dilute NaOH. Only significant at high concentrations."
        },
        frozenset(["dextrose", "amino acid"]): {
            "type":        "Maillard Reaction",
            "equation":    "Reducing sugar + amino group → Amadori products → brown melanoidins",
            "conditions":  "Heat (>40°C), low moisture, alkaline pH accelerates",
            "outcome":     "Brown discolouration and loss of amino acid bioavailability. Critical in parenteral nutrition bags.",
            "hazard_rise": "WARNING — Maillard products can be toxic at high levels; compromises drug potency",
            "temp":        "Onset at 40°C; rapid above 100°C",
            "warning":     "⚠️ Never mix amino acids with dextrose in parenteral nutrition without immediate administration. Store separately."
        },
        frozenset(["calcium chloride", "sodium bicarbonate"]): {
            "type":        "Precipitation — Calcium Carbonate Formation",
            "equation":    "CaCl₂ + 2NaHCO₃ → CaCO₃↓ + 2NaCl + H₂O + CO₂↑",
            "conditions":  "Aqueous, room temperature, neutral to alkaline pH",
            "outcome":     "Calcium carbonate precipitate forms. Causes IV line blockage in clinical settings.",
            "hazard_rise": "WARNING — precipitation in IV lines is a clinical emergency",
            "temp":        "Room temperature — spontaneous",
            "warning":     "⚠️ Never co-administer calcium and bicarbonate via same IV line. Fatal precipitate can form."
        },
        frozenset(["calcium chloride", "phosphoric acid"]): {
            "type":        "Calcium Phosphate Precipitation",
            "equation":    "3CaCl₂ + 2H₃PO₄ → Ca₃(PO₄)₂↓ + 6HCl",
            "conditions":  "Aqueous, neutral to alkaline pH",
            "outcome":     "Insoluble calcium phosphate precipitate. Critical incompatibility in IV formulations.",
            "hazard_rise": "DANGER — IV precipitate causes pulmonary embolism",
            "temp":        "Room temperature; worsened at body temperature",
            "warning":     "🚨 Known cause of patient deaths in IV nutrition. Never combine calcium and phosphate in concentrated solutions."
        },
        frozenset(["ampicillin", "glucose"]): {
            "type":        "Antibiotic Degradation",
            "equation":    "Ampicillin + glucose → Amadori products + degraded ampicillin",
            "conditions":  "Aqueous, room temperature; accelerated at 37°C",
            "outcome":     "Glucose accelerates ampicillin degradation reducing antibiotic potency.",
            "hazard_rise": "WARNING — loss of antibiotic activity",
            "temp":        "Significant at 37°C over 6 hours",
            "warning":     "⚠️ Do not co-administer ampicillin in glucose infusion bags. Use saline instead."
        },
        frozenset(["ampicillin", "hydrochloric acid"]): {
            "type":        "Acid Hydrolysis of Beta-Lactam",
            "equation":    "Ampicillin + H⁺ → ampicillin degradation products (penicilloic acid)",
            "conditions":  "Acidic aqueous (pH < 4), room temperature",
            "outcome":     "Beta-lactam ring opens irreversibly. Complete loss of antibacterial activity.",
            "hazard_rise": "WARNING — inactivated antibiotic; degradation products may cause allergic reactions",
            "temp":        "Room temperature; faster at elevated temperature",
            "warning":     "⚠️ Maintain ampicillin solutions at pH 6–7. Prepare fresh and use within 1 hour."
        },
        frozenset(["tetracycline", "calcium chloride"]): {
            "type":        "Metal Chelation — Antibiotic Inactivation",
            "equation":    "Tetracycline + Ca²⁺ → tetracycline-Ca²⁺ chelate (inactive)",
            "conditions":  "Aqueous, physiological pH, room temperature",
            "outcome":     "Calcium chelates tetracycline forming insoluble inactive complex. Explains milk-antibiotic interaction.",
            "hazard_rise": "WARNING — loss of antibiotic activity",
            "temp":        "Room temperature",
            "warning":     "⚠️ Do not administer tetracycline with calcium-containing products. Separate by at least 2 hours."
        },
        frozenset(["tetracycline", "magnesium chloride"]): {
            "type":        "Metal Chelation — Antibiotic Chelation",
            "equation":    "Tetracycline + Mg²⁺ → tetracycline-Mg²⁺ chelate",
            "conditions":  "Aqueous, physiological pH",
            "outcome":     "Magnesium chelates and inactivates tetracycline. Same mechanism as calcium interaction.",
            "hazard_rise": "WARNING — antibiotic inactivation",
            "temp":        "Room temperature",
            "warning":     "⚠️ Avoid Mg²⁺-containing antacids with tetracycline. Classic drug-mineral interaction."
        },
        frozenset(["kanamycin", "calcium chloride"]): {
            "type":        "Aminoglycoside-Cation Interaction",
            "equation":    "Kanamycin + Ca²⁺ → reduced antibiotic uptake (membrane interaction)",
            "conditions":  "Aqueous, physiological conditions",
            "outcome":     "Divalent cations compete with aminoglycosides for binding to bacterial membrane. Reduces efficacy.",
            "hazard_rise": "WARNING — reduced antibiotic efficacy",
            "temp":        "Physiological temperature",
            "warning":     "🔶 Avoid high Ca²⁺ concentrations in kanamycin selection media."
        },
        frozenset(["sodium dodecyl sulfate", "potassium chloride"]): {
            "type":        "SDS-K⁺ Precipitation",
            "equation":    "SDS⁻ + K⁺ → KDS precipitate↓",
            "conditions":  "Aqueous, room temperature; worse at low temperature",
            "outcome":     "Potassium dodecyl sulfate is poorly soluble — precipitates immediately.",
            "hazard_rise": "WARNING — assay failure; not a toxic reaction",
            "temp":        "Room temperature; worse at 4°C",
            "warning":     "🔶 Never use KCl-based buffers with SDS. Use NaCl or LiCl instead."
        },
        frozenset(["hepes", "copper sulfate"]): {
            "type":        "Metal Chelation Interference",
            "equation":    "HEPES + Cu²⁺ → HEPES-Cu²⁺ complex",
            "conditions":  "Aqueous, physiological pH",
            "outcome":     "HEPES chelates copper ions causing false results in copper-dependent enzyme assays.",
            "hazard_rise": "INFO — experimental interference rather than safety hazard",
            "temp":        "Room temperature",
            "warning":     "🔶 Do not use HEPES in copper-dependent assays. Use non-chelating buffers like MOPS instead."
        },
        frozenset(["tris buffer", "copper sulfate"]): {
            "type":        "Metal Chelation / Biuret Interference",
            "equation":    "Tris + Cu²⁺ → Tris-Cu²⁺ complex (interfering complex)",
            "conditions":  "Aqueous, alkaline pH, room temperature",
            "outcome":     "Tris chelates copper interfering with Biuret and Bradford protein assays.",
            "hazard_rise": "INFO — assay interference",
            "temp":        "Room temperature",
            "warning":     "🔶 Tris is incompatible with copper-based protein assays. Remove Tris before assay or use BCA assay instead."
        },
        frozenset(["edta", "magnesium chloride"]): {
            "type":        "Magnesium Chelation",
            "equation":    "EDTA⁴⁻ + Mg²⁺ → [Mg-EDTA]²⁻",
            "conditions":  "Aqueous, neutral pH, room temperature",
            "outcome":     "EDTA sequesters Mg²⁺ inhibiting all Mg-dependent enzymes including DNA polymerases and restriction enzymes.",
            "hazard_rise": "SAFE — intentional inhibition in stop solutions",
            "temp":        "Room temperature",
            "warning":     "✅ Used deliberately to stop restriction digests and PCR reactions. Add Mg²⁺ to overcome inhibition."
        },
        frozenset(["sodium chloride", "silver nitrate"]): {
            "type":        "Halide Precipitation Test",
            "equation":    "NaCl + AgNO₃ → AgCl↓ + NaNO₃",
            "conditions":  "Aqueous, room temperature, acidic conditions prevent carbonate interference",
            "outcome":     "White curdy AgCl precipitate — confirmatory test for chloride ions.",
            "hazard_rise": "WARNING — silver nitrate stains permanently",
            "temp":        "Room temperature",
            "warning":     "🔶 Wear gloves — silver nitrate stains skin black for days. AgCl is light-sensitive."
        },
        frozenset(["folic acid", "sodium hydroxide"]): {
            "type":        "Dissolution / Salt Formation",
            "equation":    "Folic acid + NaOH → sodium folate + H₂O",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Folic acid dissolves in alkaline conditions forming sodium folate — more water soluble.",
            "hazard_rise": "SAFE — standard pharmaceutical dissolution technique",
            "temp":        "Room temperature",
            "warning":     "✅ Standard method to dissolve folic acid for cell culture media preparation."
        },
        frozenset(["dithiothreitol", "oxygen"]): {
            "type":        "DTT Oxidation / Inactivation",
            "equation":    "2DTT-SH + O₂ → DTT-S-S-DTT + H₂O₂",
            "conditions":  "Aqueous, pH > 7, exposure to air",
            "outcome":     "DTT is oxidised by oxygen losing reducing activity. H₂O₂ generated can damage proteins.",
            "hazard_rise": "WARNING — H₂O₂ byproduct oxidises sensitive proteins",
            "temp":        "Room temperature; faster at alkaline pH",
            "warning":     "⚠️ Prepare DTT solutions fresh. Store under nitrogen or argon if possible. Use within 24 hours."
        },
        frozenset(["imidazole", "copper sulfate"]): {
            "type":        "Copper-Imidazole Complex Formation",
            "equation":    "Cu²⁺ + 4 imidazole → [Cu(imidazole)₄]²⁺",
            "conditions":  "Aqueous, neutral to alkaline pH",
            "outcome":     "Deep blue copper-imidazole complex. Interferes with His-tag protein purification.",
            "hazard_rise": "WARNING — interferes with Ni-NTA column if copper contamination present",
            "temp":        "Room temperature",
            "warning":     "🔶 Use high-purity imidazole for His-tag purification. Copper contamination ruins columns."
        },
        frozenset(["guanidine hcl", "sodium hydroxide"]): {
            "type":        "Denaturant Buffer pH Adjustment",
            "equation":    "GuHCl (acidic) + NaOH → pH-adjusted GuHCl solution",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "NaOH adjusts pH of GuHCl denaturation buffer for protein refolding dialysis.",
            "hazard_rise": "WARNING — corrosive base; GuHCl is a strong denaturant",
            "temp":        "Room temperature",
            "warning":     "⚠️ GuHCl solutions are very dense — difficult to pipette accurately. Use calibrated pH meter."
        },
        frozenset(["phenol red", "sodium hydroxide"]): {
            "type":        "pH Indicator Colour Change",
            "equation":    "Phenol red (yellow, pH<6.8) ⇌ Phenol red (red, pH 6.8–8.4) ⇌ purple (pH>8.4)",
            "conditions":  "Aqueous, any concentration, room temperature",
            "outcome":     "Phenol red undergoes colour transition indicating pH change — monitors CO₂ and metabolic activity in cell culture.",
            "hazard_rise": "SAFE — indicator dye reaction",
            "temp":        "Room temperature; reversible",
            "warning":     "✅ Safe. Yellow phenol red in cell culture indicates acidification from CO₂ or metabolic activity."
        },
        frozenset(["methylene blue", "ascorbic acid"]): {
            "type":        "Redox Indicator Reduction",
            "equation":    "Methylene blue (blue, oxidised) + ascorbic acid → leucomethylene blue (colourless, reduced)",
            "conditions":  "Aqueous, room temperature, anaerobic conditions",
            "outcome":     "Methylene blue is reduced to colourless leucomethylene blue. Reversible in presence of oxygen.",
            "hazard_rise": "SAFE — used in redox assays and cell viability studies",
            "temp":        "Room temperature",
            "warning":     "✅ Classic redox reaction used in biology demonstrations and anaerobic detection."
        },
        frozenset(["bromophenol blue", "sodium hydroxide"]): {
            "type":        "pH-Dependent Colour Change",
            "equation":    "BPB (yellow, acidic) + NaOH → BPB (blue, alkaline)",
            "conditions":  "Aqueous, room temperature",
            "outcome":     "Bromophenol blue turns from yellow to blue in alkaline conditions. Used to monitor gel loading.",
            "hazard_rise": "SAFE — pH indicator reaction",
            "temp":        "Room temperature",
            "warning":     "✅ Used as tracking dye in gel electrophoresis. Blue colour indicates alkaline pH."
        },
        frozenset(["saponin", "sodium hydroxide"]): {
            "type":        "Saponin Hydrolysis",
            "equation":    "Saponin + NaOH + H₂O → sapogenin + sugar residues",
            "conditions":  "Alkaline aqueous, elevated temperature",
            "outcome":     "Glycosidic bonds in saponin hydrolysed releasing aglycone (sapogenin) and sugar units.",
            "hazard_rise": "WARNING — NaOH is corrosive; sapogenin may irritate skin",
            "temp":        "Requires heating ~80°C",
            "warning":     "🔶 Saponins are haemolytic. Handle with gloves. Do not inhale fine powder."
        },
        frozenset(["toluene", "sulfuric acid"]): {
            "type":        "Sulfonation / Electrophilic Aromatic Substitution",
            "equation":    "C₆H₅CH₃ + H₂SO₄ → CH₃C₆H₄SO₃H + H₂O",
            "conditions":  "Fuming sulfuric acid, elevated temperature, 100°C+",
            "outcome":     "Produces toluenesulfonic acid. Industrial sulfonation reaction.",
            "hazard_rise": "EXTREME DANGER — fuming sulfuric acid and flammable toluene",
            "temp":        "100°C+ with fuming H₂SO₄",
            "warning":     "🚨 Extremely hazardous. Industrial process only. Produces toxic fumes. Never attempt at bench scale without specialist equipment."
        },
        frozenset(["acetone", "chloroform"]): {
            "type":        "Protein Precipitation (Acetone-Chloroform Method)",
            "equation":    "Physical precipitation — no covalent reaction",
            "conditions":  "Cold temperature (−20°C), 4:1 methanol:chloroform:water ratio typically used",
            "outcome":     "Proteins precipitate at interface between chloroform and aqueous layers. Removes lipids and detergents.",
            "hazard_rise": "DANGER — both solvents are toxic and flammable",
            "temp":        "−20°C for optimal precipitation",
            "warning":     "⚠️ Both flammable and toxic. Fume hood mandatory. No ignition sources."
        },
        frozenset(["acetone", "sodium hydroxide"]): {
            "type":        "Aldol Condensation",
            "equation":    "2CH₃COCH₃ + NaOH → CH₃COCH₂C(OH)(CH₃)₂ (diacetone alcohol)",
            "conditions":  "Aqueous NaOH, room temperature to mild heating",
            "outcome":     "Produces diacetone alcohol via base-catalysed aldol condensation.",
            "hazard_rise": "WARNING — flammable acetone vapours; NaOH is corrosive",
            "temp":        "Room temperature; mild heating accelerates",
            "warning":     "⚠️ Flammable vapours. No ignition sources. Fume hood required."
        },
        frozenset(["copper sulfate", "edta"]): {
            "type":        "Copper Chelation",
            "equation":    "Cu²⁺ + EDTA⁴⁻ → [Cu-EDTA]²⁻",
            "conditions":  "Aqueous, neutral to alkaline pH",
            "outcome":     "EDTA strongly chelates copper ions. Used to remove copper from solutions and inhibit copper-catalysed oxidation.",
            "hazard_rise": "SAFE — used intentionally to prevent copper-catalysed degradation",
            "temp":        "Room temperature",
            "warning":     "✅ Adding EDTA to polysorbate formulations prevents copper-catalysed peroxidation of proteins."
        },
        frozenset(["sodium chloride", "ethanol"]): {
            "type":        "DNA/RNA Precipitation",
            "equation":    "Nucleic acid + NaCl + 70% EtOH → nucleic acid pellet (physical process)",
            "conditions":  "Cold (−20°C), centrifugation at 12,000g",
            "outcome":     "Standard ethanol precipitation of nucleic acids. NaCl neutralises phosphate charges aiding precipitation.",
            "hazard_rise": "WARNING — ethanol is flammable",
            "temp":        "−20°C overnight or −80°C for 30 minutes",
            "warning":     "🔶 Standard molecular biology procedure. Keep ethanol away from open flames."
        },
        frozenset(["ammonium sulfate", "protein"]): {
            "type":        "Salting-Out Protein Precipitation",
            "equation":    "Protein + (NH₄)₂SO₄ → protein precipitate (reduced hydration shell)",
            "conditions":  "Cold aqueous (4°C), 40–80% ammonium sulfate saturation",
            "outcome":     "High ionic strength reduces protein solubility causing selective precipitation. Used in protein purification.",
            "hazard_rise": "SAFE — standard protein purification method",
            "temp":        "4°C for best results",
            "warning":     "✅ Classic protein purification step. Different proteins precipitate at different ammonium sulfate saturations."
        },
        frozenset(["sodium azide", "copper"]): {
            "type":        "Metal Azide Formation — Explosive",
            "equation":    "2NaN₃ + Cu → Cu(N₃)₂ + 2Na",
            "conditions":  "Contact with copper metal or copper alloys",
            "outcome":     "Copper azide forms as a friction-sensitive primary explosive. Extremely dangerous in drains.",
            "hazard_rise": "EXTREME DANGER — copper azide is a primary explosive",
            "temp":        "Room temperature — spontaneous on contact",
            "warning":     "🚨 NEVER pour sodium azide down copper-containing drains. Deactivate with 10% NaOH + 10% KMnO₄ before disposal."
        },
        frozenset(["hydrogen peroxide", "ferric chloride"]): {
            "type":        "Fenton-Like Reaction",
            "equation":    "Fe³⁺ + H₂O₂ → Fe²⁺ + HO₂• + H⁺ (then Fe²⁺ + H₂O₂ → Fe³⁺ + OH• + OH⁻)",
            "conditions":  "Acidic aqueous (pH 3–5), room temperature",
            "outcome":     "Generates hydroxyl radicals causing oxidative degradation of organic molecules and DNA damage.",
            "hazard_rise": "DANGER — hydroxyl radicals are extremely reactive; cause DNA strand breaks",
            "temp":        "Room temperature; faster at elevated temperature",
            "warning":     "⚠️ Used in advanced oxidation processes. Handle in fume hood. Antioxidants (ascorbate) can quench."
        },
        frozenset(["acetonitrile", "sodium hydroxide"]): {
            "type":        "Nitrile Hydrolysis",
            "equation":    "CH₃CN + NaOH + H₂O → CH₃COONa + NH₃",
            "conditions":  "Concentrated NaOH, elevated temperature (>80°C)",
            "outcome":     "Acetonitrile hydrolysed to sodium acetate and ammonia under strongly alkaline conditions.",
            "hazard_rise": "DANGER — toxic ammonia gas released; acetonitrile is flammable",
            "temp":        "Requires >80°C with concentrated NaOH",
            "warning":     "⚠️ Ammonia generation. Fume hood mandatory. Avoid heating acetonitrile with strong bases."
        },
        frozenset(["pyridine", "hydrochloric acid"]): {
            "type":        "Salt Formation",
            "equation":    "C₅H₅N + HCl → C₅H₅NH⁺Cl⁻ (pyridinium chloride)",
            "conditions":  "Aqueous or anhydrous, room temperature",
            "outcome":     "Pyridinium chloride forms — used as phase-transfer catalyst and in chemical synthesis.",
            "hazard_rise": "DANGER — pyridine is toxic and flammable; HCl is corrosive",
            "temp":        "Room temperature — exothermic",
            "warning":     "⚠️ Pyridine has a foul odour and is toxic by inhalation. Fume hood mandatory."
        },
        frozenset(["lactic acid", "calcium chloride"]): {
            "type":        "Calcium Lactate Formation",
            "equation":    "2CH₃CH(OH)COOH + CaCl₂ → Ca(C₃H₅O₃)₂ + 2HCl",
            "conditions":  "Aqueous, room temperature to mild heating",
            "outcome":     "Calcium lactate forms — used in pharmaceutical calcium supplements and food fortification.",
            "hazard_rise": "SAFE — both compounds are low hazard; product is a food-grade salt",
            "temp":        "Room temperature to 60°C",
            "warning":     "✅ Safe pharmaceutical synthesis. Calcium lactate is GRAS and used in dietary supplements."
        },
        frozenset(["citric acid", "calcium chloride"]): {
            "type":        "Calcium Citrate Precipitation",
            "equation":    "3CaCl₂ + 2C₆H₈O₇ → Ca₃(C₆H₅O₇)₂↓ + 6HCl",
            "conditions":  "Aqueous, neutral to alkaline pH",
            "outcome":     "Calcium citrate precipitates at neutral pH. Important incompatibility in IV nutrition formulations.",
            "hazard_rise": "WARNING — precipitation can block IV lines",
            "temp":        "Room temperature; worsens at body temperature",
            "warning":     "⚠️ Monitor calcium and citrate concentrations in IV bags. Calcium citrate precipitation is a clinical risk."
        },
        frozenset(["methanol", "hydrochloric acid"]): {
            "type":        "Fischer Esterification / Methyl Ester Formation",
            "equation":    "ROH + HCl (g) → ROCl + H₂O (for acid chloride) or CH₃OH + HCl ⇌ CH₃Cl + H₂O",
            "conditions":  "Anhydrous, elevated temperature, HCl gas",
            "outcome":     "Methyl chloride formation under forcing conditions. In aqueous: protonation only.",
            "hazard_rise": "DANGER — methanol is toxic; HCl is corrosive; methyl chloride is toxic gas",
            "temp":        "Elevated temperature for gas-phase reaction",
            "warning":     "⚠️ Methanol is toxic by ingestion and inhalation causing blindness. Fume hood mandatory."
        },
    }

    selected_ings = st.multiselect(
        "Select 2 or more ingredients",
        df["name"].tolist(),
        help="Choose ingredients to see predicted reactions and conditions"
    )

    if len(selected_ings) < 2:
        st.markdown(
            "<div style='text-align:center;padding:50px;color:#aaa;'>"
            "<div style='font-size:40px;margin-bottom:12px'>⚗️</div>"
            "<div style='font-size:16px;font-weight:600;margin-bottom:6px'>"
            "Select at least 2 ingredients above</div>"
            "<div style='font-size:13px'>The predictor will find known reactions,"
            " conditions, temperatures, and hazard changes.</div>"
            "</div>",
            unsafe_allow_html=True
        )
    else:
        st.divider()

        # Combined hazard
        selected_rows = df[df["name"].isin(selected_ings)]
        hazard_order  = {"DANGER": 4, "WARNING": 3, "INFO": 2, "UNKNOWN": 1, "SAFE": 0}
        worst_hazard  = selected_rows["hazard"].map(hazard_order).max()
        worst_label   = {v: k for k, v in hazard_order.items()}[worst_hazard]
        haz_cols = {
            "DANGER":  ("#fde8e8","#c0392b","🔴"),
            "WARNING": ("#fef9e7","#d35400","🟡"),
            "SAFE":    ("#eafaf1","#1e8449","🟢"),
            "INFO":    ("#ebf5fb","#1a5276","🔵"),
            "UNKNOWN": ("#f2f3f4","#717d7e","⚪"),
        }
        bg, fg, icon = haz_cols.get(worst_label, ("#f2f3f4","#717d7e","⚪"))

        st.markdown(
            f"<div style='background:{bg};border-left:5px solid {fg};"
            f"border-radius:8px;padding:14px 20px;margin-bottom:16px;'>"
            f"<b style='color:{fg}'>{icon} Combined Hazard Level: {worst_label}</b>"
            f" — based on highest-risk ingredient in selection</div>",
            unsafe_allow_html=True
        )

        # Find reactions
        names_lower = [s.lower() for s in selected_ings]
        pairs       = list(itertools.combinations(names_lower, 2))
        found_any   = False

        st.markdown("### Known Reactions")
        for pair in pairs:
            key = frozenset(pair)
            if key in reaction_db:
                found_any = True
                rxn  = reaction_db[key]
                a, b = [s.title() for s in pair]
                rise_color = "#e74c3c" if "DANGER" in rxn["hazard_rise"] else "#f39c12"

                st.markdown(
                    f"""
                    <div style='border:1px solid #ddd;border-radius:10px;
                                padding:18px 22px;margin-bottom:14px;background:#fafafa;'>
                        <div style='font-size:16px;font-weight:700;
                                    color:#1a1a1a;margin-bottom:4px'>{a} + {b}</div>
                        <div style='font-size:12px;color:#888;
                                    margin-bottom:12px'>{rxn["type"]}</div>
                        <code style='background:#f0f0f0;padding:6px 12px;
                                     border-radius:6px;font-size:13px;
                                     display:block;margin-bottom:12px'>{rxn["equation"]}</code>
                        <table style='width:100%;font-size:13px;color:#333;'>
                            <tr>
                                <td style='padding:5px 0;width:25%;color:#555'><b>⚗️ Conditions</b></td>
                                <td>{rxn["conditions"]}</td>
                            </tr>
                            <tr>
                                <td style='padding:5px 0;color:#555'><b>🌡️ Temperature</b></td>
                                <td>{rxn["temp"]}</td>
                            </tr>
                            <tr>
                                <td style='padding:5px 0;color:#555'><b>🧪 Outcome</b></td>
                                <td>{rxn["outcome"]}</td>
                            </tr>
                            <tr>
                                <td style='padding:5px 0;color:#555'><b>📈 Hazard change</b></td>
                                <td><span style='color:{rise_color};font-weight:600'>
                                    {rxn["hazard_rise"]}</span></td>
                            </tr>
                            <tr>
                                <td style='padding:5px 0;color:#555'><b>⚠️ Warning</b></td>
                                <td>{rxn["warning"]}</td>
                            </tr>
                        </table>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        if not found_any:
            st.info("No known direct reactions found between selected ingredients. This does not mean they are safe to combine — always verify with SDS and literature.")

        st.divider()
        st.markdown("### Compatibility Notes")
        for pair in pairs:
            key = frozenset(pair)
            if key not in reaction_db:
                a, b = [s.title() for s in pair]
                st.markdown(f"- **{a}** + **{b}** — no reaction data in database. Verify independently.")



# PAGE 9 — LAB WORKFLOW ASSISTANT:

elif page == "Lab Workflow":

    st.markdown("## 🧪 Lab Workflow Assistant")
    st.caption("Select ingredients for your experiment and get a safe step-by-step protocol.")
    st.divider()

    workflow_ings = st.multiselect(
        "Select ingredients for your experiment",
        df["name"].tolist(),
        help="The assistant generates a safe handling order and full protocol"
    )

    if not workflow_ings:
        st.markdown(
            "<div style='text-align:center;padding:50px;color:#aaa;'>"
            "<div style='font-size:40px;margin-bottom:12px'>🧪</div>"
            "<div style='font-size:16px;font-weight:600;margin-bottom:6px'>"
            "Select ingredients above to generate your workflow</div>"
            "<div style='font-size:13px'>Get handling order, PPE checklist,"
            " equipment list and disposal guidelines.</div>"
            "</div>",
            unsafe_allow_html=True
        )
    else:
        selected_rows = df[df["name"].isin(workflow_ings)].copy()
        hazard_order  = {"SAFE": 0, "INFO": 1, "UNKNOWN": 2, "WARNING": 3, "DANGER": 4}
        selected_rows["hazard_rank"] = selected_rows["hazard"].map(hazard_order)
        sorted_rows   = selected_rows.sort_values("hazard_rank")

        st.divider()
        st.markdown("### ✅ Pre-Experiment Checklist")

        has_danger  = "DANGER"  in selected_rows["hazard"].values
        has_warning = "WARNING" in selected_rows["hazard"].values

        if has_danger:
            st.error("🔴 **PPE Required:** Lab coat · Nitrile gloves · Safety goggles · Face shield · Fume hood mandatory")
        elif has_warning:
            st.warning("🟡 **PPE Required:** Lab coat · Nitrile gloves · Safety goggles · Fume hood recommended")
        else:
            st.success("🟢 **PPE Required:** Lab coat · Gloves · Standard eye protection")

        st.markdown("""
        - [ ] SDS sheets available for all ingredients
        - [ ] Fume hood operational and tested
        - [ ] Waste disposal containers prepared
        - [ ] Experiment logged in lab notebook
        - [ ] Eyewash station and fire extinguisher accessible
        - [ ] Supervisor informed
        """)

        st.divider()
        st.markdown("### 🔢 Safe Handling Order")
        st.caption("Handle safest ingredients first, most hazardous last.")

        haz_colors = {
            "DANGER":  ("#fde8e8", "#c0392b", "🔴"),
            "WARNING": ("#fef9e7", "#d35400", "🟡"),
            "SAFE":    ("#eafaf1", "#1e8449", "🟢"),
            "INFO":    ("#ebf5fb", "#1a5276", "🔵"),
            "UNKNOWN": ("#f2f3f4", "#717d7e", "⚪"),
        }

        for i, (_, row) in enumerate(sorted_rows.iterrows(), 1):
            bg, fg, icon = haz_colors.get(row["hazard"], ("#f2f3f4","#717d7e","⚪"))
            st.markdown(
                f"<div style='background:{bg};border-left:4px solid {fg};"
                f"border-radius:8px;padding:12px 18px;margin-bottom:10px;'>"
                f"<span style='font-size:18px;font-weight:800;color:{fg};"
                f"margin-right:14px;'>#{i}</span>"
                f"<span style='font-size:15px;font-weight:700;color:#1a1a1a'>"
                f"{row['name']}</span>"
                f"<span style='font-size:12px;color:#777;margin-left:10px;"
                f"font-family:monospace'>{row['formula']}</span><br/>"
                f"<span style='font-size:12px;color:{fg};margin-left:32px'>"
                f"{icon} {row['hazard']}</span>"
                f"<span style='font-size:12px;color:#999;margin-left:12px'>"
                f"pH {row['ph']} · MW {row['mw']:,} g/mol · Purity {row['purity']}%"
                f"</span></div>",
                unsafe_allow_html=True
            )

        st.divider()
        st.markdown("### 🧰 Equipment Needed")

        equipment = set([
            "Measuring cylinder",
            "Analytical balance",
            "Lab coat",
            "Nitrile gloves",
            "Safety goggles"
        ])

        for _, row in selected_rows.iterrows():
            name = row["name"].lower()
            haz  = row["hazard"]
            ph   = row["ph"]
            mw   = row["mw"]

            if haz == "DANGER":
                equipment.update(["Fume hood","Face shield","Chemical splash goggles","Acid/base resistant gloves"])
            if ph < 3 or ph > 11:
                equipment.update(["pH meter","Acid/base resistant containers","Neutralising agent on standby"])
            if mw > 10000:
                equipment.update(["Centrifuge","Micropipettes","Eppendorf tubes"])
            if name in ["chloroform","phenol","formaldehyde","toluene","pyridine","dimethylformamide"]:
                equipment.update(["Fume hood","Organic solvent waste container"])
            if name in ["ethanol","methanol","acetone","isopropanol","acetonitrile"]:
                equipment.update(["No open flames warning sign","Flammables storage cabinet"])
            if name in ["hydrochloric acid","sulfuric acid","phosphoric acid","acetic acid","trichloroacetic acid"]:
                equipment.update(["Acid cabinet","Neutralising agent (NaHCO₃)","Acid-resistant bench mat"])
            if name in ["sodium hydroxide","potassium hydroxide","sodium carbonate"]:
                equipment.update(["Base-resistant gloves","pH meter","Neutralising acid on standby"])

        for item in sorted(equipment):
            st.markdown(f"- {item}")

        st.divider()
        st.markdown("### 🗑️ Disposal Guidelines")

        disposal = {
            "Organic / halogenated waste": [],
            "Heavy metal waste":           [],
            "Biological waste":            [],
            "Aqueous hazardous waste":     [],
            "General / non-hazardous":     []
        }

        for _, row in selected_rows.iterrows():
            name = row["name"].lower()
            if name in ["chloroform","toluene","phenol","methanol","acetone","ethanol",
                        "isopropanol","dimethylformamide","acetonitrile","pyridine",
                        "formaldehyde","trichloroacetic acid"]:
                disposal["Organic / halogenated waste"].append(row["name"])
            elif name in ["mercury chloride","copper sulfate","silver nitrate",
                          "zinc chloride","zinc sulfate","ferric chloride"]:
                disposal["Heavy metal waste"].append(row["name"])
            elif name in ["bovine serum albumin","proteinase k","agarose","agar",
                          "streptomycin","ampicillin","kanamycin","tetracycline"]:
                disposal["Biological waste"].append(row["name"])
            elif row["hazard"] in ["SAFE","INFO"]:
                disposal["General / non-hazardous"].append(row["name"])
            else:
                disposal["Aqueous hazardous waste"].append(row["name"])

        for group, items in disposal.items():
            if items:
                st.markdown(f"**{group}:** {', '.join(items)}")

        st.divider()

        # Download
        lines = [
            "BIOSPEC ANALYSER — LAB WORKFLOW REPORT",
            "="*45, "",
            "SAFE HANDLING ORDER:"
        ]
        for i, (_, row) in enumerate(sorted_rows.iterrows(), 1):
            lines.append(f"  #{i} {row['name']} ({row['hazard']}) — pH {row['ph']} · MW {row['mw']} g/mol")
        lines += ["", "EQUIPMENT NEEDED:"]
        for item in sorted(equipment):
            lines.append(f"  - {item}")
        lines += ["", "DISPOSAL:"]
        for group, items in disposal.items():
            if items:
                lines.append(f"  {group}: {', '.join(items)}")

        st.download_button(
            label="⬇️ Download workflow as TXT",
            data="\n".join(lines).encode("utf-8"),
            file_name="biospec_lab_workflow.txt",
            mime="text/plain"
        )


# PAGE 10 — STOCK MANAGER:

elif page == "Stock Manager":
 
    st.markdown("## 🗃️ Lab Stock Manager")
    st.caption("Track reagent inventory, log usage, set reorder thresholds and export stock reports.")
    st.divider()
 
    # ── Session-state init ────────────────────────────────
    if "stock" not in st.session_state:
        # Pre-populate with a handful of entries so the page isn't empty
        default_stock = [
            {"name": n, "unit": "mL", "stock": 500.0, "threshold": 100.0,
             "location": "Shelf A1", "lot": "LOT-001", "expiry": "2026-12-31"}
            for n in ["Ethanol", "Methanol", "Chloroform"]
        ] + [
            {"name": n, "unit": "g", "stock": 50.0, "threshold": 10.0,
             "location": "Shelf B2", "lot": "LOT-002", "expiry": "2027-06-30"}
            for n in ["Sodium Azide", "Acrylamide", "Tris Buffer"]
        ]
        st.session_state.stock = default_stock
 
    if "usage_log" not in st.session_state:
        st.session_state.usage_log = []   # list of {name, amount, unit, user, note, timestamp}
 
    stock_df = pd.DataFrame(st.session_state.stock)
 
    # ── KPI strip ─────────────────────────────────────────
    total_items   = len(stock_df)
    low_stock     = int((stock_df["stock"] <= stock_df["threshold"]).sum())
    critical      = int((stock_df["stock"] <= stock_df["threshold"] * 0.5).sum())
    ok_items      = total_items - low_stock
 
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Reagents",  total_items)
    k2.metric("OK",              ok_items,  delta="Sufficient stock",   delta_color="normal")
    k3.metric("Low Stock",       low_stock, delta="At threshold",       delta_color="inverse")
    k4.metric("Critical",        critical,  delta="Below 50 % threshold", delta_color="inverse")
 
    st.divider()
 
    # ── Alerts ────────────────────────────────────────────
    if critical > 0:
        critical_names = stock_df[stock_df["stock"] <= stock_df["threshold"] * 0.5]["name"].tolist()
        st.error(f"🔴 **CRITICAL STOCK:** {', '.join(critical_names)} — reorder immediately.")
    elif low_stock > 0:
        low_names = stock_df[stock_df["stock"] <= stock_df["threshold"]]["name"].tolist()
        st.warning(f"🟡 **LOW STOCK:** {', '.join(low_names)} — approaching reorder threshold.")
    else:
        st.success("🟢 All reagents are within acceptable stock levels.")
 
    st.divider()
 
    # ══════════════════════════════════════════════════════
    # TAB LAYOUT
    # ══════════════════════════════════════════════════════
    tab_inv, tab_add, tab_usage, tab_log, tab_export = st.tabs([
        "📋 Inventory", "➕ Add / Edit Reagent", "🧪 Log Usage", "📜 Usage Log", "⬇️ Export"
    ])
 
    # ─────────────────────────────────────────────────────
    # TAB 1 — INVENTORY TABLE
    # ─────────────────────────────────────────────────────
    with tab_inv:
        st.markdown("### Current Stock Levels")
 
        # Status column
        def stock_status(row):
            ratio = row["stock"] / row["threshold"] if row["threshold"] > 0 else 999
            if ratio <= 0.5:
                return "🔴 CRITICAL"
            elif ratio <= 1.0:
                return "🟡 LOW"
            elif ratio <= 2.0:
                return "🟠 MONITOR"
            else:
                return "🟢 OK"
 
        display = stock_df.copy()
        display["status"]     = display.apply(stock_status, axis=1)
        display["stock %"]    = (display["stock"] / (display["threshold"] * 5) * 100).clip(0, 100).round(1)
 
        def colour_status(val):
            if "CRITICAL" in str(val): return "background-color:#fde8e8;color:#c0392b;"
            if "LOW"      in str(val): return "background-color:#fef9e7;color:#d35400;"
            if "MONITOR"  in str(val): return "background-color:#fff3e0;color:#e65100;"
            if "OK"       in str(val): return "background-color:#eafaf1;color:#1e8449;"
            return ""
 
        st.dataframe(
            display[["name","stock","unit","threshold","location","lot","expiry","status","stock %"]]
            .style.map(colour_status, subset=["status"]),
            use_container_width=True,
            height=380
        )
 
        st.divider()
        st.markdown("### Stock Level Visualisation")
 
        fig_stock = go.Figure()
        colours = []
        for _, r in stock_df.iterrows():
            ratio = r["stock"] / r["threshold"] if r["threshold"] > 0 else 999
            colours.append(
                "#e74c3c" if ratio <= 0.5 else
                "#f39c12" if ratio <= 1.0 else
                "#f0ad4e" if ratio <= 2.0 else
                "#27ae60"
            )
 
        fig_stock.add_trace(go.Bar(
            x=stock_df["name"],
            y=stock_df["stock"],
            name="Current Stock",
            marker_color=colours,
            text=stock_df["unit"],
            textposition="outside"
        ))
        fig_stock.add_trace(go.Scatter(
            x=stock_df["name"],
            y=stock_df["threshold"],
            mode="lines+markers",
            name="Reorder Threshold",
            line=dict(color="#e74c3c", width=2, dash="dash"),
            marker=dict(symbol="line-ew", size=8, line=dict(width=2, color="#e74c3c"))
        ))
        fig_stock.update_layout(
            height=360,
            margin=dict(t=20, b=60),
            xaxis_title="Reagent",
            yaxis_title="Quantity",
            legend=dict(orientation="h", y=1.1),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        fig_stock.update_xaxes(tickangle=-30)
        st.plotly_chart(fig_stock, use_container_width=True)
 
    # ─────────────────────────────────────────────────────
    # TAB 2 — ADD / EDIT REAGENT
    # ─────────────────────────────────────────────────────
    with tab_add:
        st.markdown("### Add a New Reagent to Stock")
 
        all_db_names = df["name"].tolist()
        other_option = "— Enter manually —"
 
        col_src, col_manual = st.columns([2, 2])
        with col_src:
            db_pick = st.selectbox(
                "Pick from ingredient library (optional)",
                [other_option] + all_db_names,
                key="sm_db_pick"
            )
 
        # Pre-fill name if chosen from library
        prefill_name = "" if db_pick == other_option else db_pick
 
        with st.form("add_reagent_form", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            r_name      = fc1.text_input("Reagent name *",  value=prefill_name)
            r_unit      = fc2.selectbox("Unit", ["mL", "L", "g", "mg", "µg", "units"])
            fc3, fc4    = st.columns(2)
            r_stock     = fc3.number_input("Current quantity *",  min_value=0.0, value=100.0, step=1.0)
            r_threshold = fc4.number_input("Reorder threshold *", min_value=0.0, value=20.0,  step=1.0)
            fc5, fc6    = st.columns(2)
            r_location  = fc5.text_input("Storage location",  placeholder="e.g. Fridge 2, Shelf C3")
            r_lot       = fc6.text_input("Lot number",        placeholder="e.g. LOT-2024-008")
            r_expiry    = st.text_input("Expiry date",        placeholder="YYYY-MM-DD")
 
            submitted = st.form_submit_button("➕ Add to inventory")
            if submitted:
                if not r_name.strip():
                    st.error("Reagent name is required.")
                else:
                    existing_names = [s["name"].lower() for s in st.session_state.stock]
                    if r_name.strip().lower() in existing_names:
                        st.warning(f"'{r_name}' already exists in inventory. Use Log Usage to update quantity.")
                    else:
                        st.session_state.stock.append({
                            "name":      r_name.strip(),
                            "unit":      r_unit,
                            "stock":     r_stock,
                            "threshold": r_threshold,
                            "location":  r_location,
                            "lot":       r_lot,
                            "expiry":    r_expiry
                        })
                        st.success(f"✅ '{r_name}' added to inventory.")
                        st.rerun()
 
        st.divider()
        st.markdown("### Remove a Reagent")
        if st.session_state.stock:
            remove_name = st.selectbox(
                "Select reagent to remove",
                [s["name"] for s in st.session_state.stock],
                key="sm_remove_sel"
            )
            if st.button("🗑️ Remove from inventory", key="sm_remove_btn"):
                st.session_state.stock = [
                    s for s in st.session_state.stock if s["name"] != remove_name
                ]
                st.success(f"'{remove_name}' removed.")
                st.rerun()
 
    # ─────────────────────────────────────────────────────
    # TAB 3 — LOG USAGE
    # ─────────────────────────────────────────────────────
    with tab_usage:
        st.markdown("### Record Reagent Usage")
        st.caption("Deduct a used quantity from the current stock.")
 
        if not st.session_state.stock:
            st.info("No reagents in inventory yet. Add some in the **Add / Edit Reagent** tab.")
        else:
            with st.form("log_usage_form", clear_on_submit=True):
                lu1, lu2 = st.columns(2)
                u_name   = lu1.selectbox(
                    "Reagent used",
                    [s["name"] for s in st.session_state.stock],
                    key="sm_use_sel"
                )
                # Find unit for chosen reagent
                u_unit   = next((s["unit"] for s in st.session_state.stock if s["name"] == u_name), "")
                lu2.text_input("Unit (auto)", value=u_unit, disabled=True, key="sm_unit_display")
 
                lu3, lu4 = st.columns(2)
                u_amount = lu3.number_input(f"Amount used ({u_unit})", min_value=0.01, value=1.0, step=0.1)
                u_user   = lu4.text_input("Operator / User", placeholder="Your name or initials")
 
                u_note   = st.text_area("Notes / Experiment reference", placeholder="e.g. PCR run #42, Batch 007…", height=80)
                u_submit = st.form_submit_button("📥 Log usage")
 
                if u_submit:
                    import datetime
                    # Deduct from stock
                    for s in st.session_state.stock:
                        if s["name"] == u_name:
                            if u_amount > s["stock"]:
                                st.error(f"Cannot deduct {u_amount} {u_unit} — only {s['stock']} {u_unit} in stock.")
                            else:
                                s["stock"] = round(s["stock"] - u_amount, 4)
                                st.session_state.usage_log.append({
                                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "name":      u_name,
                                    "amount":    u_amount,
                                    "unit":      u_unit,
                                    "user":      u_user or "—",
                                    "note":      u_note or "—"
                                })
                                new_stock = s["stock"]
                                threshold = s["threshold"]
                                st.success(f"✅ Logged {u_amount} {u_unit} of {u_name}. Remaining: {new_stock} {u_unit}.")
                                if new_stock <= threshold * 0.5:
                                    st.error(f"🔴 CRITICAL: {u_name} is now below 50 % of the reorder threshold!")
                                elif new_stock <= threshold:
                                    st.warning(f"🟡 LOW STOCK: {u_name} has reached the reorder threshold.")
                                st.rerun()
                            break
 
    # ─────────────────────────────────────────────────────
    # TAB 4 — USAGE LOG
    # ─────────────────────────────────────────────────────
    with tab_log:
        st.markdown("### Usage History")
 
        if not st.session_state.usage_log:
            st.info("No usage recorded yet. Log usage in the **Log Usage** tab.")
        else:
            log_df = pd.DataFrame(st.session_state.usage_log)[
                ["timestamp", "name", "amount", "unit", "user", "note"]
            ].iloc[::-1].reset_index(drop=True)  # newest first
 
            st.dataframe(log_df, use_container_width=True, height=350)
 
            st.divider()
            st.markdown("#### Consumption by Reagent")
            usage_summary = (
                pd.DataFrame(st.session_state.usage_log)
                .groupby("name")["amount"]
                .sum()
                .reset_index()
                .rename(columns={"amount": "total_used"})
                .sort_values("total_used", ascending=False)
            )
            fig_log = px.bar(
                usage_summary, x="name", y="total_used",
                color_discrete_sequence=["#2c4a8c"],
                text="total_used"
            )
            fig_log.update_layout(
                height=300, margin=dict(t=10, b=60),
                xaxis_title="Reagent", yaxis_title="Total Consumed",
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
            )
            fig_log.update_xaxes(tickangle=-30)
            st.plotly_chart(fig_log, use_container_width=True)
 
            if st.button("🗑️ Clear usage log", key="sm_clear_log"):
                st.session_state.usage_log = []
                st.rerun()
 
    # ─────────────────────────────────────────────────────
    # TAB 5 — EXPORT
    # ─────────────────────────────────────────────────────
    with tab_export:
        st.markdown("### Export Stock Data")
 
        # Rebuild stock_df with status
        export_stock = pd.DataFrame(st.session_state.stock).copy()
        if not export_stock.empty:
            def _status(row):
                ratio = row["stock"] / row["threshold"] if row["threshold"] > 0 else 999
                return "CRITICAL" if ratio <= 0.5 else "LOW" if ratio <= 1.0 else "MONITOR" if ratio <= 2.0 else "OK"
            export_stock["status"] = export_stock.apply(_status, axis=1)
 
            st.download_button(
                label="⬇️ Download inventory as CSV",
                data=export_stock.to_csv(index=False).encode("utf-8"),
                file_name="biospec_stock_inventory.csv",
                mime="text/csv"
            )
 
        if st.session_state.usage_log:
            log_export = pd.DataFrame(st.session_state.usage_log)
            st.download_button(
                label="⬇️ Download usage log as CSV",
                data=log_export.to_csv(index=False).encode("utf-8"),
                file_name="biospec_usage_log.csv",
                mime="text/csv"
            )
 
        st.divider()
        st.markdown("### Full Stock Report (TXT)")
 
        if not export_stock.empty:
            import datetime as _dt
            report_lines = [
                "BIOSPEC ANALYSER — STOCK MANAGER REPORT",
                "=" * 45,
                f"Generated : {_dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"Total reagents : {len(export_stock)}",
                f"Low / critical : {int((export_stock['status'].isin(['LOW','CRITICAL'])).sum())}",
                "", "INVENTORY:", ""
            ]
            for _, r in export_stock.iterrows():
                report_lines.append(
                    f"  {r['name']:30s}  {r['stock']:>10.2f} {r['unit']:<6}  "
                    f"Threshold: {r['threshold']:.2f}  Location: {r['location']}  "
                    f"Lot: {r['lot']}  Exp: {r['expiry']}  Status: {r['status']}"
                )
 
            if st.session_state.usage_log:
                report_lines += ["", "USAGE LOG:", ""]
                for entry in st.session_state.usage_log:
                    report_lines.append(
                        f"  [{entry['timestamp']}]  {entry['name']:25s}  "
                        f"-{entry['amount']} {entry['unit']}  "
                        f"by {entry['user']}  — {entry['note']}"
                    )
 
            st.download_button(
                label="⬇️ Download full report as TXT",
                data="\n".join(report_lines).encode("utf-8"),
                file_name="biospec_stock_report.txt",
                mime="text/plain"
            )
        else:
            st.info("Add reagents to inventory to enable report export.")

            
# PAGE 11 — SOLUBILITY CALCULATOR:

elif page == "Solubility Calculator":
 
    st.markdown("## ⚗️ Solubility Calculator")
    st.caption("Calculate how much solute to weigh out for a target solution. Purity-corrected.")
    st.divider()
 
    # Known solubility reference (g / 100 mL water at ~25 °C)
    solubility_ref = {
        "sodium chloride":       35.7,
        "glucose":               91.0,
        "sucrose":               200.0,
        "urea":                  108.0,
        "tris buffer":           82.0,
        "edta":                  0.5,
        "ammonium sulfate":      76.9,
        "sodium hydroxide":      111.0,
        "potassium chloride":    34.2,
        "magnesium chloride":    54.3,
        "calcium chloride":      74.5,
        "sodium bicarbonate":    9.6,
        "citric acid":           59.2,
        "acetic acid":           1000.0,   # miscible
        "glycerol":              1000.0,   # miscible
        "ethanol":               1000.0,   # miscible
        "methanol":              1000.0,   # miscible
        "acetone":               1000.0,   # miscible
        "dmso":                  1000.0,   # miscible
        "imidazole":             69.3,
        "sodium azide":          42.0,
        "guanidine hcl":         600.0,
        "lithium chloride":      83.0,
        "ammonium chloride":     37.7,
        "sodium phosphate":      7.1,
        "potassium phosphate":   25.0,
        "hepes":                 24.0,
        "histidine":             4.1,
        "l-arginine":            15.0,
        "l-glutamine":           7.2,
        "ascorbic acid":         33.0,
        "folic acid":            0.0016,
        "boric acid":            5.7,
        "dextrose":              91.0,
        "mannitol":              18.0,
        "lactic acid":           1000.0,
        "maleic acid":           44.1,
        "copper sulfate":        20.0,
        "zinc chloride":         432.0,
        "ferric chloride":       92.0,
    }
 
    # ── Input panel ──────────────────────────────────────
    col_left, col_right = st.columns([1, 1], gap="large")
 
    with col_left:
        st.markdown("### Inputs")
 
        # Ingredient selector — pre-fill MW and purity from DB
        use_db = st.toggle("Pick from ingredient library", value=True, key="sol_use_db")
 
        if use_db:
            ing_choice = st.selectbox("Select ingredient", df["name"].tolist(), key="sol_ing")
            db_row     = df[df["name"] == ing_choice].iloc[0]
            prefill_mw     = float(db_row["mw"])
            prefill_purity = float(db_row["purity"])
            prefill_name   = ing_choice.lower()
        else:
            ing_choice     = None
            prefill_mw     = 180.16
            prefill_purity = 100.0
            prefill_name   = ""
 
        mw_input     = st.number_input("Molecular weight (g/mol)",
                                       min_value=1.0, value=prefill_mw, step=0.01,
                                       format="%.2f", key="sol_mw")
        purity_input = st.number_input("Purity (%)",
                                       min_value=1.0, max_value=100.0,
                                       value=prefill_purity, step=0.1,
                                       format="%.1f", key="sol_purity")
 
        st.divider()
 
        # Target solution
        tc1, tc2 = st.columns(2)
        conc_val  = tc1.number_input("Target concentration", min_value=0.0001,
                                     value=1.0, step=0.1, format="%.4f", key="sol_conc")
        conc_unit = tc2.selectbox("Unit", ["M (mol/L)", "mM", "µM", "nM",
                                            "mg/mL", "µg/mL", "%w/v"], key="sol_cunit")
 
        vc1, vc2  = st.columns(2)
        vol_val   = vc1.number_input("Final volume", min_value=0.001,
                                     value=100.0, step=1.0, key="sol_vol")
        vol_unit  = vc2.selectbox("Unit", ["mL", "L", "µL"], key="sol_vunit")
 
    with col_right:
        st.markdown("### Result")
 
        # Unit conversions to base SI (mol/L and L)
        conc_to_molar = {
            "M (mol/L)": 1.0,
            "mM":        1e-3,
            "µM":        1e-6,
            "nM":        1e-9,
        }
        vol_to_L = {"mL": 1e-3, "L": 1.0, "µL": 1e-6}
 
        vol_L    = vol_val * vol_to_L[vol_unit]
        purity_f = purity_input / 100.0
 
        # Mass-based units
        if conc_unit in ("mg/mL", "µg/mL", "%w/v"):
            if conc_unit == "mg/mL":
                mass_g = conc_val * vol_L * 1000   # mg/mL × L × 1000 mL/L → mg, /1000 → g
                mass_g = conc_val * vol_val / 1000 if vol_unit == "mL" else conc_val * vol_L * 1000 / 1000
                # simpler: mass_g = conc_val [mg/mL] * vol [mL] / 1000
                vol_mL = vol_val if vol_unit == "mL" else vol_val * vol_to_L[vol_unit] * 1000
                mass_g = conc_val * vol_mL / 1000
            elif conc_unit == "µg/mL":
                vol_mL = vol_val if vol_unit == "mL" else vol_val * vol_to_L[vol_unit] * 1000
                mass_g = conc_val * vol_mL / 1e6
            else:  # %w/v  = g per 100 mL
                vol_mL = vol_val if vol_unit == "mL" else vol_val * vol_to_L[vol_unit] * 1000
                mass_g = conc_val * vol_mL / 100
 
            mass_corrected = mass_g / purity_f
            moles          = mass_g / mw_input
            molar_conc     = moles / vol_L if vol_L > 0 else 0
 
            st.metric("Mass to weigh (pure)",     f"{mass_g*1000:.4f} mg  ({mass_g:.6f} g)")
            st.metric("Mass to weigh (purity-corrected)", f"{mass_corrected*1000:.4f} mg  ({mass_corrected:.6f} g)")
            st.metric("Equivalent molar conc.",   f"{molar_conc*1000:.4f} mM")
 
        else:
            # Molar calculation
            conc_M         = conc_val * conc_to_molar[conc_unit]
            moles          = conc_M * vol_L
            mass_g         = moles * mw_input
            mass_corrected = mass_g / purity_f
 
            st.metric("Moles required",           f"{moles:.6f} mol  ({moles*1000:.4f} mmol)")
            st.metric("Mass to weigh (pure)",     f"{mass_g*1000:.4f} mg  ({mass_g:.6f} g)")
            st.metric("Mass to weigh (purity-corrected)", f"{mass_corrected*1000:.4f} mg  ({mass_corrected:.6f} g)")
 
        st.divider()
 
        # Solubility check
        look_name = (ing_choice or "").lower()
        sol_limit = solubility_ref.get(look_name, None)
 
        if sol_limit is not None:
            vol_mL_ref = vol_val if vol_unit == "mL" else vol_val * vol_to_L[vol_unit] * 1000
            max_mass_g = sol_limit * vol_mL_ref / 100
 
            if sol_limit >= 999:
                st.success("✅ **Solubility:** Miscible with water in all proportions.")
            elif mass_corrected <= max_mass_g:
                st.success(
                    f"✅ **Solubility check passed.** "
                    f"Max soluble: {max_mass_g*1000:.1f} mg in {vol_mL_ref:.0f} mL "
                    f"(ref: {sol_limit} g / 100 mL)."
                )
            else:
                st.error(
                    f"🔴 **Solubility limit exceeded!** "
                    f"Max soluble: {max_mass_g*1000:.1f} mg in {vol_mL_ref:.0f} mL "
                    f"(ref: {sol_limit} g / 100 mL). "
                    f"Consider heating, alternate solvent, or lower concentration."
                )
        else:
            st.info("ℹ️ No solubility reference on file for this compound. Verify independently.")
 
        st.divider()
        # Protocol snippet
        label = ing_choice if ing_choice else "compound"
        if conc_unit not in ("mg/mL", "µg/mL", "%w/v"):
            st.markdown("#### Preparation note")
            st.markdown(
                f"Weigh out **{mass_corrected*1000:.2f} mg** of {label} "
                f"(purity-corrected for {purity_input}%). "
                f"Dissolve in approximately 80% of the final volume ({vol_val * 0.8:.1f} {vol_unit}) "
                f"of solvent, mix thoroughly, then bring to final volume "
                f"({vol_val} {vol_unit})."
            )
 
 

# PAGE 12 — DILUTION CALCULATOR:

elif page == "Dilution Calculator":
 
    st.markdown("## 🔽 Dilution Calculator")
    st.caption("C₁V₁ = C₂V₂ solver and serial dilution planner.")
    st.divider()
 
    mode = st.radio(
        "Mode",
        ["Simple Dilution  (C₁V₁ = C₂V₂)", "Serial Dilution"],
        horizontal=True,
        key="dil_mode"
    )
    st.divider()
 
    # ── SIMPLE DILUTION ───────────────────────────────────
    if mode == "Simple Dilution  (C₁V₁ = C₂V₂)":
 
        st.markdown("### Simple Dilution — C₁V₁ = C₂V₂")
        st.caption("Fill in any three values and leave one blank (set to 0) to solve for it.")
 
        unit_opts = ["M", "mM", "µM", "nM", "mg/mL", "µg/mL", "ng/mL", "%"]
 
        dc1, dc2 = st.columns(2)
        with dc1:
            st.markdown("**Stock solution (1)**")
            c1_val  = st.number_input("C₁ — Stock concentration",  min_value=0.0, value=10.0,  step=0.1, key="c1v")
            c1_unit = st.selectbox("C₁ unit", unit_opts, key="c1u")
            v1_val  = st.number_input("V₁ — Volume to take (0 = solve)", min_value=0.0, value=0.0, step=0.1, key="v1v")
            v1_unit = st.selectbox("V₁ unit", ["mL", "µL", "L"], key="v1u")
 
        with dc2:
            st.markdown("**Working solution (2)**")
            c2_val  = st.number_input("C₂ — Target concentration", min_value=0.0, value=1.0,   step=0.1, key="c2v")
            c2_unit = st.selectbox("C₂ unit", unit_opts, index=1, key="c2u")
            v2_val  = st.number_input("V₂ — Final volume",          min_value=0.0, value=100.0, step=1.0,  key="v2v")
            v2_unit = st.selectbox("V₂ unit", ["mL", "µL", "L"], key="v2u")
 
        st.divider()
 
        # Convert everything to mL for arithmetic
        scale = {"mL": 1.0, "µL": 1e-3, "L": 1000.0}
 
        def conc_to_base(val, unit):
            """Normalise to a comparable float (same-scale comparison only; units must match)."""
            m = {"M": 1e6, "mM": 1e3, "µM": 1.0, "nM": 1e-3,
                 "mg/mL": 1e3, "µg/mL": 1.0, "ng/mL": 1e-3, "%": 1e4}
            return val * m.get(unit, 1.0)
 
        v1_mL = v1_val * scale[v1_unit]
        v2_mL = v2_val * scale[v2_unit]
        c1_b  = conc_to_base(c1_val, c1_unit)
        c2_b  = conc_to_base(c2_val, c2_unit)
 
        st.markdown("### Result")
        res1, res2, res3 = st.columns(3)
 
        if v1_val == 0 and c1_b > 0 and v2_mL > 0:
            # Solve for V1
            if c2_b > c1_b:
                st.error("🔴 Target concentration is higher than stock — cannot dilute to a higher concentration.")
            else:
                v1_solved_mL = (c2_b * v2_mL) / c1_b
                df_vol       = v2_mL - v1_solved_mL
                df_vol       = max(df_vol, 0)
 
                res1.metric("Volume to take (V₁)",  f"{v1_solved_mL:.4f} mL")
                res2.metric("Diluent to add",        f"{df_vol:.4f} mL")
                res3.metric("Dilution factor",       f"1 : {v2_mL/v1_solved_mL:.1f}" if v1_solved_mL > 0 else "—")
 
                st.divider()
                st.markdown("#### Protocol")
                st.markdown(
                    f"Take **{v1_solved_mL:.3f} mL** of stock ({c1_val} {c1_unit}) "
                    f"and add **{df_vol:.3f} mL** of diluent "
                    f"to reach a final volume of **{v2_val} {v2_unit}** "
                    f"at **{c2_val} {c2_unit}**."
                )
        elif v1_mL > 0 and c1_b > 0 and v2_mL > 0 and c2_b > 0:
            # All known — verify / show dilution factor
            df_expected = (c1_b * v1_mL) / v2_mL
            df_vol      = v2_mL - v1_mL
 
            res1.metric("Calculated C₂",       f"{df_expected:.4f} (normalised units)")
            res2.metric("Diluent to add",       f"{max(df_vol,0):.4f} mL")
            res3.metric("Dilution factor",      f"1 : {v2_mL/v1_mL:.1f}" if v1_mL > 0 else "—")
            st.info("All four values provided — showing verification. Set V₁ = 0 to solve for it.")
        else:
            st.info("Fill in C₁, C₂, and V₂. Set V₁ = 0 to calculate how much stock to take.")
 
    # ── SERIAL DILUTION ───────────────────────────────────
    else:
        st.markdown("### Serial Dilution Planner")
 
        sd1, sd2, sd3 = st.columns(3)
        stock_conc    = sd1.number_input("Stock concentration", min_value=0.0001, value=10.0, step=0.1, key="sd_stock")
        stock_unit    = sd1.selectbox("Unit", ["M", "mM", "µM", "nM", "mg/mL", "µg/mL"], key="sd_unit")
        n_steps       = sd2.slider("Number of dilution steps", min_value=2, max_value=12, value=6, key="sd_steps")
        dilution_f    = sd3.selectbox("Dilution factor per step",
                                      ["1:2", "1:3", "1:4", "1:5", "1:10", "Custom"], key="sd_factor")
 
        if dilution_f == "Custom":
            custom_f = st.number_input("Enter custom factor (e.g. 2.5 for 1:2.5)",
                                       min_value=1.01, value=2.0, step=0.1, key="sd_custom")
            df_num = custom_f
        else:
            df_num = float(dilution_f.split(":")[1])
 
        vol_per_step = st.number_input("Volume per tube (mL)", min_value=0.01, value=1.0, step=0.1, key="sd_vol")
 
        st.divider()
        st.markdown("### Serial Dilution Table")
 
        import math
        rows = []
        for i in range(n_steps):
            conc = stock_conc / (df_num ** i)
            v_stock = vol_per_step / df_num          # vol taken from previous tube
            v_diluent = vol_per_step - v_stock
            rows.append({
                "Step":               f"Tube {i+1}" if i > 0 else "Stock",
                "Concentration":      f"{conc:.6g} {stock_unit}",
                "Dilution":           f"1:{int(df_num**i)}" if (df_num**i) == int(df_num**i) else f"1:{df_num**i:.2f}",
                "From previous (mL)": f"{v_stock:.3f}" if i > 0 else "—",
                "Diluent (mL)":       f"{v_diluent:.3f}" if i > 0 else "—",
                "Final vol (mL)":     f"{vol_per_step:.2f}",
            })
            if i == 0:
                # stock row — no dilution step needed
                rows[0]["From previous (mL)"] = "—"
                rows[0]["Diluent (mL)"]        = "—"
 
        serial_df = pd.DataFrame(rows)
        st.dataframe(serial_df, use_container_width=True, hide_index=True)
 
        # Chart
        concs  = [stock_conc / (df_num**i) for i in range(n_steps)]
        labels = [f"Tube {i+1}" if i > 0 else "Stock" for i in range(n_steps)]
 
        fig_ser = px.line(
            x=labels, y=concs,
            markers=True,
            labels={"x": "Tube", "y": f"Concentration ({stock_unit})"},
            color_discrete_sequence=["#2c4a8c"]
        )
        fig_ser.update_layout(
            height=300, margin=dict(t=10, b=40),
            yaxis_type="log",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        fig_ser.update_traces(line=dict(width=2), marker=dict(size=8))
        st.plotly_chart(fig_ser, use_container_width=True)
        st.caption("Y-axis is log scale.")
 
        st.divider()
        # Download
        st.download_button(
            label="⬇️ Download serial dilution table as CSV",
            data=serial_df.to_csv(index=False).encode("utf-8"),
            file_name="biospec_serial_dilution.csv",
            mime="text/csv"
        )
 
 

# PAGE 13 — BUFFER CALCULATOR:

elif page == "Buffer Calculator":
 
    import math
 
    st.markdown("## 🧫 Buffer Calculator")
    st.caption("Henderson–Hasselbalch buffer design. Calculate acid/base ratios for any target pH.")
    st.divider()
 
    # Buffer system database
    buffer_systems = {
        "Acetate (pH 3.6 – 5.6)": {
            "acid":   "Acetic acid (CH₃COOH)",
            "base":   "Sodium acetate (CH₃COONa)",
            "pKa":    4.76,
            "range":  (3.6, 5.6),
            "mw_acid": 60.05,
            "mw_base": 82.03,
        },
        "Phosphate (pH 5.8 – 8.0)": {
            "acid":   "Sodium dihydrogen phosphate (NaH₂PO₄)",
            "base":   "Disodium hydrogen phosphate (Na₂HPO₄)",
            "pKa":    7.20,
            "range":  (5.8, 8.0),
            "mw_acid": 119.98,
            "mw_base": 141.96,
        },
        "Citrate (pH 3.0 – 6.2)": {
            "acid":   "Citric acid (C₆H₈O₇)",
            "base":   "Sodium citrate (C₆H₅Na₃O₇)",
            "pKa":    3.13,
            "range":  (3.0, 6.2),
            "mw_acid": 192.12,
            "mw_base": 294.10,
        },
        "Tris-HCl (pH 7.0 – 9.0)": {
            "acid":   "Tris·HCl (protonated)",
            "base":   "Tris base (free base)",
            "pKa":    8.06,
            "range":  (7.0, 9.0),
            "mw_acid": 157.60,
            "mw_base": 121.14,
        },
        "Carbonate (pH 9.2 – 10.8)": {
            "acid":   "Sodium bicarbonate (NaHCO₃)",
            "base":   "Sodium carbonate (Na₂CO₃)",
            "pKa":    10.33,
            "range":  (9.2, 10.8),
            "mw_acid": 84.01,
            "mw_base": 105.99,
        },
        "Borate (pH 8.5 – 10.0)": {
            "acid":   "Boric acid (H₃BO₃)",
            "base":   "Sodium borate / Borax (Na₂B₄O₇)",
            "pKa":    9.24,
            "range":  (8.5, 10.0),
            "mw_acid": 61.83,
            "mw_base": 381.37,
        },
        "HEPES (pH 6.8 – 8.2)": {
            "acid":   "HEPES free acid",
            "base":   "HEPES sodium salt",
            "pKa":    7.55,
            "range":  (6.8, 8.2),
            "mw_acid": 238.30,
            "mw_base": 260.29,
        },
        "MES (pH 5.5 – 6.7)": {
            "acid":   "MES free acid",
            "base":   "MES sodium salt",
            "pKa":    6.15,
            "range":  (5.5, 6.7),
            "mw_acid": 195.20,
            "mw_base": 217.22,
        },
        "MOPS (pH 6.5 – 7.9)": {
            "acid":   "MOPS free acid",
            "base":   "MOPS sodium salt",
            "pKa":    7.20,
            "range":  (6.5, 7.9),
            "mw_acid": 209.26,
            "mw_base": 231.25,
        },
    }
 
    # ── Buffer system selector ────────────────────────────
    buf_choice = st.selectbox(
        "Select buffer system",
        list(buffer_systems.keys()),
        key="buf_sys"
    )
    buf = buffer_systems[buf_choice]
    pKa = buf["pKa"]
 
    ph_min, ph_max = buf["range"]
 
    bc1, bc2, bc3 = st.columns(3)
    target_pH   = bc1.slider(
        "Target pH",
        min_value=float(ph_min),
        max_value=float(ph_max),
        value=round((ph_min + ph_max) / 2, 1),
        step=0.1,
        key="buf_ph"
    )
    total_conc  = bc2.number_input(
        "Total buffer concentration (mM)",
        min_value=1.0, max_value=2000.0, value=100.0, step=10.0,
        key="buf_conc"
    )
    final_vol   = bc3.number_input(
        "Final volume (mL)",
        min_value=1.0, max_value=5000.0, value=100.0, step=10.0,
        key="buf_vol"
    )
 
    st.divider()
 
    # ── Henderson–Hasselbalch ─────────────────────────────
    # pH = pKa + log([A-]/[HA])  →  ratio = 10^(pH - pKa)
    ratio     = 10 ** (target_pH - pKa)          # [base] / [acid]
    f_base    = ratio / (1 + ratio)               # fraction as base
    f_acid    = 1.0 - f_base
 
    conc_M    = total_conc / 1000.0               # mM → M
    vol_L     = final_vol  / 1000.0               # mL → L
    total_mol = conc_M * vol_L
 
    mol_acid  = f_acid * total_mol
    mol_base  = f_base * total_mol
 
    mass_acid_g = mol_acid * buf["mw_acid"]
    mass_base_g = mol_base * buf["mw_base"]
 
    # ── Results ───────────────────────────────────────────
    st.markdown("### Buffer Recipe")
 
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Target pH",      f"{target_pH:.1f}")
    r2.metric("pKa of system",  f"{pKa:.2f}")
    r3.metric("[Base] / [Acid]", f"{ratio:.3f}")
    r4.metric("Buffer capacity", "Good" if 0.1 < ratio < 10 else "⚠️ Poor")
 
    st.divider()
 
    col_acid, col_base = st.columns(2)
 
    with col_acid:
        st.markdown(
            f"<div style='background:#ebf5fb;border-left:4px solid #1a5276;"
            f"border-radius:8px;padding:16px 20px;'>"
            f"<div style='font-size:12px;color:#1a5276;font-weight:700;margin-bottom:4px'>ACID COMPONENT</div>"
            f"<div style='font-size:15px;font-weight:600;color:#1a1a1a'>{buf['acid']}</div>"
            f"<div style='font-size:26px;font-weight:800;color:#1a5276;margin-top:8px'>"
            f"{mass_acid_g*1000:.2f} mg</div>"
            f"<div style='font-size:13px;color:#555;margin-top:4px'>"
            f"{mol_acid*1000:.4f} mmol &nbsp;·&nbsp; {f_acid*100:.1f}% of total</div>"
            f"</div>",
            unsafe_allow_html=True
        )
 
    with col_base:
        st.markdown(
            f"<div style='background:#eafaf1;border-left:4px solid #1e8449;"
            f"border-radius:8px;padding:16px 20px;'>"
            f"<div style='font-size:12px;color:#1e8449;font-weight:700;margin-bottom:4px'>BASE COMPONENT</div>"
            f"<div style='font-size:15px;font-weight:600;color:#1a1a1a'>{buf['base']}</div>"
            f"<div style='font-size:26px;font-weight:800;color:#1e8449;margin-top:8px'>"
            f"{mass_base_g*1000:.2f} mg</div>"
            f"<div style='font-size:13px;color:#555;margin-top:4px'>"
            f"{mol_base*1000:.4f} mmol &nbsp;·&nbsp; {f_base*100:.1f}% of total</div>"
            f"</div>",
            unsafe_allow_html=True
        )
 
    st.divider()
 
    # pH range warning
    if target_pH < pKa - 1 or target_pH > pKa + 1:
        st.warning(
            f"⚠️ Target pH ({target_pH}) is more than 1 unit from pKa ({pKa}). "
            f"Buffer capacity will be low. Consider choosing a different buffer system."
        )
    else:
        st.success(
            f"✅ pH {target_pH} is within ±1 unit of pKa {pKa}. "
            f"This buffer has good capacity in this range."
        )
 
    # Preparation protocol
    st.divider()
    st.markdown("### Preparation Protocol")
    st.markdown(
        f"1. Weigh **{mass_acid_g*1000:.2f} mg** of {buf['acid']} and "
        f"**{mass_base_g*1000:.2f} mg** of {buf['base']}.\n"
        f"2. Dissolve both in approximately **{final_vol * 0.8:.0f} mL** of ultrapure water.\n"
        f"3. Mix thoroughly and check pH with a calibrated pH meter.\n"
        f"4. Adjust to pH **{target_pH:.1f}** by adding small amounts of acid or base as needed.\n"
        f"5. Bring to final volume of **{final_vol:.0f} mL** with ultrapure water.\n"
        f"6. Filter-sterilise if required (0.22 µm) and store appropriately."
    )
 
    # pH curve
    st.divider()
    st.markdown("### pH–Composition Curve")
    st.caption("How pH changes as the acid/base ratio shifts across the full buffer range.")
 
    import numpy as np
    fracs    = [i / 100 for i in range(1, 100)]          # fraction as base (0.01 → 0.99)
    ph_curve = [pKa + math.log10(f / (1 - f)) for f in fracs]
 
    fig_ph = go.Figure()
    fig_ph.add_trace(go.Scatter(
        x=[f * 100 for f in fracs], y=ph_curve,
        mode="lines",
        name="pH",
        line=dict(color="#2c4a8c", width=2.5)
    ))
    fig_ph.add_trace(go.Scatter(
        x=[f_base * 100], y=[target_pH],
        mode="markers",
        name="Your target",
        marker=dict(color="#e74c3c", size=12, symbol="circle")
    ))
    fig_ph.add_hline(y=pKa, line_dash="dot", line_color="#27ae60",
                     annotation_text=f"pKa = {pKa}", annotation_position="right")
    fig_ph.update_layout(
        height=320,
        margin=dict(t=10, b=40),
        xaxis_title="Base fraction (%)",
        yaxis_title="pH",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_ph, use_container_width=True)
 
    # Export
    st.divider()
    report = (
        f"BIOSPEC ANALYSER — BUFFER CALCULATOR REPORT\n"
        f"{'='*45}\n"
        f"Buffer system : {buf_choice}\n"
        f"Target pH     : {target_pH}\n"
        f"pKa           : {pKa}\n"
        f"Total conc.   : {total_conc} mM\n"
        f"Final volume  : {final_vol} mL\n\n"
        f"RECIPE:\n"
        f"  {buf['acid']:45s}  {mass_acid_g*1000:.2f} mg  ({mol_acid*1000:.4f} mmol)\n"
        f"  {buf['base']:45s}  {mass_base_g*1000:.2f} mg  ({mol_base*1000:.4f} mmol)\n\n"
        f"PREPARATION:\n"
        f"  Dissolve both components in ~{final_vol*0.8:.0f} mL water,\n"
        f"  adjust pH to {target_pH} with pH meter, bring to {final_vol:.0f} mL.\n"
    )
    st.download_button(
        label="⬇️ Download buffer recipe as TXT",
        data=report.encode("utf-8"),
        file_name="biospec_buffer_recipe.txt",
        mime="text/plain"
    )
