"""Rebuild Chowilla pred_examples.npz from the saved H-LSG state (no retrain).

The artifact was overwritten by a later global-model run on 2026-08-16, so the
spatial figures (Fig 2b/3b/4b) showed global-model predictions under H-LSG
captions. This script regenerates the artifact from the restored H-LSG state
and verifies it against the archived workflow summary numbers.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lsg import evaluation  # noqa: E402
from lsg.config import load_config, resolve_path  # noqa: E402
from lsg.data import resolve_train_test_indices  # noqa: E402
from lsg.lsg_max import LSGMaxModel  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "run_lsg_workflow", _ROOT / "scripts" / "run_lsg_workflow.py"
)
assert _spec is not None and _spec.loader is not None
_wf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_wf)
_load_data = _wf._load_data
_mesh_args = _wf._mesh_args


class _Args:
    synthetic = False
    regenerate_synthetic = False
    data = None
    events = None
    lf_resolution = None
    time_reduction = None


def main() -> None:
    cfg = load_config(_ROOT / "config" / "chowilla.yaml")
    models_dir = resolve_path(cfg, "models")
    out_dir = resolve_path(cfg, "evaluation")

    data, real_status = _load_data(cfg, _Args())
    if not real_status.get("available"):
        raise SystemExit("Real Fraehr data required")
    hf, lf = data["hf_depth"], data["lf_depth"]
    terrain = data["terrain_hf"]
    shape_hf, shape_lf = data["shape_hf"], data["shape_lf"]
    event_ids = [str(e) for e in data["event_ids"]]
    mesh = _mesh_args(data)

    state_path = models_dir / "lsg_max_state.npz"
    train_idx, test_idx, split_name = resolve_train_test_indices(
        event_ids, cfg, "lsg_max"
    )
    print(f"[regen] split={split_name} n_train={train_idx.size} n_test={test_idx.size}")
    model = LSGMaxModel.load_from(state_path, cfg)

    # LF max surface upsampled to HF mesh, same convention as run_lsg_workflow.
    from lsg.spatial import interpolate_lf_to_hf

    lf_max_up = np.nanmax(lf[test_idx], axis=1)
    hf_max = np.nanmax(hf[test_idx], axis=1)
    lf_up = interpolate_lf_to_hf(
        lf_max_up,
        shape_lf,
        shape_hf,
        terrain,
        xy_hf=mesh.get("xy_hf"),
        xy_lf=mesh.get("xy_lf"),
        terrain_lf=mesh.get("terrain_lf"),
    )
    pred_max = model.predict(
        lf[test_idx],
        terrain,
        shape_hf,
        shape_lf,
        xy_hf=mesh.get("xy_hf"),
        xy_lf=mesh.get("xy_lf"),
        terrain_lf=mesh.get("terrain_lf"),
    )

    thresh = float(cfg["hydrodynamic"]["depth_threshold_m"])
    wet_idx = np.load(state_path)["wet_idx"]

    sp = evaluation.dual_score_max_surface(pred_max, hf_max, wet_idx, thresh, extent_gate=lf_up)
    print("[regen] score_protocol.lsg_max:")
    for dom in ("all_cells", "wet_train"):
        d = sp[dom]
        print(f"  {dom}: csi={d['csi']:.4f} rmse={d['rmse']:.4f}")
    expect = {"all_cells": (0.3902, 3.7891), "wet_train": (0.9756, 0.0932)}
    for dom, (csi, rmse) in expect.items():
        got = (round(sp[dom]["csi"], 4), round(sp[dom]["rmse"], 4))
        if abs(got[0] - csi) > 1e-4 or abs(got[1] - rmse) > 1e-3:
            raise SystemExit(f"verification FAILED for {dom}: {got} != {(csi, rmse)}")
    print("[regen] verification PASSED (matches archived hlsg_max summary)")

    lf_sp = evaluation.dual_score_max_surface(lf_up, hf_max, wet_idx, thresh)
    print(
        f"[regen] lf_only: all csi={lf_sp['all_cells']['csi']:.4f} "
        f"wet csi={lf_sp['wet_train']['csi']:.4f} wet rmse={lf_sp['wet_train']['rmse']:.4f}"
    )

    test_ids = [event_ids[i] for i in test_idx.tolist()]
    payload = {
        "terrain_hf": terrain,
        "shape_hf": np.array(shape_hf),
        "shape_lf": np.array(shape_lf),
        "test_ids": np.array(test_ids),
        "hf_max": hf_max,
        "pred_lsg_max": pred_max,
        "lf_upsampled_max": lf_up,
        "data_mode": np.array("real"),
        "wet_idx": wet_idx,
    }
    # The Chowilla runs use max-only time reduction, so the LSG-TS variant is
    # trained on the same maximum surfaces and its derived max surface equals
    # the LSG-Max prediction (the archived H-LSG run produced bit-identical
    # lsg_max/lsg_ts score blocks for this case). The saved TS state on disk
    # originates from a later global-era run, so it must not be reloaded here.
    payload["pred_lsg_ts_max"] = pred_max
    print("[regen] pred_lsg_ts_max = pred_lsg_max (max-only TS degeneracy)")

    out_path = out_dir / "pred_examples.npz"
    np.savez_compressed(out_path, **payload)
    print(f"[regen] wrote {out_path}")


if __name__ == "__main__":
    main()
