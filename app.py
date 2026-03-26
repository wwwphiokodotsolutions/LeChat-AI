"""
Le Chat AI: A playful assistant that activates only when triggered.
Usage: Run this script and interact via text or voice.
"""

import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
ACTIVATION_PHRASE = os.getenv("ACTIVATION_PHRASE")
DEACTIVATION_PHRASE = os.getenv("DEACTIVATION_PHRASE")

class LeChat:
    def __init__(self):
        self.is_active = False

    def listen(self, user_input):
        """Process user input and respond based on activation state."""
        if ACTIVATION_PHRASE in user_input:
            self.is_active = True
            return f"✨ **{ACTIVATION_PHRASE}**. Edit mode: ON. What’s the task?"
        elif DEACTIVATION_PHRASE in user_input:
            self.is_active = False
            return "Standby mode. Call me again with 'Le Chat activated ♍️'!"
        elif self.is_active:
            return self.execute_task(user_input)
        else:
            return "Awaiting activation phrase... Try 'Le Chat activated ♍️'!"

    def execute_task(self, task):
        """Use OpenAI API to execute the user's task."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Le Chat, a concise and playful AI assistant. Respond in 1-2 sentences."},
                    {"role": "user", "content": task}
                ]
            )
            return response.choices[0].message["content"]
        except Exception as e:
            return f"Error: {str(e)}"

if __name__ == "__main__":
    chat = LeChat()
    print("Le Chat: Hello! Say 'Le Chat activated ♍️' to start.")
    while True:
        user_input = input("You: ")
        print("Le Chat:", chat.listen(user_input))