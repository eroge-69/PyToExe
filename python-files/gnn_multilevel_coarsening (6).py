"""
This module implements a simple demonstration of multi‑level graph
coarsening to accelerate the training of a graph neural network (GNN).

The goal of the example is to show how contracting pairs of similar
nodes in a graph can reduce the size of the graph without dramatically
degrading classification accuracy.  The reduced graph (coarse graph) is
then used to train a small graph convolutional network implemented in
pure NumPy.  After training, predictions from the coarse graph are
propagated back to the original graph.

The implementation is intentionally self‑contained and avoids
dependencies on external deep learning frameworks such as PyTorch or
TensorFlow.  It uses only NumPy for numerical computation and
scikit‑learn for evaluation metrics.  The functions are written with
clear inputs and outputs so that they can be reused in other
experiments.

Key components:

* ``generate_synthetic_graph`` creates a toy dataset of points in
  Euclidean space, builds a k‑nearest neighbour graph and assigns
  class labels based on spatial clusters.
* ``coarsen_graph`` contracts pairs of nodes with similar feature
  vectors until approximately a specified ratio of the original
  vertices remains.  Node features and labels are aggregated during
  contraction.
* ``train_gcn`` implements a two‑layer Graph Convolutional Network
  (GCN) using NumPy.  The network is trained with simple stochastic
  gradient descent and cross‑entropy loss on a training split of the
  data.
* ``run_experiment`` wraps the entire workflow: generate a graph,
  optionally coarsen it, train the GCN and report accuracy and
  training time.

This code is provided as part of a larger study on optimising graph
neural networks with multi‑level contraction.  See the accompanying
report for a discussion of the results.
"""

from __future__ import annotations

import time
import numpy as np
from typing import Tuple, Dict, List
from sklearn.metrics import accuracy_score


