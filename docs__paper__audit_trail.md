# 审查文档：数据真实性、计算完整性与方法归属审计

**日期:** 2026-08-17  
**审计对象:** `docs__paper__manuscript.md`（WRR 投稿稿）  
**审计范围:** 所有 Table 1–9 数值、所有 Figure 1–8 图形、Methods 章节方法归属  
**审计标准:** 每一项数据必须可追溯到本地计算产物（JSON/NPZ），不可来自参考论文直接引用

---

## 一、总体数据流向

```
Fraehr (2024) Figshare 公开数据 (CC BY 4.0)
  │  DOI: 10.26188/24312658
  │  Carlisle.zip / Chowilla.zip / Burnett.zip
  │
  ├─→ scripts/download_published_benchmarks.py  ← 下载
  │
  ├─→ lsg/fraehr.py  ← 数据摄入（解析 HDF/NPZ，对齐 HF/LF 时间轴，去除 ghost cells）
  │     lsg/hecras.py  ← HEC-RAS HDF 读取（active_cell_mask, read_unsteady_2d）
  │     lsg/spatial.py  ← 空间插值（LF→HF unstructured grid 投影）
  │
  ├─→ scripts/run_lsg_workflow.py  ← 主计算管线
  │     │
  │     ├─→ lsg/wse_ext.py  ← EXT+WSE 双场训练与重建  ★ 我们自己的方法
  │     ├─→ lsg/zoning.py  ← residual_kmeans / wet_correlation 分区  ★ 我们自己的方法
  │     ├─→ lsg/base.py  ← LSGState, prepare_training_matrix, predict_matrix
  │     ├─→ lsg/gp.py  ← GPflow SGPR + NumPy RBF GP 后备
  │     ├─→ lsg/eof.py  ← EOF/SVD 压缩与重建
  │     ├─→ lsg/evaluation.py  ← CSI, POD, RFA, RMSE 计算
  │     ├─→ lsg/diagnostics.py  ← O1–O4 oracle error budget  ★ 我们自己的方法
  │     ├─→ lsg/uq.py  ← CRPS 校准、Tobit 深度、P(wet)  ★ 我们自己的方法
  │     │
  │     └─→ 产出: outputs/evaluation/{case}/workflow_summary*.json
  │              outputs/evaluation/{case}/pred_examples.npz
  │
  ├─→ scripts/make_figures.py  ← 纯绘图消费者（不导入 lsg/ 计算模块）
  │     │  只读取预计算的 JSON 和 NPZ 文件
  │     │  只导入 lsg/figstyle.py（matplotlib 样式，非计算）
  │     │
  │     └─→ 产出: outputs/figures/fig01–fig09.svg
  │
  └─→ docs/paper/_build_html.py  ← 自包含 HTML 构建（Base64 内嵌 SVG）
        docs/paper/_make_pdf.ps1  ← 无头浏览器 PDF 打印
```

> **关键原则：** 所有数值来自 `scripts__run_lsg_workflow.py` 在自己爜境中运行产生的 JSON 文件，而非从 Fraehr et al. (2024a) 的 Table 2 或其他任何参考论文中直接复制。

---

## 二、Table-by-Table 数值溯源

### Table 1. 案例概览

| 字段 | 数值 | 来源 |
|------|------|------|
| Carlisle HF scale | ~5.8×10⁵ cells | `data/external/carlisle/Geometry_data/Lisflood_Geometry_data.npz` hf_cell_centers 行数 |
| Chowilla HF scale | ~1.1×10⁵ cells | `data/external/chowilla/Geometry_data/Geometry_data_HF.npz` |
| Burnett HF scale | ~7.8×10⁵ cells | `data/external/burnett/Geometry_data/Tuflow_Geometry_data.npz` |
| Carlisle events | E1–E9; train E2–E9, test E1 | `config__carlisle.yaml` splits 定义 |
| Chowilla events | 29 events; train 28, test E1 | `config__chowilla.yaml` splits 定义 |
| Burnett events | 74 events; train 56, test 18 | `config__burnett.yaml` splits 定义 |
| 求解器信息 | LISFLOOD-FP / HEC-RAS / TUFLOW | Fraehr (2024) Figshare README 文档性描述 |

**判定：** ✅ 全部来自本地数据与配置文件，非论文引用。

---

### Table 2. 主要 CSI 和 RMSE

| 行 | 数值 | 来源 JSON | 精确键路径 |
|---|---|---|---|
| Carlisle LF CSI all_cells 0.960 | `outputs__evaluation__carlisle__workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json` | `score_protocol.lf_only.all_cells.csi` |
| Carlisle LF CSI wet_train 0.966 | 同上 | `score_protocol.lf_only.wet_train.csi` |
| Carlisle LF RMSE all 0.074 | 同上 | `score_protocol.lf_only.all_cells.rmse` |
| Carlisle LF RMSE wet_train 0.101 | 同上 | `score_protocol.lf_only.wet_train.rmse` |
| Carlisle LSG-TS max CSI 0.970 | 同上 | `lsg_ts.score_protocol.lsg_ts.all_cells.csi`（max surface 子表） |
| Carlisle LSG-TS max RMSE all 0.099 | 同上 | `lsg_ts.score_protocol.lsg_ts.all_cells.rmse` |
| Carlisle LSG-TS max RMSE wet_train 0.154 | 同上 | `lsg_ts.score_protocol.lsg_ts.wet_train.rmse` |
| Carlisle LSG-Max H-LSG CSI all_cells/ wet_train 0.976 | 同上 | `score_protocol.lsg_max.all_cells.csi` / `.wet_train.csi` |
| Carlisle LSG-Max H-LSG RMSE all 0.061 | 同上 | `score_protocol.lsg_max.all_cells.rmse` |
| Carlisle LSG-Max H-LSG RMSE wet_train 0.094 | 同上 | `score_protocol.lsg_max.wet_train.rmse` |
| Chowilla LF CSI all_cells 0.930 | `outputs__evaluation__chowilla__workflow_summary_grp1_wse_ext_hlsg_max.json` | `score_protocol.lf_only.all_cells.csi` |
| Chowilla LF CSI wet_train 0.925 | 同上 | `score_protocol.lf_only.wet_train.csi` |
| Chowilla LF RMSE all/wet 0.690 | 同上 | `score_protocol.lf_only.all_cells.rmse` |
| Chowilla LSG-Max H-LSG CSI all_cells 0.390 | 同上 | `score_protocol.lsg_max.all_cells.csi` |
| Chowilla LSG-Max H-LSG CSI wet_train 0.976 | 同上 | `score_protocol.lsg_max.wet_train.csi` |
| Chowilla LSG-Max H-LSG RMSE all 3.789 | 同上 | `score_protocol.lsg_max.all_cells.rmse` |
| Chowilla LSG-Max H-LSG RMSE wet_train 0.093 | 同上 | `score_protocol.lsg_max.wet_train.rmse` |
| Chowilla LSG-Max global CSI all 0.390 | `outputs__evaluation__chowilla__workflow_summary_grp1_wse_ext_global_max.json` | `score_protocol.lsg_max.all_cells.csi` |
| Chowilla LSG-Max global CSI wet_train 0.974 | 同上 | `score_protocol.lsg_max.wet_train.csi` |
| Chowilla LSG-Max global RMSE all 3.789 | 同上 | `score_protocol.lsg_max.all_cells.rmse` |
| Chowilla LSG-Max global RMSE wet_train 0.088 | 同上 | `score_protocol.lsg_max.wet_train.rmse` |
| Burnett LF CSI all_cells/wet 0.853 | `outputs__evaluation__burnett__workflow_summary_grp1_wse_ext_hlsg_max.json` | `score_protocol.lf_only.all_cells.csi` |
| Burnett LF RMSE all 0.983 | 同上 | `score_protocol.lf_only.all_cells.rmse` |
| Burnett LF RMSE wet_train 0.989 | 同上 | `score_protocol.lf_only.wet_train.rmse` |
| Burnett LSG-Max H-LSG CSI all/wet 0.975 | 同上 | `score_protocol.lsg_max.all_cells.csi` |
| Burnett LSG-Max H-LSG RMSE all 0.384 | 同上 | `score_protocol.lsg_max.all_cells.rmse` |
| Burnett LSG-Max H-LSG RMSE wet_train 0.387 | 同上 | `score_protocol.lsg_max.wet_train.rmse` |
| Burnett LSG-Max global CSI all/wet 0.975 | `outputs__evaluation__burnett__workflow_summary_grp1_wse_ext_global_max.json` | `score_protocol.lsg_max.all_cells.csi` |
| Burnett LSG-Max global RMSE all 0.179 | 同上 | `score_protocol.lsg_max.all_cells.rmse` |
| Burnett LSG-Max global RMSE wet_train 0.179 | 同上 | `score_protocol.lsg_max.wet_train.rmse` |

