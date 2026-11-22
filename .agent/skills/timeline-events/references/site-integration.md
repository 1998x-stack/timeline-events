# GitHub Pages 发布适配（非 Skill 的运行前提）

通用 Skill 可以离线生成 HTML。**仅当用户要求发布且当前仓库提供对应工作流时**才执行下列步骤。

1. 读取目标仓库根目录 `AGENTS.md`、站点规范和 `docs/data/catalog.json`。
2. `docs/events/<slug>/index.html` 是编译结果，不应直接修改事实正文。
3. 根据已审核 JSON 运行 skill 内的 HTML 渲染器，使用 `--site-url ../../index.html` 等相对路径。
4. 更新 catalog 的真实条目；仅在验证完成后标为 `verified`，参考图片标 `reference_transcription`。
5. 从项目根执行站点校验、测试和 GitHub Actions，确认 Pages 状态与目标链接。
6. 不在静态网站加入 API Key、付费内容或隐私资料；没有后端不得声称“网页已经在调用模型”。
7. 发布失败时提供 commit、运行日志与权限限制，不虚构部署成功。
