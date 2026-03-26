"""VOC Library – filterable table with inline structure rendering."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.sample_data import VOCS
from utils.chem_utils import draw_molecule_svg, draw_molecule_png_b64, RDKIT_AVAILABLE


def render():
    st.markdown("<div class='section-head'>🧪 VOC Library</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='info-box'>
        Browse all Volatile Organic Compounds in the library. Filter by insect, plant,
        chemical class, or bioactivity. Click on any row to inspect its full cheminformatics
        profile in the <b>Molecule Explorer</b>.
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ──────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        bioact = st.selectbox("Bioactivity", ["All"] + sorted(VOCS["bioactivity"].unique()))
    with col2:
        chem_class = st.selectbox("Chemical Class", ["All"] + sorted(VOCS["class"].unique()))
    with col3:
        insect = st.selectbox("Insect", ["All"] + sorted(VOCS["insect"].unique()))
    with col4:
        source = st.selectbox("Emission Source", ["All"] + sorted(VOCS["emission_source"].unique()))

    df = VOCS.copy()
    if bioact != "All":
        df = df[df["bioactivity"] == bioact]
    if chem_class != "All":
        df = df[df["class"] == chem_class]
    if insect != "All":
        df = df[df["insect"] == insect]
    if source != "All":
        df = df[df["emission_source"] == source]

    st.markdown(f"**{len(df)} records** found")

    # ── Toggle: table vs card view ───────────────────────────────────────────
    view_mode = st.radio("View Mode", ["📋 Table", "🃏 Cards"], horizontal=True)

    if view_mode == "📋 Table":
        display_cols = [
            "voc_id", "name", "formula", "mw", "logp",
            "class", "emission_source", "bioactivity", "target",
            "insect", "plant", "natural_enemy", "concentration_ppm",
        ]
        def color_bio(val):
            if val == "Attractant":
                return "background-color:#d1fae5;color:#065f46;font-weight:600"
            elif val == "Repellent":
                return "background-color:#fee2e2;color:#991b1b;font-weight:600"
            return ""

        st.dataframe(
            df[display_cols].style.applymap(color_bio, subset=["bioactivity"]),
            use_container_width=True,
            height=480,
        )

    else:  # Cards
        cols_per_row = 2
        rows = [df.iloc[i:i+cols_per_row] for i in range(0, len(df), cols_per_row)]
        for row in rows:
            cols = st.columns(cols_per_row)
            for col, (_, voc) in zip(cols, row.iterrows()):
                with col:
                    bio_color = "#d1fae5" if voc["bioactivity"] == "Attractant" else "#fee2e2"
                    bio_text_color = "#065f46" if voc["bioactivity"] == "Attractant" else "#991b1b"

                    with st.container(border=True):
                        # Molecule image
                        if RDKIT_AVAILABLE:
                            b64 = draw_molecule_png_b64(voc["smiles"], 320, 180)
                            if b64:
                                st.markdown(
                                    f'<img src="data:image/png;base64,{b64}" '
                                    f'style="width:100%;border-radius:8px;background:#f8fafb;padding:4px">',
                                    unsafe_allow_html=True,
                                )
                        else:
                            st.markdown(
                                '<div style="height:100px;background:#f0fdf4;border-radius:8px;'
                                'display:flex;align-items:center;justify-content:center;'
                                'color:#4a7c59;font-size:0.8rem">Install RDKit for structure</div>',
                                unsafe_allow_html=True,
                            )

                        st.markdown(f"**{voc['name']}**")
                        st.markdown(
                            f'<span style="font-size:0.78rem;font-family:IBM Plex Mono,monospace;'
                            f'color:#4a7c59">{voc["formula"]} · MW {voc["mw"]} · LogP {voc["logp"]}</span>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f'<span style="background:{bio_color};color:{bio_text_color};'
                            f'padding:3px 10px;border-radius:20px;font-size:0.78rem;font-weight:600">'
                            f'{voc["bioactivity"]}</span>'
                            f'&nbsp;<span style="background:#ede9fe;color:#4c1d95;'
                            f'padding:3px 10px;border-radius:20px;font-size:0.78rem;font-weight:600">'
                            f'{voc["class"]}</span>',
                            unsafe_allow_html=True,
                        )
                        st.markdown("<br>", unsafe_allow_html=True)

                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"🦟 `{voc['insect'].split()[0]}`")
                            st.markdown(f"🌿 `{voc['plant'].split()[0]}`")
                        with c2:
                            st.markdown(f"🎯 {voc['target']}")
                            st.markdown(f"📍 {voc['concentration_ppm']} ppm")

                        with st.expander("SMILES"):
                            st.markdown(
                                f'<div class="smiles-box">{voc["smiles"]}</div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(f"**PubChem CID:** {voc['pubchem_cid']}")
                        st.caption(f"_{voc['notes']}_")
