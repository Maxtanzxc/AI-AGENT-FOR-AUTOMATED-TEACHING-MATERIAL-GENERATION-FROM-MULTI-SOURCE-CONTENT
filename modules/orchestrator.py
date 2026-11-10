import re
from datetime import datetime
from config import MINIMUM_PASSING_SCORE, MAX_REVISION_ITERATIONS
from modules.agents import ResearchAgent, CurriculumAgent, EvaluatorAgent


def truncate_lecture_slides(content: str) -> str:
    """
    Ensure lecture slides strictly stop at Slide 10 (Summary & Conclusion).
    Ensures generated Lecture Slides content does not exceed 10 slides.
    Cuts off any accidental Slide 11+, or trailing MCQ quiz / practice questions added after Slide 10.
    """
    if not content:
        return ""

    # 1. Cut off Slide 11 or higher
    m11 = re.search(r'\n+(?:[\*#_\[\(]\s*)*(?:SLIDE\s*(?:1[1-9]|[2-9]\d)|##\s*SLIDE\s*(?:1[1-9]|[2-9]\d))\b', content, re.IGNORECASE)
    if m11:
        content = content[:m11.start()].rstrip()

    # Find where Slide 10 begins so we never truncate legitimate slide content before Slide 10
    m10 = re.search(r'\bSLIDE\s*10\b', content, re.IGNORECASE)
    search_start = m10.start() if m10 else len(content)

    # 2. Only look for trailing Quiz / MCQ / Self-Assessment sections AFTER Slide 10
    after_slide_10 = content[search_start:]
    m_quiz = re.search(r'\n+(?:[\*#_\[\(]\s*)*(?:(?:QUICK\s*)?QUIZ|MCQ[S]?|MULTIPLE\s*CHOICE\s*QUIZ|PRACTICE\s*QUESTIONS?|SELF[- ]ASSESSMENT\s*QUIZ|TEST\s*YOUR\s*KNOWLEDGE)\b', after_slide_10, re.IGNORECASE)
    if m_quiz:
        content = content[:search_start + m_quiz.start()].rstrip()

    # 3. Cut off standalone trailing Q1. ... A) quiz questions if they appear after Slide 10
    after_slide_10_remaining = content[search_start:]
    m_q1 = re.search(r'\n+(?:Q1\.|Question\s*1[:\.])\s*.*?\n+[Aa]\)', after_slide_10_remaining, re.DOTALL | re.IGNORECASE)
    if m_q1:
        content = content[:search_start + m_q1.start()].rstrip()

    return content


