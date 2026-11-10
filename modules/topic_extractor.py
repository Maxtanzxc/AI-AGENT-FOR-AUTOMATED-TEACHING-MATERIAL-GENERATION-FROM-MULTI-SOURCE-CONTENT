import re
from config import client, MODEL_NAME
from modules.evaluator import extract_json_from_response


def extract_chapters_from_toc(text: str, filename: str = "") -> list:
    """
    Directly parse all chapters from a document's Table of Contents or outline.
    Captures all chapters (e.g. all 16 chapters) instantly without token limit truncations.
    """
    if not text:
        return []

    toc_pos = text.lower().find("contents")
    sample = text[toc_pos:toc_pos + 45000] if toc_pos != -1 else text[:45000]

    pattern = r'^(?:Chapter|Unit|Module)\s+(\d+)[\.:\s]+([^\.\n\r]+(?:\([^\)]+\)[^\.\n\r]*)?)'

    found = []
    seen_nums = set()
    for line in sample.split("\n"):
        l = line.strip()
        m = re.match(pattern, l, re.IGNORECASE)
        if m:
            ch_num = int(m.group(1))
            if ch_num not in seen_nums and ch_num <= 60:
                seen_nums.add(ch_num)
                raw_title = re.sub(r'\s*\.{2,}\s*\d*$', '', l).strip()
                raw_title = re.sub(r'[\.\s_]+$', '', raw_title).strip()

                title_parts = re.split(r'[\.:]\s+', raw_title, maxsplit=1)
                desc = title_parts[1] if len(title_parts) > 1 else raw_title
                words = re.findall(r'\b[a-zA-Z]{3,}\b', desc.lower())
                keywords = [w for w in words if w not in ('and', 'the', 'for', 'with', 'from', 'type')][:5]

                found.append({
                    "title": raw_title,
                    "source": filename,
                    "chapter_num": ch_num,
                    "keywords": keywords,
                    "summary": f"Covers core curriculum concepts and mechanisms for {raw_title}."
                })

    return found


def filter_by_chapters(text: str, selected_chapter_nums: list) -> str:
    """
    Extract the exact text intervals for selected chapters from a textbook or long document.
    Accurately identifies the body chapter sequence and slices only the selected chapters.
    """
    if not selected_chapter_nums:
        return text

    # Find candidate chapter headings in text that do not have TOC dot leaders (...)
    candidates = []
    for m in re.finditer(r'\n+((?:Chapter|Unit|Module)\s+(\d+)[\.:\s]+[^\n\r]+)', text, re.IGNORECASE):
        full_line = m.group(1)
        if not re.search(r'\.{3,}', full_line):
            ch_num = int(m.group(2))
            candidates.append((ch_num, m.start()))

    # Find the increasing sequential series of chapters in the body
    seq = []
    for ch_num, pos in candidates:
        if ch_num == 1:
            seq = [(ch_num, pos)]
        elif seq and ch_num == seq[-1][0] + 1:
            seq.append((ch_num, pos))

    if not seq:
        # Fallback to simple matching if no strict sequence found
        return text

    intervals = {}
    for i in range(len(seq)):
        ch_num, start_idx = seq[i]
        end_idx = seq[i + 1][1] if i + 1 < len(seq) else len(text)
        intervals[ch_num] = (start_idx, end_idx)

    selected_texts = []
    for ch_num in selected_chapter_nums:
        if ch_num in intervals:
            start_idx, end_idx = intervals[ch_num]
            selected_texts.append(text[start_idx:end_idx].strip())

    if selected_texts:
        return "\n\n".join(selected_texts)

    return text