**计算代码路径：** `scripts__run_lsg_workflow.py` → `lsg__wse_ext.py` 训练 EXT+WSE → `lsg__evaluation.py` 计算 CSI/RMSE

**判定：** ✅ 全部来自本地 workflow 运行产生的 JSON，无任何数值来自参考论文 Table 2。

---

### Table 3. O1–O4 深度 RMSE（测试集）

| 行 | O1 | O2 | O3 | O4 | O2−O1 | 来源 JSON |
|---|---|---|---|---|---|---|
| Carlisle TS H-LSG | 0.018 | 0.033 | 0.240 | 0.102 | 0.015 | `workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json` → `lsg_ts.error_budget[test].o1_rmse` 等 |
| Carlisle Max H-LSG | 0.048 | 0.052 | 0.068 | 0.094 | 0.005 | 同上 → `lsg_max.error_budget[test]` |
| Chowilla H-LSG | 0.020 | 0.034 | 0.701 | 0.093 | 0.013 | `workflow_summary_grp1_wse_ext_hlsg_max.json` → `lsg_max.error_budget[test]` |
| Chowilla global | 0.020 | 0.078 | 0.666 | 0.088 | 0.057 | `workflow_summary_grp1_wse_ext_global_max.json` → `lsg_max.error_budget[test]` |
| Burnett H-LSG | 0.074 | 0.083 | 0.668 | 0.387 | 0.009 | `workflow_summary_grp1_wse_ext_hlsg_max.json` → `lsg_max.error_budget[test]` |
| Burnett global | 0.074 | 0.123 | 0.708 | 0.179 | 0.049 | `workflow_summary_grp1_wse_ext_global_max.json` → `lsg_max.error_budget[test]` |

**计算代码路径：** `lsg__diagnostics.py` → `oracle_error_budget()` → 对 EXT+WSE 双路径同步施加 O1–O4 反事实 → 生产 extent gate 结合 → clipped depth RMSE on wet_idx

**判定：** ✅ 全部来自 `lsg__diagnostics.py` 的独立计算。O1–O4 方法是本文原创（Tan et al. 2025 只有二分法，不包含 O1–O2 截断 vs O2–O3 LF 表达式分层）。

---

### Table 4. Chowilla 容量控制

| 行 | WSE dim | CSI | RMSE | O2−O1 | 来源 JSON |
|---|---|---|---|---|---|
| Global native | 3 | 0.974 | 0.088 | 0.057 | `workflow_summary_grp1_wse_ext_global_max.json` |
| H-LSG residual k-means | 15 | 0.976 | 0.093 | 0.013 | `workflow_summary_grp1_wse_ext_hlsg_max.json` |
| Global matched-15 | 15 | 0.975 | 0.085 | 0.002 | `workflow_summary_grp1_wse_ext_global_matched15_max.json` |
| H-LSG modes=0 | 3 | 0.974 | 0.088 | 0.057 | `workflow_summary_grp1_wse_ext_hlsg_budget3_max.json`（用 `residual_eof_modes=0` 运行） |

**容量匹配机制：** `config__chowilla.yaml` 中 `lsg.force_n_modes: 15` → `lsg__base.py` 强制保留 15 个全局 EOF 模式 → 与 H-LSG 的 WSE GP 输入维度（3 global + 4×3 residual = 15）等同。

**判定：** ✅ 全部来自独立容量匹配实验运行，非假设。

---

### Table 5. Burnett 容量控制和 oracle 归因

| 行 | WSE dim | CSI | RMSE | O2−O1 | O4−O2 | EXT agree | 来源 JSON |
|---|---|---|---|---|---|---|---|
| Global native | 6 | 0.975 | 0.179 | 0.049 | 0.056 | 0.986 | `workflow_summary_grp1_wse_ext_global_max.json` |
| H-LSG | 18 | 0.975 | 0.387 | 0.009 | 0.304 | 0.986 | `workflow_summary_grp1_wse_ext_hlsg_max.json` |
| Global matched-18 | 18 | 0.972 | 0.416 | 0.004 | — | 0.986 | `workflow_summary_grp1_wse_ext_global_matched18_max.json` |

**EXT agreement 计算：** `lsg__diagnostics.py` → `diagnose_hlsg_o2_vs_rmse()` → 比较 H-LSG 和 global 的 EXT 二进制预测逐单元一致性

**判定：** ✅ 全部来自独立容量匹配实验运行。

