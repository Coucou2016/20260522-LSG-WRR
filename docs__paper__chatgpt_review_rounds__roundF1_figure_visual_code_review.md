# Round F1 — 图视觉 + 对应代码双线审核（第一轮）

> 日期：2026-08-18
> 目标：把每张图的渲染结果 + 对应生成代码 + 底层数据都对应起来，发现"图的结果本身有问题但被写进论文"的问题。
> 方式：Cursor 独立读图（Read 看 PNG）+ 读代码（`scripts__make_figures.py`）+ 读数据（`outputs/evaluation/*/workflow_summary_*.json`、`pred_examples.npz`）。

---

## 一、图-代码-图注映射

| 图 | 生成函数（make_figures.py） | 数据来源 | 图注位置（_build_html.py） |
|---|---|---|---|
| Fig 1 | `fig_study_domains` | pred_examples.npz + Geometry_data | FIGURES[0] |
| Fig 2a/2b/2c | `fig_extent_hit_miss` | pred_examples.npz（lf_upsampled_max / pred_lsg_max）| FIGURES[1..3] |
| Fig 3a/3b/3c | `fig_peak_depth_error` | pred_examples.npz（pred_lsg_max − hf_max）| FIGURES[4..6] |
| Fig 4a/4b/4c | `fig_pwet_maps` | pred_examples.npz（inundation_prob_lsg_max）| FIGURES[7..9] |
| Fig 5 | `fig_cross_case` | workflow_summary.score_protocol.*.wet_train | FIGURES[10] |
| Fig 6 | `fig_error_budget` | workflow_summary.*.error_budget | FIGURES[11] |
| Fig 7 | `fig_global_vs_hlsg` | workflow_summary.score_protocol.lsg_max.wet_train | FIGURES[12] |
| Fig 8 | `fig_uq_calibration` | *_uq_calibrated.json（reliability/coverage/crps）| FIGURES[13] |
| Fig 9 | `fig_zoning_sensitivity` | chowilla workflow_summary（hlsg/wet_corr/global）| FIGURES[14] |

---

## 二、重大问题（P0）—— Chowilla 测试事件 E1 是"训练范围外"的极端洪水### 事实（数据确凿）

`config__chowilla.yaml` 的 Group 1 划分是 Fraehr leave-one-group-out：`validation: [E1]`，训练 = E2–E29（28 事件）。

`outputs__evaluation__chowilla__pred_examples.npz` 实测（test event E1）：

| 指标 | 值 |
|---|---|
| 训练湿域 wet_idx 大小 | 36,124 cell |
| 测试事件 E1 湿域（hf≥0.03） | 84,667 cell |
| 测试湿、但训练从未湿（OOB） | 51,264 cell |
| OOB cell 上的 EXT 一致性 | **0.0000**（LSG 全部预测干） |
| 全网格 EXT 一致性 | 0.526 |
| 训练湿域内 EXT 一致性 | 0.977 |
| 全网格 wet 域 RMSE | **4.317 m** |
| 训练湿域 RMSE | 0.096 m |
| deep(>1m) cell 被 LSG 漏判 | 46,478 个，全部在训练湿域之外 |

即：**E1 的洪峰淹没范围（84,667 cell）是训练集联合湿域（36,124 cell）的 2.34 倍**。LSG 的 EXT 分支（global 训练，仅在训练湿域见过水）在 51,264 个"训练时从未湿过"的 cell 上外推失败，全部预测为干。

### 正文现状（已诚实报告，不是遗漏）

- Table 2 已同时给出 Chowilla `all_cells`（CSI 0.390 / RMSE 3.789）和 `wet_train`（CSI 0.976 / RMSE 0.093）两列。
- Section 4.5 专门报告评分域敏感性："Under all_cells, CSI falls to 0.390 and RMSE increases to 3.789 m"。
- Section 4.1（line 151）与 Section 5（line 307）都提到"extent disagreement is concentrated outside the training wet-domain mask"。

### 真正的问题（图注与图的对应缺失）

