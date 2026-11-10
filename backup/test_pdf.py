from modules.pdf_extractor import extract_text_from_pdf, chunk_text

text = extract_text_from_pdf("data/uploads/sample.pdf")
print(f"Extracted: {len(text)} characters")

chunks = chunk_text(text)
print(f"Chunks created: {len(chunks)}")
print(f"First chunk preview: {chunks[0][:300].encode('ascii', 'replace').decode('ascii')}")