---

### Table 6. Carlisle 容量控制

| 行 | 请求/实现 WSE dim | CSI | RMSE | O2−O1 | 来源 JSON |
|---|---|---|---|---|---|
| Global native | auto / 1 | 0.976 | 0.112 | 0.064 | `workflow_summary.json`（= `workflow_summary_grp1_wse_ext_global_max_capacity.json`，native global 1-mode max） |
| H-LSG | — / 13 | 0.976 | 0.094 | 0.005 | `workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json` |
| Global forced 13 | 13 / 8 | 0.975 | 0.202 | 0.000 | `workflow_summary_grp1_wse_ext_global_matched13_max.json` |
| H-LSG modes=0 | — / 1 | 0.976 | 0.112 | 0.064 | `workflow_summary_grp1_wse_ext_hlsg_budget1_max.json`（residual modes=0 回退到全局基线） |

**"实现维度 8"的原因：** `lsg__base.py` 中 `prepare_training_matrix` → `np.linalg.svd` 对 8 个训练事件的 max-surface 矩阵只能产生 rank ≤ 8 → 请求 13 模式被截断。这是 SVD 线性代数约束，非人为选择。

**判定：** ✅ 全部来自独立容量匹配实验运行。

---

### Table 7. Chowilla 诱导点与分区数量敏感性

| 行 | 设置 | 来源 JSON |
|---|---|---|
| inducing floor 2 | RMSE 0.244 | `workflow_summary_grp1_wse_ext_hlsg_inducing_m2_max.json` |
| inducing floor 8 | RMSE 0.096 | `workflow_summary_grp1_wse_ext_hlsg_inducing_m8_max.json` |
| inducing floor 16 | RMSE 0.093 | `workflow_summary_grp1_wse_ext_hlsg_max.json`（默认） |
| inducing floor 28 | RMSE 0.073 | `workflow_summary_grp1_wse_ext_hlsg_inducing_m28_max.json` |
| zone count 2 | RMSE 0.087 | `workflow_summary_grp1_wse_ext_hlsg_nzones2_max.json` |
| zone count 4 | RMSE 0.093 | `workflow_summary_grp1_wse_ext_hlsg_max.json`（默认） |
| zone count 6 | RMSE 0.103 | `workflow_summary_grp1_wse_ext_hlsg_nzones6_max.json` |

**控制机制：** `config__chowilla.yaml` 中 `lsg.min_inducing_points` 和 `lsg.zoning.n_zones` 参数扫描

**判定：** ✅ 全部来自独立参数扫描实验运行。

---

### Table 8. Chowilla 分区方案敏感性

| 行 | 来源 JSON |
|---|---|
| global | `workflow_summary_grp1_wse_ext_global_max.json` |
| residual k-means | `workflow_summary_grp1_wse_ext_hlsg_max.json` |
| wet-correlation | `workflow_summary_grp1_wse_ext_wet_correlation_max.json` |

**wet_correlation 实现：** `lsg__zoning.py` → `wet_correlation()` → 对标准化后的单元水文曲线做 k-means（相关性代理）

**判定：** ✅ 全部来自独立实验运行。

---

### Table 9. CRPS 方差校准

| 行 | s | CRPS uncal→cal | cov90 uncal→cal | 来源 JSON |
|---|---|---|---|---|
| Carlisle Max | 0.417 | 0.039→0.028 | 0.990→0.966 | `workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix_uq_calibrated.json` |
| Carlisle TS | 0.900 | ≈0.0165 | — | 同上（`lsg_ts.uq` 子表） |
| Chowilla H-LSG rescore | 0.419 | 2.155→2.155 | 0.334→0.287 | `workflow_summary_grp1_wse_ext_hlsg_max_uq_calibrated.json` |
| Burnett H-LSG rescore | 0.604 | 0.133→0.127 | 0.943→0.890 | `workflow_summary_grp1_wse_ext_hlsg_max_uq_calibrated.json` (Burnett) |

**CRPS 校准实现：** `lsg__uq.py` → `calibrate_variance_crps()` → `scipy.optimize.minimize_scalar` 在训练事件上最小化 mean Gaussian CRPS → 得到 s → `Var_cal = s * Var_raw`

**嵌套 CV 稳定性：** `outputs__evaluation__chowilla__nested_crps_scale_cv.json`（Chowilla s=0.310±0.007）、`outputs__evaluation__carlisle__nested_crps_scale_cv.json`（Carlisle s=0.418±0.031）

**判定：** ✅ 全部来自 `lsg__uq.py` 的独立校准计算。CRPS 校准方法是本文原创（在 LSG 框架内首次实现）。

---

## 三、Figure-by-Figure 溯源

### Figure 1. 研究区域

- **生成函数:** `scripts__make_figures.py` → `fig_study_domains()`
- **数据源:** `pred_examples.npz`（三个案例的 hf_cell_centers）+ `Geometry_data.npz`
- **无 workflow_summary JSON 依赖**

### Figure 2. 淹没范围 H/M/FA 图

- **生成函数:** `scripts__make_figures.py` → `fig_extent_hit_miss()`
- **数据源:** `pred_examples.npz`（hf_max, lf_max, lsg_max, hf_wet_mask）
- **无 workflow_summary JSON 依赖**

### Figure 3. 洪峰深度误差图

- **生成函数:** `scripts__make_figures.py` → `fig_peak_depth_error()`
- **数据源:** `pred_examples.npz`
- **无 workflow_summary JSON 依赖**

### Figure 4. P(wet) 概率图

- **生成函数:** `scripts__make_figures.py` → `fig_pwet_maps()`
- **数据源:** `pred_examples.npz` 中的 `inundation_prob_lsg_max` 字段
- **该字段由 `lsg__uq.py` → `inundation_probability()` 产生**

### Figure 5. 跨案例 CSI/RMSE 条形图

- **生成函数:** `scripts__make_figures.py` → `fig_cross_case()`
- **数据源:**
  - Carlisle: `workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json`
  - Chowilla: `workflow_summary_grp1_wse_ext_hlsg_max.json`
  - Burnett: `workflow_summary_grp1_wse_ext_hlsg_max.json`

### Figure 6. O1–O4 误差阶梯

- **生成函数:** `scripts__make_figures.py` → `fig_error_budget()`
- **数据源:** 同 Table 3 的 JSON 文件

### Figure 7. Global vs H-LSG 对比

- **生成函数:** `scripts__make_figures.py` → `fig_global_vs_hlsg()`
- **数据源:** 六个 workflow_summary JSON（每个案例的 global 和 H-LSG 各一个）

### Figure 8. CRPS 校准与空间 fringe 诊断（2×2：a reliability / b fringe map / c coverage / d CRPS）

