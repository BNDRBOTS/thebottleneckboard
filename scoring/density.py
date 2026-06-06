import re

# Precompile patterns for speed
_NUMBERS = re.compile(r'\b\d+(?:\.\d+)?\b')
_NAMED_ENTITIES = re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b')
_DATES = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b')
_CITATIONS = re.compile(r'\[\d+\]|\([A-Z][a-z]+, \d{4}\)')
_QUOTES = re.compile(r'“[^”]+”|"[^"]+"')
_TECH_TERMS = re.compile(r'\b(?:transformer|attention|backprop|gradient|inference|latent|embedding|token|fine[- ]tuning|RLHF|RAG|MoE|LoRA|QLoRA|FP16|BF16|HBM|GDDR|PCIe|CUDA|ROCm)\b', re.I)
_REPETITION = re.compile(r'\b(\w+)\s+\1\b')
_SPECULATION = re.compile(r'\b(may|might|could|possibly|perhaps|likely|unclear|remains to be seen)\b', re.I)
_PROMOTIONAL = re.compile(r'\b(breakthrough|state-of-the-art|groundbreaking|unprecedented|revolutionary|amazing|excellent)\b', re.I)

class DensityScorer:
    @staticmethod
    def score(article):
        text = article.get("full_text", "")
        if not text:
            return 0

        numbers = len(_NUMBERS.findall(text))
        named_entities = len(_NAMED_ENTITIES.findall(text))
        dates = len(_DATES.findall(text))
        citations = len(_CITATIONS.findall(text))
        quotes = len(_QUOTES.findall(text))
        tech = len(_TECH_TERMS.findall(text))
        repetition = len(_REPETITION.findall(text.lower()))
        speculation = len(_SPECULATION.findall(text.lower()))
        promotional = len(_PROMOTIONAL.findall(text.lower()))

        raw_score = (
            min(numbers, 30) * 2 +
            min(named_entities, 20) * 1.5 +
            min(dates, 15) * 3 +
            min(citations, 10) * 4 +
            min(quotes, 15) * 2 +
            min(tech, 25) * 2
        ) - (repetition * 0.5 + speculation * 1 + promotional * 1.5)

        return max(0, min(100, raw_score))
