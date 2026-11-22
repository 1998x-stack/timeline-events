---
name: timeline-events
description: 将一个历史、政策、外交、财经、科技或社会事件转化为可审计的中文时间轴网页。自动规划研究、检索及交叉核验关键节点、建立 JSON 证据链、生成可编辑且响应式的独立 HTML；可同时生成 SVG/PNG，并在具备仓库授权时发布到 GitHub Pages。触发示例：把中美贸易战做成时间轴HTML、某事件发展历程网页、参考图片的时间轴复刻、建立事件图谱并发布。
---

# Timeline Events｜从一个事件到可审计的时间轴 HTML

> **目标**：用户只提供一个事件名称，即研究、建模、校验、生成 HTML 网页；不是仅返回设计建议或一段绘图提示词。
>
> **底线**：事实模型与视觉模型分离。没有证据的数据不能用排版掩盖。`--reference-transcription` 用于忠实复刻用户图片的原始文字，并明确标记未经核验，绝不可冒称完成研究。

## 1. 任务路由

先判断用户输入属于哪一类：

| 模式 | 用户说法 | 事实处理 | 输出 |
|---|---|---|---|
| `research`（默认） | “中美贸易战，做一个时间轴 HTML” | 检索原始资料、交叉验证、逐节点 URL 映射 | HTML + sources.md；如需再导出 SVG/PNG |
| `transcription` | “把我这张时间轴图转成一模一样的 HTML” | 忠实转录图片内容，不擅自更正或补写；声明**未独立核验** | 版式还原 HTML、原图对照和核验提示 |
| `update` | “给已发布网页追加最新进展” | 读旧 JSON、查最新事件，只增修有证据事实、保留变更记录 | 新 HTML、证据差异、验证报告 |
| `publish` | “发布到 GitHub Pages” | 完成质量门禁后更新 `docs/` 目录与 `catalog.json` | Pages 站点、提交和 CI 状态 |

**默认语言**：简体中文。**输入最简**：事件名称。可选输入：起止日期、区域、读者、节点数量 4–10、设计参考、主色调、输出格式、是否公开发布。

## 2. 主题研究计划

1. 定义事件边界、关键参与方、时间范围、实际截止日期。相对日期在执行当日落实为绝对日期。
2. 从可能转折建立搜索关键词：启动、宣布、实施、生效、升级、协议、暂停、恢复、终止、裁定、实施效果。
3. 首选原始官方公告、协议正文、法律裁判、交易所文件、企业公告、论文和可复现统计表；使用媒体补充背景与时间。
4. 为每个候选节点记录 `date / actor / action / status / source_ids / uncertainty`；遇到争议数字、税率或影响分析时检索第二个**独立**来源。
5. 建立反证检查：官方表述是否单方主张、报道日是否误作生效日、总关税是否误作某一附加税率、签署是否被写成执行、预测是否被写成已发生。
6. 只选 4–10 个最具解释力的事件。超过 10 个则提出分卷或分段，不因密集而将文字缩为不可读大小。
7. 不允许把检索引擎结果摘要当作已经读过的材料；尽可能直接打开原始资料，确认标题、时间、关键词和口径。

**证据不可得时**：只生成待核验数据草稿，或在有用户上传参考图片时使用 `transcription`；明确不能把后者当作“事实调查完成”。

## 3. 数据模型与文件命名

研究模式使用仓库 `schemas/timeline.schema.json`：

```json
{
  "metadata": {"title":"事件标题", "subtitle":"摘要", "updated_at":"2026-11-22", "producer":"署名"},
  "sources": [{"id":"s1", "publisher":"原始机构", "title":"原文标题", "url":"https://..."}],
  "events": [
    {"date":"2020-01-15", "title":"短标题", "description":"可核验的一句话", "source_ids":["s1"]}
  ],
  "phases": [{"name":"阶段一", "period":"2018—2019", "summary":"阶段归纳"}],
  "insights": [{"title":"关键口径", "description":"对读图误区作解释"}]
}
```

约束：
- 4–10 个节点，时间升序，`YYYY-MM` 或 `YYYY-MM-DD`；未知精确日不要猜。
- 每个真实节点至少一个 `source_ids`，必须指向真实 `sources`。日期和语义要由 Agent 比对原文确认；CLI 只做形式校验。
- `status=planned` 的未来计划必须标为尚未发生；最后一个事件可 `highlight=true`，**红色不意味着已完全成功**。
- 如果图文不清晰，先编辑精简标题或分图，绝不能截断核心事实。
- `metadata.updated_at` 是**事实核查截止日**，不是渲染脚本运行日期。
- `metadata` 和 `events` 的自由文本不可含 HTML；渲染器会进行 HTML 转义，禁止关闭转义。

复刻模式专用 `examples/reference-image-transcription.json`：保留图中文字的 `lines` 来精准控制换行，并在 `metadata.verification_state` 中显式声明 `reference_transcription`；`metadata.notice` 必填。参考图本身给出的“机构名单”并非逐条可点击原始证据，未经核验就不能填入研究模式的 `sources` 假装真实引文。

## 4. 渲染：HTML 为第一产物

在仓库根目录，先运行：