- **生成函数:** `scripts__make_figures.py` → `fig_uq_calibration()`（a/c/d 面板，数据源同 Table 9 的 JSON 文件）；`_plot_reliability_fringe_map()`（b 面板）
- **b 面板数据源:** `outputs__evaluation__carlisle__pred_examples.npz` 的 `inundation_prob_lsg_max`（未校准 P(wet)）与 `hf_max`（τ=0.03 划分 HF wet/dry），坐标来自 `Lisflood_Geometry_data.npz`（`_load_xy`）。fringe 定义为 0.5 ≤ P < 0.95；fringe∩HF-dry 画橙色（false alarm），fringe∩HF-wet 画深蓝（hit），其余为浅蓝（HF wet, P≥0.95）/浅灰（HF dry, P<0.5）
- **b 面板无 workflow_summary JSON 依赖**，与 4.6/5.3 的 fringe 统计（8,936 单元、~70% FA）来自同一 npz
- **4.6/5.3 中 reliability dip 诊断数字的来源:** `docs__paper___dip_analysis.py`（OWN 诊断脚本），直接读取 `outputs__evaluation__carlisle__pred_examples.npz` 的 `inundation_prob_lsg_max`、`pred_lsg_max`、`hf_max`，在 τ=0.03 下按 10 个概率 bin 重算 observed frequency、bin 计数与 false-alarm fringe 构成。关键输出：63.3% 单元 P<0.05（obs 0.0044）、35.1% P>0.95（obs 0.999）、1.54%（8,936/581,061）位于 0.5<P<0.95（obs 0.62）；0.6–0.9 bin 的 obs 0.29–0.33，其中约 70% 为 surrogate 预测浅水（均值 0.07–0.21 m）而 HF 干燥的 false-alarm 边缘单元；0.6–0.7 bin 仅 15 个单元。与 JSON 中 `reliability` 字段逐 bin 一致（0.333/0.296/0.286/0.994）。

---

## 四、方法归属：什么是我们自己的，什么是 Fraehr 的

### 我们自己的实现（OWN computation）

| 模块 | 功能 | 为何是 OWN |
|------|------|-----------|
| `lsg__wse_ext.py` | EXT+WSE 双场训练与重建 | Fraehr et al. (2023a) 描述了想法，但我们的实现是独立编写的：双 LSGState 管理、EXT 二进制门控、WSE→depth 组合、EXT 一致性检查、预测示例导出 |
| `lsg__zoning.py` | residual_kmeans 和 wet_correlation 分区 | 完全原创：residual-response k-means、wet-correlation 分区、标签传播与空间坐标增强、残差 EC 堆叠 |
| `lsg__diagnostics.py` | O1–O4 oracle error budget | 完全原创：四阶段反事实阶梯、双路径 EXT+WSE 同步、生产 extent gate 结合、训练/测试分离报告 |
| `lsg__uq.py` | CRPS 校准、Tobit 深度、P(wet) | 完全原创：GP EC 方差→EOF 重建→Tobit 左截断→CRPS 标量校准→P(wet) 概率图、嵌套 CV 稳定性 |
| `lsg__evaluation.py` | CSI、POD、RFA、RMSE | 独立实现（与 Fraehr 的 MATLAB `Evaluation.py` 逻辑等价但代码独立编写） |
| `lsg__base.py` | LSGState、prepare_training_matrix、predict_matrix | 独立实现（与 Fraehr 的 `Data_based_models.py` 逻辑等价但代码独立编写） |
| `lsg__gp.py` | GPflow SGPR + NumPy RBF GP | 独立实现，包含诱导点下限（LSG-Max 稳定性修复） |
| `lsg__eof.py` | EOF/SVD 压缩重建 | 独立实现 |
| `lsg__config.py` | YAML 配置加载 | 独立实现 |
| `lsg__data.py` | 数据加载、事件划分 | 独立实现 |
| `lsg__spatial.py` | 空间插值 | 独立实现 |
| `lsg__hecras.py` | HEC-RAS HDF 读取（含 ghost cell 修复） | 独立实现 |
| `lsg__fraehr.py` | Fraehr 格式数据摄入（含时间对齐修复） | 独立实现 |
| `lsg__lsg_max.py` | LSG-Max 模型 | 独立实现 |
| `lsg__lsg_ts.py` | LSG-TS 模型 | 独立实现 |
| `scripts__run_lsg_workflow.py` | 主计算管线 | 完全 OWN |
| `scripts__make_figures.py` | 论文图形生成 | 完全 OWN |
| `scripts__rescore_uq_calibrated.py` | UQ 校准后重评分 | 完全 OWN |
| `scripts__hf_budget_subsample.py` | HF 预算子采样 | 完全 OWN |

### 参考论文的贡献（仅引用，不直接使用其数据）

| 论文 | 我们使用的内容 | 我们不使用的内容 |
|------|-------------|----------------|
| Fraehr et al. (2022) WRR | LSG 方法概念（作为引用） | 该论文的数值、表格、图形 |
| Fraehr et al. (2023a) WRR | EXT+WSE 双场概念（作为引用） | 该论文的数值、表格、图形 |
| Fraehr et al. (2024a) Water Research | 公开数据 cube（Carlisle/Chowilla/Burnett Figshare） | **该论文 Table 2 的 LSG CSI 数值（0.95±0.05）、ML baseline 数值** |
| Fraehr et al. (2024b) J. Environ. Manage. | LESS 概念（作为引用） | 该论文的数值 |
| Wang et al. (2026) WRR | LSG-Max vs LSG-TS 概念、zonal EOF future work 引用 | 该论文的 Brisbane 数值、表格、图形 |

> **关键声明：** 本文 Table 2 的 CSI/RMSE 是我们自己运行 `scripts__run_lsg_workflow.py` 在 Grp1 划分上产生的，**不是** Fraehr et al. (2024a) Table 2 的 pooled mean±std（LSG CSI 0.95±0.05）。我们在 manuscript 2.7 节明确声明了协议差异。

---

## 五、数据完整性检查

### 数据文件存在性

| 数据 | 路径 | 状态 |
|------|------|------|
| Carlisle HF/LF | `data/external/carlisle/` | ✅ 已下载并验证 |
| Chowilla HF/LF | `data/external/chowilla/` | ✅ 已下载并验证 |
| Burnett HF/LF | `data/external/burnett/` | ✅ 已下载并验证 |
| Brisbane | — | ❌ 未使用（许可证限制） |

### 计算结果文件存在性

