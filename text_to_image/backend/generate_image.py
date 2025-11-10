import os
import argparse
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from PIL import Image
from datetime import datetime
from tqdm import tqdm

# Load .env file
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize Hugging Face Inference Client
# (Requires huggingface_hub >= 0.26.0)
client = InferenceClient(
    model="black-forest-labs/FLUX.1-schnell",
    api_key=HF_TOKEN,
    provider="nebius"
)

def generate_image(prompt, output_path):
    print(f"\n🔮 Generating image for prompt: '{prompt}'\n")

    with tqdm(total=100, desc="Processing", ncols=75) as pbar:
        try:
            # Generate image
            image = client.text_to_image(prompt)
            pbar.update(100)
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            return None

    image.save(output_path)
    print(f"\n✅ Image saved as {output_path}\n")
    image.show()

def main():
    parser = argparse.ArgumentParser(description="Text-to-Image Generator using FLUX.1-schnell (Nebius)")
    parser.add_argument("--prompt", type=str, required=True, help="Text prompt for image generation")
    parser.add_argument("--output", type=str, default=None, help="Output filename")
    args = parser.parse_args()

    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"generated_{timestamp}.png"

    generate_image(args.prompt, args.output)

if __name__ == "__main__":
    main()
