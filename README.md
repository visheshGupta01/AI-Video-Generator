#AI Video Generator


Overview 
This project is a Python-based script that automatically generates a short news video using real
time headlines. It fetches trending news, generates a script using a language model, converts 
the script into audio, creates relevant visuals using an AI image generator, and compiles 
everything into a final video. 


Key Features 

1. Real-time News Fetching 
• Uses the NewsAPI to fetch the latest English-language headlines. 
• Selects a specific article (6th in the list) for processing.

2. AI-Generated Script 
• Generates a formal news script using the DistilGPT2 model. 
• Adds an intro and outro for structure. 
• Ensures the script reads like a typical news anchor briefing. 

3. Text-to-Speech Conversion 
• Uses Google Text-to-Speech (gTTS) to convert the script into audio. 
• Outputs an .mp3 file to be synced with video. 

4. Image Generation with Stable Diffusion 
• Generates an AI image based on the news headline using Stable Diffusion. 
• Ensures the visual matches the topic for better viewer engagement. 

5. Slide Creation 
• Creates three slides: Intro, Main, and Outro. 
• Each slide is created with PIL, using the generated image and custom overlaid text. 
• Handles font scaling and text wrapping. 

6. Video Assembly Using FFmpeg 
• Uses FFmpeg to: 
o Convert slides into short looping videos. 
o Concatenate them into a complete video. 
o Overlay the audio on the final video. 

7. Cleanup Process 
• Deletes temporary files like images, slides, intermediate videos, and audio files to keep 
the working directory clean.


Technologies Used 
• Python 
• gTTS (Google Text-to-Speech) 
• Pillow (PIL) 
• NewsAPI 
• Transformers (Hugging Face) 
• Stable Diffusion (Diffusers) 
• FFmpeg 


Execution Flow 
1. Fetch news headline and description. 
2. Generate script using a text-generation model. 
3. Generate audio from script. 
4. Create AI-generated image. 
5. Make slides using PIL. 
6. Convert slides to video using FFmpeg. 
7. Merge videos and add audio. 
8. Output the final video. 
9. Cleanup.


Sample Output 
• A short 60-second video that: 
o Begins with a "Breaking News" title screen. 
o Shows the headline and description on an AI-generated image. 
o Plays with audio that sounds like a news anchor's script. 
o Ends with a "Thanks for Watching" screen. 