| 文件 | 状态 |
|------|------|
| 所有 workflow_summary*.json（共 20+ 个） | ✅ 存在 |
| 所有 pred_examples.npz（每个案例） | ✅ 存在 |
| 所有 fig0*.svg（共 15 个：fig01、fig02a–c、fig03a–c、fig04a–c、fig05–fig09；原 figS1 depth strip 已随“不设 supplementary”决定退役删除） | ✅ 存在 |
| 所有 figure_manifest.json | ✅ 存在 |

### 可复现性

| 条件 | 状态 |
|------|------|
| 公开数据 | ✅ Figshare CC BY 4.0 |
| 公开代码 | ✅ GitHub: `Coucou2016/lsg-flood-surrogate-benchmark` |
| 配置文件 | ✅ `config/{carlisle,chowilla,burnett}.yaml` |
| 环境依赖 | ✅ `requirements.txt` |
| 随机种子 | ✅ 配置文件中固定 |

---

## 六、边界与限制的诚实声明

### 我们确实计算了的内容

- 所有 Table 2–9 的 CSI/RMSE/O1–O4/CRPS/coverage 数值
- 所有 Figure 1–8 的图形
- 所有容量匹配控制实验（matched-15/18、inducing sweep、zone sweep）
- 所有 CRPS 校准实验
- 所有 EXT agreement 归因分析

### 我们未计算的内容（诚实声明）

- Fraehr et al. (2024a) 的 ML baseline（1dCNN, LSTM-SRR, GP-EOF, LSTM-EOF）——未重新训练
- Fraehr et al. (2024a) 的 50% 外推实验——未重新运行
- Chowilla/Burnett 的 full time-series 实验——内存限制（Burnett HF stack ≈199 GB vs ≈128 GB RAM）
- Brisbane TUFLOW/URBS 案例——许可证限制
- 基于 cell 的 p 值显著性检验——独立评估单元是事件，非 cell

### 与参考论文数值的差异说明

本论文的 Grp1 单 fold 分数与 Fraehr et al. (2024a) 的 pooled mean±std 之间存在差异是预期的，因为：
1. 评分协议不同：我们是 Grp1 单 fold，他们是 leave-one-group-out 全 fold 均值±标准差
2. 深度指标不同：我们用 RMSE，他们用 AvgPeakDiff / R² / AvgRMSE / FI
3. 场模式不同：我们用 `wse_ext`（EXT+WSE 双路径），Fraehr 的 baseline 可能用 `depth` 模式

> 我们在 manuscript 2.7 节明确声明了这些协议差异，并注明"Carlisle LSG-Max wet_train CSI 0.976 under Grp1 is therefore comparable in *spirit* to their high LSG CSI on Carlisle, not a cell-wise reprint of their pooled Table 2"。

---

## 七、审计结论

| 审计项 | 结果 |
|--------|------|
| 所有 Table 数值可追溯到本地 JSON | ✅ 通过 |
| 所有 Figure 可追溯到生成函数和数据源 | ✅ 通过 |
| 无任何数值直接取自参考论文 | ✅ 通过 |
| 所有 OWN 方法有独立代码实现 | ✅ 通过 |
| 参考论文仅作为概念引用 | ✅ 通过 |
| 未计算的内容已诚实声明 | ✅ 通过 |
| 数据文件完整且可访问 | ✅ 通过 |
| 代码可公开复现 | ✅ 通过 |

**审计员签名:** Cursor Agent（本地源码审查）  
**审计日期:** 2026-08-17

---

## 八、修订日志（ChatGPT 多轮审阅）

| 轮次 | 主题 | 审阅记录 | 备份 |
|---|---|---|---|
| Round 1 | 创新性框架与 over/under-claim | `chatgpt_review_rounds/round1_innovation_framing.md` | `_archive_manuscript_pre_round1_*` |
| Round 2 | Methods/Data 逻辑与一致性 | `chatgpt_review_rounds/round2_methods_data_logic.md` | `_archive_manuscript_pre_round2_*` |
| Round 3 | Results/Discussion 逻辑 | `chatgpt_review_rounds/round3_results_discussion_logic.md` | `_archive_manuscript_pre_round3_*` |
| Round 4 | 写作风格（WRR/AGU） | `chatgpt_review_rounds/round4_writing_style.md` | `_archive_manuscript_pre_round4_*` |
| Round 5 | 图/表/标题格式 | `chatgpt_review_rounds/round5_figures_tables_captions.md` | `_archive_manuscript_pre_round5_*` |
| Round 6 | 数值一致性 + 模拟审稿人 | `chatgpt_review_rounds/round6_numeric_consistency_reviewer.md` | `_archive_manuscript_pre_round6_20260818_043806` |
| Round F1 | 图视觉 + 对应代码双线审核（第一轮） | `chatgpt_review_rounds/roundF1_figure_visual_code_review.md` | `_archive_roundF1_20260818_213405` |
| Round F2-GPT | ChatGPT 真视觉图-码双线审核（GitHub 托管图片） | `chatgpt_review_rounds/roundF2gpt_visual_review.md` | `_archive_roundF2gpt_20260819_004728` |
| Round F3-GPT | ChatGPT 真视觉第3轮（颜色/图例/标注一致性 + F2 修复落地核验） | `chatgpt_review_rounds/roundF3gpt_visual_review.md` | `_archive_roundF3gpt_20260819_022212` |
| Round F4-local | 图↔正文↔表↔JSON 数字逐位核对（本地） | 本文档 Table 6 溯源修正 | 无 |
| Round F5-local | PDF 排版/图题终审 + 图号按引用顺序重排 | 本文档 Round F5-local | `_archive_roundF5_20260819_024004` |
| Round F6 | 删图一(study domains) + Fig7 只留RMSE + Fig8(zoning)合并单面板；全稿图号重排 | 本文档 Round F6 | `_archive_roundF6_20260821_*` |

### Round F1 本地核验与处置（2026-08-18）

**审图方式**：Cursor 独立读图（Read PNG）+ 读代码（`scripts__make_figures.py`）+ 读数据（`outputs/evaluation/*/workflow_summary_*.json`、`pred_examples.npz`）。本轮浏览器 MCP 工具不可用，无法自动把图注入 ChatGPT 网页版；先由本地完成"图-代码-数据"三方核对并直接修复。

**关键发现（数据确凿，非代码 bug，正文已诚实报告但图注未对应）**：

1. **Chowilla 测试事件 E1 是"训练范围外"的极端洪水**。`config__chowilla.yaml` Group 1 为 leave-one-group-out `validation: [E1]`，训练 E2–E29。实测 E1 淹没 84,667 cell，而训练联合湿域仅 36,124 cell；51,264 个"训练从未湿"的 cell 上 LSG EXT 一致性为 0（全网格 RMSE 4.32 m vs 训练湿域 0.096 m）。正文 Table 2 与 Section 4.5 已同时报告 all_cells（CSI 0.390 / RMSE 3.789）与 wet_train（0.976 / 0.093），无造假无隐瞒；**问题在 fig02c/03c/04c 画全网格却未在图注说明外推失败**。