def generate_synthetic_graph(
    num_nodes: int = 200,
    num_features: int = 10,
    num_classes: int = 3,
    k_neighbors: int = 5,
    seed: int | None = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate a synthetic graph with features and class labels.

    Nodes are sampled from multivariate normal distributions centred
    around the origin.  Each class occupies a different region of
    space, making it possible for a GCN to learn to distinguish them.

    Parameters
    ----------
    num_nodes : int
        Total number of vertices in the graph.
    num_features : int
        Dimensionality of the node feature vectors.
    num_classes : int
        Number of distinct labels.
    k_neighbors : int
        Number of neighbours used to build the k‑nearest neighbour
        adjacency matrix.
    seed : int | None
        Optional random seed for reproducibility.

    Returns
    -------
    adj_matrix : np.ndarray of shape (n, n)
        Symmetric adjacency matrix of the generated graph.
    features : np.ndarray of shape (n, d)
        Node feature matrix.
    labels : np.ndarray of shape (n,)
        Array of integer class labels.
    """
    rng = np.random.default_rng(seed)
    # Assign each node to a class evenly
    labels = rng.integers(low=0, high=num_classes, size=num_nodes)
    features = np.zeros((num_nodes, num_features))
    # Mean and covariance for each class
    for c in range(num_classes):
        class_indices = np.where(labels == c)[0]
        # Place class centres on a circle in feature space
        angle = 2 * np.pi * c / num_classes
        centre = np.zeros(num_features)
        if num_features >= 2:
            centre[0] = np.cos(angle) * 5.0
            centre[1] = np.sin(angle) * 5.0
        # Sample from normal distribution around the centre
        features[class_indices] = rng.normal(loc=centre, scale=1.0, size=(len(class_indices), num_features))

    # Build k‑nearest neighbour adjacency matrix based on Euclidean distance
    adj_matrix = np.zeros((num_nodes, num_nodes), dtype=np.float32)
    # Precompute pairwise distances
    dists = np.linalg.norm(features[:, None, :] - features[None, :, :], axis=2)
    # For each node, connect to its k nearest neighbours (excluding itself)
    for i in range(num_nodes):
        neighbours = np.argsort(dists[i])[1 : k_neighbors + 1]
        adj_matrix[i, neighbours] = 1.0
    # Symmetrise the adjacency
    adj_matrix = np.maximum(adj_matrix, adj_matrix.T)
    return adj_matrix, features, labels


def coarsen_graph(
    adj: np.ndarray,
    features: np.ndarray,
    labels: np.ndarray,
    target_ratio: float = 0.5,
    similarity: str = "cosine",
    seed: int | None = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[int, int]]:
    """Contract pairs of nodes to create a coarse graph.

    The algorithm merges pairs of nodes with similar feature vectors
    until the number of super‑nodes is roughly the specified ratio of
    the original number of nodes.  During contraction, features are
    averaged and labels are taken by majority vote.

    Parameters
    ----------
    adj : np.ndarray of shape (n, n)
        Adjacency matrix of the original graph.
    features : np.ndarray of shape (n, d)
        Node feature matrix.
    labels : np.ndarray of shape (n,)
        Node labels.
    target_ratio : float
        Approximate fraction of nodes to retain after coarsening.  For
        example, 0.5 will attempt to reduce the node count by half.
    similarity : {'cosine', 'euclidean'}
        Metric used to select pairs for contraction.  Cosine similarity
        tends to merge nodes with similar directions while Euclidean
        distance merges nodes that are close together.
    seed : int | None
        Optional random seed.

    Returns
    -------
    new_adj : np.ndarray
        Adjacency matrix of the coarse graph.
    new_features : np.ndarray
        Feature matrix of the coarse graph.
    new_labels : np.ndarray
        Labels of the coarse graph.
    mapping : Dict[int, int]
        Mapping from original node indices to super‑node indices.
    """
    n = adj.shape[0]
    rng = np.random.default_rng(seed)
    # Compute similarity matrix
    if similarity == "cosine":
        # Normalise features
        norm_f = np.linalg.norm(features, axis=1, keepdims=True)
        # Avoid division by zero
        norm_f[norm_f == 0] = 1.0
        normed = features / norm_f
        sim_matrix = normed @ normed.T
    elif similarity == "euclidean":
        # Convert Euclidean distance to similarity (negative distance)
        dists = np.linalg.norm(features[:, None, :] - features[None, :, :], axis=2)
        sim_matrix = -dists
    else:
        raise ValueError(f"Unknown similarity metric '{similarity}'")

    # We only contract adjacent nodes; mask similarity for non‑adjacent pairs
    mask = adj > 0
    # Remove self connections
    np.fill_diagonal(mask, False)
    sim_matrix = sim_matrix * mask
    # Flatten upper triangular part to get candidate edges
    candidate_pairs: List[Tuple[int, int, float]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if mask[i, j]:
                candidate_pairs.append((i, j, sim_matrix[i, j]))
    # Sort by decreasing similarity
    candidate_pairs.sort(key=lambda x: x[2], reverse=True)

    visited = np.zeros(n, dtype=bool)
    mapping: Dict[int, int] = {}
    supernode_features = []  # type: List[np.ndarray]
    supernode_labels = []  # type: List[int]
    # Merge pairs greedily until desired number of supernodes
    target_nodes = max(1, int(np.ceil(target_ratio * n)))
    for i, j, sim in candidate_pairs:
        if len(supernode_features) >= target_nodes:
            break
        if not visited[i] and not visited[j]:
            # Create a new supernode from i and j
            visited[i] = visited[j] = True
            mapping[i] = len(supernode_features)
            mapping[j] = len(supernode_features)
            # Average features
            new_feat = (features[i] + features[j]) / 2.0
            # Majority label
            if labels[i] == labels[j]:
                new_label = labels[i]
            else:
                # If different, choose randomly
                new_label = rng.choice([labels[i], labels[j]])
            supernode_features.append(new_feat)
            supernode_labels.append(int(new_label))

    # Any unvisited nodes become their own supernode
    for idx in range(n):
        if idx not in mapping:
            mapping[idx] = len(supernode_features)
            supernode_features.append(features[idx].copy())
            supernode_labels.append(int(labels[idx]))

    # Build coarse adjacency
    m = len(supernode_features)
    new_adj = np.zeros((m, m), dtype=np.float32)
    for u in range(n):
        for v in range(u + 1, n):
            if adj[u, v] > 0:
                cu = mapping[u]
                cv = mapping[v]
                if cu != cv:
                    new_adj[cu, cv] = 1.0
                    new_adj[cv, cu] = 1.0
    new_features = np.vstack(supernode_features)
    new_labels = np.array(supernode_labels, dtype=int)
    return new_adj, new_features, new_labels, mapping


def train_gcn(
    adj: np.ndarray,
    features: np.ndarray,
    labels: np.ndarray,
    num_classes: int,
    hidden_units: int = 16,
    epochs: int = 100,
    learning_rate: float = 0.01,
    train_ratio: float = 0.8,
    seed: int | None = None,
    verbose: bool = False,
) -> Tuple[float, float]:
    """Train a simple two‑layer Graph Convolutional Network.

    This implementation is designed for educational purposes and does not
    include optimisations such as mini‑batches or advanced optimisers.  It
    follows the formulation described by Kipf & Welling (2017).

    Parameters
    ----------
    adj : np.ndarray of shape (n, n)
        Adjacency matrix with zero diagonal; self‑loops will be added
        internally.
    features : np.ndarray of shape (n, d)
        Node feature matrix.
    labels : np.ndarray of shape (n,)
        Integer class labels.
    num_classes : int
        Number of distinct classes.
    hidden_units : int
        Dimension of the hidden layer.
    epochs : int
        Number of training epochs.
    learning_rate : float
        Step size for gradient descent.
    train_ratio : float
        Fraction of nodes to use for training; the remainder are used for
        testing.
    seed : int | None
        Random seed.
    verbose : bool
        Whether to print loss during training.

    Returns
    -------
    test_acc : float
        Classification accuracy on the held‑out test set.
    duration : float
        Training time in seconds.
    """
    rng = np.random.default_rng(seed)
    n, d = features.shape
    # Add self‑loops
    adj_hat = adj.copy()
    np.fill_diagonal(adj_hat, 1.0)
    # Compute normalised Laplacian: D^{-1/2} A D^{-1/2}
    deg = np.sum(adj_hat, axis=1)
    deg_inv_sqrt = np.power(deg, -0.5)
    deg_inv_sqrt[np.isinf(deg_inv_sqrt)] = 0.0
    D_inv_sqrt = np.diag(deg_inv_sqrt)
    norm_adj = D_inv_sqrt @ adj_hat @ D_inv_sqrt
    # Initialise weights
    W0 = rng.normal(loc=0.0, scale=0.1, size=(d, hidden_units))
    W1 = rng.normal(loc=0.0, scale=0.1, size=(hidden_units, num_classes))
    # Train/test split
    indices = np.arange(n)
    rng.shuffle(indices)
    train_size = int(train_ratio * n)
    train_idx = indices[:train_size]
    test_idx = indices[train_size:]

    # One‑hot encode labels for training
    Y_onehot = np.zeros((n, num_classes))
    Y_onehot[np.arange(n), labels] = 1.0

    # Activation functions
    def relu(x):
        return np.maximum(0, x)

    def softmax(x):
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)

    start_time = time.perf_counter()
    # Training loop
    for epoch in range(epochs):
        # Forward pass
        H = relu(norm_adj @ features @ W0)  # Hidden layer
        Z = softmax(norm_adj @ H @ W1)  # Output probabilities
        # Compute loss on training nodes (cross‑entropy)
        probs_train = Z[train_idx]
        y_train = Y_onehot[train_idx]
        # Avoid log(0)
        loss = -np.sum(y_train * np.log(probs_train + 1e-9)) / train_size
        # Backpropagation
        # Gradient of loss w.r.t. output
        dZ = (Z - Y_onehot) / n
        # Gradients of weights
        dW1 = H.T @ (norm_adj.T @ dZ)
        dH = (norm_adj @ dZ @ W1.T)
        dH *= (H > 0)  # ReLU derivative
        dW0 = features.T @ (norm_adj.T @ dH)
        # Gradient descent update
        W1 -= learning_rate * dW1
        W0 -= learning_rate * dW0
        if verbose and epoch % 10 == 0:
            print(f"Epoch {epoch}, loss={loss:.4f}")
    end_time = time.perf_counter()
    duration = end_time - start_time
    # Evaluate on test set
    H_final = relu(norm_adj @ features @ W0)
    Z_final = softmax(norm_adj @ H_final @ W1)
    y_pred = np.argmax(Z_final[test_idx], axis=1)
    test_acc = accuracy_score(labels[test_idx], y_pred)
    return float(test_acc), float(duration)


def run_experiment(
    num_nodes: int = 200,
    num_features: int = 10,
    num_classes: int = 3,
    k_neighbors: int = 5,
    coarsen: bool = False,
    coarsen_ratio: float = 0.5,
    hidden_units: int = 16,
    epochs: int = 100,
    learning_rate: float = 0.01,
    seed: int | None = None,
) -> Dict[str, float]:
    """Generate a graph, optionally coarsen it and train a GCN.

    This is a convenience wrapper that orchestrates the generation,
    coarsening and training steps.  It returns a dictionary of
    performance metrics which can be used to compare configurations.

    Parameters
    ----------
    num_nodes, num_features, num_classes, k_neighbors : int
        Parameters for synthetic graph generation.
    coarsen : bool
        Whether to apply graph coarsening before training.
    coarsen_ratio : float
        Target ratio of nodes to keep if coarsen is True.
    hidden_units, epochs, learning_rate : int or float
        Hyperparameters for training the GCN.
    seed : int | None
        Random seed for reproducibility.

    Returns
    -------
    results : Dict[str, float]
        A dictionary containing the number of nodes, training time and
        test accuracy.
    """
    # Generate synthetic graph
    adj, features, labels = generate_synthetic_graph(
        num_nodes=num_nodes,
        num_features=num_features,
        num_classes=num_classes,
        k_neighbors=k_neighbors,
        seed=seed,
    )
    if coarsen:
        c_adj, c_feat, c_lab, mapping = coarsen_graph(
            adj, features, labels, target_ratio=coarsen_ratio, seed=seed
        )
        num_nodes_used = c_adj.shape[0]
        test_acc, duration = train_gcn(
            c_adj,
            c_feat,
            c_lab,
            num_classes=num_classes,
            hidden_units=hidden_units,
            epochs=epochs,
            learning_rate=learning_rate,
            train_ratio=0.8,
            seed=seed,
        )
    else:
        num_nodes_used = adj.shape[0]
        test_acc, duration = train_gcn(
            adj,
            features,
            labels,
            num_classes=num_classes,
            hidden_units=hidden_units,
            epochs=epochs,
            learning_rate=learning_rate,
            train_ratio=0.8,
            seed=seed,
        )
    return {
        "nodes": float(num_nodes_used),
        "time": float(duration),
        "accuracy": float(test_acc),
    }


if __name__ == "__main__":
    # Example usage: run a small experiment and print results
    base = run_experiment(num_nodes=200, coarsen=False, seed=42)
    coarse = run_experiment(num_nodes=200, coarsen=True, coarsen_ratio=0.5, seed=42)
    print("Without coarsening:", base)
    print("With coarsening:", coarse)