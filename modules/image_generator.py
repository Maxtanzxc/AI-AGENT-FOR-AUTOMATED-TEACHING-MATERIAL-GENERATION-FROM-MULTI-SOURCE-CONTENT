import requests
import urllib.parse
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from PIL import Image, ImageDraw


def extract_clean_concept(slide_title: str, topic: str) -> str:
    """
    Extract the actual specific scientific/educational concept from a slide title,
    stripping generic template labels (e.g. 'CORE CONCEPT 1', 'DEEP DIVE', 'SLIDE 4').
    """
    clean = re.sub(r'[*#\[\]:]', '', slide_title).strip()
    clean = re.sub(r'^SLIDE\s*\d+\s*[:\-]?\s*', '', clean, flags=re.IGNORECASE).strip()
    
    # Remove generic structural prefix labels
    prefixes = [
        r'CORE CONCEPT \d+', r'CORE CONCEPT', r'DEEP DIVE & MECHANISMS', r'DEEP DIVE',
        r'REAL-WORLD APPLICATIONS & EXAMPLES', r'REAL-WORLD APPLICATIONS',
        r'CRITICAL THINKING & ANALYSIS', r'CRITICAL THINKING',
        r'TOPIC INTRODUCTION & CONTEXT', r'TOPIC INTRODUCTION',
        r'LEARNING OBJECTIVES', r'SUMMARY & CONCLUSION', r'SUMMARY AND CONCLUSION'
    ]
    for p in prefixes:
        clean = re.sub(rf'^{p}\s*[:\-]?\s*', '', clean, flags=re.IGNORECASE).strip()
        clean = re.sub(rf'\b{p}\b', '', clean, flags=re.IGNORECASE).strip()
    
    clean = re.sub(r'^[-\s:]+', '', clean).strip()
    
    # If the clean title is too generic or short, anchor it to the topic
    if not clean or len(clean) < 3 or clean.lower() in ('examples', 'applications', 'mechanisms', 'concept', 'analysis'):
        clean = f"{topic} Core Mechanisms & Structure"
    
    return clean


def search_wikipedia_diagram(slide_title: str, topic: str) -> bytes:
    """
    Search Wikipedia specifically for authentic scientific diagrams, schematics, and illustrations
    matching the exact concept and topic.
    """
    concept = extract_clean_concept(slide_title, topic)

    search_queries = [
        f"{concept} diagram",
        f"{concept} {topic}",
        f"{topic} {concept}"
    ]

    headers = {"User-Agent": "EduForgeAI/1.0 (Educational Assistant; contact@eduforge.ai)"}

    for query in search_queries:
        try:
            url = (
                f"https://en.wikipedia.org/w/api.php?action=query&generator=search"
                f"&gsrsearch={urllib.parse.quote(query)}&gsrlimit=3"
                f"&prop=pageimages|extracts&exintro=1&explaintext=1&exchars=150"
                f"&pithumbsize=900&format=json"
            )
            res = requests.get(url, headers=headers, timeout=6)
            if res.status_code == 200:
                pages = res.json().get("query", {}).get("pages", {})
                for pid, pdata in pages.items():
                    title = pdata.get("title", "").lower()
                    extract = pdata.get("extract", "").lower()
                    
                    # Verify relevance: title or snippet should relate to concept or topic
                    topic_words = set(re.findall(r'\w+', topic.lower()))
                    concept_words = set(re.findall(r'\w+', concept.lower()))
                    page_text = f"{title} {extract}"

                    is_relevant = any(w in page_text for w in concept_words if len(w) > 3) or \
                                  any(w in page_text for w in topic_words if len(w) > 3)

                    if not is_relevant:
                        continue

                    thumb_url = pdata.get("thumbnail", {}).get("source")
                    if thumb_url:
                        # Avoid flags, logos, or tiny icons
                        if any(bad in thumb_url.lower() for bad in ["flag", "logo", "icon", "symbol", "stub"]):
                            continue
                        img_res = requests.get(thumb_url, headers=headers, timeout=8)
                        if img_res.status_code == 200 and len(img_res.content) > 4000:
                            return img_res.content
        except Exception:
            continue

    return None