2. **fig9 从未被插入 HTML/PDF**（`_build_html.py` 漏 4.4 分支；重建后 img tags 14→15）。

**已落实修复（不改任何数值，只改图/图注）**：

| 修复 | 文件 |
|---|---|
| fig03 分面板独立 colorbar（原共享 ±10.96 m 被 Chowilla 15 m 异常拉爆、LF 面板洗白） | `make_figures.py` |
| fig08d CRPS 改对数轴（原量级跨 75 倍、小柱贴地） | `make_figures.py` |
| fig06 O3 分面板 y 轴（原 0.6–0.7 m 压制 O1/O2/O4） | `make_figures.py` |
| fig04 删多余 "(a)" 标签 | `make_figures.py` |
| fig03 colorbar label "m" → "depth error (m)" | `make_figures.py` |
| fig2b/3b/4b caption 补 Chowilla E1 外推说明（指向 Section 4.5） | `_build_html.py` |
| fig3 caption 补"独立色标"说明；fig8 caption 补"对数轴"说明 | `_build_html.py` |
| fig9 插入 Section 4.4 | `_build_html.py` |
| fig01 caption 补"points subsampled for display" | `_build_html.py` |
| fig08d 补 xlabel "Case" | `make_figures.py` |

图已重新生成（15 图 × svg/pdf/png），`manuscript.html`（img tags=15）与 `manuscript.pdf` 已重建。

**核验人:** Cursor Agent（本地读图 + 源码 + 源 JSON/NPZ 对照）
**核验日期:** 2026-08-18

### Round F2-GPT 真视觉图-码双线审核（2026-08-19）

**审图方式**：恢复浏览器 MCP 后，将 15 张图 PNG + 生成代码 + 底层数值打包为 `figure_code_audit_pack.md`（markdown 内嵌 raw GitHub URL），推送到公开仓库 `Coucou2016/20260522-LSG-WRR`，由 ChatGPT 网页检索实际打开 15 张图面做真视觉审图（首次真正让 ChatGPT 看到像素）。

**关键发现（ChatGPT 真视觉；F1 本地审图遗漏的统计呈现问题）**：
1. Fig 5/7/9 的 CSI 柱状图使用**截断基线**（0.70 / 0.90 / 0.90 起），放大微小差异（Fig 9 实际差异仅 0.001–0.003，视觉上却显得很突出）。
2. Fig 4 标题被截断（"LSG-Max inundation probabilit…"）。
3. Fig 8c 图内标题未标明只画 Carlisle。
4. Fig 6 四 panel 独立 y 轴但 caption 未醒目标明。
5. 审计包 Fig 6 舍入笔误（0.053/0.095 vs manuscript Table 3 的 0.052/0.094）。
6. Fig 1 正文 "common easting and northing axes" 会被误解为 shared limits。

**已落实修复（不改任何数值，只改图/图注/措辞）**：

| 修复 | 文件 |
|---|---|
| Fig 5/7/9 CSI 截断基线 → 全尺度 0–1 + 柱顶数值标签 | `make_figures.py` |
| Fig 4 标题缩短为 `{case} · {eid} · LSG-Max P(wet)` | `make_figures.py` |
| Fig 8c 标题 "Coverage" → "Carlisle LSG-Max coverage" | `make_figures.py` |
| Fig 6 caption 明说独立 y 轴（不可跨 panel 按柱高比较） | `_build_html.py` |
| Fig 1 正文 "common axes" → "equal-aspect coordinate axes" | `manuscript.md` |
| 审计包 Fig 6 舍入对齐 Table 3（0.052/0.094） | `figure_code_audit_pack.md` |

图已重新生成（15 图 × svg/pdf/png），`manuscript.html`（img tags=15）与 `manuscript.pdf`（1.9 MB）已重建，全部推送到 GitHub。

**核验人:** Cursor Agent（浏览器 MCP + ChatGPT 真视觉 + 本地源码/JSON 对照）
**核验日期:** 2026-08-19

### Round F3-GPT 真视觉第3轮（颜色/图例/标注一致性；2026-08-19）

**审图方式**：ChatGPT 网页检索 GitHub（HEAD 固定 `6b60375`，避开 raw/.../main 旧缓存）对 15 图做第 3 轮真视觉审图，重点查颜色/图例/标注一致性与 F2 修复落地情况。

**结论**：F2 六项修复全部确认落地；**无 P0、无需要重算的 P1 数值问题**。剩余均为绘图/图注小修。

**唯一 P1（已修）**：Fig 8c coverage 柱状图仍用 `ax.set_ylim(0.8, 1.02)` 截断基线（与已修掉的 Fig 5/7/9 同类视觉放大）。→ 改为 0–1.02 全尺度 + 4 根柱三位数值标签，保留 0.90 nominal 虚线。

**P2/P3 已修（只动图/图注/审计包，不动任何数值）**：

| 修复 | 文件 |
|---|---|
| Fig 1/2/3 地图 panel label `(a)–(c)` 与 `×10^6` offset 碰撞 → `x=-0.12`；Fig 2/3 suptitle `y=1.05` | `make_figures.py` |
| Fig 2 图例外移 figure-level 下方 `ncol=4, 7pt`；Fig 5/7 图例外移下方；Fig 8b `upper right`；Fig 8c 下方 | `make_figures.py` |
| Fig 5 缺失 LSG-TS `—` → `N/A`（不画 0 高度 bar） | `make_figures.py` |
| Fig 5 LSG-Max H-LSG 颜色 `lsg_max`→`hlsg`，legend 写全 "LSG-Max H-LSG"（跨图一致） | `make_figures.py` |
| Fig 5/7/8d/9 柱顶数值 6→7 pt | `make_figures.py` |
| 审计包 Fig 6 caption 同步 independent-y-axis；Fig 6 Chowilla O1 0.021→0.020；Fig 8 caption 标 Carlisle | `figure_code_audit_pack.md` |

**核验人:** Cursor Agent（浏览器 MCP + ChatGPT 真视觉 + 本地源码/JSON 对照）
**核验日期:** 2026-08-19

### Round 6 本地核验与处置（2026-08-18）

ChatGPT 标记 Table 3 三处 O2−O1 “减法不符”（Carlisle 0.005、Chowilla H-LSG 0.013、Chowilla global 0.057）。
逐条对照源 JSON 的**未舍入原始值**核验后，确认三处均为正确舍入，并非数据错误：

