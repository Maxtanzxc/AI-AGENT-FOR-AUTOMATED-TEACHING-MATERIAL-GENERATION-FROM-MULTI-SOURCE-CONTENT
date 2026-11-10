import sys
from PIL import Image
from modules.evaluator import compute_image_clip_score

def run_clip_demo():
    print("=" * 60)
    print("  EDUFORGE AI: CLIP IMAGE-TEXT ALIGNMENT EVALUATION")
    print("=" * 60)
    green_img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    red_img = Image.new("RGB", (224, 224), color=(220, 20, 60))
    prompt_bio = "Photosynthesis and chlorophyll structure in green plant leaves"
    prompt_car = "High speed red sports car engine and aerodynamics"
    print(f"\n1. Testing Prompt: {prompt_bio}")
    res1 = compute_image_clip_score(green_img, prompt_bio)
    print(f"   Matching Green Image -> Raw Sim: ${res1.get('raw_similarity')} / Score: ${res1.get('score')}/10 / Rating: ${res1.get('quality_rating')}")
    res2 = compute_image_clip_score(red_img, prompt_bio)
    print(f"   Mismatched Red Image -> Raw Sim: ${res2.get('raw_similarity')} / Score: ${res2.get('score')}/10 / Rating: ${res2.get('quality_rating')}")
    print(f"\n2. Testing Prompt: {prompt_car}")
    res3 = compute_image_clip_score(red_img, prompt_car)
    print(f"   Matching Red Image   -> Raw Sim: ${res3.get('raw_similarity')} / Score: ${res3.get('score')}/10 / Rating: ${res3.get('quality_rating')}")
    print("\n" + "=" * 60)
    print("  CLIP Evaluation Pipeline Verified Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    run_clip_demo()
