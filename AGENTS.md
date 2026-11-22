# AGENTS.md — Timeline Events 工程、研究与出版协议

> 对所有在本仓库工作的 AI Agent（Pi、Agent、Codex、GitHub Actions、研究助手）生效。本文件具有高于 README 示例的执行优先级：任何实际提交应遵循核验、排版、测试与发布门禁。仅当用户明确要求图片原样转录时，允许保留待核验原文，但**不得冒称已经调查确认**。

## 0. 项目职责与非目标

**使命**：把历史、政策、外交、经济、科技、社会或企业事件转化为**事实可追溯、时间顺序明确、网页文字可读、设计可复用**的时间轴信息产品。

**输入**：一个事件名称（可带时间范围、背景图片、研究重点）。

**标准产出**：一个结构化 JSON 数据文件、一个可离线打开的 HTML 页面、证据映射与核验说明；在请求或发布流程需要时补充 SVG、PNG、GitHub Pages 目录卡和 CI 报告。

**非目标**：

- 仅靠语言模型想象世界大事的日期、轮次、协议、票数或关税金额；
- 在未验证来源时把用户上传的图片转录数据发布成“经核验”研究稿；
- 把图片或 Canvas 放大当作唯一 HTML 内容；
- 在静态 GitHub Pages 浏览器里伪装成已接入外部大模型；
- 对未具备调度器的静态网页承诺实时自动更新。

## 1. 执行顺序（不得跳过）

1. **Read**：读取 `README.md`、对应入口的 `SKILL.md`、`references/*`、相关 schema 和现有数据。确认任务是研究、图片转录、更新还是部署。
2. **Scope**：明确具体主题、时间范围、终止日期、面向读者和图片或网页格式。非必需参数可按默认值推进；不要为了可选配色反复询问用户。
3. **Research**：如需增加事实，检索一手资料，逐节点建立证据；遇到关税、财政、法律、争议数字需要精确口径。
4. **Model**：编排 `metadata / sources / events / phases / insights`，保留原始来源及不确定性。必要时将长时间跨度拆成多个专题。
5. **Render**：调用 `scripts/render_html.py` 生成语义化 HTML。图片转录仅可使用 `--reference-transcription`；其他研究稿严禁绕过验证器。
6. **Inspect**：使用可用浏览器检查 2048×1280 桌面版，375px/768px 移动版与平板版；抽查 DOM 文本、链接、字体、重叠与视觉。
7. **Validate**：运行完整 Python 测试、SKILL 双目录一致性、站点目录链接校验、可选 PNG/SVG 输出校验。
8. **Publish**：经授权更新 `docs/`、`catalog.json` 与 `README`，完成 commit；关注 GitHub Actions 和 Pages 成果。已合并不等于 Pages 可访问。
9. **Report**：中文简述改动、准确文件路径、测试/部署状况、真实 URL、证据截止日期及未完成内容。

## 2. 文件职责与单一事实源

```text
timeline-events/
├── .pi/skills/timeline-events/SKILL.md     # Pi 入口，必须与 .agent 一字不差
├── .agent/skills/timeline-events/SKILL.md  # Agent 入口
├── AGENTS.md                              # 本协作约束
├── README.md                              # 用户操作与示例
├── references/
│   ├── evidence-policy.md                 # 既有 SVG 工作流事实规范
│   ├── visual-spec.md                     # 既有 SVG 工作流视觉规范
│   ├── html-design-spec.md                # 2048×1280 HTML 复刻坐标
│   ├── site-architecture.md               # Pages 首页、分类和导航
│   └── source-governance.md               # 已核验 vs 原图转录治理
├── schemas/
│   └── timeline.schema.json               # 研究模式输入 schema
├── scripts/
│   ├── timeline_events.py                 # SVG/PNG 的既有确定性渲染器
│   ├── render_html.py                     # HTML 唯一生成入口
│   ├── check_site.py                      # 目录与链接门禁
│   └── verify_skill_sync.py               # 两份 SKILL 正文一致性
├── templates/
│   ├── timeline.html                      # 自包含 HTML 模板
│   └── timeline.css                       # 参考图高保真样式
├── examples/
│   ├── us-china-trade-war-verified.json   # 已有历史研究数据示例；截止日见内容
│   └── reference-image-transcription.json # 上传图片原文转录，未经事实独立审计
├── docs/                                   # GitHub Pages 根目录（项目子路径）
│   ├── index.html                         # 首页 / 导航 / 创作入口
│   ├── data/catalog.json                  # 唯一事件目录、分类数据源
│   ├── assets/site.css                    # 首页样式
│   ├── assets/site.js                     # 搜索、筛选、提示词复制
│   └── events/<slug>/index.html           # 每篇独立静态 HTML 页面
├── tests/                                  # 自动化测试
└── .github/workflows/                      # 测试与 Pages 自动发布
```

