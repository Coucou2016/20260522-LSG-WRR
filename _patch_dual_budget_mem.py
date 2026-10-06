from pathlib import Path

path = Path("lsg/diagnostics.py")
text = path.read_text(encoding="utf-8")
start = text.find("def combine_dual_stage_depth(")
end = text.find("\ndef dual_oracle_error_budget(", start)
if start < 0 or end < 0:
    raise SystemExit(f"anchors missing start={start} end={end}")
end2 = text.find("\ndef interpolate_wet_pair(", end)
if end2 < 0:
    raise SystemExit("end2 missing")

new_combine = '''def combine_dual_stage_depth(
    ext_tf: np.ndarray,
    wse_wet: np.ndarray,
    dual: Any,
    terrain: np.ndarray,
    dry_threshold_m: float,
    *,
    wet_only: bool = False,
    time_chunk: int = 256,
) -> np.ndarray:
    """Gate EXT+WSE into depth (mirrors ``predict_dual_depth``).

    When ``wet_only`` is True, return ``(n, n_wet)`` on ``dual.wse.wet_idx`` only,
    avoiding full-mesh temporaries (needed for LSG-TS oracle budgets).
    """
    from lsg.wse_ext import wse_to_depth

    terrain = np.asarray(terrain, dtype=np.float64).reshape(-1)
    ext_tf = np.asarray(ext_tf, dtype=np.float64)
    wse_wet = np.asarray(wse_wet, dtype=np.float64)
    n = int(ext_tf.shape[0])
    n_cells = int(terrain.size)
    tf_idx = np.asarray(dual.ext.wet_idx, dtype=np.int64)
    wet_idx = np.asarray(dual.wse.wet_idx, dtype=np.int64)
    af = np.asarray(dual.af_idx, dtype=np.int64)
    thr = float(dual.extent_binary_threshold)
    chunk = max(1, int(time_chunk))

    if not wet_only:
        ext_full = np.zeros((n, n_cells), dtype=np.float64)
        ext_full[:, tf_idx] = ext_tf
        if af.size:
            ext_full[:, af] = 1.0
        ext_bin = ext_full >= thr
        del ext_full
        wse_full = np.broadcast_to(terrain, (n, n_cells)).copy()
        wet_z = terrain[wet_idx]
        recon = np.where(wse_wet > wet_z + dry_threshold_m, wse_wet, wet_z)
        wse_full[:, wet_idx] = recon
        wse_gated = np.where(ext_bin, wse_full, terrain)
        del ext_bin, wse_full
        return wse_to_depth(wse_gated, terrain, dry_threshold_m)

    # Wet-only path: map EXT onto WSE wet cells without (n, n_cells) buffers.
    n_wet = int(wet_idx.size)
    wet_z = terrain[wet_idx]
    wet_inv = np.full(n_cells, -1, dtype=np.int64)
    wet_inv[wet_idx] = np.arange(n_wet, dtype=np.int64)
    out = np.empty((n, n_wet), dtype=np.float64)
    for s in range(0, n, chunk):
        e = min(n, s + chunk)
        ext_wet = np.zeros((e - s, n_wet), dtype=np.float64)
        cols = wet_inv[tf_idx]
        mask = cols >= 0
        if np.any(mask):
            ext_wet[:, cols[mask]] = ext_tf[s:e, mask]
        if af.size:
            cols_af = wet_inv[af]
            mask_af = cols_af >= 0
            if np.any(mask_af):
                ext_wet[:, cols_af[mask_af]] = 1.0
        ext_bin = ext_wet >= thr
        recon = np.where(
            wse_wet[s:e] > wet_z + dry_threshold_m, wse_wet[s:e], wet_z
        )
        wse_gated = np.where(ext_bin, recon, wet_z)
        depth = wse_gated - wet_z
        out[s:e] = np.where(depth < dry_threshold_m, 0.0, depth)
    return out


'''

