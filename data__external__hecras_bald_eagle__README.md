# Bald Eagle Creek (Lock Haven, PA) — HEC-RAS 2D case

Independent, fully reproducible case for this study. **Not** a completed HF/LF result library: the official ZIP is a student workshop (terrain + GIS + DSS inflows). Depth rasters exist only after you run plans in HEC-RAS.

## Source

- Tutorial: https://www.hec.usace.army.mil/confluence/rasdocs/hgt/latest/tutorials/2d-unsteady-flow/creating-a-simple-2d-model
- ZIP: `Creating a Simple 2D Model.zip`
- Direct: https://www.hec.usace.army.mil/confluence/rasdocs/hgt/files/latest/213685242/213685260/1/1728427351910/Creating+a+Simple+2D+Model.zip
- Downloaded: 2026-08-14, 45 685 116 bytes
- Licence / copyright: U.S. Army Corps of Engineers, Hydrologic Engineering Center. Tutorial data for HEC-RAS instruction. Redistribute according to USACE/HEC terms; this repo keeps `original/` unmodified.

## Official ZIP contents (unmodified under `original/`)

```
2.3 W - Creating a Simple 2D Model/
  Flow_Data/
    Simple2DModel_Flows.dsc
    Simple2DModel_Flows.dss          # four inflows, 15 min, Dec 1998–Jan 1999
  GIS_Data/
    bec_boundary.{shp,shx,dbf,prj}
    PA_SPCS_ft.prj                   # NAD83 Pennsylvania North ftUS
  Terrain/
    BEC_10ft.tif                     # channel TIN, 10 ft
    DEM.tif                          # USGS floodplain DEM
```

No `.prj` HEC-RAS project, no geometry HDF, no plan HDF. Students build the 2D model in the GUI.

DSS pathnames (`Simple2DModel_Flows.dsc`):

- `//SAYERS DAM OUTFLOW/FLOW/…/15MIN/2DMODEL/`
- `//MARSH CREEK/FLOW/…/15MIN/2DMODEL/`
- `//BEECH CREEK FLOW/FLOW/…/15MIN/2DMODEL/`
- `//FISHING CREEK/FLOW/…/15MIN/2DMODEL/`

## This study's meshes (not in the ZIP)

| Role | Cell size | Folder | Status |
|------|-----------|--------|--------|
| HF | 200 ft (~61 m) | `hf_200ft/` | skeleton — build in RAS Mapper |
| LF | 500 ft (~152 m) | `lf_500ft/` | skeleton |
| LF | 1000 ft (~305 m) | `lf_1000ft/` | skeleton |

## Event protocol

Same `(a, s, tau)` LHS as Merced. Multi-tributary:

```
a_j = a_storm * (1 + eps_j),   eps_j ~ U(-0.15, 0.15)
```

`s` and `tau` are shared across tributaries of one event. Export DSS hydrographs to CSV in HEC-DSSVue (or RAS) before `scripts/generate_hecras_events.py` can write scaled CSVs. Parameter tables do not require DSS decoding.

## What to do in the HEC-RAS GUI

1. New project in `hf_200ft/` (copy terrain/GIS; do not edit `original/`).
2. Create RAS Terrain from `BEC_10ft.tif` + `DEM.tif`.
3. Import `bec_boundary` as the 2D flow-area perimeter.
4. Generate computation points at **200 ft**, add breaklines as in the tutorial.
5. Unsteady flow: four Flow Hydrographs from `Simple2DModel_Flows.dss`; downstream Normal Depth.
6. Run the official event once; confirm `*.p##.hdf` appears.
7. File → Save Geometry As for **500 ft** and **1000 ft** meshes (`lf_500ft/`, `lf_1000ft/`).
8. Reuse the same unsteady file (event library) on all three geometries.

Python in this repo can list HDF groups and read Depth/WSE **after** those plan files exist. It will not invent inundation fields.