`docs/data/catalog.json` 是首页已发布数量和分类展示的唯一数据源；不能在前端硬编码虚构数量。研究事实的唯一数据源是对应 JSON；HTML 是**编译产物**，不应在生成后手工改正文文字而不更新数据。

## 3. Agent 角色协作与审计产物

同一个 Agent 可以承担多个角色，但不得跳过角色职责：

| 角色 | 输入 | 职责 | 可检查的产物 |
|---|---|---|---|
| Research Planner | 事件名称 | 定义问题、时间范围、关键参与方与信息缺口 | 研究计划 / 搜索关键词 |
| Evidence Researcher | 计划 | 搜索并阅读原始材料、建立事实候选 | 来源 URL、原文时间、关键语句 |
| Source Critic | 候选节点 | 检查反例、主体、数字口径和发生状态 | 争议说明、修订意见 |
| Chronology Editor | 经核验的事实 | 挑选 4–10 个转折点、写阶段与精炼文案 | 规范 JSON |
| Layout Engineer | JSON、模板 | 渲染可编辑 HTML、可选 SVG/PNG | 实际可打开页面 |
| QA Reviewer | 页面与 JSON | 检查事实/DOM/视觉/安全/移动端/链接 | 测试记录及差异清单 |
| Publisher | 全部通过的材料 | 更新 catalog、CI、Pages | Git commit、站点 URL、部署状态 |

角色之间以**结构化文件和可定位证据**传递结论，不以“我已经看过了”的自然语言宣称替代记录。

## 4. 事实治理与研究规则

### 4.1 最小证据单元

每个真实事件至少具备以下内容：

- `date`：事件发生日期，精度按证据决定，不能凭感觉编造日。
- `actor + action + object`：主体、行为和作用对象。
- `status`：宣布/计划、签署、实施、生效、暂停、完成或裁决。
- `source_ids`：指向实际打开确认过的原始网页或文件。
- `updated_at`：当前事实核对截至日期，不得用脚本运行日期假装更新。
- `uncertainty`：存在争议或单方声明时，在正文或来源注释显式说明。

### 4.2 优先级与冲突

优先官方原始公告、协议和裁判文书；其次论文与一手数据库；媒体用于交叉确认与补齐时间。来源内容冲突时，不可拼成虚假的统一结论；可写“甲方声明……，乙方回应……”，必要时在正文短句中保留争议。

对于经济与科技类数据：核对美元 / 人民币、亿美元 / 亿美元货值、实际税率 / 某一附加税率、税率 / 百分点、预测 / 统计等口径。

**技术边界**：现有 Python 验证器只能验证格式、引用存在、URL 语法、时间顺序和文案长度，**不能**判断 URL 内容是不是支持断言。研究 Agent 必须承担语义审计，不能把 CLI 成功等同于事实真实性。

### 4.3 参考图片转录治理

用户要求“与所附图片一模一样”的文字复刻时：

1. 图片文字按照视觉从左到右抄录，不得以模型“印象中的历史”静默修改。
2. 独立保存 `examples/reference-image-transcription.json`，使用 `reference_transcription` 状态。
3. 若原图本身疑似事实有误，在可见的**版式外**声明“仅为内容转录，未经独立核验”；有核验要求时另做研究版。
4. 禁止为通过 schema 而将官网首页 URL 写成具体主张来源。参考模式与研究模式必须分离。
5. 首页卡片标注“原图复刻 · 尚未核验”，且内容计数实事求是。

