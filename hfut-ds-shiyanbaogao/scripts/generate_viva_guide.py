from __future__ import annotations

import argparse
import re
from pathlib import Path
from xml.sax.saxutils import escape

from hfut_ds_common import FORBIDDEN_MARKS, read_json


MIN_GENERAL_QUESTIONS = 8
MIN_PROBLEM_QUESTIONS = 8
MIN_RUNTIME_QUESTIONS = 6


def compact_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def as_text(value: object, field: str, minimum: int = 1, maximum: int = 220) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    text = re.sub(r"\s+", " ", value).strip()
    length = compact_count(text)
    if not (minimum <= length <= maximum):
        raise ValueError(f"{field} must contain {minimum}-{maximum} non-whitespace characters; got {length}")
    return text


def as_text_list(value: object, field: str, minimum_items: int = 1, maximum_items: int = 12) -> list[str]:
    if not isinstance(value, list) or not (minimum_items <= len(value) <= maximum_items):
        raise ValueError(f"{field} must contain {minimum_items}-{maximum_items} items")
    return [as_text(item, f"{field}[{index}]", 1, 120) for index, item in enumerate(value)]


def validate_qa(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    question = as_text(value.get("question"), f"{field}.question", 4, 70)
    answer = as_text(value.get("answer"), f"{field}.answer", 12, 220)
    keywords = as_text_list(value.get("keywords"), f"{field}.keywords", 2, 6)
    return {"question": question, "answer": answer, "keywords": keywords}


def validate_spec(spec: dict) -> dict[str, object]:
    title = as_text(spec.get("experiment_title"), "experiment_title", 2, 100)
    topic = as_text(spec.get("topic"), "topic", 2, 100)
    overview_value = spec.get("overview")
    if not isinstance(overview_value, list) or not (4 <= len(overview_value) <= 10):
        raise ValueError("overview must contain 4-10 entries")
    overview: list[dict[str, str]] = []
    for index, item in enumerate(overview_value):
        if not isinstance(item, dict):
            raise ValueError(f"overview[{index}] must be an object")
        overview.append(
            {
                "label": as_text(item.get("label"), f"overview[{index}].label", 2, 20),
                "value": as_text(item.get("value"), f"overview[{index}].value", 4, 180),
            }
        )
    general_value = spec.get("general_questions")
    if not isinstance(general_value, list) or not (MIN_GENERAL_QUESTIONS <= len(general_value) <= 20):
        raise ValueError(f"general_questions must contain {MIN_GENERAL_QUESTIONS}-20 items")
    general = [validate_qa(item, f"general_questions[{index}]") for index, item in enumerate(general_value)]
    problem_value = spec.get("problems")
    if not isinstance(problem_value, list) or not problem_value:
        raise ValueError("problems must be a non-empty array")
    problems: list[dict[str, object]] = []
    for index, item in enumerate(problem_value, 1):
        if not isinstance(item, dict):
            raise ValueError(f"problems[{index}] must be an object")
        questions_value = item.get("questions")
        if not isinstance(questions_value, list) or not (MIN_PROBLEM_QUESTIONS <= len(questions_value) <= 16):
            raise ValueError(
                f"problems[{index}].questions must contain {MIN_PROBLEM_QUESTIONS}-16 items"
            )
        problems.append(
            {
                "name": as_text(item.get("name"), f"problems[{index}].name", 2, 80),
                "task_summary": as_text(item.get("task_summary"), f"problems[{index}].task_summary", 8, 220),
                "data_structure": as_text(item.get("data_structure"), f"problems[{index}].data_structure", 4, 160),
                "implementation_route": as_text(
                    item.get("implementation_route"), f"problems[{index}].implementation_route", 12, 260
                ),
                "complexity": as_text(item.get("complexity"), f"problems[{index}].complexity", 8, 160),
                "boundary_cases": as_text_list(
                    item.get("boundary_cases"), f"problems[{index}].boundary_cases", 2, 8
                ),
                "oral_summary": as_text(item.get("oral_summary"), f"problems[{index}].oral_summary", 20, 320),
                "questions": [
                    validate_qa(question, f"problems[{index}].questions[{q_index}]")
                    for q_index, question in enumerate(questions_value)
                ],
            }
        )
    runtime_value = spec.get("runtime_questions")
    if not isinstance(runtime_value, list) or not (MIN_RUNTIME_QUESTIONS <= len(runtime_value) <= 16):
        raise ValueError(f"runtime_questions must contain {MIN_RUNTIME_QUESTIONS}-16 items")
    runtime = [validate_qa(item, f"runtime_questions[{index}]") for index, item in enumerate(runtime_value)]
    normalized = {
        "experiment_title": title,
        "topic": topic,
        "overview": overview,
        "general_questions": general,
        "problems": problems,
        "runtime_questions": runtime,
    }
    serialized = str(normalized)
    lowered = serialized.lower()
    for mark in FORBIDDEN_MARKS:
        if mark.lower() in lowered:
            raise ValueError(f"forbidden source mark in viva spec: {mark}")
    privacy_patterns = (
        (r"(?<!\d)1[3-9]\d{9}(?!\d)", "phone number"),
        (r"(?<!\d)\d{8,18}(?!\d)", "student-ID-like number"),
        (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "email address"),
        (r"(?:[A-Za-z]:\\|/Users/|/home/)", "personal absolute path"),
    )
    for pattern, label in privacy_patterns:
        if re.search(pattern, serialized):
            raise ValueError(f"viva spec contains a {label}")
    if re.search(r"\b(?:TODO|TBD)\b|待补充|示例答案", serialized, re.I):
        raise ValueError("viva spec contains unfinished/example text")
    return normalized


def register_fonts() -> tuple[str, str]:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.pdfbase.ttfonts import TTFont

    candidates = [
        (Path(r"C:\Windows\Fonts\msyh.ttc"), Path(r"C:\Windows\Fonts\msyhbd.ttc")),
        (Path(r"C:\Windows\Fonts\simsun.ttc"), Path(r"C:\Windows\Fonts\simhei.ttf")),
        (Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"), Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")),
        (Path("/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf"), Path("/usr/share/fonts/opentype/noto/NotoSansCJKsc-Bold.otf")),
    ]
    for regular, bold in candidates:
        if not regular.is_file():
            continue
        try:
            pdfmetrics.registerFont(TTFont("VivaRegular", str(regular)))
            if bold.is_file():
                pdfmetrics.registerFont(TTFont("VivaBold", str(bold)))
            else:
                pdfmetrics.registerFont(TTFont("VivaBold", str(regular)))
            return "VivaRegular", "VivaBold"
        except Exception:
            continue
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    return "STSong-Light", "STSong-Light"


