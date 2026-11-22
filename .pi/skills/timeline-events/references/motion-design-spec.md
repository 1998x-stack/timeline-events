# Apple-inspired Motion & Interaction v1.1

> 用途：将参考图“静态信息阅读”升级为“有明确触觉/视觉反馈的可交互阅读”。此文件只借鉴自然、克制、清晰的交互原则；不是 Apple 官方组件库，也不声称与 Apple 的 Liquid Glass 完全一致。

## 1. 原则

1. **反馈服务于操作**：卡片抬升意味着可打开，时间轴节点有光晕意味着可点击，底部详情板承载附加信息，而不是制造无关动效。
2. **从轻到重**：hover / active（180–380 ms）、单次滚动入场（≤680 ms）、点击节点详情（350 ms），不使用重复飘浮、无限轮播和跟随鼠标的大幅度位移。
3. **视觉不改变事实**：静态 HTML 参考图的 2048 × 1280 坐标、节点文本、阶段卡与页脚不会随着动效重新排序。红色是最后一个节点，不代表“结局已发生”。
4. **保持控制权**：操作可被键盘触发，详情有关闭按钮、Esc 关闭、上一项/下一项与焦点返回，移动端保持原文纵向列表。
5. **无障碍优先**：`prefers-reduced-motion: reduce` 停用滚动渐入、3D 微倾斜、位移与缩放动画；`focus-visible` 轮廓明显。交互信息不能只依赖颜色。
6. **不依赖外部服务**：页面单文件、内联 CSS + JS，不引入 npm、第三方 CDN 或追踪器。JavaScript 不执行时，所有事件正文仍可阅读。

## 2. 时间轴详情交互

- 生成器将可见节点圆点渲染为 `.event-dot` 按钮，保留原坐标与尺寸；`data-event-index` 与 `aria-haspopup="dialog"` 映射事件序号。
- 移动端每条事件有 `.mobile-event-action` 详情按钮。
- 页面附带一个**原生 `<dialog>`** 作为 sheet（含 `aria-labelledby`, `aria-describedby`）；不会使用背景假模态遮罩。
- 打开时读取 JSON 事件 `title/date/description/source_ids`，只通过 `textContent` 和 DOM `createElement` 填写内容，杜绝脚本拼接未转义事实文本。研究模式显示可点击原始来源链接；参考图转录显示“未经独立事实审计”。
- 在详情内支持上/下一节点、左右方向键、Esc、单击遮罩关闭与回到原按钮。第一个和最后一个节点的前后按钮正确 disabled。
- 点击前无 JS 的文档依旧包含事件原文，详情层是增强而不是唯一的内容承载。

## 3. 首页交互

- 卡片整体为真正的 `<a href>`：整卡可点击/Tab 聚焦，不能在链接里嵌套第二个链接。
- 六大分类使用按钮，点击分类更新筛选、清空搜索框并滚动至真实事件列表；若该分类没有作品，展示空结果而不是虚构作品。
- 视觉反馈：卡片 hover 轻抬、active 回弹，按钮 active 缩小、固定头部 backdrop blur、页面顶部滚动进度、Hero 示意卡最多几度的轻倾斜。
- 使用 IntersectionObserver 做**一次性入场**，新检索出来的卡片也能被观察；浏览器不支持 IO 或系统要求减小动态时，内容必须立即可见。
- 动画在触屏及粗指针设备上减少 hover 行为，重要点击不设延迟。

## 4. QA 与性能门禁

- `node --check docs/assets/site.js` 和 `node --check templates/timeline.interactions.js`。
- `render_html.py` 必须内联当前的 `timeline.interactions.js`，禁止只在 `docs/events/...` 手工插入交互代码造成生成器漂移。
- 研究模式与转录模式都能打开详情，确保 JSON 中的 `</script>` 不会破坏 HTML 结构。
- 不能使用 CSS `display:none` 隐藏未入场的内容：无 JS 时正文必须可读。
- 高分辨率桌面、375px 手机、键盘 Tab/Enter/Esc、系统 reduced motion、打印视图分别测试。
- 有条件时用真实浏览器做端到端操作；不可用时如实报告只做了静态、语法或单元测试。

## 5. 设计资料

- Apple HIG Motion: https://developer.apple.com/design/human-interface-guidelines/motion
- Apple HIG Buttons: https://developer.apple.com/design/human-interface-guidelines/buttons
- Apple HIG Accessibility: https://developer.apple.com/design/human-interface-guidelines/accessibility

这些是交互设计参考，不意味着本项目从属于 Apple 或具有 Apple 官方背书。
