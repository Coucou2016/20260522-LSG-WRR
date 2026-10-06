# Merced River (Yosemite Valley) — HEC-RAS 2D case

Primary independent, fully reproducible case for this study. Official tutorial data only; **this folder does not contain computed inundation rasters.**

## Source

- Tutorial: https://www.hec.usace.army.mil/confluence/rasdocs/hgt/latest/tutorials/2d-unsteady-flow/2d-model-development-and-refinement
- ZIP name: `2D Model Development and Refinement.zip`
- Direct URL (Confluence attachment): https://www.hec.usace.army.mil/confluence/rasdocs/hgt/files/latest/217579855/217579980/1/1729558697904/2D+Model+Development+and+Refinement.zip
- Downloaded: 2026-08-14
- Size: **168 258 405 bytes** (valid ZIP, 79 entries / 72 files after extract)
- Licence / copyright: U.S. Army Corps of Engineers, Hydrologic Engineering Center. Tutorial workshop data. Keep `original/` byte-for-byte; redistribute under USACE/HEC terms.

The workshop builds a 2D model of the **Merced River in Yosemite Valley**. Official computational mesh in the instructions is **200 ft**. Inflow is **USGS 15-minute discharge at Happy Isles Bridge** (site 11264500). Downstream BC is Normal Depth. Calibration uses observed high-water marks in the GIS pack.

## Official ZIP contents (`original/` — do not edit)

```
2D Model Development and Refinement/
  Flow_Data/
    streamflow.dss              # HEC-DSS, two records Dec 1996 / Jan 1997, 15 min USGS
    streamflow.dsc              # catalog (text)
    streamflow.dsc.h5           # DSS catalog index (not 2D results)
  GIS_Data/
    2DArea.*                    # 2D flow-area perimeter
    Banklines.*, Breaklines.*, Channel_Polygon.*, River.*
    BoundaryConditions.*, ReferencePoints.*
    NLCD_2019.tif               # land cover
    Mannings N Values.xlsx
    OBS HWM/Floodplain HWM.*    # observed high-water marks
    Backup/                     # duplicate shapefiles
  Terrain/USGS_Data/
    USGS_OPR_CA_YosemiteNP_2019_D19_BE_11SKB*.tif   # 15 tiles, 2019 Yosemite lidar
```

**No HEC-RAS `.prj` project, no `*.g##.hdf` geometry results, no `*.p##.hdf` plan results.** Students create the model in the GUI. Python can read terrain paths, GIS, the DSS catalog, and the USGS RDB copy of Q0; it cannot read Depth until you run a plan.

DSS pathnames:

- `/MERCED R A HAPPY ISLES BRIDGE/YOSEMITE CA/FLOW/01DEC1996/15MIN/USGS/`
- `/MERCED R A HAPPY ISLES BRIDGE/YOSEMITE CA/FLOW/01JAN1997/15MIN/USGS/`

Projection (`GIS_Data/2DArea.prj`): NAD83 / California zone 3 (ftUS), EPSG:2227.

## Copied / linked working folders

| Folder | Contents |
|--------|----------|
| `terrain/` | 15 USGS 2019 lidar GeoTIFFs |
| `gis/` | perimeter, breaklines, NLCD, Manning table, HWM |
| `boundary/` | `streamflow.dss` + catalog; `usgs_11264500_happy_isles_1997_iv.txt` (NWIS IV, 1996-12-31–1997-01-08) |
| `events/` | 40-event LHS table + 10 test hydrograph CSVs |
| `hf_100ft/`, `lf_400ft/`, `lf_800ft/` | **skeletons + `geometry.yaml` only** |

## This study's meshes (not in the ZIP)

| Role | Cell size | Folder | Status |
|------|-----------|--------|--------|
| Official tutorial | 200 ft | (build separately if you want a check-run) | not pre-built |
| HF | 100 ft (~30.5 m) | `hf_100ft/` | must be created in RAS Mapper |
| LF | 400 ft (~122 m) | `lf_400ft/` | must be created in RAS Mapper |
| LF | 800 ft (~244 m) | `lf_800ft/` | must be created in RAS Mapper |

Do not pretend these three meshes already exist.

## Event protocol

```
Q_i(t) = a_i * Q_0((t - tau_i) / s_i)
a in [0.6, 1.6], s in [0.8, 1.2], tau in [-3 h, +3 h]
LHS, seed 20260814
40 events: 24 train / 6 val / 10 test
test: 6 interpolation + 4 extrapolation
```

Same `(a, s, tau)` drives HF-100, LF-400, and LF-800. Parameter table: `events/event_parameters.csv`. Ten test hydrographs (from the USGS RDB, not invented depths): `events/hydrographs/ME*.csv`.

## What to do in the HEC-RAS GUI

1. Install HEC-RAS 6.x (not present on this machine as of 2026-08-14).
2. New project; copy terrain/GIS into a working folder — **never edit `original/`**.
3. RAS Mapper: Create New RAS Terrain from the 15 USGS tifs (or Project → Download Data → USGS Terrain if you prefer live tiles).
4. Import `2DArea.shp` as the 2D flow-area perimeter. Generate computation points at **200 ft** first (official). Run the 1997 Happy Isles hydrograph from `streamflow.dss` (or the USGS CSV). Downstream: Normal Depth.
5. Confirm a `*.p##.hdf` is written. Then `python scripts/probe_hecras.py --case-root data/external/hecras_merced --list-paths`.
6. Save Geometry As:
   - 100 ft → `hf_100ft/`
   - 400 ft → `lf_400ft/`
   - 800 ft → `lf_800ft/`
   Use breaklines (`Breaklines.shp` / `Banklines.shp`) on all three. 100 ft will be slower; 800 ft is the coarse LF.
7. Attach the **same** event-library unsteady file (10 test events first, then the remaining 30) to all three geometries and compute. Do not invent inundation fields in Python.

`lsg.hecras` reads Depth / WSE / cell centres from those HDF files once they exist.
