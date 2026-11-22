# Timeline Events｜事件时间轴信息图生成 Skill

只输入一个事件名称，让支持 Web 检索的 Agent **研究事实 → 挑选关键节点 → 生成结构化证据 → 排版高清时间轴 → 导出图片**。设计参考用户提供的中国财经时间轴示例：白底、深蓝主轴、上下交错事件、蓝色历史节点、红色结尾节点。

## 一图看懂

**输入**：例如“中美贸易战：从2018年到目前，请生成一张带证据链的时间轴”。

**输出**：SVG 矢量图 + 3200×2000 PNG 图片 + Markdown 逐节点证据清单。

**核心原则**：模型负责研究，确定性 Python 程序负责绘图。避免生成模型在图片内直接“画字”时产生错别字、误写日期、凭空编造轮次等问题。

## Agent Skill 入口

两份同步的 Agent Skills：

- **Pi**：.pi/skills/timeline-events/SKILL.md
- **Agent**：.agent/skills/timeline-events/SKILL.md

完整流程和验收规则以两个 SKILL.md 为准。引用同一渲染程序 scripts/timeline_events.py。

## 直接运行仓库示例

Python 3.10+。SVG 仅需要标准库；PNG 需要 CairoSVG。系统建议安装 Noto Sans CJK 中文字体。

~~~bash
python -m pip install -r requirements.txt
python scripts/timeline_events.py examples/us-china-trade-war-verified.json --output dist/trade-war --format both
~~~

查看 dist/trade-war.svg、dist/trade-war.png、dist/trade-war.sources.md。示例**仅涵盖截至2025年5月13日的若干已核验历史节点**，不是2026年的最新全景报道。需要当下事件，请让 Agent 重新检索权威来源并构造新的 JSON。

不想安装依赖可先跑：

~~~bash
python scripts/timeline_events.py examples/us-china-trade-war-verified.json --output dist/trade-war --format svg
~~~

## 新事件的正确用法

在能够读取本仓库 SKILL 的 Agent 中输入：

> 使用 timeline-events Skill，研究“中韩自贸协定第二阶段谈判”，截至今天，交叉核验，挑选 6–10 个关键节点，按照参考图片风格生成 SVG、PNG 和 sources.md。

Agent 按 SKILL 先搜索研究，再写出符合 schemas/timeline.schema.json 的 JSON，再调用上述脚本。**命令行本身不具备互联网检索或自动生成事实的能力**；只传一个字符串给脚本不会产生未经核验的历史叙述。

## 目录

~~~text
timeline-events/
├── .pi/skills/timeline-events/SKILL.md
├── .agent/skills/timeline-events/SKILL.md
├── AGENTS.md
├── README.md
├── scripts/
│   ├── timeline_events.py
│   └── verify_skill_sync.py
├── schemas/timeline.schema.json
├── references/
│   ├── evidence-policy.md
│   └── visual-spec.md
├── examples/us-china-trade-war-verified.json
├── tests/test_timeline.py
└── .github/workflows/ci.yml
~~~

## 质量控制

数据强制要求至少一个真实来源、每个事件必须绑定 source_ids、日期有序、4–10 个节点、描述尺寸受控。过长的文本报错而非隐藏文字。SVG 可解析、PNG 有实际像素、证据文档与节点对应。CI 自动测试并上传示例图片 artifact。

~~~bash
python -m unittest discover -s tests -v
python scripts/verify_skill_sync.py
~~~

## 安全与使用边界

- 搜索得到的网址**不代表**事实已被核实：必须阅读原文与核实句子和数字。
- 不能把官方一方的主张直接写成各方承认的定论。
- 对历史事件可标月份；精确到日的信息必须来自证据。
- 图片末端红点突出最后一项节点，**并不**自动代表重大突破或最终结局。
- 未来计划只能标注 status=planned，不能称已经发生。
- 不伪造来源、商标、水印或媒体署名；底部为实际来源数量与资料说明。

## 二次开发

渲染器没有网络调用，也不使用外部 API 密钥。可修改颜色、字号、布局样式，或将 JSON 生产流程连接至你自己的研究 Agent。若要扩展 10 个以上节点，请做多页布局，不要偷偷删减来源文字。