new_dual = '''def dual_oracle_error_budget(
    dual: Any,
    hf_ext: np.ndarray,
    lf_ext: np.ndarray,
    hf_wse: np.ndarray,
    lf_wse: np.ndarray,
    hf_depth_full: np.ndarray,
    terrain: np.ndarray,
    *,
    split: str = "test",
    dry_threshold_m: float | None = None,
) -> dict[str, Any]:
    """Matched EXT+WSE O1–O4 scored as gated depth RMSE on ``dual.wet_idx``."""
    dry = (
        float(dry_threshold_m)
        if dry_threshold_m is not None
        else float(dual.depth_threshold_m)
    )
    terrain = np.asarray(terrain, dtype=np.float64).reshape(-1)
    wet_idx = np.asarray(dual.wet_idx, dtype=np.int64)

    ext_stages = _branch_oracle_stages(dual.ext, hf_ext, lf_ext)
    wse_stages = _branch_oracle_stages(dual.wse, hf_wse, lf_wse)
    k_ext = int(ext_stages.pop("n_modes"))
    k_wse = int(wse_stages.pop("n_modes"))

    # Wet-only + one stage at a time (LSG-TS full-mesh cubes OOMed at ~9 GiB).
    truth = np.asarray(hf_depth_full, dtype=np.float64)[:, wet_idx]
    depth_stages: dict[str, np.ndarray | None] = {}
    for name in ("o1", "o2", "o3", "o4"):
        ext_f = ext_stages.get(name)
        wse_f = wse_stages.get(name)
        if ext_f is None or wse_f is None:
            depth_stages[name] = None
            continue
        depth_wet = combine_dual_stage_depth(
            ext_f, wse_f, dual, terrain, dry, wet_only=True
        )
        ext_stages[name] = None
        wse_stages[name] = None
        depth_stages[name] = depth_wet
        # Drop finished stage arrays before allocating the next.
        del depth_wet

    n_modes_full = int(dual.wse.eof_modes_full.shape[0]) if (
        getattr(dual.wse, "eof_modes_full", None) is not None
        and np.asarray(dual.wse.eof_modes_full).size
    ) else int(dual.wse.n_modes)
    row = _score_oracle_depth_stages(
        depth_stages,
        truth,
        n_modes=k_wse,
        n_modes_full=n_modes_full,
        split=split,
        threshold_m=dry,
        notes=DUAL_BUDGET_NOTE,
    )
    row["n_modes_ext"] = k_ext
    row["n_modes_wse"] = k_wse
    return row


'''

# Still holding all 4 depth_stages - for TS that's ~16GB. Score incrementally instead.
new_dual = '''def dual_oracle_error_budget(
    dual: Any,
    hf_ext: np.ndarray,
    lf_ext: np.ndarray,
    hf_wse: np.ndarray,
    lf_wse: np.ndarray,
    hf_depth_full: np.ndarray,
    terrain: np.ndarray,
    *,
    split: str = "test",
    dry_threshold_m: float | None = None,
) -> dict[str, Any]:
    """Matched EXT+WSE O1–O4 scored as gated depth RMSE on ``dual.wet_idx``."""
    dry = (
        float(dry_threshold_m)
        if dry_threshold_m is not None
        else float(dual.depth_threshold_m)
    )
    terrain = np.asarray(terrain, dtype=np.float64).reshape(-1)
    wet_idx = np.asarray(dual.wet_idx, dtype=np.int64)

    ext_stages = _branch_oracle_stages(dual.ext, hf_ext, lf_ext)
    wse_stages = _branch_oracle_stages(dual.wse, hf_wse, lf_wse)
    k_ext = int(ext_stages.pop("n_modes"))
    k_wse = int(wse_stages.pop("n_modes"))

    truth = _clip(np.asarray(hf_depth_full, dtype=np.float64)[:, wet_idx], dry)
    o_rmse: dict[str, float | None] = {}
    n_samples = int(truth.shape[0])
    n_cells = int(truth.shape[1])
    for name in ("o1", "o2", "o3", "o4"):
        ext_f = ext_stages.pop(name, None)
        wse_f = wse_stages.pop(name, None)
        if ext_f is None or wse_f is None:
            o_rmse[name] = None
            continue
        depth_wet = combine_dual_stage_depth(
            ext_f, wse_f, dual, terrain, dry, wet_only=True
        )
        del ext_f, wse_f
        o_rmse[name] = float(_rmse(_clip(depth_wet, dry), truth))
        del depth_wet

    n_modes_full = int(dual.wse.eof_modes_full.shape[0]) if (
        getattr(dual.wse, "eof_modes_full", None) is not None
        and np.asarray(dual.wse.eof_modes_full).size
    ) else int(dual.wse.n_modes)
    o1 = o_rmse["o1"]
    o2 = o_rmse["o2"]
    row = {
        "split": split,
        "n_samples": n_samples,
        "n_cells": n_cells,
        "n_modes": int(k_wse),
        "n_modes_full": n_modes_full,
        "in_sample_full_rank": bool(k_wse >= n_samples and split == "train"),
        "o1_rmse": o1,
        "o2_rmse": o2,
        "o3_rmse": o_rmse["o3"],
        "o4_rmse": o_rmse["o4"],
        "o2_minus_o1": None if o1 is None or o2 is None else float(o2 - o1),
        "notes": DUAL_BUDGET_NOTE,
        "n_modes_ext": k_ext,
        "n_modes_wse": k_wse,
    }
    return row


'''

path.write_text(text[:start] + new_combine + new_dual + text[end2 + 1 :], encoding="utf-8")
print("PATCHED", start, end, end2)
