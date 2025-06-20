from utils.assistant_manager import AssistantManager

import os
from dotenv import load_dotenv

load_dotenv()

assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
api_key = os.getenv("OPENAI_API_KEY")

assistant_manager = AssistantManager(assistant_id=assistant_id, openai_api_key=api_key)
