# Streamlit Cloud Deployment Guide

## Environment Variables Setup

For the app to work on Streamlit Cloud, you need to configure your API keys:

### 1. Go to Streamlit Cloud Settings
- Open your app on Streamlit Cloud
- Click the hamburger menu (☰) → Settings → Secrets

### 2. Add Your Secrets
Copy and paste this into the secrets editor:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
GROQ_MODEL = "llama-3.3-70b-versatile"
```

### 3. Accept PlayAI TTS Terms (Optional)
For voice responses to work:
1. Visit: https://console.groq.com/playground?model=playai-tts
2. Accept the terms of service
3. Voice chat will automatically use PlayAI TTS

**Note:** If you don't accept the terms, voice chat will still work using browser TTS as a fallback.

## Features That Require Configuration

### ✅ Works Without Setup
- All UI features
- Text chat
- Decision making
- Health council
- Temporal reasoning
- Simulation
- History tracking

### 🔑 Requires API Key
- **Voice Transcription**: Needs `GROQ_API_KEY` in secrets
- **AI Chat**: Needs `GROQ_API_KEY` in secrets
- **Voice Responses**: Needs PlayAI terms acceptance (or uses browser TTS fallback)

## Troubleshooting

### Voice Transcription Returns Empty
**Problem:** "Transcription returned empty" message

**Solutions:**
1. Check that `GROQ_API_KEY` is set in Streamlit Cloud secrets
2. Restart the app after adding secrets
3. Try speaking louder and clearer
4. Use text chat as alternative

### Voice Response Not Playing
**Problem:** No audio playback after voice message

**Solutions:**
1. Accept PlayAI TTS terms at Groq console
2. Browser TTS will work as fallback automatically
3. Check browser audio permissions

### App Crashes on Startup
**Problem:** App won't load

**Solutions:**
1. Check all secrets are properly formatted (TOML syntax)
2. Ensure no trailing spaces in secret values
3. Check Streamlit Cloud logs for specific errors

## Local Development

For local development, use `.env` file:

```bash
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Make sure `.env` is in `.gitignore` to avoid committing secrets!
