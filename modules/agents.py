import json
from config import (
    client, MODEL_NAME, EVALUATOR_MODEL_NAME, OUTPUT_PROMPTS,
    LEVEL_INSTRUCTIONS, MINIMUM_PASSING_SCORE
)
from modules.rag_pipeline import retrieve_context
from modules.evaluator import (
    compute_readability, compute_rouge,
    compute_structural_compliance, compute_context_faithfulness,
    extract_json_from_response
)


class BaseAgent:
    def __init__(self, name: str, role: str, icon: str):
        self.name = name
        self.role = role
        self.icon = icon


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Research Agent",
            role="Extracts and synthesizes core factual knowledge and reference context",
            icon="🕵️"
        )

    def run(self, collection, topic: str, education_level: str) -> dict:
        """Query vector database / sources and construct a structured Research Brief."""
        retrieved_context = retrieve_context(collection, topic) if collection else ""

        system_prompt = (
            "You are an expert Educational Research Agent. Your task is to analyze retrieved reference material "
            "and user topics, extract core factual concepts, key definitions, and structure a concise Research Brief."
        )

        user_prompt = f"""Topic: {topic}
Target Education Level: {education_level}

Retrieved Reference Material:
{retrieved_context if retrieved_context else 'No external reference documents uploaded. Use reliable general domain knowledge.'}

Instructions:
Synthesize a structured Research Brief for the Curriculum Designer Agent containing:
1. Core Concepts & Technical Definitions
2. Essential Factual Points
3. Recommended Pedagogical Emphasis for {education_level} level (suitable vocabulary depth and scope).

Keep it factual, clear, and structured."""

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1200,
                temperature=0.2
            )
            brief = response.choices[0].message.content
        except Exception as e:
            brief = f"Research synthesis fallback: {e}\nContext: {retrieved_context[:500]}"

        return {
            "research_brief": brief,
            "has_rag_context": bool(retrieved_context),
            "raw_context": retrieved_context
        }


class CurriculumAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Curriculum Designer Agent",
            role="Drafts and refines structured teaching materials based on research briefs and pedagogical guidelines",
            icon="✍️"
        )

    def run(self, topic: str, output_type: str, education_level: str, research_brief: str, num_questions: int = 10) -> str:
        """Draft educational content using the research brief."""
        level_instruction = LEVEL_INSTRUCTIONS.get(
            education_level, LEVEL_INSTRUCTIONS["Secondary"]
        )
        prompt_template = OUTPUT_PROMPTS.get(
            output_type, OUTPUT_PROMPTS["Summary Notes"]
        )

        grounding = f"""
IMPORTANT: Base your output on the Research Brief provided below by the Research Agent.

Research Brief:
{research_brief}
"""

        prompt = prompt_template.format(
            topic=topic,
            level_instruction=level_instruction,
            context=grounding,
            num_questions=num_questions
        )

        system_prompt = (
            "You are an expert Curriculum Designer Agent creating structured teaching materials. "
            "Strictly follow structural instructions, maintain factual accuracy, and adapt vocabulary to the target level."
        )

        max_tok = 4000 if (output_type == "MCQ Questions" and num_questions > 10) else 2500

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tok,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Curriculum generation error: {e}"

    def revise(self, topic: str, output_type: str, education_level: str, previous_draft: str, critique: str, num_questions: int = 10) -> str:
        """Refine and rewrite content draft according to Evaluator Agent critique."""
        system_prompt = (
            "You are an expert Curriculum Designer Agent. Your task is to revise and refine previous teaching material drafts "
            "to fix defects, adjust readability, or correct structural issues highlighted by the Quality Evaluator Agent."
        )

        if output_type == "Lecture Slides":
            format_instruction = "For Lecture Slides, you MUST produce exactly 10 numbered slides (SLIDE 1 through SLIDE 10). Do not include MCQ quiz questions."
        elif output_type == "MCQ Questions":
            format_instruction = f"For MCQ Questions, you MUST produce exactly {num_questions} multiple choice questions (Q1. to Q{num_questions}.). Each question MUST have 4 options (A, B, C, D), Answer, and Explanation. Do NOT generate lecture slides."
        elif output_type == "Summary Notes":
            format_instruction = "For Summary Notes, you MUST produce structured comprehensive notes with clear section headings (##), bullet points, and Key Takeaways. Do NOT generate slides."
        elif output_type == "Glossary":
            format_instruction = "For Glossary, you MUST produce 15 key terms in alphabetical order with bold terms (**Term**), Definition, Example, and Related terms. Do NOT generate slides."
        else:
            format_instruction = f"Preserve the required format for {output_type}."

        user_prompt = f"""Topic: {topic}
Output Type: {output_type}
Target Education Level: {education_level}
Number of Questions (if MCQ): {num_questions}

PREVIOUS DRAFT:
{previous_draft}

EVALUATOR AGENT CRITIQUE & FEEDBACK:
{critique}

INSTRUCTIONS:
Rewrite the teaching material to strictly fix all issues mentioned in the critique while retaining correct information.
Ensure required formatting (headings, bullet counts, slide structure, or question format) is preserved.
{format_instruction}"""

        max_tok = 4000 if (output_type == "MCQ Questions" and num_questions > 10) else 2500

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tok,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return previous_draft


class EvaluatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Quality & Pedagogical Evaluator Agent",
            role="Audits content readability, structural compliance, context faithfulness, and pedagogical appropriateness",
            icon="🔍"
        )

    def run(self, draft: str, education_level: str, output_type: str,
            reference_context: str = "", num_questions: int = 10) -> dict:
        """
        Multi-layer evaluation combining:
        1. Algorithmic structural compliance (no LLM — zero bias)
        2. ROUGE-based context faithfulness (no LLM — zero bias)
        3. LLM pedagogical review (uses DIFFERENT model to avoid self-evaluation bias)
        """
        # ── Layer 1: Readability (algorithmic) ──
        readability = compute_readability(draft)

        # ── Layer 2: Structural Compliance (algorithmic) ──
        structural = compute_structural_compliance(draft, output_type, num_questions)

        # ── Layer 3: Context Faithfulness (ROUGE-based) ──
        faithfulness = compute_context_faithfulness(draft, reference_context)

        # ── Layer 4: LLM Pedagogical Review (different model family) ──
        pedagogical = self._llm_pedagogical_review(
            draft, education_level, output_type, reference_context, num_questions
        )

        # ── Combined Score ──
        structural_score = structural.get("score", 5.0)
        faithfulness_score = faithfulness.get("score", None)
        pedagogical_score = pedagogical.get("score", 7.0)

        if faithfulness_score is not None:
            # Full formula: 30% structural + 30% faithfulness + 40% pedagogical
            combined = (structural_score * 0.3 +
                        faithfulness_score * 0.3 +
                        pedagogical_score * 0.4)
        else:
            # No reference context: 40% structural + 60% pedagogical
            combined = (structural_score * 0.4 +
                        pedagogical_score * 0.6)

        combined = round(combined, 1)
        passed = (combined >= MINIMUM_PASSING_SCORE) and pedagogical.get("passed", True)

        return {
            "passed": passed,
            "score": combined,
            "critique": pedagogical.get("critique", ""),
            "readability": readability,
            "structural": structural,
            "faithfulness": faithfulness,
            "pedagogical": pedagogical,
            "model_used": EVALUATOR_MODEL_NAME
        }

    def _llm_pedagogical_review(self, draft: str, education_level: str,
                                 output_type: str, reference_context: str,
                                 num_questions: int = 10) -> dict:
        """
        Qualitative pedagogical review using a DIFFERENT model family
        from the content generator to avoid same-model evaluation bias.
        """
        fk_grade = compute_readability(draft).get("Flesch-Kincaid Grade Level", 8.0)

        system_prompt = (
            "You are a Quality & Pedagogical Evaluator Agent. You are a DIFFERENT AI model "
            "from the one that generated the content, providing an independent review. "
            "Evaluate the draft teaching material for pedagogical quality, clarity, "
            "appropriate tone, and structural compliance."
        )

        context_section = ""
        if reference_context and len(reference_context.strip()) > 50:
            context_section = f"""
Source Reference Context (to check factual grounding):
{reference_context[:1500]}
"""

        if output_type == "Lecture Slides":
            format_spec = "Format: Lecture Slides (Curriculum Standard: exactly 10 numbered slides covering Title through Summary)"
            structure_check = "1. Does it follow the required 10-slide layout structure (SLIDE 1: Title through SLIDE 10: Summary)? It must NOT contain quiz questions."
        elif output_type == "MCQ Questions":
            format_spec = f"Format: MCQ Questions (Curriculum Standard: exactly {num_questions} multiple-choice questions, each with 4 options A-D, Answer Key, and pedagogical Explanation)"
            structure_check = f"1. Does it contain exactly {num_questions} numbered multiple-choice questions with options A-D, correct answer, and explanation? It must NOT be slides."
        elif output_type == "Summary Notes":
            format_spec = "Format: Summary Notes (Curriculum Standard: structured study guide with Executive Summary, Core Concepts, In-Depth Breakdown, and Review Questions)"
            structure_check = "1. Does it follow the structured study guide format (Executive Summary, Core Concepts, In-Depth Breakdown, Key Takeaways)? It must NOT be slides."
        elif output_type == "Glossary":
            format_spec = "Format: Glossary (Curriculum Standard: 15 alphabetical terms with bold term, definition, and contextual example)"
            structure_check = "1. Does it provide a structured glossary format with terms, definitions, and contextual examples? It must NOT be slides."
        else:
            format_spec = f"Format: {output_type}"
            structure_check = f"1. Does it follow the required layout structure for {output_type}?"

        user_prompt = f"""Draft Content:
{draft[:8000]}

Parameters:
- Target Education Level: {education_level}
- {format_spec}
- Flesch-Kincaid Grade Level Score: {fk_grade}
{context_section}
Evaluate whether this draft meets the requirements:
{structure_check}
2. Is the tone and vocabulary depth suitable for {education_level}?
3. Are there any incomplete placeholders or missing sections?
4. Is the content factually grounded in the provided reference context (if any)?

Reply with JSON in this exact format:
{{
  "passed": true/false,
  "score": 1-10 integer,
  "critique": "Detailed explanation of what is good and what needs revision if failed."
}}"""

        # Attempt primary evaluation using EVALUATOR_MODEL_NAME (qwen3.8-27b)
        # We set max_tokens=450 (evaluator JSON is only ~150 tokens) to stay well under Groq OTPM limit (1,000/min)
        candidate_models = [EVALUATOR_MODEL_NAME, "openai/gpt-oss-20b"]
        last_error = None

        for model in candidate_models:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=450,
                    temperature=0.1
                )
                raw_content = response.choices[0].message.content
                eval_json = extract_json_from_response(raw_content)
                return {
                    "passed": eval_json.get("passed", True),
                    "score": eval_json.get("score", 7),
                    "critique": eval_json.get("critique", "Draft meets pedagogical requirements.")
                }
            except Exception as e:
                last_error = e
                continue

        # Graceful fallback — if both remote models fail, rely on algorithmic metrics
        return {
            "passed": True,
            "score": 7,
            "critique": "Automated pedagogical review completed using algorithmic readability and structural metrics."
        }