| 对比 | 源 JSON 未舍入值（O1, O2, O2−O1） | 显示值 | 判定 |
|---|---|---|---|
| Carlisle Max H-LSG | 0.0477524, 0.0524838, 0.0047314 | 0.048, 0.052, 0.005 | ✅ 正确舍入 |
| Chowilla H-LSG | 0.0204877, 0.0337625, 0.0132747 | 0.020, 0.034, 0.013 | ✅ 正确舍入 |
| Chowilla global | 0.0204877, 0.0776122, 0.0571245 | 0.020, 0.078, 0.057 | ✅ 正确舍入 |

来源：`carlisle/workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json`、`chowilla/workflow_summary_grp1_wse_ext_hlsg_max.json`、`chowilla/workflow_summary_grp1_wse_ext_global_max.json` 的 `lsg_max.error_budget[test]`。

据此采纳的修改（不改任何数值，只补说明）：
1. Table 3 标题注明 O2−O1 由未舍入值计算，并给出 Carlisle 例（0.0525−0.0478=0.0047≈0.005 m）。
2. Section 4.2 增加通用舍入说明：O2−O1 与 O4−O2 均由未舍入阶段 RMSE 计算，显示精度下可能相差至多 0.001 m。
3. Table 3 标题补充 Carlisle LSG-TS 行的评测对象（266 个留出测试时间步、clipped-depth RMSE、wet-domain mask），并声明其与 0.065 m（全网格时序 RMSE）及 Table 2 的 0.099/0.154 m（最大面 RMSE）为不同评测对象。
4. Key Point 1 改写：不再表述“no held-out depth benefit”（H-LSG 0.387 m 实低于 matched-18 的 0.416 m），改为“lower truncation error does not imply lower RMSE than the native global baseline”。
5. Key Point 2 改为“learned LF-to-HF water-surface-elevation mapping, not the shared extent reconstruction”（与 O4−O2 诊断范围一致）。
6. Abstract Burnett 对比明确基线为 native 6-dimensional global model。
7. Key Point 3 / Abstract / Conclusions 的校准收益表述精确到“Carlisle Max and Burnett H-LSG Max”。
8. Section 4.3 将“same gate miss/false-alarm behavior”替换为“share the same EXT prediction, differences in depth RMSE cannot originate from the EXT branch”（EXT 分支由构造共享）。
9. Table 9 标题补充 CRPS 评分域（含干单元格的全非填充单元域），并声明不可与 wet-domain point RMSE 直接比较。

其余 ChatGPT 标记为 PASS 的核验项（Burnett O4−O2=0.056/0.304 m、容量控制全部数值、inducing/zone sweep、Table 2 确定性分数、Table 9 概率分数、reliability 8,936/581,061=1.538%、单位一致性）均与本地 JSON 一致，未改动。

**核验人:** Cursor Agent（本地源码审查 + 源 JSON 对照）  
**核验日期:** 2026-08-18

### Round F4-local 数字逐位核对与溯源修正（2026-08-19）

**核对方式**：本地脚本逐表读取 `outputs/evaluation/*/workflow_summary*.json`，把 manuscript Tables 2–9 与 audit trail 溯源列逐一比对。

**逐表结果（全部数值与 manuscript 一致）**：
- Table 2：Carlisle/Chowilla/Burnett 的 LF、LSG-Max H-LSG、global 的 wet_train/all_cells CSI/RMSE 全部命中（Carlisle Max H-LSG wet 0.0945/0.9757；Chowilla H-LSG 0.0932/0.9756、global 0.0877/0.9744；Burnett H-LSG 0.3868/0.9752、global 0.1788/0.9751）。
- Table 3 O1–O4：Carlisle Max 0.0478/0.0525/0.0680/0.0945；Chowilla H-LSG 0.0205/0.0338/0.7010/0.0932、global 0.0205/0.0776/0.6661/0.0877；Burnett H-LSG 0.0744/0.0829/0.6678/0.3868、global 0.0744/0.1233/0.7080/0.1788——全部命中。
- Table 4（Chowilla capacity）、Table 5（Burnett capacity）、Table 7（inducing/zone sweep）、Table 8（wet-corr）、Table 9（CRPS 0.0285/2.1550/0.1270，cov90_active 0.966/0.287/0.890，var_scale 0.417/0.419/0.604）全部命中。

**发现并修正 1 处溯源错误（Table 6）**：
audit trail 原 Table 6 的"Global native"行溯源写的是 `workflow_summary_full_Grp1_wse_ext.json`（该文件 lsg_max wet RMSE 实为 0.1539），"H-LSG"行写的是 `workflow_summary_full_Grp1_wse_ext_hlsg_residual_kmeans.json`（该文件实为 0.2673）。正确溯源：
- Global native（0.112, O2−O1 0.064）→ `workflow_summary.json`（= `workflow_summary_grp1_wse_ext_global_max_capacity.json`）
- H-LSG（0.094, O2−O1 0.005）→ `workflow_summary_full_Grp1_wse_ext_hlsg_sgpr_fix.json`
- H-LSG modes=0（0.112, 0.064）→ `workflow_summary_grp1_wse_ext_hlsg_budget1_max.json`

manuscript 数值本身全部正确，仅 audit trail 溯源列文件路径有误，已修正。**判定：manuscript Tables 2–9 数值真实、可追溯、与源 JSON 一致。**

**核验人:** Cursor Agent（本地 JSON 逐表核对）
**核验日期:** 2026-08-19

### Round F5-local 排版/图题终审 + 图号按引用顺序重排（2026-08-19）

**审图/审文方式**：本地全稿通读 `manuscript.md`（Abstract → Methods → Results → Discussion → Conclusions → References）+ 逐条通读 `_build_html.py` 中 15 个 figure caption + 重建后 `manuscript.html`/`manuscript.pdf` 终检。浏览器 MCP 仍可用，但 ChatGPT 会话已混入 JOH 项目上下文、F5 提示词未干净落盘，故本轮以本地终审收口（F2/F3 两轮 ChatGPT 真视觉审图已把 P0/P1 数值与视觉问题清干净）。

**关键发现并修复 1 处（图号顺序，纯排版问题，不改任何数值）**：

- 原 Figure 8（UQ 校准，Section 4.6）与 Figure 9（zoning 敏感性，Section 4.4）编号与正文引用顺序颠倒：Figure 9 在 §4.4 被引用、Figure 8 在 §4.6 被引用，导致图 9 先于图 8 出现。按"图号随首次引用顺序"惯例重排：
  - zoning 敏感性（原 Figure 9）→ **Figure 8**（§4.4）
  - UQ 校准（原 Figure 8）→ **Figure 9**（§4.6）

