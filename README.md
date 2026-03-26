# Le Chat AI 🐱♍️

A playful AI assistant that **only activates when triggered** (e.g., "Le Chat activated ♍️"). Built with Python and the OpenAI API.

## Features
- **Activation/Deactivation:** Responds only to specific phrases.
- **Task Execution:** Uses OpenAI's GPT-4 for text-based tasks.
- **Extensible:** Add voice, GitHub, or other integrations.

## Setup
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install openai python-dotenv
   ```
3. Add your OpenAI API key to `.env`:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```
4. Run the script:
   ```bash
   python app.py
   ```

## Example Usage
```plaintext
You: Le Chat activated ♍️ – write a Python function to sort a list.
Le Chat: ✨ Edit mode: ON. Here’s a function: `sorted_list = sorted(your_list)`.
You: Le Chat standby.
Le Chat: Standby mode. Call me again with 'Le Chat activated ♍️'!
```

## Extensions
- **Voice Activation:** Use `speech_recognition` for voice commands.
- **GitHub Integration:** Edit code repositories with `PyGithub`.
- **Web Interface:** Deploy with Flask for a browser-based UI.

## License
MIT

---