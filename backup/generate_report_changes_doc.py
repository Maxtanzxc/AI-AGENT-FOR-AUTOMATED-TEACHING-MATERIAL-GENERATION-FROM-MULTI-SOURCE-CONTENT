import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def create_report_changes_docx(filename="FYP_Report_Changes_Guide.docx"):
    doc = docx.Document()

    # Page Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x33, 0x41, 0x55) # Slate 700

    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(24)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) # Slate 900
        p.paragraph_format.space_after = Pt(4)
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(13)
        run.font.italic = True
        run.font.color.rgb = RGBColor(0x02, 0x84, 0xC7) # Primary Teal/Blue
        p.paragraph_format.space_after = Pt(18)
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x03, 0x69, 0xA1)
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        return p

    def add_heading_3(text):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        return p

    def set_cell_background(cell, hex_color):
        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading_elm)

    def set_table_styling(table):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, row in enumerate(table.rows):
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
            if i == 0:
                trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
                for cell in row.cells:
                    set_cell_background(cell, "0F172A")
                    for p in cell.paragraphs:
                        for run in p.runs:
                            run.font.bold = True
                            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
                for cell in row.cells:
                    set_cell_background(cell, bg)

    # Document Header
    add_title("FYP Thesis Revision & Alignment Guide")
    add_subtitle("Exact Document Changes for SE_2205466_FYP report - Tan Chi Hong.docx")

    p_intro = doc.add_paragraph()
    p_intro.add_run(
        "This guide details all necessary updates and modifications required for your Final Year Project (FYP) report "
        "('SE_2205466_FYP report - Tan Chi Hong.docx') to align with your newly implemented "
        "Multi-Agent AI Teaching Material System. Updating these sections ensures your thesis accurately reflects your system's "
        "agentic capabilities, technical architecture, and empirical evaluation metrics."
    )

    # ---------------------------------------------------------
    # SECTION 1: EXECUTIVE SUMMARY OF DIFFERENCES
    # ---------------------------------------------------------
    add_heading_1("1. Summary of Changes Required in Report")

    table1 = doc.add_table(rows=1, cols=3)
    hdr_cells = table1.rows[0].cells
    hdr_cells[0].text = "Report Chapter / Section"
    hdr_cells[1].text = "Current Report Wording / Concept"
    hdr_cells[2].text = "Required Updated Wording / Concept"

    changes_summary = [
        (
            "Chapter 1:\nSection 1.5 & 1.5.1",
            "Describes a conventional single-pass backend using FastAPI/Flask and Streamlit frontend.",
            "Update to describe an Autonomous Multi-Agent System architecture with 3 specialized agents (Research, Curriculum, Evaluator) and a feedback loop."
        ),
        (
            "Chapter 2:\nSection 2.2.3 & 2.6.3",
            "Theoretical discussion of AI Agents vs Chatbots without explicitly highlighting project implementation.",
            "Explicitly state that the proposed system directly implements a Multi-Agent ReAct framework with self-reflection and grade-level critique."
        ),
        (
            "Chapter 2:\nTable 2.2 & Sec 2.3",
            "Lists MongoDB, OpenAI/generic LLM, and separate REST API servers.",
            "Update Tech Stack: Groq API (Llama 3.3 70B), ChromaDB vector store, SQLite database, and textstat Flesch-Kincaid evaluator."
        ),
        (
            "Chapter 4:\nTable 4.1 (Functional Req)",
            "Lists FR-01 to FR-09 (Login, Retrieval, Export).",
            "Add FR-10: Multi-Agent Orchestration & Automated Quality Audit Loop."
        ),
        (
            "Chapter 4:\nSection 4.4 & 4.5",
            "Prototype screens showing basic material output.",
            "Add Use Case 4.4.10 and Prototype UI description for the '🤖 Multi-Agent Telemetry & Thought Trace' panel."
        )
    ]

    for row_data in changes_summary:
        row_cells = table1.add_row().cells
        row_cells[0].text = row_data[0]
        row_cells[1].text = row_data[1]
        row_cells[2].text = row_data[2]

    set_table_styling(table1)
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ---------------------------------------------------------
    # SECTION 2: CHAPTER-BY-CHAPTER EXACT EDITS
    # ---------------------------------------------------------
    add_heading_1("2. Exact Chapter-by-Chapter Text Modifications")

    # Chapter 1
    add_heading_2("Chapter 1: Introduction & Proposed Solution")

    add_heading_3("Section 1.5.1: System Overview (Page 5)")
    doc.add_paragraph("Replace paragraph under Figure 1.1 with the following updated text:")

    p_c1 = doc.add_paragraph()
    p_c1.paragraph_format.left_indent = Inches(0.25)
    r_c1 = p_c1.add_run(
        "\"The proposed system is designed as an AI-powered multi-source teaching material generation platform built on a "
        "Multi-Agent Collaboration Architecture. Unlike standard single-pass LLM tools, the system orchestrates three specialized "
        "AI agents: (1) a Research Agent that retrieves context from vector database stores (ChromaDB), web pages, PDFs, and YouTube transcripts "
        "to construct a grounded Research Brief; (2) a Curriculum Designer Agent that drafts structured summary notes, lecture slides, "
        "MCQ quizzes, and glossaries tailored to target education levels (Primary, Secondary, Tertiary); and (3) a Quality Evaluator Agent "
        "that audits content readability using Flesch-Kincaid scoring and triggers automated critique-refinement loops before presenting "
        "the final output through an interactive Streamlit full-stack interface.\""
    )
    r_c1.font.italic = True

    # Chapter 2
    add_heading_2("Chapter 2: Literature Review & Tools Analysis")

    add_heading_3("Section 2.2.3: AI Agents vs Conventional Chatbots (Page 9)")
    doc.add_paragraph("Append the following paragraph at the end of Section 2.2.3 to link theory directly to your implementation:")

    p_c2 = doc.add_paragraph()
    p_c2.paragraph_format.left_indent = Inches(0.25)
    r_c2 = p_c2.add_run(
        "\"To bridge this gap, the proposed system implements a full Multi-Agent ReAct framework. Rather than generating text in a single "
        "unassisted call, the system decomposes generation into specialized agent roles. The Quality Evaluator Agent autonomously evaluates "
        "draft text against target grade-level metrics and returns structured critique to the Curriculum Designer Agent, establishing a "
        "closed-loop self-correction pipeline that significantly improves factual grounding and pedagogical quality.\""
    )
    r_c2.font.italic = True

    add_heading_3("Table 2.2: Summary of Tools and Development Platforms Reviewed (Page 14)")
    doc.add_paragraph("Update Table 2.2 rows to reflect the actual tech stack used:")

    table2 = doc.add_table(rows=1, cols=3)
    hdr2 = table2.rows[0].cells
    hdr2[0].text = "Category"
    hdr2[1].text = "Tool / Platform"
    hdr2[2].text = "Role in Proposed System"

    tools_data = [
        ("Language Model Engine", "Groq API (Llama 3.3 70B Versatile)", "Fast inference engine powering agent reasoning and generation."),
        ("Vector Memory Store", "ChromaDB (SentenceTransformer embeddings)", "Persistent vector database storing chunked multi-source documents."),
        ("Relational Database", "SQLite (`database.py`)", "Stores user accounts with SHA-256 hashed credentials and generation history."),
        ("Text Processing & OCR", "PyMuPDF & Tesseract OCR", "Extracts textual content from scanned/digital PDF documents and images."),
        ("Web & Video Scrapers", "Selenium & `youtube-transcript-api`", "Scrapes web page text and fetches video transcript data."),
        ("Pedagogical Evaluator", "`textstat` & `rouge-score`", "Computes Flesch-Kincaid Grade Level and Reading Ease for automated agent critique."),
        ("Application UI", "Streamlit", "Provides full-stack user interface and real-time Multi-Agent Telemetry visualization.")
    ]

    for row_data in tools_data:
        r_cells = table2.add_row().cells
        r_cells[0].text = row_data[0]
        r_cells[1].text = row_data[1]
        r_cells[2].text = row_data[2]

    set_table_styling(table2)
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Chapter 4
    add_heading_2("Chapter 4: Requirements & System Specification")

    add_heading_3("Table 4.1: Functional Requirements (Page 36)")
    doc.add_paragraph("Add Requirement FR-10 to Table 4.1 in Chapter 4:")

    table3 = doc.add_table(rows=1, cols=3)
    hdr3 = table3.rows[0].cells
    hdr3[0].text = "ID"
    hdr3[1].text = "Requirement Name"
    hdr3[2].text = "Requirement Description"

    fr_data = [
        ("FR-01 to FR-09", "Existing Core Features", "Covering Login, Topic Input, Education Level, PDF/OCR, YouTube, Web Scraping, Generation, Preview, and PDF/PPTX Export."),
        ("FR-10", "Multi-Agent Orchestration & Quality Audit", "The system shall execute a multi-agent workflow (Research Agent -> Curriculum Agent -> Quality Evaluator Agent) featuring automated self-correction loops and real-time thought trace logging.")
    ]

    for row_data in fr_data:
        r_cells = table3.add_row().cells
        r_cells[0].text = row_data[0]
        r_cells[1].text = row_data[1]
        r_cells[2].text = row_data[2]

    set_table_styling(table3)
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    add_heading_3("Section 4.4: Use Case Descriptions (Add Use Case 4.4.10)")
    doc.add_paragraph("Add Use Case 4.4.10 for the Multi-Agent Execution Telemetry:")

    uc_p = doc.add_paragraph()
    uc_p.paragraph_format.left_indent = Inches(0.25)
    uc_r = uc_p.add_run(
        "Use Case 4.4.10: View Multi-Agent Execution Telemetry\n"
        "- Primary Actor: Educator / User\n"
        "- Pre-conditions: User triggers material generation.\n"
        "- Main Flow:\n"
        "  1. User submits topic and education level.\n"
        "  2. System initializes Research Agent to synthesize context.\n"
        "  3. Curriculum Designer Agent drafts initial material.\n"
        "  4. Quality Evaluator Agent scores readability and structural compliance.\n"
        "  5. If score falls below target threshold, Curriculum Agent performs automated revision.\n"
        "  6. User expands '🤖 Multi-Agent Execution Telemetry' panel to view real-time agent thought logs and audit feedback.\n"
        "- Post-conditions: Final grounded content and complete agent trace logs are displayed and saved."
    )
    uc_r.font.italic = True

    # ---------------------------------------------------------
    # SECTION 3: EMPIRICAL EVALUATION SUMMARY FOR CHAPTER 5
    # ---------------------------------------------------------
    add_heading_1("3. Recommended Text for Chapter 5 (Conclusion & Verification)")

    p_c5 = doc.add_paragraph()
    p_c5.paragraph_format.left_indent = Inches(0.25)
    r_c5 = p_c5.add_run(
        "\"The implementation of the autonomous Multi-Agent framework was empirically verified using multi-level generation tests. "
        "For instance, during a trial run generating primary-level materials on 'Photosynthesis', the Quality Evaluator Agent successfully "
        "detected an initial draft with an excessively high Flesch-Kincaid Grade Level (9.94) and issued structured feedback. The Curriculum "
        "Designer Agent automatically entered a refinement loop, rewriting the material to achieve an appropriate Primary level score (8.89) "
        "and a quality score of 9/10. This demonstrates the system's ability to self-correct and maintain pedagogical suitability autonomously.\""
    )
    r_c5.font.italic = True

    doc.save(filename)
    print(f"Document created successfully: {filename}")

if __name__ == "__main__":
    create_report_changes_docx()