def extract_subtopics(input_data) -> list:
    """
    Identify distinct subtopics or all chapters from extracted document text.
    Handles single documents and multiple uploaded files.
    """
    if not input_data:
        return []

    # Case 1: Multiple or tagged documents passed as a dictionary {filename: text}
    if isinstance(input_data, dict):
        if len(input_data) == 0:
            return []

        all_subtopics = []
        docs_needing_llm = {}

        for fname, text in input_data.items():
            # First attempt: Check for structured Table of Contents / Chapter markers
            toc_chapters = extract_chapters_from_toc(text, fname)
            if len(toc_chapters) >= 3:
                all_subtopics.extend(toc_chapters)
            else:
                docs_needing_llm[fname] = text

        # If any documents did not have structured TOC chapters, run LLM subtopic extraction
        if docs_needing_llm:
            if len(docs_needing_llm) == 1:
                fname, text = next(iter(docs_needing_llm.items()))
                llm_topics = _extract_subtopics_via_llm(text, filename=fname, doc_count=1)
            else:
                llm_topics = _extract_subtopics_via_llm(docs_needing_llm, doc_count=len(docs_needing_llm))
            all_subtopics.extend(llm_topics)

        return all_subtopics

    # Case 2: Raw string passed
    text = str(input_data)
    toc_chapters = extract_chapters_from_toc(text)
    if len(toc_chapters) >= 3:
        return toc_chapters

    return _extract_subtopics_via_llm(text, doc_count=1)


