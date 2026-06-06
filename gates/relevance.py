import re

AI_KEYWORDS = re.compile(
    r'\b(?:AI|artificial intelligence|machine learning|deep learning|LLM|large language model|'
    r'foundation model|generative|GPT|Claude|Gemini|Gemma|Llama|Mistral|'
    r'transformer|neural network|inference|training|compute|GPU|TPU|'
    r'safety|alignment|regulation|policy|security|misuse|chip|semiconductor|'
    r'autonomous|agent|reasoning|multimodal|fine[- ]tuning|RLHF|RAG|'
    r'Codex|Copilot|GitHub Copilot|OpenAI Codex|DALL-E|Midjourney|Stable Diffusion)\b',
    re.IGNORECASE
)

def is_ai_relevant(title, raw_metadata):
    text = title + " " + str(raw_metadata.get("summary", "")) + " " + raw_metadata.get("body", "")
    if AI_KEYWORDS.search(text):
        return True
    words = set(re.findall(r'\b[a-z]{3,}\b', text.lower()))
    ai_terms = {"ai", "model", "training", "data", "neural", "network", "algorithm", "compute"}
    if len(words.intersection(ai_terms)) >= 2:
        return True
    return False
