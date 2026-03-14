import streamlit as st
import anthropic

def build_prompt(*args, **kwargs):
    return "Analyze the following climate patterns..."

def get_ai_analysis(*args, **kwargs) -> str:
    try:
        key = st.secrets.get("CLAUDE_API_KEY", "")
        if not key:
            return ""
    except (KeyError, FileNotFoundError, Exception):
        return ""
        
    try:
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role":"user","content": build_prompt(*args, **kwargs)}]
        )
        return msg.content[0].text
    except Exception:
        return ""
