import os
import uuid
import requests
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from transformers import pipeline, set_seed
from diffusers import StableDiffusionPipeline
import torch

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

generator = pipeline('text-generation', model='distilgpt2')
set_seed(42)

pipe = StableDiffusionPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4", cache_dir="./model_cache"
).to("cuda" if torch.cuda.is_available() else "cpu")


def fetch_news():
    url = f'https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}'
    res = requests.get(url)
    data = res.json()
    if res.status_code != 200 or not data.get('articles'):
        raise Exception("Failed to fetch news.")
    article = data['articles'][5]
    return article.get('title', ''), article.get('description', '')


def generate_script(title, description):
    intro_prompt = f"Anchor: Good evening. In today's top story, {title}."
    outro_prompt = "Anchor: That's all for now. Stay tuned for further updates."
    prompt = f"{intro_prompt} {description} In today's developments,"
    ai_output = generator(prompt, max_length=200, num_return_sequences=1)[0]['generated_text']
    ai_middle = ai_output.replace(prompt, '').strip()
    return f"{intro_prompt.replace('Anchor: ', '')} {description} {ai_middle} {outro_prompt.replace('Anchor: ', '')}"


def generate_audio(script, output_path="audio.mp3"):
    tts = gTTS(text=script, lang='en')
    tts.save(output_path)
    return output_path


def generate_image(prompt, output_path="image.png"):
    image = pipe(prompt=prompt, num_inference_steps=15).images[0]
    image.save(output_path)
    return output_path


def create_slide_with_image(text, filename, image_path, font_path="arial.ttf", font_size=48):
    img = Image.open(image_path)
    img_width, img_height = img.size
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    text_lines = text.split('.')

    while True:
        try:
            text_width = max([draw.textbbox((0, 0), line, font=font)[2] for line in text_lines])
            text_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in text_lines]) + 10 * (len(text_lines) - 1)
        except Exception:
            text_width = max([draw.textsize(line, font=font)[0] for line in text_lines])
            text_height = sum([draw.textsize(line, font=font)[1] for line in text_lines]) + 10 * (len(text_lines) - 1)

        if text_width <= img_width and text_height <= img_height:
            break
        font_size -= 2
        font = ImageFont.truetype(font_path, font_size)

    y = (img_height - text_height) // 3
    for line in text_lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except Exception:
            text_width, text_height = draw.textsize(line, font=font)

        draw.text(((img_width - text_width) / 2, y), line, fill="black", font=font)
        y += text_height + 10

    img.save(filename)


def generate_video(title, description, script):
    uid = str(uuid.uuid4())
    print("Generating Image")
    image_path = generate_image(title)
    create_slide_with_image("Breaking News", "intro.png", image_path, font_size=60)
    create_slide_with_image(f"{title}\n{description}", "main.png", image_path, font_size=40)
    create_slide_with_image("Thanks for watching", "outro.png", image_path, font_size=40)

    os.system("ffmpeg -y -loop 1 -t 3 -i intro.png -vf format=yuv420p intro.mp4")
    os.system("ffmpeg -y -loop 1 -t 54 -i main.png -vf format=yuv420p main.mp4")
    os.system("ffmpeg -y -loop 1 -t 3 -i outro.png -vf format=yuv420p outro.mp4")

    with open("inputs.txt", "w") as f:
        f.write("file 'intro.mp4'\nfile 'main.mp4'\nfile 'outro.mp4'\n")
    os.system("ffmpeg -y -f concat -safe 0 -i inputs.txt -c copy combined.mp4")
    
    print("Generating Audio")
    audio_path = generate_audio(script)
    final_video_path = f"news_video_{uid}.mp4"
    os.system(f"ffmpeg -y -i combined.mp4 -i {audio_path} -c:v copy -c:a aac -shortest {final_video_path}")

    for file in ["intro.png", "main.png", "outro.png", "intro.mp4", "main.mp4", "outro.mp4", "combined.mp4", "inputs.txt", audio_path, image_path]:
        try: os.remove(file)
        except: pass

    return final_video_path


def generate_news_video():
    print("Fetching News...")
    title, description = fetch_news()
    print("Generating Script...")
    script = generate_script(title, description)
    video_path = generate_video(title, description, script)
    return video_path


if __name__ == "__main__":
    print("Generating video...")
    path = generate_news_video()
    print(f"Video saved to: {path}")
