# OfflineMind
Eliminate reading interruptions - instantly explain any text in any app using Gemma 3n. No context switching, no tracking, pure focus.

## Introduction
Offlinemind is a smart offline assistant that explains selected words or sentences using a local LLM (Gemma 3n via Ollama). It shows a quick pop-up with a concise explanation and allows language translation. Great for readers, learners, and travelers — no internet or browser distractions needed.

## Features
- Hotkey-based (F9) activation
- No browser or history required
- Uses local Ollama API (Gemma 3n model)
- Floating explanation window with language switch
- Pronunciation using Text-to-Speech

## Requirements

- Python 3.8+
- Ollama installed and running
- macOS (recommended) or Windows/Linux with adjustments

## Setup Instructions

### 1. Clone the Repo (or Copy the Script)

```bash
git clone https://github.com/Sanyam-jain30/OfflineMind.git
cd offlinemind
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Ollama (If Not Already Running)
Make sure Ollama is installed and running with the Gemma 3n model.

```bash
OLLAMA_HOST=127.0.0.1:3000 ollama serve
```

Then pull the model:

```bash
ollama run gemma3n
```

You should see it loading and then staying idle, waiting for requests.

## Run Offlinemind
After starting Ollama, run the script:

```bash
python offlinemind.py
```

Then select any text anywhere (like in your browser or PDF), press F9, and watch the magic happen!


## Customization
- You can change the hotkey (F9) in the script.
- Add more languages in the available_languages list.
- Works best in reading apps or editors that allow selection + Cmd+C.


## Troubleshooting
- If nothing happens on F9, make sure:
    1. Text is selected
    2. Ollama is running
    3. You allowed accessibility permissions (on macOS)
- TTS might need additional voices on some systems (try say on terminal to test).


## License
MIT License.
