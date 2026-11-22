# Timeline Events

**把一个复杂事件转化为可信、可编辑、可交互的时间轴网页。**

[![CI](https://github.com/1998x-stack/timeline-events/actions/workflows/ci.yml/badge.svg)](https://github.com/1998x-stack/timeline-events/actions/workflows/ci.yml)
[![Pages](https://github.com/1998x-stack/timeline-events/actions/workflows/pages.yml/badge.svg)](https://github.com/1998x-stack/timeline-events/actions/workflows/pages.yml)

[访问 GitHub Pages 首页](https://1998x-stack.github.io/timeline-events/) · [参考图复刻样例](https://1998x-stack.github.io/timeline-events/events/us-china-trade-war/) · [规范 Skill](skills/timeline-events/SKILL.md) · [工程治理 AGENTS.md](AGENTS.md)

## 为什么做这个项目

媒体时间线经常有两个问题：**事实看起来专业，但缺乏逐节点来源**；或 **图片效果漂亮，却难以编辑、检索和无障碍阅读**。本项目把研究与排版分离：Agent 检索核验事实，确定性 Python 模板生成自包含 HTML、SVG、PNG；GitHub Pages 展示经过状态标注的作品。

> 原图转录不等于事件事实核验。示例包含用户提供的参考图复刻，所有事实必须重新研究后才能标记为 `verified`。

## 30 秒快速开始

**最推荐的方式：** 将以下提示交给安装了本 Skill 的 Agent：

> 使用 timeline-events Skill，研究“中韩自贸协定第二阶段谈判”，核验每一条时间轴节点的原始资料，生成独立 HTML 页面和证据清单，采用简洁 Apple-inspired 动态点击效果。

**不需要 Agent 的本地渲染：**

```bash
# 参考图转录（保留未经独立核验标记）
python skills/timeline-events/scripts/render_html.py \
  skills/timeline-events/examples/reference-image-transcription.json \
  --reference-transcription --output dist/reference.html

# 来源结构化示例（资料截止日期以 JSON 为准）
python skills/timeline-events/scripts/render_html.py \
  skills/timeline-events/examples/us-china-trade-war-verified.json \
  --output dist/researched.html

# SVG（标准库）与 PNG（可选 CairoSVG）
python -m pip install -r requirements.txt
python skills/timeline-events/scripts/timeline_events.py \
  skills/timeline-events/examples/us-china-trade-war-verified.json \
  --output dist/researched --format both
```

命令行引擎是**渲染器，不是联网研究代理**。输入只有主题名称时，由支持研究工具的 Agent 完成搜索、阅读、交叉核验与结构化建模。

## 专业目录（单一事实源）

```text
skills/timeline-events/          # ✅ Canonical、独立可安装的 Skill
├── SKILL.md                     # Agent 主指令：短、精、可执行
├── README.md                    # 离线使用与能力边界
├── references/                  # 研究证据、HTML、动效、视觉规范
├── schemas/                     # 时间轴 JSON 数据约定
├── templates/                   # 可编辑 HTML/CSS/JS 模板
├── scripts/                     # 单文件 HTML、SVG/PNG 渲染引擎
└── examples/                    # 已核验示例 / 原图未核验转录
.pi/skills/timeline-events/      # Pi 完整镜像，自动同步
.agent/skills/timeline-events/   # Agent 完整镜像，自动同步
scripts/                         # 兼容旧 CLI、站点检查、Skill 同步
examples/ references/ schemas/ templates/   # 已迁入 Skill 内部
AGENTS.md                        # 项目级质量、治理与协作规则
README.md                        # 本页（对外使用说明）
governance/site-architecture.md  # 项目站点分类与内容治理
docs/                             # GitHub Pages 发布站点（非 Skill）
tests/                            # 工程级单元/集成/安全回归
.github/workflows/                # CI 和 Pages 部署
```

Skill 内的资源才需要随技能一起安装；`docs/`、`.github/`、仓库 `AGENTS.md` 属于网站项目。`scripts/` 目录中保留薄兼容入口，旧调用不受破坏。

## 两种严谨的数据模式

| 模式 | 入口 | 来源要求 | 首页状态 |
|---|---|---|---|
| 研究出版 | 普通 JSON + `render_html.py` | 每个节点有来源 ID；需要 Agent 实际阅读来源 | `verified`（仅审核完成后） |
| 参考图片复刻 | `--reference-transcription` | 对照图片逐字还原；不能冒充事实核验 | `reference_transcription` |

已验证样例的截止日期是 **2025-05-13**，不是2026年的最新研究报告。动态事实进展需重新检索。

## Apple-inspired 交互

- 首页：卡片抬升/按压反馈、分类筛选、滚动渐入、真实目录搜索、可复制 Agent 指令。
- 事件页：上下交错时间轴节点可点击，原生详情面板支持左右方向键、Esc、焦点还原、来源链接；移动端为纵向时间轴。
- 无障碍：`prefers-reduced-motion`、语义化 DOM、`focus-visible`、无 JS 时正文照常显示。
- 无前端构建工具和第三方 CDN，输出 HTML 可以脱离仓库独立打开。

## 目录分类

国际关系与贸易、政策与法治、科技与产业、商业与金融、社会与文化、历史与战争。首页分类数字来自 `docs/data/catalog.json`，未收录的事件不造假填充。详细定义见 [governance/site-architecture.md](governance/site-architecture.md)。

## 开发、测试与发布

```bash
# 检测 2 个独立 Skill 镜像完整一致
python scripts/sync_skill.py --check

# 修改规范 Skill 后同步两份镜像
python scripts/sync_skill.py

# 单元/集成/页面检查
python -m unittest discover -s tests -v
python scripts/check_site.py
node --check docs/assets/site.js
node --check skills/timeline-events/templates/timeline.interactions.js
```

推送到 `main` 后 `.github/workflows/ci.yml` 负责验证，`.github/workflows/pages.yml` 负责网站部署。**代码提交、CI 通过、Pages 部署、公网可访问**必须分别核验，不可混为一谈。

## 技术与安全边界

- 来源链接的合法 URL 结构不代表 URL 内真实支持该段文字；仍需研究者校对原文。
- 原图复刻只保证版式与文字转录，不代表事件事实均已独立核验。
- 不把 API Token、个人隐私、不可公开的原始材料放入 `docs/`。
- 无需浏览器插件或第三方 JS 就能阅读核心正文；动态效果只做渐进增强。

## 维护入口

[AGENTS.md](AGENTS.md) 定义角色分工、证据审计、HTML/移动端规范、发布门禁；[Skill references 索引](skills/timeline-events/references/README.md) 给出按需阅读路径。建议在 PR 中同时提交生成后的演示页面截图和自动化测试结果。
