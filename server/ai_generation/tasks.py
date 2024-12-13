import logging
import requests
import feedparser
from datetime import datetime
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.core.files.base import ContentFile
from podcasts.models import Podcast, Episode, Category
from openai import OpenAI
import time
import json
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence


logger = logging.getLogger(__name__)
class PodcastGenerator:
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.endpoint = "https://models.inference.ai.azure.com"
        self.model_name = "gpt-4o-mini"
        self.client = OpenAI(
            base_url=self.endpoint,
            api_key=self.openai_api_key,
        )
        self.rss_feeds = settings.RSS_FEEDS

    def fetch_latest_post(self, category_name):
        feed_url = self.rss_feeds.get(category_name)
        if not feed_url:
            return None
        feed = feedparser.parse(feed_url)
        if feed.entries:
            entry = feed.entries[0]
            return {
                'title': entry.title,
                'summary': entry.summary,
                'link': entry.link,
                'full_text': entry.content[0].value if 'content' in entry else entry.summary
            }
        return None

    def generate_script(self, title, full_text):
        prompt = f"""
        Write a funny and interesting mini podcast script based on this news feed, be at most 300 words long in Persian/Farsi. write only one paragraph. only one paragraph in farsi.
        Title: {title}
        Content: {full_text[:1000]}
        Only send me the script in Persian/Farsi.
        Only send the عنوان: <title in persian> and بدنه: <body in persian>.
        just this structure:
        عنوان:‌ <title in persian>
        بدنه: <body in persian>
        just this structure:
        عنوان:‌ <title in persian>
        بدنه: <body in persian>
        just this structure:
        عنوان:‌ <title in persian>
        بدنه: <body in persian>
        just this structure:
        عنوان:‌ <title in persian>
        بدنه: <body in persian>
        
        """
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an assistant to make mini-podcast script"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            top_p=1.0,
            model=self.model_name
        )
        ai_response = response.choices[0].message.content.strip()
        return self.process_ai_output(ai_response)

    def process_ai_output(self, ai_output):
        # Split the AI output into lines
        print(ai_output)
        ai_output = ai_output.replace("**", "").replace("title:", "عنوان:").replace("body:", "بدنه:")
        lines = ai_output.split('\n')

        # Initialize variables to store title and script
        title = ""
        script = ""

        # Iterate through the lines to find the title and script
        for line in lines:
            if line.startswith("عنوان:"):
                title = line.replace("عنوان:", "").strip()
            elif line.startswith("بدنه:"):
                # Get the content after 'بدنه:'
                script = line.replace("بدنه:", "").strip()
                # Include any subsequent lines as part of the script
                script_index = lines.index(line) + 1
                if script_index < len(lines):
                    script += "\n" + "\n".join(lines[script_index:]).strip()
                break

        return title, script

    def synthesize_speech(self, text):
        my_remote_iran_server_url = "http://178.239.151.132:5000/synthesize"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "text": text[:800]
        }
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.post(my_remote_iran_server_url, headers=headers, data=json.dumps(data), timeout=120)
                if response.status_code == 200:
                    return response.content
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                if attempt == max_retries - 1:  # Last attempt
                    logger.error(f"Failed to synthesize speech after {max_retries} attempts: {str(e)}")
                    return None
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
        
        return None

    def create_podcast_and_episode(self, category, title, script, link, audio_content):
        # Ensure the podcast exists
        podcast, _ = Podcast.objects.get_or_create(
            title=f"پادکست {category} هوش مصنوعی",
            defaults={
                'description': f"پادکست‌های تولید شده توسط هوش مصنوعی با موضوع {category}",
                'author': 'هوش مصنوعی',
                'owner_id': 1,
            }
        )
        podcast.categories.add(Category.objects.get_or_create(name=category)[0])

        # Create the episode
        episode = Episode(
            podcast=podcast,
            title=title,
            description="ساخته شده از مقاله‌ی زیر:\n" + link,
            transcript=script,
            created_at=timezone.now()
        )
        filename = f"{title}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
        episode.audio_file.save(filename, ContentFile(audio_content))
        episode.save()