def render(spec: dict[str, object], output: Path) -> int:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import CondPageBreak, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    regular, bold = register_fonts()
    red = colors.HexColor("#9E1B32")
    deep = colors.HexColor("#22242A")
    gray = colors.HexColor("#667085")
    pale = colors.HexColor("#F8F4F5")
    line = colors.HexColor("#E6D8DC")
    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleCN", parent=styles["Title"], fontName=bold, fontSize=24, leading=34, textColor=red, alignment=TA_CENTER, spaceAfter=8 * mm)
    subtitle = ParagraphStyle("SubtitleCN", parent=styles["Normal"], fontName=regular, fontSize=12, leading=20, textColor=deep, alignment=TA_CENTER)
    h1 = ParagraphStyle("H1CN", parent=styles["Heading1"], fontName=bold, fontSize=16, leading=24, textColor=red, spaceBefore=4 * mm, spaceAfter=3 * mm)
    h2 = ParagraphStyle("H2CN", parent=styles["Heading2"], fontName=bold, fontSize=12.5, leading=19, textColor=deep, spaceBefore=3 * mm, spaceAfter=2 * mm)
    body = ParagraphStyle("BodyCN", parent=styles["BodyText"], fontName=regular, fontSize=10.5, leading=17, textColor=deep, alignment=TA_LEFT, spaceAfter=2 * mm)
    question = ParagraphStyle("QuestionCN", parent=body, fontName=bold, fontSize=10.8, leading=17, textColor=red, spaceBefore=2.5 * mm, spaceAfter=1 * mm)
    answer = ParagraphStyle("AnswerCN", parent=body, leftIndent=5 * mm, firstLineIndent=0, borderColor=line, borderWidth=0.6, borderPadding=4, backColor=colors.white, spaceAfter=1.2 * mm)
    keyword = ParagraphStyle("KeywordCN", parent=body, fontSize=9.2, leading=14, textColor=gray, leftIndent=5 * mm, spaceAfter=2.5 * mm)
    note = ParagraphStyle("NoteCN", parent=body, fontSize=9.8, leading=16, textColor=gray, backColor=pale, borderPadding=7, spaceAfter=4 * mm)
    small = ParagraphStyle("SmallCN", parent=body, fontSize=9.4, leading=15, textColor=gray)

    def p(text: object, style=body) -> Paragraph:
        return Paragraph(escape(str(text)), style)

    def qa_block(items: list[dict[str, object]]) -> list[object]:
        flow: list[object] = []
        for index, item in enumerate(items, 1):
            flow.append(
                KeepTogether(
                    [
                        p(f"Q{index}　{item['question']}", question),
                        p(f"答：{item['answer']}", answer),
                        p("关键词：" + " / ".join(item["keywords"]), keyword),
                    ]
                )
            )
        return flow

    def page(canvas, doc) -> None:
        canvas.saveState()
        canvas.setAuthor("")
        canvas.setCreator("")
        canvas.setTitle(str(spec["experiment_title"]) + " 验收口述问答")
        canvas.setFont(regular, 8.5)
        if doc.page > 1:
            canvas.setFillColor(gray)
            canvas.drawString(18 * mm, A4[1] - 12 * mm, str(spec["experiment_title"]) + "｜实验验收口述问答")
            canvas.setStrokeColor(line)
            canvas.line(18 * mm, A4[1] - 14 * mm, A4[0] - 18 * mm, A4[1] - 14 * mm)
        canvas.setFillColor(gray)
        canvas.drawCentredString(A4[0] / 2, 10 * mm, f"第 {doc.page} 页")
        canvas.restoreState()

    output.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=19 * mm,
        bottomMargin=16 * mm,
        title=str(spec["experiment_title"]) + " 验收口述问答",
        author="",
        subject="数据结构实验面对面验收复习",
    )
    story: list[object] = [Spacer(1, 28 * mm), p(str(spec["experiment_title"]), title), p("实验验收口述问答手册", subtitle), Spacer(1, 8 * mm), p(f"主题：{spec['topic']}", subtitle), Spacer(1, 15 * mm)]
    story.append(p("使用方法：先遮住答案自行口述，再核对关键词。答案是可直接说出口的提纲，应结合本次程序真实实现理解后复述；全文不展示源码。", note))
    total = len(spec["general_questions"]) + len(spec["runtime_questions"]) + sum(len(item["questions"]) for item in spec["problems"])
    story.append(p(f"本手册共覆盖 {len(spec['problems'])} 道题、{total} 个模拟问题。", small))
    story.append(PageBreak())

    story.append(p("一、实验总览", h1))
    data = [[p("项目", h2), p("口述要点", h2)]]
    for item in spec["overview"]:
        data.append([p(item["label"], body), p(item["value"], body)])
    table = Table(data, colWidths=[34 * mm, 125 * mm], repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), pale),
        ("TEXTCOLOR", (0, 0), (-1, 0), red),
        ("GRID", (0, 0), (-1, -1), 0.5, line),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 4 * mm))
    story.append(p("二、基础与共性问题", h1))
    story.extend(qa_block(spec["general_questions"]))

    for index, item in enumerate(spec["problems"], 1):
        story.append(CondPageBreak(95 * mm))
        story.append(p(f"三-{index}、{item['name']}", h1))
        rows = [
            ("题目目标", item["task_summary"]),
            ("数据结构", item["data_structure"]),
            ("实现主线", item["implementation_route"]),
            ("复杂度", item["complexity"]),
            ("边界情况", "；".join(item["boundary_cases"])),
        ]
        for label, value in rows:
            story.append(p(f"【{label}】{value}", body))
        story.append(p("【30 秒口述】", h2))
        story.append(p(item["oral_summary"], note))
        story.append(p("【模拟提问】", h2))
        story.extend(qa_block(item["questions"]))

    story.append(CondPageBreak(105 * mm))
    story.append(p("四、运行、测试与调试追问", h1))
    story.extend(qa_block(spec["runtime_questions"]))
    story.append(p("五、验收前一分钟检查", h1))
    checklist = [
        "能用一句话说清每题输入、输出和目标。",
        "能说明采用的存储结构、关键成员和不变式。",
        "能按数据流口述核心步骤，不背代码行。",
        "能直接给出最好、最坏或平均复杂度中本题需要的结论。",
        "能解释至少两个边界用例，以及错误输入如何处理。",
        "能说明 main 只负责测试，算法由类的成员函数完成。",
        "被追问替代方案时，先比较存储、操作代价和适用场景。",
    ]
    story.extend(p(f"□ {item}", body) for item in checklist)
    document.build(story, onFirstPage=page, onLaterPages=page)
    return total


