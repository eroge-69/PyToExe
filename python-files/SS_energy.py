#!/usr/bin/env python

from Bio.PDB import PDBParser
from Bio.PDB.Polypeptide import is_aa
from math import sqrt

# Constants
R0 = 1.775  # Equilibrium S–S bond length in Ångströms
K = 100.0  # Spring constant in kcal/(mol·Å²)

def distance(atom1, atom2):
    """Calculate distance between two atoms."""
    return sqrt(sum((atom1.coord - atom2.coord) ** 2))

def harmonic_energy(r, r0=R0, k=K):
    """Calculate harmonic potential energy."""
    return 0.5 * k * (r - r0) ** 2

def find_disulfide_bonds(structure):
    """Find all disulfide bonds in the structure."""
    cysteines = []
    for model in structure:
        for chain in model:
            for residue in chain:
                if is_aa(residue) and residue.get_resname() == 'CYS':
                    if 'SG' in residue:
                        cysteines.append(residue['SG'])

    disulfide_bonds = []
    for i, atom1 in enumerate(cysteines):
        for j in range(i + 1, len(cysteines)):
            atom2 = cysteines[j]
            d = distance(atom1, atom2)
            if 1.9 < d < 2.2:  # Threshold for S–S bond
                disulfide_bonds.append((atom1, atom2, d))
    return disulfide_bonds

def main(pdb_path):
    parser = PDBParser(PERMISSIVE=True)
    structure = parser.get_structure('PDB_structure', pdb_path)
    
    ss_bonds = find_disulfide_bonds(structure)

    total_energy = 0.0
    print(f"Found {len(ss_bonds)} disulfide bond(s):")
    for atom1, atom2, d in ss_bonds:
        e = harmonic_energy(d)
        total_energy += e
        print(f"- Between {atom1.get_parent().get_full_id()} and {atom2.get_parent().get_full_id()}:")
        print(f"  Distance: {d:.2f} Å, Energy: {e:.2f} kcal/mol")

    print(f"\nTotal disulfide bond energy: {total_energy:.2f} kcal/mol")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python disulfide_bond_energy.py <pdb_file>")
    else:
        main(sys.argv[1])