# AGENTS.md · Timeline Events 工程、研究与发布协议

此文件对在 `timeline-events` 仓库工作的所有 Agent、生成人员及审查者生效。**本文件是仓库级约束，不属于可移植 Skill 的内部资源。** 一个独立安装的 Skill 只需读取 `skills/timeline-events/SKILL.md` 及其 references，不需要依赖此仓库。

## A. 目标、不可妥协规则与权威目录

项目使命：把复杂事件变为**有证据、可读、可互动、可复现**的时间轴网页。默认输出独立 HTML，可选 SVG/PNG 和 GitHub Pages。

优先级：**事实准确 → 证据可追溯 → 内容易读 → 用户可控交互 → 视觉装饰 → 自动化规模**。

最重要的限制：
- 没有读过来源正文，就不能声称事实已经核验；不能将外部网页的标题误当成事件证据。
- 用户图片是转录来源，不天然是事实来源。转录产物始终标注 `reference_transcription`。
- 时间轴“红色最后节点”不代表事件已经最终成功；节点等距不代表真实时间比例。
- 不在 HTML 或 GitHub Pages 中伪造 AI 实时生成能力、已核验标记、发布次数、用户数量或页面浏览量。
- 不可把测试通过等同于事实真伪经验证；工程测试与事实审计是两套门禁。

### 单一事实源 / 目录决策

- **规范 Skill**：`skills/timeline-events/`。包含 SKILL.md、references/、schemas/、templates/、scripts/、examples/。这是唯一可以直接手工维护的 Skill 源目录。
- **交付镜像**：`.pi/skills/timeline-events/` 和 `.agent/skills/timeline-events/`。必须由 `python scripts/sync_skill.py` 生成，并支持各自独立安装；不允许手工分别修改。
- **仓库 CLI 兼容入口**：`scripts/render_html.py` 和 `scripts/timeline_events.py` 仅转发到规范 Skill 内的引擎；旧命令继续可用。
- **站点专用设施**：`docs/`、`docs/data/catalog.json`、`scripts/check_site.py`、`governance/site-architecture.md`、`tests/`、`.github/workflows/`。这些不应复制进可安装的 Skill 包。
- **唯一研究数据源**：对应的结构化 JSON；已生成 HTML 只是可再生的产物，不能手工修改正文。

规范文件变更后 **必须** 同步全量 Skill 镜像，运行 `python scripts/sync_skill.py --check`，并执行完整测试。不要用 git symlink 作为唯一路径；某些客户端、打包器和 Windows 文件系统不可靠地跟随或复制 symlink。

## B. Agent 协作角色和明确产物

| 角色 | 输入 | 责任 | 交接物 |
|---|---|---|---|
| Planner | 用户事件 / 参考图 | 定义时间范围、参与方、受众与来源缺口 | 研究任务说明 |
| Researcher | 研究任务说明 | 查找一手来源并阅读全文 | URL、日期、语义、证据摘录 |
| Critic | 候选事实 | 交叉核验、识别反证、分清宣布/实施/到期 | 质疑清单、纠错记录 |
| Chronology Editor | 已核验节点 | 选择 4—10 个状态转折、写标题摘要 | JSON（schema 合法） |
| HTML Engineer | JSON、Skill 模板 | 生成自包含可编辑 HTML，保留静态正文 | index.html + 交互脚本 |
| QA | HTML、数据、来源 | 检查 XSS、键盘、移动端、视觉、链接与事实 | 测试 / 审核报告 |
| Publisher | 审查通过材料 | 更新 catalog、CI、Pages，确认外网 | Commit / Workflow / URL |

可以由单一 Agent 执行多角色，但每个阶段的证据与产物仍必须可追踪；不要把“已检查”当作测试结果。

## C. 事实治理

研究模式：每个节点包含 `date`、`title`、`description`、`source_ids`；按时间升序排列。优先原始政府公文、协议、判决、论文和数据库；新闻辅助补充。涉及关税、税率、金额、法律效力、科技管制、领土冲突等，尽量用至少两个独立来源核对，区分单方声明与客观程序状态。

转录模式：单独存入 Skill 的参考示例或项目 `data/`，标明 `metadata.verification_state=reference_transcription` + `metadata.notice`，通过 `--reference-transcription` 生成；首页状态不能使用 `verified`。禁止为了通过审查把官网首页网址冒充具体新闻出处。

发布时间：`metadata.updated_at` 必须是确实完成资料查阅的截止日期；未知精确日时只填有证据的月份；未来计划单独表明而不充当已发生节点。

更多逐项校验见 `skills/timeline-events/references/evidence-policy.md` 和 `source-governance.md`。

