import os
import sys
import django

# Add the project root directory to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Set Django settings module
os.environ["DJANGO_SETTINGS_MODULE"] = "podcast_platform.settings"

# Initialize Django
django.setup()

# Import after Django setup
from ai_generation.tasks import transcribe_episodes, generate_episode_summaries

transcribe_episodes()
generate_episode_summaries()