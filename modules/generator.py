from modules.orchestrator import AgentOrchestrator


def generate_material_agentic(collection, topic: str, output_type: str,
                              education_level: str, num_questions: int = 10) -> dict:
    """Multi-agent generation pipeline returning final output, telemetry logs, and evaluation."""
    orchestrator = AgentOrchestrator()
    return orchestrator.run_pipeline(
        collection=collection,
        topic=topic,
        output_type=output_type,
        education_level=education_level,
        num_questions=num_questions
    )


def generate_material(collection, topic: str, output_type: str,
                      education_level: str, num_questions: int = 10) -> str:
    """Backwards-compatible interface returning string output from multi-agent pipeline."""
    res = generate_material_agentic(collection, topic, output_type, education_level, num_questions=num_questions)
    return res.get("final_output", "")


def generate_material_no_rag(topic: str, output_type: str,
                              education_level: str, num_questions: int = 10) -> str:
    """Backwards-compatible interface returning string output without RAG collection."""
    res = generate_material_agentic(None, topic, output_type, education_level, num_questions=num_questions)
    return res.get("final_output", "")