def _extract_subtopics_via_llm(input_data, filename: str = "", doc_count: int = 1) -> list:
    """Fallback LLM subtopic extractor for unstructured articles and documents without a TOC."""
    if isinstance(input_data, dict):
        doc_sections = []
        chars_per_doc = max(2500, min(5000, 12000 // len(input_data)))
        for fname, text in input_data.items():
            sample = text[:chars_per_doc].strip()
            doc_sections.append(f"=== DOCUMENT: {fname} ===\n{sample}")
        text_sample = "\n\n".join(doc_sections)
    else:
        prefix = f"=== DOCUMENT: {filename} ===\n" if filename else ""
        text_sample = prefix + str(input_data)[:8000]

    system_prompt = (
        "You are an expert at analyzing educational documents, syllabi, and textbooks. "
        "Your task is to identify 5 to 10 major academic chapters, conceptual units, or instructional modules from the text. "
        "Skip non-instructional administrative front matter (such as Acknowledgements, About the Publisher, Copyright, Dedication, Preface, or Accessibility Statement). "
        "Always respond with a valid JSON object."
    )

    if doc_count > 1:
        user_prompt = f"""Analyze the following extracted text from {doc_count} educational documents and identify 3 to 6 major academic chapters or conceptual units for EACH document.

{text_sample}

Return a JSON object with a "subtopics" key containing an array of subtopics found.
CRITICAL REQUIREMENT: You MUST extract 3 to 6 distinct academic subtopics from EVERY document listed above so that all uploaded files have selectable subtopics.
Do NOT list every tiny subsection. Focus on main chapters or core conceptual units. Skip acknowledgements, publisher info, and front matter.
Each subtopic should have:
- "title": Clean subtopic or chapter title (do NOT put document filename in title, e.g. "Chapter 2: The Number Systems")
- "source": The exact document filename it belongs to
- "keywords": 3-5 key terms that identify this section in the text
- "summary": A one-sentence summary of what this section covers

Example format:
{{
  "subtopics": [
    {{"title": "Photosynthesis Light Reactions", "source": "Lecture1.pdf", "keywords": ["photosynthesis", "chlorophyll", "thylakoid"], "summary": "Covers light reactions in doc 1"}},
    {{"title": "Cellular Respiration Overview", "source": "Lecture2.pdf", "keywords": ["respiration", "glycolysis", "ATP"], "summary": "Explains respiration in doc 2"}}
  ]
}}"""
    else:
        user_prompt = f"""Analyze the following extracted text from an educational document and identify 5 to 10 major academic chapters, units, or core subtopics.

TEXT SAMPLE:
{text_sample}

Return a JSON object with a "subtopics" key containing an array of 5 to 10 major academic subtopics found.
Do NOT list every micro-subsection. Extract clean, meaningful chapter-level or unit-level titles. Skip acknowledgements, publisher info, and administrative front matter.
Each subtopic should have:
- "title": Clean chapter or module title (e.g. "Chapter 2: The Number Systems")
- "keywords": 3-5 key terms that identify this section in the text
- "summary": A one-sentence summary of what this section covers

Example format:
{{
  "subtopics": [
    {{"title": "Chapter 1: Introduction to Computer Organization", "keywords": ["computer organization", "hardware", "assembly"], "summary": "Covers foundational computing architecture concepts."}},
    {{"title": "Chapter 2: The Number Systems", "keywords": ["binary", "two complement", "hexadecimal"], "summary": "Explains representation of unsigned and signed numbers."}}
  ]
}}"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=3500,
            temperature=0.1
        )

        raw_content = response.choices[0].message.content
        result = extract_json_from_response(raw_content)

        if isinstance(result, list):
            subtopics = result
        elif isinstance(result, dict):
            for key in ["subtopics", "topics", "chapters", "sections", "results"]:
                if key in result and isinstance(result[key], list):
                    subtopics = result[key]
                    break
            else:
                for v in result.values():
                    if isinstance(v, list):
                        subtopics = v
                        break
                else:
                    subtopics = []
        else:
            subtopics = []

        validated = []
        for item in subtopics:
            if isinstance(item, dict) and "title" in item:
                raw_t = item.get("title", "Unknown")
                clean_t = re.sub(r'^\[.*?\]\s*', '', raw_t).strip() or raw_t
                validated.append({
                    "title": clean_t,
                    "source": item.get("source", filename),
                    "keywords": item.get("keywords", []),
                    "summary": item.get("summary", "")
                })

        return validated

    except Exception as e:
        print(f"Subtopic extraction error: {e}")
        return []


def filter_text_by_subtopics(text: str, selected_subtopics: list, filename: str = None, all_subtopics: list = None) -> str:
    """
    Filter text to keep only portions related to selected subtopics.
    Supports chapter-boundary slicing when chapters are present, and keyword filtering as fallback.
    """
    if not selected_subtopics:
        return text

    # If filename and all_subtopics provided, check if this file was explicitly deselected
    if filename and all_subtopics:
        file_all_subs = [s for s in all_subtopics if s.get("source") == filename]
        if file_all_subs:
            file_selected_subs = [s for s in selected_subtopics if s.get("source") == filename]
            if not file_selected_subs:
                # The user had subtopics for this file, but selected NONE of them -> exclude file completely
                return ""
            subtopics_to_use = file_selected_subs
        else:
            subtopics_to_use = selected_subtopics
    else:
        subtopics_to_use = selected_subtopics

    # Check if selected subtopics have chapter_num defined
    selected_ch_nums = [s["chapter_num"] for s in subtopics_to_use if "chapter_num" in s and s["chapter_num"] is not None]
    if selected_ch_nums:
        # Exact chapter-boundary slicing
        return filter_by_chapters(text, selected_ch_nums)

    # Collect all keywords from relevant subtopics
    all_keywords = []
    for item in subtopics_to_use:
        all_keywords.extend(item.get("keywords", []))
        clean_title = item.get("title", "")
        if "]" in clean_title:
            clean_title = clean_title.split("]", 1)[-1].strip()
        all_keywords.append(clean_title)

    all_keywords = [kw for kw in all_keywords if kw and len(kw.strip()) > 1]
    if not all_keywords:
        return text

    # Split text into paragraphs
    if "\n\n" in text:
        paragraphs = text.split("\n\n")
    else:
        paragraphs = [s.strip() + "." for s in text.split(". ") if s.strip()]

    # Keep paragraphs that contain any keyword (case-insensitive)
    filtered_parts = []
    for para in paragraphs:
        para_lower = para.lower()
        if any(kw.lower() in para_lower for kw in all_keywords):
            filtered_parts.append(para)

    filtered = "\n\n".join(filtered_parts)

    if len(filtered) < len(text) * 0.10:
        return text

    return filtered
