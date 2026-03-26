"""Molecule Explorer – full cheminformatics profile for a selected VOC."""

import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.sample_data import VOCS
from utils.chem_utils import (
    draw_molecule_png_b64, compute_descriptors,
    get_lipinski_verdict, RDKIT_AVAILABLE,
)


def render():
    st.markdown("<div class='section-head'>🔬 Molecule Explorer</div>", unsafe_allow_html=True)

    # ── Compound Selector ────────────────────────────────────────────────────
    voc_names = VOCS["name"].tolist()
    selected = st.selectbox("Select a VOC compound", voc_names)
    voc = VOCS[VOCS["name"] == selected].iloc[0]

    bio_color = "#d1fae5" if voc["bioactivity"] == "Attractant" else "#fee2e2"
    bio_text = "#065f46" if voc["bioactivity"] == "Attractant" else "#991b1b"

    st.markdown("<br>", unsafe_allow_html=True)
    col_img, col_info = st.columns([1, 2])

    with col_img:
        if RDKIT_AVAILABLE:
            b64 = draw_molecule_png_b64(voc["smiles"], 360, 260)
            if b64:
                st.markdown(
                    f'<img src="data:image/png;base64,{b64}" '
                    f'style="width:100%;border-radius:12px;border:1px solid #d1fae5;background:#f8fafb;padding:8px">',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Install RDKit for 2D structure rendering:\n`pip install rdkit`")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**SMILES String**")
        st.markdown(
            f'<div class="smiles-box">{voc["smiles"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"**InChIKey:** `{voc['inchikey']}`")
        st.markdown(f"**PubChem CID:** [{voc['pubchem_cid']}](https://pubchem.ncbi.nlm.nih.gov/compound/{voc['pubchem_cid']})")

    with col_info:
        st.markdown(f"## {voc['name']}")
        st.markdown(
            f'<span style="background:{bio_color};color:{bio_text};padding:4px 14px;border-radius:20px;'
            f'font-size:0.85rem;font-weight:700">{voc["bioactivity"]}</span>'
            f'&nbsp;<span style="background:#ede9fe;color:#4c1d95;padding:4px 14px;border-radius:20px;'
            f'font-size:0.85rem;font-weight:600">{voc["class"]}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Formula", voc["formula"])
        c2.metric("MW (g/mol)", voc["mw"])
        c3.metric("LogP", voc["logp"])

        c4, c5, c6 = st.columns(3)
        c4.metric("Emission Source", voc["emission_source"])
        c5.metric("Concentration", f"{voc['concentration_ppm']} ppm")
        c6.metric("Target", voc["target"])

        st.markdown("---")
        st.markdown("**🦟 Associated Insect**")
        st.markdown(f"*{voc['insect']}*")
        st.markdown("**🌿 Host Plant**")
        st.markdown(f"*{voc['plant']}*")
        st.markdown("**🐝 Natural Enemy**")
        st.markdown(f"*{voc['natural_enemy']}*")
        st.markdown("**📝 Notes**")
        st.markdown(f"_{voc['notes']}_")

    # ── Computed Descriptors ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-head'>Computed Molecular Descriptors</div>", unsafe_allow_html=True)

    if RDKIT_AVAILABLE:
        desc = compute_descriptors(voc["smiles"])
        verdict = get_lipinski_verdict(voc["smiles"])

        col_desc, col_verdict = st.columns(2)

        with col_desc:
            st.markdown("**RDKit Descriptor Values**")
            if desc:
                d_col1, d_col2 = st.columns(2)
                items = list(desc.items())
                mid = len(items) // 2
                for k, v in items[:mid]:
                    d_col1.metric(k, v)
                for k, v in items[mid:]:
                    d_col2.metric(k, v)
            else:
                st.warning("Could not parse SMILES for descriptor calculation.")

        with col_verdict:
            st.markdown("**VOC Volatility Profile**")
            if verdict:
                for rule, result in verdict.items():
                    if "VOC Volatility" in rule:
                        level = result
                        color = "#22c55e" if level == "HIGH" else "#f59e0b"
                        st.markdown(
                            f'<div style="background:{color};color:white;font-weight:700;'
                            f'font-size:1.1rem;padding:10px 16px;border-radius:8px;margin-bottom:12px">'
                            f'Volatility: {level}</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(f"- **{rule}:** {result}")
            else:
                st.warning("Could not parse SMILES for volatility assessment.")

        # ── Radar chart of normalized descriptors ───────────────────────────
        if desc:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Descriptor Radar Chart**")

            # Normalize to 0–1 scale for radar (approximate max values)
            norms = {
                "MW": (desc.get("Molecular Weight", 0), 500),
                "LogP": (desc.get("LogP (Wildman-Crippen)", 0) + 2, 10),
                "TPSA": (desc.get("TPSA (Å²)", 0), 150),
                "HBD": (desc.get("H-Bond Donors", 0), 5),
                "HBA": (desc.get("H-Bond Acceptors", 0), 10),
                "RotBonds": (desc.get("Rotatable Bonds", 0), 15),
                "Rings": (desc.get("Ring Count", 0), 5),
                "Csp3": (desc.get("Fraction Csp3", 0), 1),
            }
            cats = list(norms.keys())
            vals = [min(v / mx, 1.0) for v, mx in norms.values()]
            vals += [vals[0]]  # close polygon
            cats += [cats[0]]

            fig = go.Figure(go.Scatterpolar(
                r=vals, theta=cats,
                fill="toself",
                fillcolor="rgba(74,124,89,0.25)",
                line=dict(color="#1a3a2a", width=2),
                name=voc["name"],
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 1]),
                    bgcolor="#f0fdf4",
                ),
                showlegend=False,
                height=340,
                margin=dict(t=30, b=30),
                font=dict(family="Inter"),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("""
        **RDKit not installed.** Install it for full cheminformatics features:
        ```
        pip install rdkit
        ```
        Descriptor values shown above are from the pre-loaded database.
        """)
