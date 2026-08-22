"""
Primary: abstractive summarization via a pretrained HuggingFace model.
Fallback / alt options: extractive summarization via sumy, offering
TextRank, LSA, and Luhn algorithms so the user/judges can compare approaches.
Long input is chunked (map step) then re-summarized (reduce step).
"""

_PIPELINE = None
_MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

try:
    from transformers import pipeline
    _PIPELINE = pipeline("summarization", model=_MODEL_NAME)
    _USE_TRANSFORMER = True
except Exception as e:
    print(f"[summarizer] Could not load transformer model ({e}). Using extractive fallback.")
    _USE_TRANSFORMER = False


def _get_extractive_summarizer(algorithm: str):
    from sumy.summarizers.text_rank import TextRankSummarizer
    from sumy.summarizers.lsa import LsaSummarizer
    from sumy.summarizers.luhn import LuhnSummarizer

    mapping = {
        "textrank": TextRankSummarizer,
        "lsa": LsaSummarizer,
        "luhn": LuhnSummarizer,
    }
    cls = mapping.get(algorithm, TextRankSummarizer)
    return cls()


def _extractive_summary(text: str, sentence_count: int = 5, algorithm: str = "textrank") -> str:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer

    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = _get_extractive_summarizer(algorithm)
    sentences = summarizer(parser.document, sentence_count)
    return " ".join(str(s) for s in sentences)


def _chunk_text(text: str, max_words: int = 500):
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]


def _length_targets(mode: str, length_pct: int):
    """
    mode: 'short' | 'detailed' — used as a base preset
    length_pct: 10-50, lets the user fine-tune within that preset via a slider
    """
    base = {"short": (90, 30), "detailed": (180, 80)}
    max_len, min_len = base.get(mode, base["short"])

    # scale by requested percentage (relative to a 500-word chunk baseline)
    scale = max(0.3, min(2.0, length_pct / 20))
    return int(max_len * scale), int(min_len * scale)


def _transformer_summary(text: str, mode: str = "short", length_pct: int = 20) -> str:
    max_len, min_len = _length_targets(mode, length_pct)
    chunks = _chunk_text(text, max_words=500)

    chunk_summaries = []
    for chunk in chunks:
        word_count = len(chunk.split())
        this_max = min(max_len, max(20, word_count // 2))
        this_min = min(min_len, max(10, this_max // 2))
        result = _PIPELINE(chunk, max_length=this_max, min_length=this_min, do_sample=False)
        chunk_summaries.append(result[0]["summary_text"])

    combined = " ".join(chunk_summaries)

    if len(chunk_summaries) > 1:
        word_count = len(combined.split())
        this_max = min(max_len, max(20, word_count // 2))
        this_min = min(min_len, max(10, this_max // 2))
        final = _PIPELINE(combined, max_length=this_max, min_length=this_min, do_sample=False)
        return final[0]["summary_text"]

    return combined


def summarize_text(text: str, mode: str = "short", algorithm: str = "auto", length_pct: int = 20) -> str:
    """
    algorithm: 'auto' (transformer if available, else textrank),
               'transformer', 'textrank', 'lsa', 'luhn'
    """
    text = text.strip()

    use_transformer = _USE_TRANSFORMER and algorithm in ("auto", "transformer")

    if use_transformer:
        try:
            return _transformer_summary(text, mode=mode, length_pct=length_pct)
        except Exception as e:
            print(f"[summarizer] Transformer failed ({e}), using extractive fallback.")

    extractive_algo = algorithm if algorithm in ("textrank", "lsa", "luhn") else "textrank"
    base_sentences = 3 if mode == "short" else 6
    sentence_count = max(1, round(base_sentences * (length_pct / 20)))
    return _extractive_summary(text, sentence_count=sentence_count, algorithm=extractive_algo)


def which_engine_used(algorithm: str = "auto") -> str:
    if algorithm in ("auto", "transformer") and _USE_TRANSFORMER:
        return f"transformer ({_MODEL_NAME})"
    algo = algorithm if algorithm in ("textrank", "lsa", "luhn") else "textrank"
    return f"extractive ({algo})"