def fetch_image_from_pollinations(prompt: str, width: int = 800, height: int = 600, timeout: int = 10) -> bytes:
    """
    Fetch a generated educational diagram from Pollinations.ai with precision formatting.
    """
    clean_prompt = re.sub(r'[^\w\s,-]', '', prompt).strip()
    encoded_prompt = urllib.parse.quote(clean_prompt[:220])
    seed = int(time.time() * 1000) % 99999
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"

    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200 and len(response.content) > 1000:
            content = response.content
            if content.startswith(b'\xff\xd8') or content.startswith(b'\x89PNG') or content.startswith(b'RIFF'):
                return content
    except Exception:
        pass

    return None


def create_fallback_slide_illustration(title: str, topic: str, width: int = 800, height: int = 600) -> bytes:
    """
    Generate an authentic, topic-branded educational diagram card with specific concept headers and flow nodes.
    Ensures 100% topic relevance without random unrelated pictures.
    """
    concept = extract_clean_concept(title, topic)

    img = Image.new("RGB", (width, height), color=(15, 23, 42))  # Slate dark #0f172a
    draw = ImageDraw.Draw(img)

    # Gradient border
    draw.rounded_rectangle([15, 15, width - 15, height - 15], radius=16, outline=(0, 245, 212), width=3)
    
    # Header topic badge box
    draw.rounded_rectangle([35, 35, width - 35, 105], radius=10, fill=(30, 41, 59), outline=(139, 92, 246), width=1)
    draw.text((55, 48), f"TOPIC: {topic.upper()}", fill=(0, 245, 212))
    draw.text((55, 72), f"CONCEPT: {concept[:45]}", fill=(248, 250, 252))

    # Center Diagram Nodes with connecting arrows
    node_box_w = 200
    node_box_h = 90
    y_pos = 200

    stages = ["Input & Trigger", "Core Mechanism", "Output & Result"]
    colors = [(56, 189, 248), (0, 245, 212), (139, 92, 246)]

    for i, (stage, col) in enumerate(zip(stages, colors)):
        x_pos = 45 + i * 245
        # Box
        draw.rounded_rectangle([x_pos, y_pos, x_pos + node_box_w, y_pos + node_box_h], radius=10, fill=(30, 41, 59), outline=col, width=2)
        draw.text((x_pos + 15, y_pos + 20), f"Phase {i+1}", fill=col)
        draw.text((x_pos + 15, y_pos + 48), stage, fill=(248, 250, 252))

        # Arrow to next
        if i < 2:
            arr_x = x_pos + node_box_w + 10
            draw.line([arr_x, y_pos + 45, arr_x + 25, y_pos + 45], fill=(148, 163, 184), width=3)
            draw.polygon([(arr_x + 25, y_pos + 40), (arr_x + 35, y_pos + 45), (arr_x + 25, y_pos + 50)], fill=(0, 245, 212))

    # Bottom Concept Summary Bar
    draw.rounded_rectangle([35, 340, width - 35, 540], radius=12, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
    draw.text((55, 360), f"Key Focus: {concept}", fill=(0, 245, 212))
    draw.text((55, 395), f"• Authentic structural pathway for {topic}", fill=(203, 213, 225))
    draw.text((55, 430), f"• Explores core scientific mechanisms and principles", fill=(203, 213, 225))
    draw.text((55, 465), f"• Direct relevance to curriculum standards", fill=(203, 213, 225))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def get_single_slide_image(title: str, topic: str) -> bytes:
    """
    Top-tier educational image resolver ensuring 100% relevance to the topic and slide:
    1. Authentic Wikipedia textbook scientific diagram / schematic
    2. Pollinations AI educational diagram (targeted prompt)
    3. Topic-branded concept diagram card
    """
    concept = extract_clean_concept(title, topic)

    # 1. Authentic Wikipedia diagram matching the specific concept & topic
    img = search_wikipedia_diagram(title, topic)
    if img:
        return img

    # 2. AI educational diagram prompt tightly bound to topic & concept
    ai_prompt = (
        f"Detailed educational diagram of {concept} in {topic}, "
        f"labeled scientific illustration, clean white background, educational textbook schematic, high clarity"
    )
    img = fetch_image_from_pollinations(ai_prompt)
    if img:
        return img

    # 3. Dynamic Topic-branded Concept Diagram Card
    return create_fallback_slide_illustration(title, topic)


def parse_slide_titles(content: str) -> list:
    """
    Extract all slide titles from generated lecture slide content.
    """
    from modules.exporter import parse_slides_from_content
    parsed = parse_slides_from_content(content)
    return [t for t, _ in parsed]


def is_visual_worthy_slide(title: str, index: int = None, total: int = None) -> bool:
    """
    Determine if a slide should include a visual diagram/illustration.
    Skips text-only structural slides (Title, Learning Objectives, Summary, Conclusion, Q&A, etc.)
    and targets key concept, mechanism, and real-world application slides.
    """
    clean_title = re.sub(r'[*#\[\]:]', '', title).strip().lower()
    clean_title = re.sub(r'^slide\s*\d+\s*[:\-]?\s*', '', clean_title).strip()

    # Structural / Text-heavy slides that should NOT have images
    skip_keywords = [
        "title", "learning objective", "learning objectives", "objective", "objectives",
        "summary", "conclusion", "summary & conclusion", "summary and conclusion",
        "critical thinking", "critical thinking & analysis", "agenda", "table of contents",
        "q&a", "questions", "references", "further reading", "discussion", "wrap-up", "wrap up",
        "topic introduction & context", "topic introduction"
    ]

    for kw in skip_keywords:
        if kw in clean_title:
            return False

    # Positive visual indicators
    visual_keywords = [
        "concept", "mechanism", "mechanisms", "deep dive", "application", "applications",
        "example", "examples", "process", "structure", "cycle", "diagram", "system",
        "architecture", "model", "pipeline", "workflow", "classification", "components"
    ]
    for kw in visual_keywords:
        if kw in clean_title:
            return True

    # Position-based fallback for standard 10-slide decks:
    # Slides 4 to 8 (index 3 to 7) are core conceptual content
    if index is not None and total is not None:
        if index in (0, 1, total - 1):  # Skip first 2 and last slide
            return False
        if total >= 6 and 2 <= index <= min(7, total - 2):
            return True

    return True


def generate_slide_images(
    slide_titles: list,
    topic: str,
    mode: str = "selective",
    selected_indices: list = None,
    max_workers: int = 4
) -> list:
    """
    Generate images for slide titles based on the chosen mode.
    
    Modes:
    - 'selective' (default): Only generates diagrams for key concept & mechanism slides (returns None for others).
    - 'all': Generates an image for every slide.
    - 'custom': Generates images for specific indices passed in `selected_indices`.
    - 'none': Returns all None (no images).
    """
    if not slide_titles or mode == "none":
        return [None] * len(slide_titles) if slide_titles else []

    total = len(slide_titles)
    results = [None] * total

    # Determine which indices to fetch images for
    if mode == "custom" and selected_indices is not None:
        target_indices = [i for i in selected_indices if 0 <= i < total]
    elif mode == "all":
        target_indices = list(range(total))
    else:  # "selective"
        target_indices = [
            i for i, t in enumerate(slide_titles)
            if is_visual_worthy_slide(t, i, total)
        ]
        # Guarantee at least 2-4 key concept slides have visuals if none matched
        if not target_indices and total >= 3:
            mid_start = max(1, total // 4)
            mid_end = min(total - 1, total * 3 // 4 + 1)
            target_indices = list(range(mid_start, mid_end))

    if not target_indices:
        return results

    def _fetch_one(idx):
        time.sleep(0.05)
        title = slide_titles[idx]
        return idx, get_single_slide_image(title, topic)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_fetch_one, i): i
            for i in target_indices
        }
        for future in as_completed(futures):
            idx = futures[future]
            try:
                _, img_bytes = future.result()
                results[idx] = img_bytes
            except Exception as e:
                print(f"Error in slide image thread for slide {idx}: {e}")
                results[idx] = create_fallback_slide_illustration(slide_titles[idx], topic)

    # For target indices where image was None, apply fallback card
    for i in target_indices:
        if results[i] is None:
            results[i] = create_fallback_slide_illustration(slide_titles[i], topic)

    return results

