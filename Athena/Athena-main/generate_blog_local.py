import subprocess
import streamlit as st

@st.cache_data
def create_content(transcript):
    prompt = f"Create a blog post in markdown format for the given transcript\n{transcript}\n"

    command = [
        "ollama",
        "chat",
        "llama2",  
        "--prompt",
        prompt
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return f"Error: {result.stderr}"

    # Parse Ollama JSON output (last JSON line contains the response)
    output = result.stdout.strip().splitlines()
    for line in reversed(output):
        try:
            import json
            data = json.loads(line)
            if 'message' in data and 'content' in data['message']:
                return data['message']['content'].strip()
        except Exception:
            continue

    # fallback raw output if JSON parse fails
    return result.stdout.strip()