class AgentOrchestrator:
    """Multi-Agent Orchestrator managing interaction flow, feedback loops, and telemetry."""

    def __init__(self):
        self.research_agent = ResearchAgent()
        self.curriculum_agent = CurriculumAgent()
        self.evaluator_agent = EvaluatorAgent()

    def run_pipeline(self, collection, topic: str, output_type: str,
                     education_level: str, max_iterations: int = MAX_REVISION_ITERATIONS,
                     num_questions: int = 10) -> dict:
        logs = []

        def log_step(agent_name: str, icon: str, action: str, details: str):
            logs.append({
                "agent_name": agent_name,
                "icon": icon,
                "action": action,
                "details": details,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })

        # Step 1: Research Agent
        log_step(
            self.research_agent.name,
            self.research_agent.icon,
            "Autonomous Research & Context Retrieval",
            f"Querying vector database context for topic '{topic}' targeting {education_level} level..."
        )

        research_res = self.research_agent.run(collection, topic, education_level)
        research_brief = research_res["research_brief"]
        has_rag = research_res["has_rag_context"]

        log_step(
            self.research_agent.name,
            self.research_agent.icon,
            "Research Brief Synthesized",
            f"Grounding mode: {'RAG Vector Memory' if has_rag else 'General LLM Knowledge'}.\nBrief Summary:\n{research_brief[:300]}..."
        )

        # Step 2: Curriculum Agent Initial Draft
        log_step(
            self.curriculum_agent.name,
            self.curriculum_agent.icon,
            "Initial Content Synthesis",
            f"Drafting {output_type}{f' ({num_questions} questions)' if output_type == 'MCQ Questions' else ''} tailored for {education_level} level using Research Brief guidelines..."
        )

        current_draft = self.curriculum_agent.run(
            topic=topic,
            output_type=output_type,
            education_level=education_level,
            research_brief=research_brief,
            num_questions=num_questions
        )

        if output_type == "Lecture Slides":
            current_draft = truncate_lecture_slides(current_draft)

        log_step(
            self.curriculum_agent.name,
            self.curriculum_agent.icon,
            "Draft Material Created",
            f"Generated initial draft ({len(current_draft)} characters)."
        )

        # Iterative Loop: Evaluator Agent & Curriculum Refinement
        iteration = 1
        final_eval = None

        while iteration <= max_iterations:
            log_step(
                self.evaluator_agent.name,
                self.evaluator_agent.icon,
                f"Pedagogical Audit (Iteration {iteration}/{max_iterations})",
                f"Evaluating readability metrics, structural compliance, and quality..."
            )

            eval_res = self.evaluator_agent.run(
                draft=current_draft,
                education_level=education_level,
                output_type=output_type,
                reference_context=research_brief,
                num_questions=num_questions
            )
            final_eval = eval_res

            readability = eval_res.get("readability", {})
            grade_lvl = readability.get("Flesch-Kincaid Grade Level", "N/A")
            reading_ease = readability.get("Flesch Reading Ease", "N/A")
            score = eval_res.get("score", 0)
            passed = eval_res.get("passed", False)
            critique = eval_res.get("critique", "")

            # Target score met or passed
            if passed and score >= MINIMUM_PASSING_SCORE:
                log_step(
                    self.evaluator_agent.name,
                    self.evaluator_agent.icon,
                    f"Audit Passed ✅ (Score: {score}/10)",
                    f"Target minimum score ({MINIMUM_PASSING_SCORE}/10) achieved on iteration {iteration}.\nGrade Level: {grade_lvl} | Reading Ease: {reading_ease}"
                )
                break

            if iteration >= max_iterations:
                log_step(
                    self.evaluator_agent.name,
                    "⚠️",
                    f"Max Refinement Iterations Reached ({max_iterations})",
                    f"Final best score: {score}/10 (Target: {MINIMUM_PASSING_SCORE}/10).\nGrade Level: {grade_lvl} | Reading Ease: {reading_ease}\nFeedback: {critique}"
                )
                break

            # If score is below threshold, trigger revision
            log_step(
                self.evaluator_agent.name,
                self.evaluator_agent.icon,
                f"Revision Required (Score: {score}/10 < {MINIMUM_PASSING_SCORE})",
                f"Grade Level: {grade_lvl} | Reading Ease: {reading_ease}\nCritique to address: {critique}"
            )

            log_step(
                self.curriculum_agent.name,
                self.curriculum_agent.icon,
                f"Refinement Loop (Iteration {iteration} → {iteration + 1})",
                f"Rewriting content to fix defects and improve score to >={MINIMUM_PASSING_SCORE}..."
            )

            current_draft = self.curriculum_agent.revise(
                topic=topic,
                output_type=output_type,
                education_level=education_level,
                previous_draft=current_draft,
                critique=critique,
                num_questions=num_questions
            )

            if output_type == "Lecture Slides":
                current_draft = truncate_lecture_slides(current_draft)

            iteration += 1

        if output_type == "Lecture Slides":
            current_draft = truncate_lecture_slides(current_draft)

        log_step(
            "System Orchestrator",
            "🚀",
            "Multi-Agent Pipeline Complete",
            f"Final teaching material ready after {min(iteration, max_iterations)} iteration(s)."
        )

        return {
            "final_output": current_draft,
            "research_brief": research_brief,
            "evaluation": final_eval,
            "logs": logs,
            "iterations": iteration
        }
