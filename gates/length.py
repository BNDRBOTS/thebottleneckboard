from config import MIN_WORD_COUNT, MIN_CHAR_COUNT

def meets_length(article_dict):
    full_text = article_dict.get("full_text")
    if not full_text:
        full_text = article_dict.get("raw_metadata", {}).get("summary", "")
    if not isinstance(full_text, str):
        full_text = ""
    word_count = len(full_text.split())
    char_count = len(full_text)
    return word_count >= MIN_WORD_COUNT or char_count >= MIN_CHAR_COUNT
