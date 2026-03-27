"""Chemical Similarity Search – Tanimoto / Morgan fingerprints + PubChem images."""

import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.sample_data import VOCS
from utils.chem_utils import (
    tanimoto_similarity, similarity_matrix,
    get_structure_image_url, RDKIT_AVAILABLE,
)


def render():
    st.markdown(
        "<div class='section-head'>🔍 Chemical Similarity Search</div>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class='info-box'>
    Uses <b>Morgan fingerprints</b> (radius=2, 2048 bits) and <b>Tanimoto coefficient</b>
    to find structurally similar VOCs. Score of 1.0 = identical; &gt;0.4 = structurally similar.
    Molecular structures rendered via PubChem.
    </div>
    """, unsafe_allow_html=True)

    if not RDKIT_AVAILABLE:
        st.error(
            "**RDKit is required for similarity calculations.**\n\n"
            "Add `rdkit` to your `requirements.txt` and redeploy."
        )
        return

    tab1, tab2 = st.tabs(["🔎 Query Search", "🗺️ Similarity Matrix"])

    # ── Tab 1: query search ───────────────────────────────────────────────────
    with tab1:
        col_a, col_b = st.columns([2, 1])
        with col_a:
            mode = st.radio(
                "Query by", ["Select from Library", "Enter SMILES"], horizontal=True
            )
        with col_b:
            threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.2, 0.05)

        query_smiles = None
        query_name   = None

        if mode == "Select from Library":
            selected     = st.selectbox("Select query VOC", VOCS["name"].tolist())
            query_row    = VOCS[VOCS["name"] == selected].iloc[0]
            query_smiles = query_row["smiles"]
            query_name   = selected
        else:
            query_smiles = st.text_input(
                "Enter SMILES string",
                placeholder="e.g. CC1=CCC(CC1)C(C)=C",
            )
            query_name = "Custom Query"

        if query_smiles and st.button("🔍 Search", type="primary"):
            with st.spinner("Computing Tanimoto similarities..."):
                results = []
                for _, row in VOCS.iterrows():
                    sim = tanimoto_similarity(query_smiles, row["smiles"])
                    results.append({
                        "VOC":         row["name"],
                        "Class":       row["class"],
                        "Formula":     row["formula"],
                        "Bioactivity": row["bioactivity"],
                        "Insect":      row["insect"],
                        "Similarity":  sim,
                        "SMILES":      row["smiles"],
                        "CID":         row.get("pubchem_cid", 0),
                    })

                results_df = pd.DataFrame(results)
                results_df = results_df[results_df["Similarity"] >= threshold]
                results_df = results_df.sort_values("Similarity", ascending=False)

            if results_df.empty:
                st.warning(f"No VOCs found with similarity ≥ {threshold}")
            else:
                st.success(f"Found **{len(results_df)}** VOCs with similarity ≥ {threshold}")

                # Bar chart
                fig = px.bar(
                    results_df,
                    x="Similarity", y="VOC",
                    color="Bioactivity",
                    color_discrete_map={
                        "Attractant": "#22c55e",
                        "Repellent":  "#ef4444",
                    },
                    orientation="h",
                    text="Similarity",
                    hover_data=["Class", "Formula", "Insect"],
                )
                fig.update_traces(
                    texttemplate="%{text:.3f}", textposition="outside"
                )
                fig.add_vline(
                    x=0.4, line_dash="dash", line_color="#f59e0b",
                    annotation_text="Similar (0.4)",
                )
                fig.update_layout(
                    height=max(250, len(results_df) * 40),
                    margin=dict(t=10, b=10, l=10, r=60),
                    xaxis=dict(range=[0, 1.15]),
                    font=dict(family="Inter"),
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True)

                # ── Top 4 structures via PubChem ──────────────────────────────
                st.markdown("**Top 4 Most Similar Structures**")
                top4 = results_df.head(4)
                cols = st.columns(min(4, len(top4)))
                for col, (_, row) in zip(cols, top4.iterrows()):
                    with col:
                        img_url = get_structure_image_url(
                            pubchem_cid=row["CID"],
                            smiles=row["SMILES"],
                            width=240, height=160,
                        )
                        if img_url:
                            st.image(img_url, use_container_width=True)
                        bio_c = (
                            "#22c55e"
                            if row["Bioactivity"] == "Attractant"
                            else "#ef4444"
                        )
                        st.markdown(
                            f"**{row['VOC']}**  \n"
                            f'<span style="color:{bio_c};font-weight:700">'
                            f'{row["Similarity"]:.3f}</span>',
                            unsafe_allow_html=True,
                        )

                # Full results table
                st.markdown("**All Results**")
                def color_bio(val):
                    if val == "Attractant":
                        return "background-color:#d1fae5;color:#065f46;font-weight:600"
                    elif val == "Repellent":
                        return "background-color:#fee2e2;color:#991b1b;font-weight:600"
                    return ""

                display = results_df.drop(columns=["SMILES", "CID"]).copy()
                display["Similarity"] = display["Similarity"].apply(
                    lambda x: f"{x:.4f}"
                )
                st.dataframe(
                    display.style.map(color_bio, subset=["Bioactivity"]),
                    use_container_width=True, hide_index=True,
                )

    # ── Tab 2: full pairwise heatmap ──────────────────────────────────────────
    with tab2:
        st.markdown("**Pairwise Tanimoto Similarity Matrix — All VOCs**")
        st.caption("Computed using Morgan fingerprints (radius=2, 2048 bits)")

        with st.spinner("Computing full similarity matrix..."):
            smiles_list = VOCS["smiles"].tolist()
            names = [
                (n[:22] + "…" if len(n) > 22 else n)
                for n in VOCS["name"].tolist()
            ]
            mat = similarity_matrix(smiles_list, names)

        fig_heat = px.imshow(
            mat,
            color_continuous_scale=["#f0fdf4", "#1a3a2a"],
            zmin=0, zmax=1,
            text_auto=".2f",
            aspect="auto",
            labels=dict(color="Tanimoto"),
        )
        fig_heat.update_layout(
            height=550,
            margin=dict(t=10, b=80, l=10, r=10),
            font=dict(family="Inter", size=9),
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_tickangle=-40,
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("""
        **Interpretation guide**
        - **1.00** = Identical structure · **0.85+** = Very similar
        - **0.40–0.85** = Structurally related · **< 0.40** = Structurally distinct
        """)
