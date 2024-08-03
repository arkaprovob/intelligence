"""
QNA: A package for question-answering synthesis using RAG techniques.
"""
from .synthesizer_factory import RAGSynthesizer, get_synthesizer_instance

__version__ = "0.1.0"
__all__ = ['RAGSynthesizer', 'get_synthesizer_instance']