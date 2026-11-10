import sys
from modules.generator import generate_material_agentic

if __name__ == "__main__":
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    print("Testing Multi-Agent Generation Pipeline...")
    res = generate_material_agentic(
        collection=None,
        topic="Photosynthesis",
        output_type="Summary Notes",
        education_level="Primary"
    )

    print("\n--- FINAL OUTPUT SAMPLE ---")
    print(res["final_output"][:300])

    print("\n--- AGENT THOUGHT TRACE & LOGS ---")
    for log in res["logs"]:
        print(f"[{log['timestamp']}] {log['icon']} {log['agent_name']} -> {log['action']}")
        print(f"   Details: {log['details'][:120]}...\n")

    print(f"Iterations completed: {res['iterations']}")
    print("Evaluation result:", res["evaluation"])