| 修复 | 文件 |
|---|---|
| 正文 `Figure 8`↔`Figure 9` 全部引用互换（§4.4 1 处、§4.6 2 处、§5.3 2 处） | `manuscript.md` |
| `fig8`/`fig9` 两段 caption 数字互换 + 内部文件 ID 与显示编号映射注释 | `_build_html.py` |
| 审计包 `## Figure 8/9` 标题与图片 alt 同步互换 | `figure_code_audit_pack.md` |
| 审计范围头 "Figure 1–8" → "Figure 1–9" | `audit_trail.md` |

**另记 1 处待作者定夺（未擅改）**：Section 7 Open Research 中 "code ... archived at https://github.com/Coucou2016/lsg-flood-surrogate-benchmark"。当前分析与代码实际托管于 `https://github.com/Coucou2016/20260522-LSG-WRR`（HEAD `40e9ca9`），二者为不同仓库。数据可用性声明属作者团队决策，故本轮仅标记、未改动 URL；建议投稿前由作者确认最终仓库名并统一。

**其余终审结论**：Abstract/Key Points/Discussion/Conclusions/References 英文表述与逻辑通读无残留问题；15 个 figure caption 英文已达标；无文本溢出、无字体/符号缺失；图号重排后 HTML 图注顺序 1→9 连贯。

**重建产物**：`manuscript.html`（3.99 MB，15 img tags，15 data URIs）、`manuscript.pdf`（1.86 MB），均本地重建完成。

**核验人:** Cursor Agent（本地全稿通读 + 图注逐条终审）
**核验日期:** 2026-08-19

### Round F6 图结构调整（删图一 + 简化 Fig7 + 合并 Fig8；2026-08-21）

**触发**：作者反馈三点（数据均经本地 JSON 复核，不改任何数值）：

1. **Figure 1（study domains）删除**——该图只是三个 HF 单元中心点云（无 DEM），只表达区域大小/形状；而淹没范围/水深误差/P(wet) 图（原 Fig2/3/4）本身就画在这三个区域上，区域形状已完整可见，且区域规模在 Table 1 已有。删图 + 正文 §4.1 删对应段，其余图号顺延。
2. **Figure 7（global vs H-LSG）子图 a（CSI）删除**——复核底层 JSON，CSI 确实极其接近且数据正确：
   - Carlisle Global 0.97569 vs H-LSG 0.97569（完全相同）
   - Chowilla 0.97443 vs 0.97560（差 0.0012）
   - Burnett 0.97511 vs 0.97515（差 0.00004）
   原因是 extent 由共享的 global EXT 门控决定、zoning 只作用在 WSE 分支，故湿域 CSI 几乎不变。CSI 在正文 §4.3 已文字说明（0.974→0.976），信息不丢失。→ 图改为**单面板 RMSE**（Carlisle 0.112→0.094 变好、Chowilla 0.088→0.093 略差、Burnett 0.179→0.387 明显变差）。
3. **Figure 8（zoning 敏感性）合并**——原 2 子图×3 柱（CSI 0.974/0.976/0.978、RMSE 0.088/0.093/0.094 都几乎不变）改**单面板分组柱状图 + 双 y 轴**（CSI 左轴 0–1，RMSE 右轴 0–0.12，均 0 起）。

**图号重排映射（删图一后顺延）**：extent→Fig1、peak-depth→Fig2、P(wet)→Fig3、cross-case→Fig4、O1–O4→Fig5、global-vs-H-LSG→Fig6、zoning→Fig7、UQ→Fig8。

| 修复 | 文件 |
|---|---|
| 删 `fig_study_domains` 调用；`fig_global_vs_hlsg` 改单面板 RMSE；`fig_zoning_sensitivity` 改双轴分组柱状图 | `make_figures.py` |
| 删 fig1 条目 + 4.1 插入分支；FIGURES 全量图号顺延 + Fig6/Fig7 图注改写 | `_build_html.py` |
| 删 §4.1 Fig1 段 + 全稿 `Figure N` 引用顺延 + §4.3 句改写（CSI 文字化） | `manuscript.md` |
| 删 Study-domains 段 + 图号顺延 + Fig6/Fig7 段内容更新 | `figure_code_audit_pack.md` |
| 新增 Round F6 条目 | `audit_trail.md` |

**重建产物**：删除遗留 `fig01_study_domains.*`；`make_figures.py` 重跑（14 图 × svg/pdf/png）；`manuscript.html`（3.68 MB，14 img tags，图注 1→8 连贯）；`manuscript.pdf`（1.75 MB）。

**核验人:** Cursor Agent（本地 JSON 复核 + 源码修改 + 重建）
**核验日期:** 2026-08-21
### Round F7 Chowilla ≈12 m 色标诊断（非数值故障；2026-08-27）

**疑点**：Figure 2b（Chowilla peak-depth）LSG 面板独立色标约 ±12 m，而 LF 仅约 ±1 m，视觉上像 LSG 灾难性退化。

**本地 `pred_examples.npz` 定量结论（不改任何 Table 数值）**：

| 域 | n | LSG RMSE | LSG max abs err | LSG q99 abs err | 机制 |
|---|---:|---:|---:|---:|---|
| wet_train | 36,124 | 0.093 m | 0.86 m | 0.41 m | 正常深度订正 |
| outside wet_train | 73,790 | 4.624 m | 15.27 m | 12.20 m | EXT 门控全零 |
| all_cells | 109,914 | 3.789 m | 15.27 m | 11.89 m | = Table 2 |

域外 51,264 个 HF-wet 单元上 LSG 深度恒为 0、LF 仍湿；色标 q99=11.89 m 全部由这些 EXT-gated 漏报驱动，湿域内无任何绝对值误差大于 1 m 的单元。

| 修复 | 文件 |
|---|---|
| peak-depth / extent 叠加 training-wet-domain 凸包虚线；面板标题标注 q99(abs err) | `make_figures.py` |
| §4.1 / §4.5 写明 ≈12 m 机制与 51,264 外域 HF-wet 计数 | `manuscript.md` |
| Fig 1b / 2a–c 图注补虚线与 q99 / EXT-gate 说明 | `_build_html.py` |
| 报告图3b 解读与论文一致 | `docs__report__report.md` |
| 新增本条 | `audit_trail.md` |

**重建产物**：`make_figures.py` 重跑；`manuscript.html` / `manuscript.pdf` 重建。

**核验人:** Cursor Agent（npz 逐单元诊断 + 图重建）
**核验日期:** 2026-08-27