## D. 技术实现和 HTML/CSS/JS 不变量

1. HTML 第一、SVG/PNG 第二：正文是可选中复制的语义化 DOM，绝非把 PNG 当主页面。
2. 2048×1280 是桌面参考版坐标基准；移动端须有自然纵向事件列表，并允许浏览器字体缩放。
3. 节点为原生按钮；详情为原生 `<dialog>`，支持 Enter/Space、Esc、左右键、焦点返回和初次显示的静态可读性。
4. 对不可信文字用 `html.escape(quote=True)`；嵌入脚本的 JSON 字符串必须转义 `<`, `>`, `&`，用 DOM `textContent` 填充详情。
5. `prefers-reduced-motion: reduce` 与 `focus-visible` 必须有效。动效是信息反馈而不是阅读前置条件。
6. 不引入不必要的 npm、CDN 字体、analytics 或远端 JavaScript。单文件 HTML 必须离线可读。
7. 只维护 Skill 内模板，发布后的 `docs/events/.../index.html` 必须由渲染器生成且经确定性比对，不要直接手改正文。
8. 首页统计来自 `docs/data/catalog.json`，不得硬编码虚构条目和数字。
9. 六大分类 ID 固定为 diplomacy、policy、technology、business、society、history；分类扩展先修改站点设计文档、catalog、测试与 UI。
10. 绝不把 API Key、访问令牌、私人资料和受限文件包含在静态 Pages 产物里。

## E. 目录发布、仓库操作与权限

GitHub Pages 使用项目子路径 `/timeline-events/`；在目录里使用相对 URL（`./events/<slug>/`），事件页返回链接用 `../../index.html`。目录必须与真实 `docs/events/<slug>/index.html` 一一对应。

用户授权发布后按顺序：更新 JSON → 渲染页面 → 更新 catalog → 检查 HTML/links → 测试 → Commit → Actions CI → Pages 部署 → 访问公网链接。提交与 Actions 成功分别报告，不凭提交即宣称部署完成。

在无法联网、缺失密钥或缺少浏览器时，仍可生成离线产物，但必须写明无法核验的部分。不可对 Pages 管理权限或 API 状态做猜测。

## F. 修改一个文件时还必须改什么

| 变更 | 同步修改 |
|---|---|
| `SKILL.md` 或内部 reference | 运行 sync，更新两个镜像，必要时 README |
| `templates/timeline.{html,css,js}` | HTML 引擎、示例产物、交互测试、设计规范 |
| `schemas/timeline.schema.json` | 研究和参考样例、验证器、相关测试 |
| 发布事件 | data JSON、events 页面、catalog、来源证据说明 |
| 分类体系 | governance/site-architecture.md、catalog、首页 UI、check_site.py |
| CLI 路径 | README、CI / Pages 工作流、兼容适配入口、单元测试 |
| Apple-inspired 动效 | motion-design-spec、reduced-motion、键盘与移动端测试 |

## G. 本地与 CI 必须通过

```bash
python scripts/sync_skill.py --check
python scripts/verify_skill_sync.py
python -m unittest discover -s tests -v
python scripts/check_site.py
node --check docs/assets/site.js
node --check skills/timeline-events/templates/timeline.interactions.js
python skills/timeline-events/scripts/render_html.py skills/timeline-events/examples/reference-image-transcription.json \
  --reference-transcription --output /tmp/reference.html
python skills/timeline-events/scripts/render_html.py skills/timeline-events/examples/us-china-trade-war-verified.json \
  --output /tmp/researched.html
```

有条件的场景增加浏览器访问检查：2048 宽桌面、768 平板、375 手机；点击所有节点、上一/下一、Esc/Tab/焦点返回；检查缩放、打印、无 JS 和减少动态效果。浏览器无法使用时不得声称已完成浏览器端 E2E。

## H. DoD / 对用户的交付承诺

- [ ] 事实与研究截止日期可信；逐节点 URL 与内容支持对应。
- [ ] `reference_transcription` 和 `verified` 不混用。
- [ ] 完整 Skill 包可从 `.pi/` 和 `.agent/` 任意一个目录**单独复制即运行**。
- [ ] 两个镜像与规范源文件的字节内容完全一致，没有缺文件。
- [ ] HTML 生成输出与 `docs/events/` 提交产物一致。
- [ ] 单元测试、站点链接、JS 语法、PNG/SVG（按需）通过。
- [ ] 用户可获得准确的 Commit、CI、Pages 状态和实际链接。

若任何门禁没有执行，直接标注“未验证”，不要默默跳过。