def verify_evidence_alignment(spec: dict[str, object], evidence_path: Path | None) -> None:
    if not evidence_path:
        return
    evidence = read_json(evidence_path)
    if int(evidence.get("problem_count", -1)) != len(spec["problems"]):
        raise ValueError("viva spec problem count does not match extracted evidence")
    evidence_problems = evidence.get("problems", [])
    if len(evidence_problems) != len(spec["problems"]):
        raise ValueError("viva spec and evidence problem lists are not aligned")
    for index, item in enumerate(evidence_problems, 1):
        if str(item.get("task", "")) != f"T{index}":
            raise ValueError(f"evidence task order is invalid at T{index}")
        code = item.get("code", {})
        if not isinstance(code, dict) or not code.get("files"):
            raise ValueError(f"evidence contains no code facts for T{index}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a concise, code-grounded data-structures lab viva PDF.")
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--render-dir", type=Path)
    args = parser.parse_args()
    if not args.spec.is_file():
        parser.error("--spec must be an existing JSON file")
    if args.evidence and not args.evidence.is_file():
        parser.error("--evidence must be an existing JSON file")
    if args.output.exists():
        parser.error("output PDF already exists")
    spec = validate_spec(read_json(args.spec))
    verify_evidence_alignment(spec, args.evidence)
    total = render(spec, args.output)
    if not args.output.is_file() or args.output.stat().st_size < 4096:
        raise RuntimeError("generated viva PDF is unexpectedly small")
    print(f"Generated {total} simulated questions: {args.output}")
    if args.render_dir:
        from convert_report import render_pdf

        pages = render_pdf(args.output, args.render_dir)
        print(f"Rendered {pages} pages to {args.render_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
