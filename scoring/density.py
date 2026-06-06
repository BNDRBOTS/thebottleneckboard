import re

class DensityScorer:
    @staticmethod
    def score(article):
        text = article.get("full_text", "")
        if not text:
            return 0

        numbers = len(re.findall(r'\b\d+(?:\.\d+)?\b', text))
        named_entities = len(re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text))
        dates = len(re.findall(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b', text))
        citations = len(re.findall(r'\[\d+\]|\([A-Z][a-z]+, \d{4}\)', text))
        quotes = len(re.findall(r'“[^”]+”|"[^"]+"', text))
        technical_terms = len(re.findall(r'\b(?:transformer|attention|backprop|gradient|inference|latent|embedding|token|fine[- ]tuning|RLHF|RAG|MoE|LoRA|QLoRA|FP16|BF16|HBM|GDDR|PCIe|CUDA|ROCm)\b', text.lower()))

        repetition = len(re.findall(r'\b(\w+)\s+\1\b', text.lower()))
        speculation = len(re.findall(r'\b(may|might|could|possibly|perhaps|likely|unclear|remains to be seen)\b', text.lower()))
        promotional = len(re.findall(r'\b(breakthrough|state-of-the-art|groundbreaking|unprecedented|revolutionary|amazing|excellent)\b', text.lower()))

        raw_score = (
            min(numbers, 30) * 2 +
            min(named_entities, 20) * 1.5 +
            min(dates, 15) * 3 +
            min(citations, 10) * 4 +
            min(quotes, 15) * 2 +
            min(technical_terms, 25) * 2
        ) - (repetition * 0.5 + speculation * 1 + promotional * 1.5)

        return max(0, min(100, raw_score))
