import os
from dotenv import load_dotenv
from groq import Groq

import shutil
import pytesseract

load_dotenv()

# Tesseract OCR Configuration
TESSERACT_PATH_ENV = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
if os.path.exists(TESSERACT_PATH_ENV):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH_ENV
    IS_TESSERACT_AVAILABLE = True
elif shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")
    IS_TESSERACT_AVAILABLE = True
else:
    IS_TESSERACT_AVAILABLE = False

# Selenium Configuration
SELENIUM_HEADLESS = True
SELENIUM_PAGE_TIMEOUT = 12

try:
    import selenium
    IS_SELENIUM_AVAILABLE = True
except ImportError:
    IS_SELENIUM_AVAILABLE = False

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")

client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "openai/gpt-oss-120b"      # most capable available model
EVALUATOR_MODEL_NAME = "qwen/qwen3.8-27b"  # different model family for unbiased evaluation (qwen3.8-27b has fast non-thinking output)

# Multi-Agent Evaluation & Iteration Settings
MINIMUM_PASSING_SCORE = 7.0       # Minimum composite score required to pass evaluation (0-10)
MAX_REVISION_ITERATIONS = 3       # Maximum refinement loops to prevent excessive latency/costs

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5

LEVEL_INSTRUCTIONS = {
    "Primary": "Use very simple vocabulary suitable for children aged 10 to 12. Avoid all technical jargon. Use short sentences and relatable everyday examples.",
    "Secondary": "Use clear language suitable for students aged 13 to 17. Introduce technical terms with brief plain-English explanations alongside them.",
    "Tertiary": "Use academic language appropriate for university students. Include technical terminology, cite concepts precisely and assume prior subject knowledge."
}


OUTPUT_PROMPTS = {
    "Summary Notes": """Generate comprehensive structured summary notes on the topic: {topic}
Education level: {level_instruction}

{context}

Format your output EXACTLY as follows:
- Start with a one-paragraph overview of the topic (3-4 sentences)
- Then use ## headings for each major concept (minimum 4 headings)
- Under each heading write 5-6 bullet points
- Each bullet point must be a complete, informative sentence — not just a phrase
- Include a "Key Takeaways" section at the end with 4-5 summary points
- End with a one-paragraph conclusion

Do not use vague bullet points like "It is important" — each point must state a specific fact or concept.""",

    "Lecture Slides": """Generate detailed lecture slide content on the topic: {topic}
Education level: {level_instruction}

{context}

Format your output EXACTLY as follows — produce exactly 10 numbered slides:

SLIDE 1: [TITLE - Topic Name]
Subtitle: [one sentence describing what this lecture covers]
Key themes: [list 3 themes this lecture addresses]

SLIDE 2: [LEARNING OBJECTIVES]
By the end of this lecture, students will be able to:
- [specific measurable objective 1]
- [specific measurable objective 2]
- [specific measurable objective 3]
- [specific measurable objective 4]

SLIDE 3: [TOPIC INTRODUCTION & CONTEXT]
- [Bullet point 1 — full informative sentence, not a phrase]
- [Bullet point 2 — full informative sentence]
- [Bullet point 3 — full informative sentence]
- [Bullet point 4 — full informative sentence]
- [Bullet point 5 — full informative sentence]
Speaker note: [one sentence hint for the presenter on what to emphasise]

SLIDE 4: [CORE CONCEPT 1: SPECIFIC DESCRIPTIVE TITLE]
- [Bullet point 1 — full informative sentence]
- [Bullet point 2 — full informative sentence]
- [Bullet point 3 — full informative sentence]
- [Bullet point 4 — full informative sentence]
- [Bullet point 5 — full informative sentence]
Speaker note: [one sentence hint for the presenter]

SLIDE 5: [CORE CONCEPT 2: SPECIFIC DESCRIPTIVE TITLE]
- [Bullet point 1 — full informative sentence]
- [Bullet point 2 — full informative sentence]
- [Bullet point 3 — full informative sentence]
- [Bullet point 4 — full informative sentence]
- [Bullet point 5 — full informative sentence]
Speaker note: [one sentence hint for the presenter]

SLIDE 6: [CORE CONCEPT 3: SPECIFIC DESCRIPTIVE TITLE]
- [Bullet point 1 — full informative sentence]
- [Bullet point 2 — full informative sentence]
- [Bullet point 3 — full informative sentence]
- [Bullet point 4 — full informative sentence]
- [Bullet point 5 — full informative sentence]
Speaker note: [one sentence hint for the presenter]

SLIDE 7: [DEEP DIVE & MECHANISMS]
- [Bullet point 1 — full informative sentence]
- [Bullet point 2 — full informative sentence]
- [Bullet point 3 — full informative sentence]
- [Bullet point 4 — full informative sentence]
- [Bullet point 5 — full informative sentence]
Speaker note: [one sentence hint for the presenter]

SLIDE 8: [REAL-WORLD APPLICATIONS & EXAMPLES]
- [Bullet point 1 — full informative sentence]
- [Bullet point 2 — full informative sentence]
- [Bullet point 3 — full informative sentence]
- [Bullet point 4 — full informative sentence]
- [Bullet point 5 — full informative sentence]
Speaker note: [one sentence hint for the presenter]

SLIDE 9: [CRITICAL THINKING & ANALYSIS]
- [Bullet point 1 — full informative sentence]
- [Bullet point 2 — full informative sentence]
- [Bullet point 3 — full informative sentence]
- [Bullet point 4 — full informative sentence]
- [Bullet point 5 — full informative sentence]
Speaker note: [one sentence hint for the presenter]

SLIDE 10: [SUMMARY & CONCLUSION]
Key points covered:
- [summary point 1]
- [summary point 2]
- [summary point 3]
Discussion question: [one thought-provoking question for students]
Further reading: [suggest one type of resource to explore next]

CRITICAL RULES:
- Produce EXACTLY 10 numbered slides (Slide 1 to Slide 10). Do NOT add extra slides.
- Do NOT include any multiple-choice questions (MCQs), quizzes, test questions, A/B/C/D option lists, or answer keys anywhere in the slides. Slide 9 must focus purely on analytical discussion concepts, NOT quizzes.
- Every bullet point must be a complete, informative sentence with real educational content.""",

    "MCQ Questions": """Generate a comprehensive multiple choice quiz on the topic: {topic}
Education level: {level_instruction}

{context}

Format your output EXACTLY as follows:

Generate exactly {num_questions} questions. Cover a balanced range of difficulty across Easy, Medium, and Hard.

For each question use this format:

Q[number]. [difficulty: Easy/Medium/Hard]
[Question text — must be a clear, unambiguous question]
A) [option]
B) [option]
C) [option]
D) [option]
Answer: [correct letter]
Explanation: [2-3 sentences explaining WHY this is correct and why the other options are wrong]

Rules:
- Questions must test genuine understanding, not just memorization
- All four options must be plausible — no obviously wrong answers
- Vary question types: definition, application, comparison, cause-effect
- Explanations must be genuinely educational""",

    "Glossary": """Generate a detailed educational glossary on the topic: {topic}
Education level: {level_instruction}

{context}

Format your output EXACTLY as follows:

Generate exactly 15 key terms. Order them alphabetically.

For each term use this format:

**[Term]**
Definition: [clear, precise definition in 2-3 sentences appropriate for the education level]
Example: [one concrete real-world example or application of this term]
Related terms: [2-3 related terms from the glossary]

Rules:
- Definitions must be accurate and precise — do not use vague language
- Examples must be concrete and relevant to the education level
- Include a mix of core terms, technical terms and conceptual terms"""
}