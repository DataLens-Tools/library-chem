# 🌿 VOC·BIO Library
### Cheminformatics-Enhanced VOC–Insect–Plant Interaction Database

A Streamlit-based research tool for exploring Volatile Organic Compounds (VOCs)
emitted by insects and host plants, their bioassay outcomes (attractant/repellent),
and their ecological roles in insect–plant–natural enemy interactions.



##  Installation

```bash
# 1. Clone / place the project folder
cd voc_library

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```



##  Project Structure

```
voc_library/
├── app.py                    # Main entry point & navigation
├── requirements.txt
├── data/
│   └── sample_data.py        # Sample VOC, insect, plant & bioassay records
├── utils/
│   └── chem_utils.py         # RDKit cheminformatics utilities
└── pages/
    ├── dashboard.py          # Overview statistics & charts
    ├── voc_library.py        # Filterable VOC table + card view
    ├── molecule_explorer.py  # Full cheminformatics profile per compound
    ├── insect_plant.py       # Insect & host plant databases + interaction matrix
    ├── bioassay.py           # Bioassay results, effect sizes, significance
    ├── network.py            # Semiochemical knowledge graph
    └── similarity.py         # Morgan fingerprint Tanimoto similarity search
```



##  Features

| Feature | Description |
|---|---|
| **VOC Library** | Browse/filter VOCs by class, bioactivity, insect, plant |
| **Molecule Explorer** | 2D structure rendering, RDKit descriptors, radar chart, volatility profile |
| **Insect–Plant DB** | Species tables, interaction matrix heatmap |
| **Bioassay Results** | Effect size charts, dose–response, p-value significance |
| **Interaction Network** | NetworkX + Plotly knowledge graph: VOC↔Insect↔Plant↔Enemy |
| **Similarity Search** | Tanimoto search by query SMILES or library compound; full pairwise matrix |



##  Adding Your Own Data

Edit `data/sample_data.py` and add rows to the `VOCS`, `INSECTS`, `PLANTS`,
and `BIOASSAYS` DataFrames. Each VOC requires at minimum:
- `smiles` — canonical SMILES string
- `name`, `formula`, `class`
- `bioactivity` — `"Attractant"` or `"Repellent"`
- `insect`, `plant`



##  Tech Stack

- **Streamlit** — UI framework
- **RDKit** — Cheminformatics engine (structure rendering, descriptors, fingerprints)
- **Plotly** — Interactive charts
- **NetworkX** — Graph/network analysis
- **Pandas** — Data manipulation



##  Data Sources & References

Sample data based on published literature including:
- Al-Zahrani et al. (2023), Hassan et al. (2022), Siddiqui et al. (2023)
- James & Price (2004), Turlings & Wäckers (2004)
- PheroBase, PubChem, NIST Chemistry WebBook



*Developed as a collaborative research tool for insect–plant VOC interaction research.*