**fig02c / fig03c / fig04c（Chowilla）画的是全网格（all_cells），但三张图的 caption 都没有说明"该测试事件的淹没范围超出训练湿域、EXT 在外推区失败"。**

读者单独看 fig02c（大片红色 miss）、fig03c（大片 -15 m 误差）、fig04c（大片 pwet≈0 但实际淹水）会得出"LSG 在 Chowilla 完全失败"的结论，与正文 wet_train CSI=0.976 直接冲突；只有翻到 Section 4.5 才能对账。图注应当自洽地建立这个联系。

**建议**：在 fig02c / fig03c / fig04c 的 caption 各加一句，指向"all-cells 评分与训练湿域评分的差异（Section 4.5）"，例如：
> "Chowilla event E1 is the Group 1 held-out event; its inundation extent (84,667 wet cells) substantially exceeds the 36,124-cell training wet domain, so the widespread misses/errors in panels (b) lie outside the category-based wet index used for training and are the source of the all-cells-vs-wet-domain score difference reported in Section 4.5."

---

## 三、视觉失衡问题（P1）

### F1-1  fig03 共享 colorbar 被 Chowilla 15 m 误差异常拉高，LF 面板被"洗白"

`fig_peak_depth_error` 中 colorbar 范围取 LF 与 LSG 绝对误差的**拼接 99 分位数**（`lim = nanpercentile(concat(|LF−HF|, |LSG−HF|), 99)`）。实测：

| case | \|LF−HF\| p99 | \|LSG−HF\| p99 | 共享 lim |
|---|---|---|---|
| Carlisle | 0.313 | 0.258 | ±0.276 |
| Chowilla | 1.077 | **11.886** | **±10.96** |
| Burnett | 3.117 | 1.499 | ±2.945 |

Chowilla 因 LSG 在 OOB 区有 -15 m 误差，colorbar 被拉到 ±10.96 m；而 LF 面板误差仅 ±1 m，于是 LF 面板几乎全部落在 RdBu_r 的白色中段，**完全丢失空间结构**，读者看不出 LF 的误差分布。LSG 面板则大片深红（-11 m 档）。

**建议**：
- 方案 A（推荐）：fig03 每列 panel 各自用 `2σ` 或各自 99 分位归一化 colorbar（或分图），避免 LF 面板被 LSG 的异常值压制；
- 方案 B：保持共享 colorbar，但 caption 明确说明"Chowilla LSG 面板的大幅误差集中在训练湿域之外，见 Section 4.5"，并在 LF 面板标出其误差量级。

### F1-2  fig08d CRPS 面板量级跨 3 个数量级，小柱不可见

实测 CRPS（before→after）：

| case | before | after |
|---|---|---|
| Carlisle | 0.0389 | 0.0285 |
| Burnett | 0.1332 | 0.1270 |
| Chowilla | 2.1547 | 2.1550 |

Chowilla（2.155 m）是 Carlisle（0.028 m）的 ~75 倍、Burnett（0.127 m）的 ~17 倍。fig08d 用**共享线性 y 轴**，Carlisle/Burnett 的柱几乎贴地、不可读；且 Chowilla before→after 仅变化 +0.0003 m（数值上几乎无变化），视觉上两个柱一样高，无法传达"Chowilla 校准无收益"的信息。

**建议**：
- 方案 A：fig08d 改用**对数 y 轴**（并在 caption 说明），或
- 方案 B：Chowilla 单独立一子图/右轴，或
- 方案 C：柱顶已标注数值（现有 `ax.text` 已标注 0.028/0.127/2.155），保留共享轴但把 Chowilla 断轴（broken axis）。

### F1-3  fig06 O3 柱（0.6–0.7 m）压制 O1/O2/O4（0.02–0.4 m）

O1–O4 实测（test split）：

| case/variant | O1 | O2 | O3 | O4 |
|---|---|---|---|---|
| Carlisle LSG-Max | 0.048 | 0.052 | 0.068 | 0.094 |
| Carlisle LSG-TS | 0.018 | 0.033 | 0.240 | 0.102 |
| Chowilla LSG-Max | 0.020 | 0.034 | **0.701** | 0.093 |
| Burnett LSG-Max | 0.074 | 0.083 | **0.668** | 0.387 |