## 5. 时间轴内容设计标准

### 5.1 时间范围与节点密度

- 默认 4–10 个节点；10 个为参考图密度上限。长主题可按时代/阶段拆分系列。
- 关键节点必须代表真正的**状态变化**；避免纯新闻报道频次构成的伪时间轴。
- 事件按日期升序；视觉上均匀间隔时必须写明“不按时间比例”。
- 首尾月份自动计算历时。**不能把起算点写成研究启动时间而用结束节点估算假的历时**。
- 最后节点可标红作为“最近”，但不能据此认定冲突已经结束。

### 5.2 文案

- 事件标题简短、描述不超过三行；复杂背景放在图外证据文档。
- 标题、副标题、来源说明均为真实可复制 DOM 文本。中文文本原则上避免全大写字母混排和不必要的术语堆积。
- 书写“暂停至YYYY-MM-DD”时要确认是哪一类措施被暂停，不能推成所有措施同步解除。
- 重要结论“为什么重要”必须比“发生了什么”更有解释力，但不能超出已知证据。

## 6. HTML 与 CSS 工程规范

- **参考版 2048×1280**：顶端标题、分割线、概览条、交错节点、阶段卡片、阅读提示、页脚。坐标与视觉 tokens 参见 `references/html-design-spec.md`。
- HTML 第一、图片第二。不是把 PNG 填进 `<img>` 就算转化完成。
- 生成器默认输出**自包含 HTML**：CSS 内联、事件文字静态写入 DOM、缩放脚本无外部依赖；页面至少离线可读。
- 移动设备切换为自然流的纵向 `ol/li` 列表；不能强迫用户在手机上阅读 2K 缩小字。
- 语义结构包含 `main/article/header/section/footer/h1/h2/time`；来源 URL 在 `<a>` 中显示可点击并用 `rel="noopener noreferrer"` 保护外链。
- 所有未信任字符串使用 `html.escape(quote=True)`；禁止在浏览器里直接将 JSON 拼为 `innerHTML`。
- 保持浏览器无外部网络也能显示关键正文；动态功能不是正文存在的前提。
- 支持键盘导航、focus-visible 和减少动态效果偏好；颜色对比不应只靠红蓝传达含义。
- CSS 变量集中管理基本颜色和字体；不随意叠加第三方 CSS 框架。

### 6.1 图片像素视觉差异

`2048×1280` 是布局坐标基准，字体本地渲染可在不同系统略有差异。**优先保证文本不溢出和内容正确**，再追求像素级的模仿。不要承诺所有平台 100% 逐像素一致。可以记录比对截图和坐标误差；若必须调整模板先更新 `references/html-design-spec.md`。

## 7. 首页信息架构与数据纪律

首页应有：品牌与路径、主张、真实统计、可检索目录、一级分类、发布状态、研究流程、可复制的 SKILL 指令、使用文档与源码链接；详情见 `references/site-architecture.md`。

分类固定为以下一级 ID，未来扩展需更新 catalog / UI / tests / 文档：

1. `diplomacy`：国际关系与贸易；
2. `policy`：政策与法治；
3. `technology`：科技与产业；
4. `business`：商业与金融；
5. `society`：社会与文化；
6. `history`：历史与战争。

每篇文章**一个主分类**，允许多个 `tags`；不要为了增加版面丰富度填虚构文章、虚假浏览量、虚假评级或“已核验”的假标签。

`docs/data/catalog.json` 的条目必须包含：`slug/title/description/range/nodes/category/tags/updated_at/status/url`。`url` 指向实际存在的 `docs/events/<slug>/index.html`；将路径写成 GitHub Pages 的域名根路径 `/events/...` 会破坏项目站点的 `/timeline-events/` 前缀。

首页“创作入口”只生成并复制 prompt；没有后端就绝不显示运行进度、模型响应或“HTML 已生成”。如未来新增 API：先做密钥保护、调用配额、费用控制、滥用检测、日志脱敏和明确授权，然后才可启用。

