from modules.pdf_extractor import extract_text_from_pdf
from modules.rag_pipeline import clear_collection, add_to_collection, retrieve_context

collection = clear_collection("test")

text = extract_text_from_pdf("data/uploads/sample.pdf")
chunks_added = add_to_collection(collection, text, "PDF:sample")
print(f"Added {chunks_added} chunks")

context = retrieve_context(collection, "photosynthesis")
print(f"Retrieved context length: {len(context)}")
print(context[:300])