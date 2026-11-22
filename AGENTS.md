# AGENTS.md｜timeline-events 项目协作规则

你正在维护一个“研究驱动、可审计、确定性绘图”的 Agent Skill。

1. 用户只输入主题时，先调用可用研究工具检索核验，建立来源映射，再写 JSON。不要让渲染程序捏造事实。
2. 使用 .pi/skills/timeline-events/SKILL.md 或 .agent/skills/timeline-events/SKILL.md 作为完整作业指令，两份正文必须相同。
3. 任何数字、轮次、谈判地点、签署与生效日期都应有可查的原始材料；未核验内容不得进入正式图。
4. 严格保持输入数据与输出图一致；文本溢出时缩短编辑稿或分图，禁止无提示截断。
5. scripts/timeline_events.py 是唯一渲染入口。不要在两个 Skill 目录内维护重复脚本。
6. 变更 schema、样式、路径、CLI 时，必须同步 README、两个 Skill 文件、示例和测试。
7. 交付前运行 python -m unittest discover -s tests -v 与 python scripts/verify_skill_sync.py，并渲染 SVG/PNG。
8. CI失败必须修复，不以“代码已上传”代替验收。
9. 不要修改原始证据来适配预设叙事；有不确定性就写明。
