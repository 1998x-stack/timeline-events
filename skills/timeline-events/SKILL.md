---
name: timeline-events
description: 输入历史、政策、外交、财经、科技或社会事件，检索核验并生成中文版式精确、可交互的时间轴 HTML；支持参考图片高保真复刻、SVG/PNG 导出和证据链。适用于“做事件时间线网页”“把图片复刻为HTML”“Apple风格点击时间轴”。
---

# Timeline Events · 事件研究与交互时间轴

**触发**：用户只说一个事件名称、一个事件主题或给一张时间轴参考图，期待真正生成 HTML / SVG / PNG，而不是仅得到提示词。

**进阶研究输出**：遇到人物崛起、政治权力网络、企业发展与长期争议，可在标准 JSON 加入可选 `research` 字段，生成分章研究报告、关系说明、主张核验与方法披露。见 `references/research-dossier.md`。

**运行环境**：Python 3.10+。本 SKILL 目录必须包含自身的 `scripts/`、`templates/`、`schemas/`、`references/` 与 `examples/`。允许从任何仓库根或任意工作目录运行。

## 先判断工作模式

- `research`（默认）：独立检索事实、阅读原文、建证据链；产出结构化 JSON、HTML、来源说明。
- `transcription`：仅按用户所给参考图忠实复刻，**明确未经独立核验**；不能把参考图写成研究事实。
- `update`：读取旧数据，对新增节点和政策状态做再核验，保留修订信息并重新生成。
- `publish`：在用户明确要求发布时，先遵守目标仓库 `AGENTS.md`，然后更新网站与目录，检查 CI 和 Pages。

## 完整流水线

1. **Scope**：界定主题、起止时间、参与方、读者和截止日期；可选配色、节点数不影响启动任务。
2. **Research**：原始协议、政府公告、裁判文书、论文和一手数据库优先，辅助新闻交叉核验；不得凭印象编日期或数字。阅读 `references/evidence-policy.md`、`references/source-governance.md`。
3. **Edit**：选取 4–10 个转折节点，按真实日期升序；记录主体、状态、简短标题、可核实描述及 URL。生成满足 `schemas/timeline.schema.json` 的 JSON。
4. **Render**：HTML 为第一产物；生成器只渲染结构化数据，不自行编造资料。模板位于 `templates/`，图片使用 `scripts/timeline_events.py`。
5. **Deep Dossier（选用）**：对复杂事件将 `research.chapters`、`research.connections`、`research.claim_audit`、`research.hypotheses`、`research.methodology` 纳入同一 JSON；标注来源与反证，禁止将同一社交圈的接触写成没有证据的秘密因果。
6. **Review**：核对原始来源与每个断言；检测 XSS 转义、文字溢出、手机纵轴、键盘焦点、动效关闭、来源披露与页面无 JS 可读性。
7. **Deliver**：交付 HTML + JSON + 证据；若请求 SVG/PNG 再生成；仅在被授权且测试通过后发布 Pages。

## 如何调用（路径以当前 SKILL.md 所在目录为准）

设 `SKILL_DIR` 是加载的 `SKILL.md` 所在文件夹，不是调用者当前工作目录。可在 shell 中设置：

```bash
SKILL_DIR=/absolute/path/to/timeline-events
python "$SKILL_DIR/scripts/render_html.py" "$SKILL_DIR/examples/reference-image-transcription.json" \
  --reference-transcription --output dist/reference/index.html
python "$SKILL_DIR/scripts/render_html.py" "$SKILL_DIR/examples/us-china-trade-war-verified.json" \
  --output dist/verified/index.html
python -m pip install CairoSVG
python "$SKILL_DIR/scripts/timeline_events.py" "$SKILL_DIR/examples/us-china-trade-war-verified.json" \
  --output dist/verified/timeline --format both
```

对于一个**新事件**：先调查并写 `data/<slug>.json`，再将上述输入路径替换成该文件。命令行不会自动联网检索。`metadata.updated_at` 表示核验截止日期，不得作为虚假的实时更新时间。

## HTML 与 Apple-inspired 动效

- 页面自包含，CSS/JS 内联，核心正文为真实 DOM；不依赖第三方 CDN。
- 2048×1280 横版白底财经时间轴，深蓝主轴、蓝红节点、四阶段与提示卡；手机改纵向原生阅读布局。
- 圆点为按钮，点击原生详情 `<dialog>`；支持左右键、Esc、焦点返回和来源链接。
- 首页卡片微抬、按压回弹、分类点击筛选；不要用动画掩盖信息。
- `prefers-reduced-motion: reduce` 必须有效；禁用 JS 时正文仍然完整展示。
- 具体规则阅读 `references/html-design-spec.md` 和 `references/motion-design-spec.md`。

## 证据边界

- 研究模式每条事件至少有一个已阅原始来源 `source_ids`；重要争议尽量两源比对。
- 转录模式需要 `metadata.verification_state=reference_transcription` 和明确的 `metadata.notice`，调用时加 `--reference-transcription`。
- **静态资料合法不代表来源支持内容**：`schemas` 与 CLI 验证不能代替人工语义核验。
- 未来事件必须显式标计划，最新节点红色仅是视觉强调，不能写成冲突结束。

## 校验门禁

从项目根（如有）执行 `python -m unittest discover -s tests -v`；通用 Skill 只需验证：

```bash
python "$SKILL_DIR/scripts/render_html.py" "$SKILL_DIR/examples/us-china-trade-war-verified.json" \
  --output /tmp/timeline-research.html
python "$SKILL_DIR/scripts/render_html.py" "$SKILL_DIR/examples/reference-image-transcription.json" \
  --reference-transcription --output /tmp/timeline-reference.html
```

仅在运行实际成功后向用户声称生成完成；如不能进行浏览器交互测试，需单独说明。发布 Pages 时再阅读 `references/site-integration.md` 和仓库根 `AGENTS.md`。

## 人物崛起深度研究示例

```bash
python "$SKILL_DIR/scripts/render_research.py" "$SKILL_DIR/examples/emmanuel-macron-rise.json" --output dist/emmanuel-macron/index.html
```

结构化 `research` 在标准时间轴下方渲染为深度专题，保持不依赖外网 JS、带原文引用、支持键盘导航与减少动态。`research.claim_audit` 应将可核实、应限定、原文数字不符和缺乏证据分别标注。
