from PIL import Image
import io
import random

def analyze_screenshot(image_bytes):
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Example placeholder logic — dimensions & color mode check
        width, height = image.size
        mode = image.mode

        # Simple strategy detection based on size (replace with real image parsing later)
        strategy = "Breakout" if width > 1000 else "Pullback"
        confidence = round(random.uniform(0.7, 0.95), 2)

        return {
            "width": width,
            "height": height,
            "mode": mode,
            "strategy_detected": strategy,
            "confidence_score": confidence,
            "comment": f"Image appears to reflect a {strategy} setup ({int(confidence * 100)}% confidence)."
        }
    except Exception as e:
        return {
            "error": str(e),
            "comment": "Failed to analyze screenshot. Make sure it's a valid image."
        }
