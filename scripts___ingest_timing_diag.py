"""Diagnose where Chowilla ingest spends time (unbuffered, step-timed)."""
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

t0 = time.time()
def mark(msg):
    print(f"[{time.time()-t0:7.2f}s] {msg}", flush=True)

mark("import lsg.config ...")
from lsg.config import load_config
mark("import lsg.data ...")
from lsg.data import detect_real_event_data
mark("import lsg.fraehr ...")
from lsg.fraehr import ingest_fraehr_case

mark("load_config chowilla.yaml")
cfg = load_config("config/chowilla.yaml")
mark("detect_real_event_data")
st = detect_real_event_data(cfg)
mark(f"detect done: case_root={st.get('case_root')} available={st.get('available')}")
case_root = Path(st["case_root"])
mark("ingest_fraehr_case (max)")
data = ingest_fraehr_case(case_root, threshold_m=0.03, time_reduction="max")
mark(f"ingest done: hf_depth shape={data['hf_depth'].shape} n_events={len(data['event_ids'])}")
mark("DONE")
