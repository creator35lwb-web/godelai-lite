"""
MemPalace-Lite v2 — Inference-time memory framework for small language models.

Part of the GodelAI-Lite ecosystem. Adds episodic memory, reasoning
continuity, and identity governance to any HuggingFace causal LM with
zero fine-tuning.

Quick start:
    from mempalace import MemPalaceLite, GodelAILite

    memory = MemPalaceLite()
    agent  = GodelAILite(model=model, tokenizer=tokenizer)
    reply  = agent.chat("My name is Jordan and I am a marine biologist.")
"""

from .core import MemoryEntry, MemPalaceLite
from .macp import ReasoningStep, MACPLite
from .gifp import GIFPLite
from .agent import GodelAILite, BaselineGemma

__version__ = '0.1.0'
__author__ = 'Alton Lee Wei Bin (creator35lwb)'

__all__ = [
    'MemoryEntry',
    'MemPalaceLite',
    'ReasoningStep',
    'MACPLite',
    'GIFPLite',
    'GodelAILite',
    'BaselineGemma',
]
