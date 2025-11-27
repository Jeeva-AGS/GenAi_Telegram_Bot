from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

# Load model once (cached)
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

def describe_image(image_path: str):
    raw_image = Image.open(image_path).convert("RGB")

    inputs = processor(raw_image, return_tensors="pt")
    output = model.generate(**inputs, max_new_tokens=30)

    caption = processor.decode(output[0], skip_special_tokens=True)

    # Generate simple tags from caption → 3 keywords
    words = caption.lower().replace(",", "").split()
    
    # Filter out filler words
    stop = {"the", "a", "an", "of", "with", "on", "in", "and"}
    keywords = [w for w in words if w not in stop]

    tags = keywords[:3] if len(keywords) >= 3 else keywords

    return caption, tags