## 8. 变更策略与保留兼容

- **不要删除**已有的 `scripts/timeline_events.py`、`schemas/timeline.schema.json`、`examples/us-china-trade-war-verified.json`、旧测试、SVG/PNG CI；HTML 是增强而非替代。
- 修改 SKILL 必须同时修改 `.pi` 与 `.agent` 文件，`verify_skill_sync.py` 必须通过。
- 修改 HTML 生成器同步模板、示例数据、测试以及 README 使用方式。
- 数据 schema 变更应能解释向后兼容，旧验证示例至少仍可生成 HTML/SVG/PNG。
- 不接受引入网络端脚本、CDN 字体或无必要的大型框架作为核心正文依赖。
- GitHub Pages 为静态公开内容：不要把 API Key、访问令牌、个人信息或付费材料放入 `docs/`。
- 不要通过 GitHub Pages 工作流越权修改不在本项目的其它仓库。

## 9. 本地验证与 CI 门禁

从仓库根目录执行：

```bash
python -m unittest discover -s tests -v
python scripts/verify_skill_sync.py
python scripts/check_site.py
python scripts/render_html.py examples/reference-image-transcription.json \
  --reference-transcription \
  --output dist/reference/index.html
python scripts/render_html.py examples/us-china-trade-war-verified.json \
  --output dist/verified/index.html
python -m pip install -r requirements.txt
python scripts/timeline_events.py examples/us-china-trade-war-verified.json \
  --output dist/verified/timeline --format both
```

验收表：

- [ ] schema / 年月顺序 / 事件长度 / 末节点高亮合法；
- [ ] 来源真实可访问且内容确实支持节点语义；
- [ ] 默认研究模式拒绝缺少来源的转录数据；
- [ ] 转录模式必须有 `reference_transcription` + 可见免责声明；
- [ ] HTML 2048×1280 桌面版 10 节点、4 阶段、3 提示，中文不溢出；
- [ ] 手机纵向列表可读、打印不会丢失核心内容；
- [ ] HTML 正文可被 DOM 选择、复制，动态文本安全转义；
- [ ] 首页目录中链接可在构建产物中解析，分类 ID 合法、无虚报数量；
- [ ] 检索、过滤、prompt 复制等前端功能可通过手工或自动浏览器测试；
- [ ] Python 测试与 GitHub Actions 全通过，已有 SVG/PNG 产物不回退；
- [ ] Pages 发布结果查看 Actions URL + 公网 HTTP 状态，不能用提交成功替代。

### 9.1 GitHub Pages 发布

发布工作流在 `.github/workflows/pages.yml`，源文件来自 `docs/`，不再维护易失的手工 `gh-pages` 内容快照。部署须请求 `pages:write` 和 `id-token:write`，尽量使用最小权限。首次部署前需由仓库管理员在 **Settings → Pages → Build and deployment → Source = GitHub Actions** 开启 Pages；仅使用默认 `GITHUB_TOKEN` 的工作流无法自动完成首次启用。

**失败处理**：CI 或 Pages 未通过时，需要读取对应 job 日志、定位问题、修改后再运行。不可无限自动重试，也不可隐瞒错误状态。

## 10. 报告格式

发布后用中文提供：

1. 完成的实际修改（参考 HTML / SKILL / 首页 / AGENTS / 测试）；
2. 可用的仓库文件链接与 Pages 站点链接（仅在验证上线后描述为已上线）；
3. 最新 commit、构建与部署状态、通过的测试数量；
4. 数据来源日期、参考转录/审校状态、任何残余风险；
5. 如因权限无法打开 Pages，说明需要用户完成的**一项具体设置**，不要猜测成功。

## 11. 最终的工作原则

**Correctness > Provenance > Legibility > Decoration > Automation.**

时间轴的价值来自时间和因果逻辑的可信组织，不来自图上有多少个圆点。对于复杂事件，宁可减少节点、明确边界、附来源，也不输出“看起来专业但事实不可追溯”的图片或 HTML。
