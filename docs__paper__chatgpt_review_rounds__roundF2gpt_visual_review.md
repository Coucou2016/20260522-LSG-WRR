# Round F2-GPT — ChatGPT 真视觉图-码双线审核 + 落地修复

> 日期：2026-08-19（UTC+8）
> 方式：GitHub 仓库托管图片 + ChatGPT 网页检索看图（首次真正视觉审图）
> 仓库：https://github.com/Coucou2016/20260522-LSG-WRR
> 审核包：https://raw.githubusercontent.com/Coucou2016/20260522-LSG-WRR/main/docs/paper/chatgpt_review_rounds/figure_code_audit_pack.md

---

## 一、ChatGPT 总体结论

ChatGPT 实际打开了 15 张 PNG 图面 + 完整 `make_figures.py` + `manuscript.md`，做了真视觉审图。结论：

> **没有 P0 级问题**（无结果画反、单位错、阈值错、索引错）。代码正负号、事件索引、
> τ=0.03 m、hit/miss/FA 分类、Fig 5/7/9 数据源总体正确。
> 主要风险是**视觉编码会让读者得出比正文更强或不同的第一印象**，尤其 Chowilla
> scoring-domain、独立色标、CSI 截断柱状图。

---

## 二、ChatGPT 逐图发现（15 面板）

| 图 | 发现 | 严重度 |
|---|---|---|
| Fig 1 | "common easting and northing axes" 会被误解为 shared limits（实际是 equal-aspect） | P3 |
| Fig 2a Carlisle | 图例在 panel (a) 右上角覆盖真实淹没场 | P2 |
| Fig 2b Chowilla | 图上无 training wet-domain 边界，读者看不到正文关键解释（miss 集中在训练湿域外） | P1 |
| Fig 2c Burnett | 长窄 domain 使标题拥挤；图例覆盖上游 floodplain | P2 |
| Fig 3a Carlisle | 通过 | — |
| Fig 3b Chowilla | 独立色标使 ±1 m vs ±10–11 m 尺度差异被掩盖（第一眼显得误差相近） | P1 |
| Fig 3c Burnett | 同类独立色标解释问题 | P3 |
| Fig 4a Carlisle | 标题被截断 "LSG-Max inundation probabilit..." | P2 |
| Fig 4b Chowilla | 应强化 scoring-domain caveat（同步叠 wet-domain boundary） | P2 |
| Fig 4c Burnett | 通过；标题可统一缩短 | — |
| Fig 5 | **CSI 从 0.70 起（截断基线）放大 0.925 vs 0.976 的小差异**；LSG-TS 缺失 "—" 易误读 | P1 |
| Fig 6 | 四 panel 独立 y 轴但 caption 未醒目标明；审计包 O2/O4 舍入与 manuscript 不一致 | P1+P2 |
| Fig 7 | **CSI 从 0.90 起，截断基线放大 0–0.0012 的细微差异** | P1 |
| Fig 8 | panel (c) 未标明只画 Carlisle；panel (b) legend 覆盖空间结构 | P2 |
| Fig 9 | **CSI 固定 0.90–1.01，实际差异仅 0.001–0.003，视觉放大** | P1 |

**ChatGPT 强调的 6 项优先修复：**
1. Fig 2b/3b/4b Chowilla training wet-domain 边界或 caption caveat
2. Fig 3 caption 明确独立色标不可横向比较（显示各 panel 99th-percentile limit）
3. Fig 5/7/9 CSI 不要截断基线柱状图（改 0–1 全尺度 + 数值标签）
4. Fig 6 保留 independent y ranges 但 caption 明说
5. 统一 Fig 6 Carlisle Max 舍入（0.053/0.095 → 0.052/0.094，与 manuscript Table 3 一致）
6. Fig 4a 缩短标题；Fig 8c 标明 Carlisle coverage

---

## 三、本轮落地修复

### 代码（`scripts__make_figures.py`）
| 修改 | 内容 |
|---|---|
| `fig_cross_case` | CSI ylim (0.7,1.02)→(0,1.02) + 柱顶数值标签 |
| `fig_global_vs_hlsg` | CSI ylim (0.9,1.01)→(0,1.01) + 柱顶数值标签 |
| `fig_zoning_sensitivity` | CSI ylim (0.9,1.01)→(0,1.01) + CSI/RMSE 柱顶数值标签 |
| `fig_pwet_maps` | 标题缩短为 `{case} · {eid} · LSG-Max P(wet)`（修复截断） |
| `fig_uq_calibration` | panel (c) 标题 "Coverage"→"Carlisle LSG-Max coverage" |

### caption（`docs__paper___build_html.py`）
| 修改 | 内容 |
|---|---|
| Fig 6 caption | 明说 "Each panel uses an independent y-axis limit … bars should not be compared across panels by height" |

### 正文（`docs__paper__manuscript.md`）
| 修改 | 内容 |
|---|---|
| §4.1 line 149 | "common easting and northing axes" → "equal-aspect easting and northing coordinate axes" |

### 审计包（`figure_code_audit_pack.md`）
| 修改 | 内容 |
|---|---|
| Fig 6 数据表 | Carlisle LSG-Max O2 0.053→0.052、O4 0.095→0.094（与 manuscript Table 3 一致） |

---

## 四、ChatGPT 建议但本轮未做（记录备查）

- **Fig 2b/3b/4b 叠加 training wet-domain boundary 虚线**：需要从 `pred_examples.npz`
  读 wet_train mask 并在空间图上叠加轮廓，改动较大；caption 已在 Round F1 补了 caveat。
  若后续需要，可作为独立增强。
- **Fig 2a/2c 图例移到 figure-level**：较大改动，涉及 `fig_extent_hit_miss` 布局重构。
- **Fig 3 caption 显示各 panel 99th-percentile limit**：可选，需在 caption 动态注入数值。
- **Fig 8b legend 移出覆盖区**：小改，但 fringe map 左下角是唯一空白区，暂保留。

---

## 五、与 Round F1（Cursor 独立审图）的对比

Round F1 已发现并修复：fig09 未插入 HTML、Chowilla 外推 caption、fig03 共享色标拉爆、
fig08d log 轴、fig06 O3 压制、fig04 多余 (a)、fig03 colorbar 标签、fig08d xlabel。

Round F2-GPT（本轮）**新发现**（F1 遗漏）：
1. **Fig 5/7/9 CSI 截断基线柱状图放大微小差异**（统计呈现的实质问题，F1 未抓住）
2. Fig 4a 标题截断
3. Fig 8c 未标明 Carlisle（panel 标题层面）
4. Fig 6 caption 未明说独立 y 轴
5. 审计包 Fig 6 舍入笔误（0.053/0.095 vs manuscript 0.052/0.094）
6. Fig 1 "common axes" 措辞

说明"双线审核"有效：Cursor 独立审图抓视觉失衡（色标/坐标轴），ChatGPT 真视觉抓
统计呈现（截断基线）+ 措辞 + 舍入一致性，两者互补。