```bash
python scripts/render_html.py data/<slug>.json \
  --output dist/<slug>/index.html
```

生成 HTML 的要求：
- **单文件独立**：内联 CSS、正文全部是真实 DOM 文本；浏览器无 JS 时仍可读正文。JS 只用于响应式缩放，不负责加载故事内容。
- **原版风格**：2048×1280 白底信息图；顶部深蓝标题/分割线/灰色副标题，浅蓝阶段跨度卡，深蓝主轴；事件上下交错；历史蓝点，末端红点；四阶段卡、三个阅读提示、底部来源和等距提醒。
- **响应式**：桌面保持参考图位置关系；窄屏改为垂直事件列表，避免缩得无法阅读。
- **语义与无障碍**：h1/h2、article/section、ol、time、足够的对比度、可选择与复制的文字、移动端可聚焦链接。
- **事实披露**：生成页必须有可见的证据说明或转录免责声明，不得只在注释里写“未核验”。

用户给图片、要求视觉一模一样时：

```bash
python scripts/render_html.py examples/reference-image-transcription.json \
  --reference-transcription \
  --output dist/reference/index.html
```

**禁止**在正式研究出版流程中使用 `--reference-transcription` 绕过缺少证据的错误。这样生成的页面必须在站点目录用“原图复刻 · 尚未核验”标注。

## 5. 可选：导出其他格式

研究模式可继续用已有的 SVG/PNG 渲染器：

```bash
python -m pip install -r requirements.txt
python scripts/timeline_events.py data/<slug>.json \
  --output dist/<slug>/timeline --format both
```

输出：`index.html`、`timeline.svg`、`timeline.png`、`timeline.sources.md`。注意旧 PNG 渲染器和新 HTML 渲染器目前是独立版式实现，不能声称像素完全相同。HTML 的精确视觉基准见 `references/html-design-spec.md`。

## 6. 内容分类及发布

六大类见 `references/site-architecture.md`，首页正式数据在 `docs/data/catalog.json`。发布一个新页面的顺序：

1. 采用规范化 slug（如 `us-china-trade-war`），将**已核验**数据放入 `data/<slug>.json`，生成 `docs/events/<slug>/index.html`。
2. 编辑 `docs/data/catalog.json`，添加真实存在的条目。`status` 只能按实际状态填写 `verified` 或 `reference_transcription`；不得把未核验示例标为验证完成。
3. 使用正确的相对路径 `./events/<slug>/`，适配项目子路径 `/timeline-events/`。分类标签需来自既定 taxonomy id。
4. 发布前执行测试、网页 DOM 结构检查、链接检查、移动端和桌面视觉检查。
5. 提交并运行 GitHub Actions，部署后实际请求公开 Pages URL 验证；成功部署日志 **不等于**公开站点可访问。
6. 若 Pages 未启用或 GitHub 权限不够，明确告知需要在仓库 Settings → Pages 将 Source 设为 GitHub Actions；默认 GITHUB_TOKEN 无法首次开启 Pages。不得谎称站点已上线。

**仓库路径**：
- `.pi/skills/timeline-events/SKILL.md`
- `.agent/skills/timeline-events/SKILL.md`

两份 SKILL 正文必须逐字节相同，使用 `python scripts/verify_skill_sync.py` 校验。全部执行细则在根目录 `AGENTS.md`。

## 7. 质量门禁 / Definition of Done

```bash
python -m unittest discover -s tests -v
python scripts/verify_skill_sync.py
python scripts/render_html.py examples/reference-image-transcription.json --reference-transcription --output dist/reference/index.html
```

检查：
- [ ] 事件日期顺序/具体状态/数字口径/URL 来源对应且原文可验证
- [ ] 资料截止时间准确；未来事项非事实化；争议与单方主张有标注
- [ ] 2048×1280 布局中 10 个节点无重叠，文字不被裁剪，简体中文清晰
- [ ] 窄屏事件列表按时间排列，全文可阅读；键盘操作可用
- [ ] HTML 单文件离线可阅读，内容经 HTML 转义，不插入用户脚本
- [ ] 参考转录模式必须标记“未核验”且不出现在验证完成筛选里
- [ ] 首页分类数量来自 catalog，不虚增条目，搜索筛选和提示词复制可用
- [ ] 现有 SVG/PNG 功能及测试未被破坏
- [ ] CI 全绿、Pages 部署状态与真实公网打开状态分别记录

## 8. 使用者交付清单

向用户提供：完整 HTML 链接或文件、研究数据截止日、SVG/PNG（如请求）、来源列表或来源文档、发布到哪个仓库/分支/提交、CI 与 Pages 真实状态、无法核实的限制事项。不要说“后台会自动更新”——除非确实创建有调度器与可运行的数据流水线。

## 9. 延伸设计参考

- `references/html-design-spec.md`：与用户参考图的坐标/排版规范、响应式行为
- `references/site-architecture.md`：首页内容层级、分类与检索策略、目录统计口径
- `references/source-governance.md`：事实与来源质量、可核验性、发布审批
- `AGENTS.md`：工作分工、编码规则、内容生命周期、CI / Pages 运维
