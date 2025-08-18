import numpy as np
import sys
import json

def cronbach_alpha(data):
    """Compute Cronbach's alpha for a 2D numpy array (rows = participants, cols = items)."""
    k = data.shape[1]  # number of items
    item_variances = data.var(axis=0, ddof=1)
    total_variance = data.sum(axis=1).var(ddof=1)
    if total_variance == 0:
        return np.nan
    alpha = (k / (k - 1)) * (1 - (item_variances.sum() / total_variance))
    return alpha

def alpha_if_deleted(data):
    """Return Cronbach's alpha if each item is deleted."""
    k = data.shape[1]
    alphas = []
    for i in range(k):
        reduced_data = np.delete(data, i, axis=1)
        alphas.append(cronbach_alpha(reduced_data))
    return alphas

def main():
    if len(sys.argv) != 2:
        print("Usage: python alpha_if_deleted.py datafile.txt")
        sys.exit(1)

    filepath = sys.argv[1]

    # Load input file (expects JSON-like matrix, as in your example)
    with open(filepath, "r") as f:
        matrix = json.load(f)

    data = np.array(matrix, dtype=float)

    # Compute overall alpha
    overall_alpha = cronbach_alpha(data)
    print(f"Overall Cronbach's alpha = {overall_alpha:.4f}")

    # Compute alpha if deleted
    alphas_deleted = alpha_if_deleted(data)
    print("\nCronbach's alpha if item deleted:")
    for i, a in enumerate(alphas_deleted, start=1):
        print(f"Item {i:2d}: {a:.4f}")

if __name__ == "__main__":
    main()
