from sentence_transformers import SentenceTransformer, util

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    return _model