@shared_task
def generate_podcasts():
    print("Starting podcast generation process...")
    generator = PodcastGenerator()
    rss_feeds = settings.RSS_FEEDS
    print(f"Found {len(rss_feeds)} categories in RSS feeds.")

    for category in rss_feeds.keys():
        print(f"Processing category: {category}")
        post = generator.fetch_latest_post(category)
        if not post:
            print(f"No post found for category: {category}")
            continue

        print(f"Fetched latest post for category '{category}': {post['title']}")
        ai_title, script = generator.generate_script(post['title'], post['full_text'])
        if not script:
            print(f"Failed to generate script for post: {post['title']}")
            print(script)
            continue

        print(f"Generated script for post: {post['title']}")
        audio_content = generator.synthesize_speech(script)
        if not audio_content:
            print(f"Failed to synthesize speech for script of post: {post['title']}")
            print(audio_content)
            continue

        print(f"Synthesized speech for post: {post['title']}")
        generator.create_podcast_and_episode(category, ai_title, script, post["link"], audio_content)
        print(f"Podcast generated for category '{category}' with title '{post['title']}'")

    print("Podcast generation process completed.")

def transcribe_audio(path):
    print(f"Transcribing audio file: {path}")
    r = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio_data = r.record(source)
    text = r.recognize_google(audio_data, language='fa-IR')
    print(f"Transcription result: {text}")
    return text

def get_large_audio_transcription(path):
    print(f"Processing large audio file: {path}")
    sound = AudioSegment.from_file(path)
    chunks = split_on_silence(sound,
        min_silence_len=500,
        silence_thresh=sound.dBFS - 14,
        keep_silence=500,
    )
    folder_name = "audio_chunks"
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    print(f"Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        chunk.export(chunk_filename, format="wav")
        print(f"Exported chunk {i} to {chunk_filename}")
        try:
            text = transcribe_audio(chunk_filename)
        except sr.UnknownValueError:
            print(f"Chunk {i} could not be understood")
            text = ""
        except sr.RequestError:
            print(f"Request error for chunk {i}")
            text = ""
        whole_text += text + " "
        os.remove(chunk_filename)
        print(f"Removed chunk file: {chunk_filename}")
    os.rmdir(folder_name)
    print(f"Final transcription: {whole_text.strip()}")
    return whole_text.strip()

@shared_task
def transcribe_episodes():
    print("Starting transcription of episodes without transcripts...")
    episodes = Episode.objects.filter(
        models.Q(transcript__isnull=True) | 
        models.Q(transcript__exact='')
    )
    print(f"Found {episodes.count()} episodes without transcripts")
    for episode in episodes:
        print(f"Processing episode: {episode.title}")
        audio_file_path = episode.audio_file.path
        print(f"Audio file path: {audio_file_path}")
        transcript = get_large_audio_transcription(audio_file_path)
        if transcript:
            episode.transcript = transcript
            episode.save()
            print(f"Saved transcript for episode: {episode.title}")
        else:
            print(f"No transcript generated for episode: {episode.title}")

@shared_task
def generate_episode_summaries():
    print("Starting AI summary generation for episodes...")
    
    episodes = Episode.objects.filter(
        models.Q(transcript__isnull=False) & 
        models.Q(transcript__gt='') &
        (models.Q(ai_summary__isnull=True) | models.Q(ai_summary__exact=''))
    )
    
    print(f"Found {episodes.count()} episodes needing summaries")
    
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=settings.OPENAI_API_KEY,
    )

    for episode in episodes:
        print(f"Processing summary for episode: {episode.title}")
        
        prompt = f"""
        لطفا خلاصه‌ای کوتاه (حداکثر ۱۰۰ کلمه) از متن زیر تهیه کنید و کلمات کلیدی اصلی را مشخص کنید.
        فرمت خروجی باید به این صورت باشد:
        خلاصه: <خلاصه متن>
        کلیدواژه‌ها: <کلمات کلیدی با کاما جدا شده>

        متن:
        {episode.transcript}
        """

        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes Persian text"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                top_p=1.0,
                model="gpt-4o-mini"
            )
            
            summary = response.choices[0].message.content.strip()
            episode.ai_summary = summary
            episode.save()
            print(f"Saved AI summary for episode: {episode.title}")
            print(f"Summary: {summary}")
            
        except Exception as e:
            print(f"Error generating summary for episode {episode.title}: {str(e)}")
            continue

    print("AI summary generation completed.")

#generate_podcasts()
