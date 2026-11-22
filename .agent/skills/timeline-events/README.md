# timeline-events · Portable Agent Skill

独立可安装的时间轴创作 SKILL。输入事件名称，Agent 调查并写出有来源的 JSON，然后使用内置 Python 生成高质量单文件 HTML；也支持 SVG/PNG、交互节点和参考图片复刻。

## 结构

- `SKILL.md`：Agent 指令（首先读取）。
- `scripts/render_html.py`：HTML 渲染器，依赖 Python 标准库。
- `scripts/timeline_events.py`：SVG 绘图；PNG 需要 CairoSVG。
- `templates/`：HTML/CSS/JS 可编辑模板。
- `schemas/timeline.schema.json`：研究数据和转录数据结构约定。
- `references/`：按需加载的来源核验、视觉、动态交互规范。
- `examples/`：已核验历史片段与未核验图片原文转录的隔离示例。

## 快速运行

```bash
python scripts/render_html.py examples/reference-image-transcription.json \
  --reference-transcription --output dist/reference.html
python scripts/render_html.py examples/us-china-trade-war-verified.json \
  --output dist/researched.html
```

`reference-image-transcription.json` **只转录图片文字**；不是原始信源研究报告。每次研究应另建经过核验的数据文件。

## 安装说明

完整目录可复制到任何支持 Agent Skills 的客户端。当前仓库同时维护 `.pi/skills/timeline-events` 和 `.agent/skills/timeline-events` 的全量镜像，便于按目录直接复制；镜像内容由根目录 `scripts/sync_skill.py` 生成，不应手工分叉。