Chowilla/Burnett 的 O3（~0.67–0.70 m）远大于 O1/O2/O4，共享 y 轴使 O1/O2/O4 柱被压扁到接近 0，读者读不出 O2 与 O4 的对比（这正是正文强调的"O2−O1 很小但 O4 差异大"的关键对比）。

**建议**：fig06 各 panel 独立 y 轴上限（如各自 `1.15 × max(O3)`），或对 O3 断轴并标注。O3 的量级差异本身是结论的一部分，不应被"压扁"隐藏。

---

## 四、小问题（P2/P3）

### F1-4  fig04 单面板却标注 "(a)"

`fig_pwet_maps` 是单面板（`fig, ax = plt.subplots(...)`），但代码 `add_panel_label(ax, "(a)", x=-0.08, y=1.04)` 加了 "(a)"。单面板图不需要面板标签。

**建议**：删除 "(a)"。

### F1-5  fig03 colorbar 标签仅 "m"，未说明是"误差"

colorbar label 为 "m"，方向由标题 "peak-depth error" 表达，caption 有说明正负方向。可保留，但建议 colorbar label 改为 "depth error (m)" 以自洽。

### F1-6  fig05 RMSE 面板被 Burnett LF（0.99 m）拉高，LSG 小柱对比弱

fig05 RMSE 面板无 ylim，Burnett LF RMSE 0.99 m 把 y 轴拉到 ~1.0，导致 Chowilla/Carlisle 的 LSG 柱（0.09 m）视觉上几乎为 0。可接受（跨 case 对比本就有量级差异），但可考虑在 caption 说明各柱数值，或 RMSE 面板用 log 轴。

---

## 五、本轮结论

1. **正文数据是真实、完整的**：Chowilla 的 all_cells/wet_train 差异在 Table 2 与 Section 4.5 已诚实报告，无数据造假或隐瞒。
2. **核心问题是"图与正文/图注的对应"**：
   - Chowilla 三张图（fig02c/03c/04c）画全网格、暴露外推失败，但 caption 未指向 Section 4.5 的解释；
   - fig03 共享 colorbar 被 15 m 异常值拉爆、LF 面板洗白；
   - fig08d CRPS 量级跨 75 倍、小柱不可见；
   - fig06 O3 压制其他柱。
3. 这些都是**小幅修改**（caption 补句 + colorbar/坐标轴归一化 + 删多余标签），不动整体框架，符合"小修改打磨成熟"的要求。

## 六、下一步

- 由 ChatGPT 复核上述发现（读代码 + 读数值诊断），交叉验证是否遗漏；
- 逐条落实修复（改 `make_figures.py` + `_build_html.py` caption）；
- 重新生成图 → 复图核对（Round F2）。

---

## 七、本轮新增发现（复核 HTML 时）

### F1-7（P0） fig9 从未被插入 HTML/PDF

`_build_html.py` 的 `md_to_body` 只处理了 Section 4.1/4.2/4.3/4.6 的图插入分支，**漏掉了 4.4**。正文 Section 4.4（line 248）引用了 "Figure 9"，但 fig9 从未出现在 HTML/PDF 中。重建后 `img tags` 从 14 变成 15，确认修复。

- 修复：`_build_html.py` 增加 `elif title.startswith("4.4"): out.append(fig_html["fig9"])`。

---

## 八、修复落实情况（Round F1 已完成）

