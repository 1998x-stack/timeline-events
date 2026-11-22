# Timeline Events｜把复杂事件放回时间里

**事件名称 → 原始资料核验 → 结构化时间轴 → 高清 HTML/SVG/PNG → GitHub Pages。**

本仓库提供可复用的 Pi/Agent SKILL、Python 确定性渲染器和静态事件资料库网站。新增的 HTML 引擎把用户参考图片复刻为**可选择文本、可编辑 CSS、响应式可阅读**的真实页面，而不是插入一张图片。

- **首页**：[Timeline Events GitHub Pages](https://1998x-stack.github.io/timeline-events/)
- **示例时间轴**：[中美贸易战参考图 HTML 复刻](https://1998x-stack.github.io/timeline-events/events/us-china-trade-war/)
- **部署前提示**：以上是目标地址，是否已经公开可访问以 GitHub Actions 部署结果和实际网站访问为准。

## 1. 使用 SKILL（只需主题）

在可以读取本仓库文件的 Pi / Agent 环境中输入：

> 使用 timeline-events SKILL，深度调查“中韩自贸协定第二阶段谈判”，截至今天，挑选6–10个关键节点，交叉核对原始来源，生成与参考图风格一致的可编辑 HTML、来源说明，必要时导出 SVG 和 PNG。

对应目录：

- `.pi/skills/timeline-events/SKILL.md`
- `.agent/skills/timeline-events/SKILL.md`

两者保持字节级一致；共用 `scripts/render_html.py` 和 `scripts/timeline_events.py`，不会出现两个版本的渲染逻辑。

## 2. 直接体验：用户参考图复刻

上传图片中的文字被逐条抄录到 `examples/reference-image-transcription.json`，以原图版式在 `2048×1280` 画布上还原：顶部粗标题、浅蓝概览栏、10 个上下交错节点、4 个阶段卡、3 个阅读提示及底部资料注释。

```bash
python scripts/render_html.py examples/reference-image-transcription.json \
  --reference-transcription \
  --output dist/reference/index.html
```

浏览器打开 `dist/reference/index.html`，无需联网或安装前端依赖。手机会切换为纵向时间轴列表。

> **事实提示**：此示例是用户上传图片的**忠实文字转录，不是独立事实审计**。原图中的事件、法律和关税数字尚未由本示例逐条核对。图片复刻和经核验研究是两种不同状态，不得混用。

## 3. 严格研究模式（默认）

为任一真实事件创建完整的 `data/<slug>.json`（按 `schemas/timeline.schema.json` 编写）；每个事件提供原始来源 URL 和 `source_ids`。缺乏来源时，默认不允许生成冒充审校完成的页面。

```bash
# 本仓库既有的研究数据示例：仅覆盖其内标明的历史时段
python scripts/render_html.py examples/us-china-trade-war-verified.json \
  --output dist/trade-war/index.html

# 可选：SVG + PNG（PNG 需要 CairoSVG）
python -m pip install -r requirements.txt
python scripts/timeline_events.py examples/us-china-trade-war-verified.json \
  --output dist/trade-war/timeline --format both
```

HTML 引擎输出一个**独立的 HTML 文件**，可离线打开。PNG 与 SVG 为现有绘图引擎的独立版式输出，不等同于 HTML 的像素截图。

## 4. 网站架构与分类

首页已包含：品牌与介绍、真实数量、事件浏览搜索、6 大类主题导航、证据流水线、可复制的 Agent 生成指令、项目使用文档。

| 主分类 ID | 名称 | 主题示例 |
|---|---|---|
| `diplomacy` | 国际关系与贸易 | 双边谈判、贸易争端、制裁、国际组织 |
| `policy` | 政策与法治 | 立法、司法、监管、公共治理 |
| `technology` | 科技与产业 | AI、芯片、能源、产业升级 |
| `business` | 商业与金融 | 企业发展、并购、宏观经济、资本市场 |
| `society` | 社会与文化 | 社会事件、公共卫生、教育、文化 |
| `history` | 历史与战争 | 战役、条约、政权与重要历史转折 |

`docs/data/catalog.json` 是唯一的目录数据源：分类数量和节点总量均从真实条目计算。当前仅收录一份**图片复刻演示**，其它类别是结构规划，不虚构文章填充版面。

网站创作表单仅**生成可复制的 Agent 指令**；GitHub Pages 是静态托管，不能在浏览器里秘密调用模型或直接生产未核验的事件数据。

更多信息架构：`references/site-architecture.md`。

## 5. 目录

```text
.pi/skills/timeline-events/SKILL.md    Pi 版入口
.agent/skills/timeline-events/SKILL.md Agent 版入口
AGENTS.md                               多角色职责、内容审计与开发协作规范
references/                             视觉、来源、网站分类与研究规范
schemas/timeline.schema.json            研究数据格式
scripts/render_html.py                  HTML 渲染器（标准库）
scripts/timeline_events.py              SVG/PNG 渲染器（原有）
templates/timeline.{html,css}           可维护的 DOM/CSS 版式
examples/                               可复现示例
docs/                                   GitHub Pages 公开网站
docs/events/us-china-trade-war/         用户图片 HTML 复刻示例
tests/                                  回归测试
.github/workflows/                      CI + Pages 发布
```

## 6. 质量测试

```bash
python -m unittest discover -s tests -v
python scripts/verify_skill_sync.py
python scripts/check_site.py
```

GitHub Actions 自动验证双目录 SKILL、HTML 渲染、旧 SVG/PNG 输出与静态站点链接，并上传示例产物。Pages 工作流在 `main` 更新时把 `docs/` 部署为项目站点。

**发布纪律**：只有研究 Agent 阅读原文并完成逐节点语义核对后，才能给目录条目标记 `verified`；渲染器校验 URL 形式不是事实审计。

## 7. 维护与贡献

- 变更前阅读 `AGENTS.md` 和目标 SKILL。
- HTML 模板改动同步测试 2048×1280 参考图与手机纵向展示。
- 提交任何事件需注明研究截止日、关键出处和残余争议。
- 不向静态站点上传密钥、个人隐私、付费原始材料或未获授权的媒体图片。
- 不在 `docs/` 直接手工修改生成的事件正文，变更应回到 JSON 再生成。
