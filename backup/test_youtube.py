from modules.youtube_extractor import get_transcript

text = get_transcript("https://www.youtube.com/watch?v=D1Ymc311XS8")
print(f"Extracted: {len(text)} characters")
print(text[:300])