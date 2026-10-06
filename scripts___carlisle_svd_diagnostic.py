"""Major-3 diagnostic: singular values of the Carlisle max-surface training matrix.

Reports whether the mean-centered 8-event training matrix is rank 8 or rank 7
(the 8th singular value should be ~0 if mean-centering costs one rank).
"""
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from lsg.config import load_config
from lsg.data import detect_real_event_data
from lsg.fraehr import ingest_fraehr_case

cfg = load_config("config/carlisle.yaml")
st = detect_real_event_data(cfg)
case_root = Path(st["case_root"])

data = ingest_fraehr_case(case_root, threshold_m=0.03, time_reduction="max")
hf = data["hf_depth"]  # (n_events, n_cells) or (n_events, 1, n_cells)
hf = np.asarray(hf, dtype=np.float64)
if hf.ndim == 3:
    hf = hf[:, 0, :]
ids = [str(e) for e in data["event_ids"]]
print("event order:", ids)
print("hf shape:", hf.shape)

# lsg_max train = E2..E9 (8 events), test = E1. Mean-center the training block.
from lsg.data import resolve_train_test_indices

train_idx, test_idx, split = resolve_train_test_indices(ids, cfg, "lsg_max")
print("split:", split, "train:", [ids[i] for i in train_idx.tolist()])
print("test:", [ids[i] for i in test_idx.tolist()])

X = np.asarray(hf[train_idx], dtype=np.float64)
print("train matrix shape:", X.shape)
if X.ndim == 3:
    X = X[:, 0, :]
mu = X.mean(axis=0)
C = X - mu
u, s, vt = np.linalg.svd(C, full_matrices=False)
print("\nSingular values of mean-centered training matrix:")
for i, si in enumerate(s, 1):
    print(f"  s{i} = {si:.6e}   ratio to s1 = {si / s[0]:.3e}")
print(f"\nRank under eps*s1 tolerance (eps=1e-12): {(s > 1e-12 * s[0]).sum()}")
print(f"Rank under eps*s1 tolerance (eps=1e-10): {(s > 1e-10 * s[0]).sum()}")
print(f"Rank under eps*s1 tolerance (eps=1e-8):  {(s > 1e-8 * s[0]).sum()}")
