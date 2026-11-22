#!/usr/bin/env python3
"""Evidence-backed Chinese timeline infographic renderer.

Only renders user-reviewed structured JSON. Never searches or invents events.
Python 3.10+, SVG output uses the standard library; PNG needs CairoSVG.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date, datetime
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

WIDTH, HEIGHT = 3200, 2000
NAVY = "#153847"
DEEP = "#142e3b"
BLUE = "#377fa8"
RED = "#bc2433"
MUTED = "#74878f"
FAINT = "#aabac0"
PALE = "#eaf4f8"
FONT = "Noto Sans CJK SC, Source Han Sans SC, Microsoft YaHei, sans-serif"

class TimelineError(ValueError):
    """Bad evidence data, impossible layout, or unsafe/ambiguous input."""

def cells(s: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)

def wrap(s: str, max_cells: int) -> list[str]:
    if not isinstance(s, str) or not s.strip():
        raise TimelineError("文本不能为空")
    output, line, size = [], "", 0
    for char in s.strip():
        if char == "\n":
            if line:
                output.append(line)
            line, size = "", 0
            continue
        width = cells(char)
        if size + width > max_cells and line:
            output.append(line)
            line, size = "", 0
        line += char
        size += width
    if line:
        output.append(line)
    return output

def event_date(value: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}(?:-\d{2})?", value):
        raise TimelineError("事件日期必须为 YYYY-MM 或 YYYY-MM-DD")
    try:
        return datetime.strptime(value if len(value) == 10 else value + "-01", "%Y-%m-%d").date()
    except ValueError as e:
        raise TimelineError("日期不存在: " + value) from e

def validate(data: dict) -> None:
    if not isinstance(data, dict):
        raise TimelineError("JSON 顶层必须是对象")
    meta = data.get("metadata")
    if not isinstance(meta, dict):
        raise TimelineError("缺少 metadata")
    for field in ("title", "subtitle", "updated_at"):
        if not isinstance(meta.get(field), str) or not meta[field].strip():
            raise TimelineError("metadata." + field + " 不能为空")
    if cells(meta["title"]) > 78 or cells(meta["subtitle"]) > 122:
        raise TimelineError("主标题或副标题过长；请精简而不是截断")
    try:
        updated = datetime.strptime(meta["updated_at"], "%Y-%m-%d").date()
    except ValueError as e:
        raise TimelineError("updated_at 必须为真实的 YYYY-MM-DD 日期") from e

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        raise TimelineError("至少提供一条可访问的原始来源 URL")
    source_ids = set()
    for item in sources:
        if not isinstance(item, dict):
            raise TimelineError("sources 元素必须是对象")
        for key in ("id", "publisher", "title", "url"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise TimelineError("sources 缺少字段: " + key)
        if item["id"] in source_ids:
            raise TimelineError("重复来源 id: " + item["id"])
        source_ids.add(item["id"])
        url = urlsplit(item["url"])
        if url.scheme not in ("https", "http") or not url.netloc:
            raise TimelineError("来源 URL 不合法: " + item["id"])

    events = data.get("events")
    if not isinstance(events, list) or not 4 <= len(events) <= 10:
        raise TimelineError("时间轴需 4–10 个事件。更多事件请拆成多页")
    last_date = None
    highlighted = 0
    for idx, item in enumerate(events):
        if not isinstance(item, dict):
            raise TimelineError("events 元素必须是对象")
        for field in ("date", "title", "description"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise TimelineError("事件缺少字段: " + field)
        day = event_date(item["date"])
        if last_date and day < last_date:
            raise TimelineError("events 必须按日期升序，不能自动重排")
        last_date = day
        if day > updated and item.get("status") != "planned":
            raise TimelineError("未来事件必须显式标记 status=planned")
        if item.get("status", "confirmed") not in ("confirmed", "planned"):
            raise TimelineError("status 仅允许 confirmed/planned")
        if len(wrap(item["title"], 16)) > 2:
            raise TimelineError("事件标题过长: " + item["title"])
        if len(wrap(item["description"], 20)) > 3:
            raise TimelineError("事件描述超过三行: " + item["title"])
        refs = item.get("source_ids")
        if not isinstance(refs, list) or not refs or any(r not in source_ids for r in refs):
            raise TimelineError("每个节点必须关联存在的 source_ids: " + item["title"])
        if item.get("highlight", False):
            highlighted += 1
            if idx != len(events) - 1:
                raise TimelineError("只允许高亮最后一个事件")
    if highlighted > 1:
        raise TimelineError("最多高亮一个节点")
    phases = data.get("phases", [])
    if not isinstance(phases, list) or len(phases) > 4:
        raise TimelineError("phases 最多四个")
    for item in phases:
        if not isinstance(item, dict) or any(not isinstance(item.get(k), str) or not item[k] for k in ("name", "period", "summary")):
            raise TimelineError("每个阶段需要 name/period/summary")
        if cells(item["summary"]) > 38:
            raise TimelineError("阶段说明过长")
    insights = data.get("insights", [])
    if not isinstance(insights, list) or len(insights) > 3:
        raise TimelineError("insights 最多三个")
    for item in insights:
        if not isinstance(item, dict) or any(not isinstance(item.get(k), str) or not item[k] for k in ("title", "description")):
            raise TimelineError("每条结论需要 title/description")
        if len(wrap(item["description"], 53)) > 2:
            raise TimelineError("结论内容过长，请拆分")

def text(x, y, value, size=28, fill=DEEP, bold=False, anchor="start") -> str:
    weight = "700" if bold else "400"
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}">{escape(str(value))}</text>')

def rect(x, y, w, h, fill, stroke="none", rx=0, stroke_width=1) -> str:
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>')

def line(x1, y1, x2, y2, color, width=3) -> str:
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"/>'

def month_label(day: date) -> str:
    return f"{day.year:04d}.{day.month:02d}"

def duration(first: date, last: date) -> str:
    months = (last.year - first.year) * 12 + last.month - first.month
    years, remainder = divmod(months, 12)
    return (f"{years}年" if years else "") + (f"{remainder}个月" if remainder else "")

def render_svg(data: dict) -> str:
    validate(data)
    meta, events = data["metadata"], data["events"]
    start, end = event_date(events[0]["date"]), event_date(events[-1]["date"])
    items = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{escape(meta["title"], quote=True)}">']
    a = items.append
    a(rect(0, 0, WIDTH, HEIGHT, "#ffffff"))
    a(text(122, 137, meta["title"], 72 if cells(meta["title"]) < 61 else 58, DEEP, True))
    a(text(3065, 119, meta.get("producer", "资料整理") + " · " + meta["updated_at"], 29, MUTED, anchor="end"))
    a(line(120, 175, 3070, 175, NAVY, 5))
    a(text(125, 248, meta["subtitle"], 36, MUTED))
    a(rect(390, 340, 2420, 126, PALE, NAVY, 27, 3))
    span = duration(start, end)
    duration_label = " · " + span if span else ""
    a(text(1600, 426, f'{month_label(start)} 至 {month_label(end)}{duration_label} · {len(events)}个关键节点', 57, NAVY, True, "middle"))
    a(text(3030, 507, "蓝色：历史节点    红色：最后节点", 27, MUTED, anchor="end"))
    y = 927
    a(line(138, y, 3064, y, NAVY, 13))
    n = len(events)
    # Non-proportional, evenly spaced centers; this is stated in the footer.
    xs = [240 + i * (2720 / (n - 1)) for i in range(n)]
    for idx, event in enumerate(events):
        x = xs[idx]
        top = idx % 2 == 0
        recent = event.get("highlight", idx == n - 1)
        accent = RED if recent else BLUE
        if top:
            a(line(x, 810, x, 893, FAINT, 4))
            a(text(x, 551, month_label(event_date(event["date"])), 42, accent, True, "middle"))
            for j, part in enumerate(wrap(event["title"], 16)):
                a(text(x, 611 + j * 44, part, 34, DEEP, True, "middle"))
            for j, part in enumerate(wrap(event["description"], 20)):
                a(text(x, 717 + j * 40, part, 29, DEEP, False, "middle"))
        else:
            a(line(x, 960, x, 1049, FAINT, 4))
            a(text(x, 1133, month_label(event_date(event["date"])), 42, accent, True, "middle"))
            for j, part in enumerate(wrap(event["title"], 16)):
                a(text(x, 1200 + j * 44, part, 34, DEEP, True, "middle"))
            for j, part in enumerate(wrap(event["description"], 20)):
                a(text(x, 1307 + j * 40, part, 29, DEEP, False, "middle"))
        radius = 27 if recent else 24
        a(f'<circle cx="{x:.1f}" cy="{y}" r="{radius+6}" fill="#ffffff"/>')
        a(f'<circle cx="{x:.1f}" cy="{y}" r="{radius}" fill="{accent}"/>')

    phases = data.get("phases", [])
    a(text(142, 1504, "阶段划分", 42, NAVY, True))
    if phases:
        card_w = (2930 - (len(phases) - 1) * 18) / len(phases)
        for j, phase in enumerate(phases):
            left = round(142 + j * (card_w + 18), 1)
            bg = ["#e8f3f8", "#eff5f7", "#fbf4e8", "#fff0f1"][j]
            a(rect(left, 1534, round(card_w, 1), 136, bg, "#dae6eb", 18, 2))
            a(text(left + 25, 1579, phase["name"], 32, RED if j == len(phases)-1 else NAVY, True))
            a(text(left + card_w - 22, 1579, phase["period"], 26, BLUE, False, "end"))
            a(text(left + 25, 1632, phase["summary"], 27, DEEP))

    insights = data.get("insights", [])
    if insights:
        a(text(142, 1732, "关键结论", 42, NAVY, True))
        card_w = (2930 - (len(insights) - 1) * 21) / len(insights)
        for j, insight in enumerate(insights):
            left = round(142 + j * (card_w + 21), 1)
            a(rect(left, 1751, round(card_w, 1), 174, "#f8fafb", "#dce7ec", 16, 2))
            a(rect(left + 23, 1774, 9, 48, RED if j == len(insights)-1 else BLUE, rx=3))
            a(text(left + 54, 1803, insight["title"], 32, NAVY, True))
            for k, part in enumerate(wrap(insight["description"], 53)):
                a(text(left + 54, 1855 + k*39, part, 26, DEEP))
    a(line(142, 1940, 3065, 1940, "#cfdbdf", 2))
    a(text(144, 1975, f'资料来源：{len(data["sources"])}份可追溯材料；完整 URL 见同名 sources.md', 24, MUTED))
    a(text(3064, 1975, "时间节点等距展示，不代表实际时间比例", 24, MUTED, anchor="end"))
    a("</svg>")
    return "\n".join(items) + "\n"

def render_manifest(data: dict) -> str:
    meta = data["metadata"]
    source_map = {s["id"]: s for s in data["sources"]}
    parts = ["# " + meta["title"], "", "生成日期：" + meta["updated_at"], "",
             "> 信息图仅渲染提供的证据数据；来源是否真实支持结论仍须人工复核。", "",
             "## 节点与证据", ""]
    for i, item in enumerate(data["events"], 1):
        parts += [f'### {i}. {item["date"]} — {item["title"]}', "",
                  item["description"], ""]
        if item.get("status") == "planned":
            parts += ["**注意：未来计划，尚未发生。**", ""]
        for key in item["source_ids"]:
            s = source_map[key]
            parts.append(f'- [{s["publisher"]}｜{s["title"]}]({s["url"]})')
        parts.append("")
    parts += ["## 全部参考资料", ""]
    for s in data["sources"]:
        parts.append(f'- [{s["id"]}] {s["publisher"]} — [{s["title"]}]({s["url"]})')
    return "\n".join(parts) + "\n"

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Render a sourced event timeline as SVG and PNG")
    parser.add_argument("input", type=Path, help="Reviewed timeline JSON")
    parser.add_argument("--output", type=Path, default=Path("dist/timeline"), help="Output path without extension")
    parser.add_argument("--format", choices=["both", "svg", "png"], default="both")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        svg = render_svg(data)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.format in ("both", "svg"):
            args.output.with_suffix(".svg").write_text(svg, encoding="utf-8")
        if args.format in ("both", "png"):
            try:
                import cairosvg
            except ImportError as exc:
                raise TimelineError("PNG 需要先安装 CairoSVG: pip install -r requirements.txt") from exc
            cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(args.output.with_suffix(".png")))
        args.output.with_name(args.output.name + ".sources.md").write_text(render_manifest(data), encoding="utf-8")
        print("OK: " + str(args.output))
        return 0
    except (TimelineError, ValueError, OSError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
