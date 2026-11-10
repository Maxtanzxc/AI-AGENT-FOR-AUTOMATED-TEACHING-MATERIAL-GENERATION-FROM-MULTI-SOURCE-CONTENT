from modules.pdf_extractor import extract_text_from_pdf
from modules.rag_pipeline import clear_collection, add_to_collection
from modules.generator import generate_material

collection = clear_collection("test")
text = extract_text_from_pdf("data/uploads/sample.pdf")
add_to_collection(collection, text, "PDF:sample")

result = generate_material(
    collection,
    "photosynthesis",
    "Summary Notes",
    "Secondary"
)
print(result)