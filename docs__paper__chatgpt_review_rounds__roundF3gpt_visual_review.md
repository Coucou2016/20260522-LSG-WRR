# Round F3-GPT — 图-码真视觉双线审核（颜色 / 图例 / 标注一致性 + F2 修复落地核验）

**审图方式**：恢复浏览器 MCP 后，由 ChatGPT 网页检索 GitHub 公开仓库
`Coucou2016/20260522-LSG-WRR`（HEAD 固定到 `6b60375`，因 raw/.../main 命中了旧缓存，
ChatGPT 改用 SHA 固定读取），对 15 张图 PNG + 生成代码 + `figure_code_audit_pack.md`
做第 3 轮真视觉审图。

**核验人**：Cursor Agent（浏览器 MCP + ChatGPT 真视觉）+ ChatGPT
**核验日期**：2026-08-19

---

## ChatGPT 结论概览

- 上一轮 F2 声明修复的 6 项全部确认落地（Fig 5/7/9 CSI 0–1 轴 + 柱顶数值、Fig 4 标题、
  Fig 8c 标题、Fig 6 caption 独立 y 轴说明、Fig 1 equal-aspect 措辞）。
- **本轮未发现 P0 级错误，也无需要重算实验的 P1 数值问题。** 剩余均为绘图/图注层面的小修。
- 唯一建议优先修的 P1：**Figure 8c 仍保留截断基线**（coverage 柱状图 y 轴 0.80–1.02 起）。

---

## 逐图发现与处置

### P1（优先修复）

| 图 | 问题 | 处置 |
|---|---|---|
| Fig 8c | coverage 柱状图仍用 `ax.set_ylim(0.8, 1.02)` 截断基线，与已修掉的 Fig 5/7/9 同类视觉放大（0.990→0.966 几百分点被放大） | 改为 `0–1.02` 全尺度 + 4 根柱加三位数值标签，保留 0.90 nominal 虚线（`zorder=0`）；Before/After 图例移到 panel 下方 axes 外 |

### P2（图例 / panel 标注 / 审计包同步）

| 图 | 问题 | 处置 |
|---|---|---|
| Fig 1b/c | panel label `(b)/(c)` 与 y 轴 `×10^6` offset text 几乎相连 | 地图类 panel label 统一由 `x=-0.05` → `x=-0.12` |
| Fig 2a/b/c | legend 压在数据上（panel (a) 右上遮住 hit/false-alarm），字号 6 pt | 改为 figure-level `loc="outside lower center", ncol=4, fontsize=7`；panel label `x=-0.12`；suptitle `y=1.05` 增大与 panel title 间距 |
| Fig 3b/c | `(a)` 与 `×10^6` 相连；Burnett suptitle 与两个 panel title 垂向间距不足 | panel label `x=-0.12`；suptitle `y=1.05` |
| Fig 5 | legend 压住 Burnett 柱下部；Chowilla/Burnett 缺 LSG-TS 用 `—` 易被读成"接近 0" | legend 移到 figure-level 下方 `ncol=3`；`—` → `N/A`（且不画 0 高度 bar） |
| Fig 7 | legend 压住 Burnett 柱下部 | legend 移到 figure-level 下方 `ncol=2` |
| Fig 8b | fringe legend 压住 fringe spatial pattern | legend 由 `lower left` → `upper right` |
| Fig 8c | Before/After legend 压住柱底部 | 移到 panel 下方 axes 外 `bbox_to_anchor=(0.5, -0.22), ncol=2` |
| 审计包 Fig 6 | 摘录 caption 未同步 `_build_html.py` 新增的 independent-y-axis 两句 | 已同步 |
| 审计包 Fig 6 | Chowilla LSG-Max O1 写 0.021，manuscript Table 3 为 0.020 | 核对源 JSON（`chowilla_hlsg_max` test o1=0.0204877）→ 改为 0.020 |
| 审计包 Fig 8 | caption 把 (c) 泛写成 all-cell/active-cell，未标 Carlisle | 已同步为 "Carlisle all-cell and active-cell 90% coverage" |

### P3（字号 / 颜色语义统一）

| 图 | 问题 | 处置 |
|---|---|---|
| Fig 5/7/8d/9 | 柱顶数值 6 pt，缩放后偏小 | 统一升到 7 pt |
| Fig 5 | LSG-Max H-LSG 用 `PALETTE["lsg_max"]` 深蓝，而 Fig 7/9 同族用 `PALETTE["hlsg"]` 蓝，跨图颜色语义不一致 | Fig 5 改用 `PALETTE["hlsg"]`，legend 写完整为 "LSG-Max H-LSG" |

---

## 落地文件清单

| 文件 | 变更 |
|---|---|
| `scripts__make_figures.py` | Fig 5（颜色 hlsg / N/A / 7pt / 图例外移）、Fig 7（7pt / 图例外移）、Fig 8c（0–1 轴 + 标签 + 图例外移）、Fig 8b（图例位置）、Fig 8d（7pt）、Fig 9（7pt）、Fig 1/2/3（panel label x=-0.12 + suptitle y=1.05 + Fig 2 图例外移） |
| `docs__paper__chatgpt_review_rounds__figure_code_audit_pack.md` | Fig 6 caption 同步、Chowilla O1 0.021→0.020、Fig 8 caption 同步、Fig 5/7/8 代码片段同步 |
| `docs__paper___build_html.py` | 无改动（caption 已正确，仅审计包摘录落后） |

图已重新生成（15 图 × svg/pdf/png，共 45 文件），`manuscript.html` 与 `manuscript.pdf` 重建中。

**判定**：本轮为纯图面/图注清理，不触碰任何数值；manuscript 正文数值保持不变。
