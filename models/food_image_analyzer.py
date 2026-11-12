"""
Lightweight image feature demonstration.
This is NOT a food-safety test and does not reliably identify pathogens or edibility.
For a research-grade classifier, train/evaluate a CNN on a labelled dataset.
"""
from PIL import Image, ImageStat
import os

def analyze_food_image(path):
    try:
        image = Image.open(path).convert("RGB")
        image.thumbnail((256, 256))
        stats = ImageStat.Stat(image)
        brightness = sum(stats.mean) / 3
        saturation_proxy = max(stats.mean) - min(stats.mean)
        # Heuristic visual condition score; deliberately described as a demo estimate.
        score = 75
        notes = []
        if brightness < 65:
            score -= 15
            notes.append("image is quite dark; retake in brighter, even lighting")
        elif brightness > 220:
            score -= 8
            notes.append("image may be overexposed")
        if saturation_proxy < 12:
            score -= 8
            notes.append("low colour variation detected")
        score = max(20, min(95, score))
        label = "Looks visually acceptable (demo estimate)" if score >= 65 else "Needs manual inspection"
        if not notes:
            notes.append("basic image brightness and colour features look typical")
        return {
            "label": label,
            "confidence": score,
            "notes": notes,
            "filename": os.path.basename(path),
            "disclaimer": "Visual heuristic only. It cannot confirm freshness, contamination, or whether food is safe to eat. Check smell, texture, temperature, expiry and official food-safety guidance."
        }
    except Exception as exc:
        return {"label": "Image analysis unavailable", "confidence": 0, "notes": [str(exc)],
                "disclaimer": "This prototype does not make food-safety decisions."}