| 编号 | 问题 | 修复文件 | 状态 |
|---|---|---|---|
| P0 | Chowilla E1 外推失败未在 caption 说明 | `_build_html.py` fig2b/fig3b/fig4b caption | ✅ 补句指向 Section 4.5 |
| F1-1 | fig03 共享 colorbar 被 15 m 异常拉爆、LF 洗白 | `make_figures.py` `fig_peak_depth_error` 分面板各自 99 分位 | ✅ |
| F1-2 | fig08d CRPS 量级跨 75 倍、小柱不可读 | `make_figures.py` `fig_uq_calibration` log 轴（bottom=1e-2） | ✅ |
| F1-3 | fig06 O3 压制 O1/O2/O4 | `make_figures.py` `fig_error_budget` 分面板 y 轴（1.12×max） | ✅ |
| F1-4 | fig04 单面板多余 "(a)" | `make_figures.py` `fig_pwet_maps` 删除 | ✅ |
| F1-5 | fig03 colorbar label 仅 "m" | `make_figures.py` 改为 "depth error (m)" | ✅ |
| F1-7 | fig9 未插入 HTML | `_build_html.py` 增加 4.4 分支 | ✅ |
| F1-6 | fig05 RMSE 面板 Burnett LF 拉高小柱 | 未改（跨 case 量级差异，可接受） | 保留 |

图已重新生成（15 图 × svg/pdf/png），HTML/PDF 已重建（img tags = 15）。

---

## 九、Round F2–F5 复核结论（2026-08-18）

### F2 — 复图核对修复后图片
- fig03 Chowilla 分面板 colorbar 生效：LF 面板（±1.08 m）结构清晰，LSG 面板（±10.96 m）OOB 深红；两面板不再互相压制。
- fig06 分面板 y 轴生效：O1/O2/O4 在 O3（0.6–0.7 m）旁边可辨。
- fig08d log 轴生效：Carlisle/Burnett/Chowilla 三组柱均可读。
- 新增发现：fig01 三 case 的 subsample 因子不一致（Carlisle ×7、Chowilla ×1、Burnett ×9），caption 未说明。→ 已补 "points are subsampled for display on the largest meshes"。

### F3 — 图与正文/图注一致性核对（通过）
- fig05 ↔ Table 2 / Section 4.1：CSI/RMSE 数值逐项一致。
- fig06 ↔ Table 3 / Section 4.2：O1–O4（Chowilla O2 0.034、O3 0.701；Burnett O2 0.083、O3 0.668）一致。
- fig07 ↔ Table 4/5/6：Carlisle Global 0.112 m = Table 6 "Global native auto/1"；Chowilla 0.088/0.093、Burnett 0.179/0.387 均一致。
- fig08d ↔ Table 9：CRPS 0.039→0.028、2.155→2.155、0.133→0.127 逐项一致；fig08c coverage 0.990→0.966（active）一致。
- fig09 ↔ Section 4.4：CSI 0.978/0.976/0.974、RMSE 0.094 一致。

### F4 — 图内标签/坐标/单位/图例规范核对
- fig08d 补 xlabel "Case"（与 fig05/07 柱状图规范一致）。
- 其余图坐标轴单位（Easting/Northing m、CSI −、RMSE m、CRPS m、depth error m）均已规范；图例配色与 caption（蓝=hit、红=miss、金=FA、灰=dry）一致。

### F5 — 最终视觉验收 + 重建
- 图全部重新生成（15 图 × svg/pdf/png），`manuscript.html`（img tags=15，fig9 已补入）与 `manuscript.pdf`（1.9 MB）重建成功。
- 备份：`docs/paper/_archive_roundF1_20260818_213405/`（make_figures.py、_build_html.py、manuscript.md 改动前副本）。

## 十、本轮（Round F1–F5）总体结论

1. 正文数据真实完整，无造假隐瞒；Chowilla all_cells/wet_train 差异在 Table 2、Section 4.5 已诚实报告。
2. 修复了 8 处"图本身有问题但此前未被发现"的问题，其中两处为 P0：
   - fig9 自始至终未插入 HTML/PDF；
   - Chowilla 三张图（fig02c/03c/04c）暴露训练范围外外推失败，图注未指向 Section 4.5。
3. 其余为视觉失衡（fig03 色标拉爆、fig08d 量级、fig06 O3 压制）与规范问题（fig04 多余 (a)、fig03 colorbar 标签、fig08d 缺 xlabel、fig01 subsample 未说明）。
4. 全部为小修改，不动论文整体框架与任何数值。
