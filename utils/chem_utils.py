"""
Cheminformatics utilities using RDKit
"""

import base64
import io

try:
    from rdkit import Chem
    from rdkit.Chem import Draw, Descriptors, rdMolDescriptors, AllChem, DataStructs
    from rdkit.Chem.Draw import rdMolDraw2D
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


def mol_from_smiles(smiles: str):
    """Parse SMILES string into RDKit mol object."""
    if not RDKIT_AVAILABLE:
        return None
    try:
        mol = Chem.MolFromSmiles(smiles)
        return mol
    except Exception:
        return None


def draw_molecule_svg(smiles: str, width: int = 300, height: int = 200) -> str:
    """Render a molecule as an inline SVG string."""
    if not RDKIT_AVAILABLE:
        return ""
    mol = mol_from_smiles(smiles)
    if mol is None:
        return ""
    try:
        drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
        drawer.drawOptions().addStereoAnnotation = True
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        return svg
    except Exception:
        return ""


def draw_molecule_png_b64(smiles: str, width: int = 300, height: int = 200) -> str:
    """Render molecule as base64 PNG (fallback)."""
    if not RDKIT_AVAILABLE:
        return ""
    mol = mol_from_smiles(smiles)
    if mol is None:
        return ""
    try:
        img = Draw.MolToImage(mol, size=(width, height))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""


def compute_descriptors(smiles: str) -> dict:
    """Compute key molecular descriptors for a VOC."""
    if not RDKIT_AVAILABLE:
        return {}
    mol = mol_from_smiles(smiles)
    if mol is None:
        return {}
    try:
        return {
            "Molecular Weight": round(Descriptors.ExactMolWt(mol), 3),
            "LogP (Wildman-Crippen)": round(Descriptors.MolLogP(mol), 3),
            "TPSA (Å²)": round(Descriptors.TPSA(mol), 3),
            "H-Bond Donors": rdMolDescriptors.CalcNumHBD(mol),
            "H-Bond Acceptors": rdMolDescriptors.CalcNumHBA(mol),
            "Rotatable Bonds": rdMolDescriptors.CalcNumRotatableBonds(mol),
            "Ring Count": rdMolDescriptors.CalcNumRings(mol),
            "Aromatic Rings": rdMolDescriptors.CalcNumAromaticRings(mol),
            "Heavy Atom Count": mol.GetNumHeavyAtoms(),
            "Fraction Csp3": round(rdMolDescriptors.CalcFractionCSP3(mol), 3),
        }
    except Exception:
        return {}


def tanimoto_similarity(smiles1: str, smiles2: str, radius: int = 2) -> float:
    """Compute Tanimoto similarity between two molecules using Morgan fingerprints."""
    if not RDKIT_AVAILABLE:
        return 0.0
    mol1 = mol_from_smiles(smiles1)
    mol2 = mol_from_smiles(smiles2)
    if mol1 is None or mol2 is None:
        return 0.0
    try:
        fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, radius, nBits=2048)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, radius, nBits=2048)
        return round(DataStructs.TanimotoSimilarity(fp1, fp2), 4)
    except Exception:
        return 0.0


def similarity_matrix(smiles_list: list, names: list) -> "pd.DataFrame":
    """Build a pairwise Tanimoto similarity matrix."""
    import pandas as pd
    n = len(smiles_list)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            matrix[i][j] = tanimoto_similarity(smiles_list[i], smiles_list[j])
    return pd.DataFrame(matrix, index=names, columns=names)


def get_lipinski_verdict(smiles: str) -> dict:
    """Assess Lipinski Ro5 and volatility-related rules."""
    if not RDKIT_AVAILABLE:
        return {}
    mol = mol_from_smiles(smiles)
    if mol is None:
        return {}
    mw = Descriptors.ExactMolWt(mol)
    logp = Descriptors.MolLogP(mol)
    hbd = rdMolDescriptors.CalcNumHBD(mol)
    hba = rdMolDescriptors.CalcNumHBA(mol)
    tpsa = Descriptors.TPSA(mol)
    rot = rdMolDescriptors.CalcNumRotatableBonds(mol)

    # VOC-specific volatility indicators
    volatile = mw < 300 and logp < 6 and tpsa < 80
    return {
        "MW < 300 (volatile)": ("✅" if mw < 300 else "❌") + f"  {mw:.1f} g/mol",
        "LogP < 6 (semi-volatile)": ("✅" if logp < 6 else "❌") + f"  {logp:.2f}",
        "TPSA < 80 Å² (airborne)": ("✅" if tpsa < 80 else "❌") + f"  {tpsa:.1f} Å²",
        "H-Bond Donors ≤ 1": ("✅" if hbd <= 1 else "❌") + f"  {hbd}",
        "H-Bond Acceptors ≤ 4": ("✅" if hba <= 4 else "❌") + f"  {hba}",
        "Rotatable Bonds ≤ 10": ("✅" if rot <= 10 else "❌") + f"  {rot}",
        "🧪 VOC Volatility Profile": "HIGH" if volatile else "MODERATE",
    }
