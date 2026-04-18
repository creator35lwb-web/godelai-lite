import os
import torch
from typing import Dict, List
from transformers import GenerationConfig

from .core import MemPalaceLite
from .macp import MACPLite
from .gifp import GIFPLite


class GodelAILite:
    """
    GodelAI-Lite: Gemma 4 (or any HuggingFace causal LM) augmented with
    MemPalace-Lite v2 + MACP-Lite + GIFP-Lite v2.

    Pass any pre-loaded model and tokenizer. The augmentation layer is
    model-agnostic — works with Gemma 4, Llama, Mistral, etc.

    Usage:
        agent = GodelAILite(model=model, tokenizer=tokenizer)
        response = agent.chat("My name is Alex and I am a marine biologist.")
    """

    def __init__(self, model, tokenizer, memory_path: str = None):
        self.model = model
        self.tokenizer = tokenizer
        if memory_path and os.path.exists(memory_path):
            self.memory = MemPalaceLite.load(memory_path)
        else:
            self.memory = MemPalaceLite()
        self.continuity = MACPLite()
        self.identity = GIFPLite(
            role='helpful AI assistant with persistent memory')
        self.identity.set_constraints([
            'Always be helpful and accurate',
            'Reference previous context when relevant',
            'Maintain logical consistency across turns',
            'Acknowledge uncertainty when present',
        ])

    def build_prompt(self, user_input: str) -> str:
        identity = self.identity.get_identity_prompt()
        ctx = self.memory.get_context()
        if ctx:
            return identity + '\n' + ctx + '\n\n' + user_input
        return identity + '\n' + user_input

    def _generate(self, prompt: str, max_tokens: int = 256) -> str:
        # Instruct-tuned models require chat template for correct generation
        messages = [{'role': 'user', 'content': prompt}]
        formatted = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(
            formatted, return_tensors='pt',
            truncation=True, max_length=2048)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        cfg = GenerationConfig(
            max_new_tokens=max_tokens, temperature=0.7, top_p=0.9,
            do_sample=True, pad_token_id=self.tokenizer.eos_token_id)
        with torch.no_grad():
            out = self.model.generate(**inputs, generation_config=cfg)
        return self.tokenizer.decode(
            out[0, inputs['input_ids'].shape[1]:].cpu(),
            skip_special_tokens=True).strip()

    def chat(self, user_input: str, refine: bool = False) -> str:
        self.continuity.start_chain(user_input)
        response = self._generate(self.build_prompt(user_input))
        score = self.identity.check_consistency(response)
        self.continuity.add_step(
            user_input, response, score,
            'continue' if score > 0.7 else 'refine')
        for fact in self.memory.extract_facts(response,
                                              user_input=user_input):
            self.memory.add_fact(fact)
        self.memory.add_to_history('User: ' + user_input, 'user_input')
        self.memory.add_to_history(
            'Assistant: ' + response[:200], 'assistant_output')
        self.identity.record_behavior(response)
        if refine and score < 0.5:
            refined = self._generate(
                self.build_prompt('Provide a clearer answer to: ' + user_input))
            return response + '\n\n[Refined]: ' + refined
        return response

    def save_memory(self, path: str):
        self.memory.save(path)

    def load_memory(self, path: str):
        self.memory = MemPalaceLite.load(path)

    def get_memory_state(self) -> Dict:
        return self.memory.to_dict()

    def get_reasoning_chain(self) -> str:
        return self.continuity.get_chain_summary()


class BaselineGemma:
    """
    Plain causal LM with no memory, no identity layer, no continuity.
    Used as the honest comparison baseline for GodelAI-Lite evaluation.
    """

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self._history: List[str] = []

    def chat(self, user_input: str) -> str:
        messages = [{'role': 'user', 'content': user_input}]
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(
            prompt, return_tensors='pt',
            truncation=True, max_length=2048)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        cfg = GenerationConfig(
            max_new_tokens=256, temperature=0.7, top_p=0.9,
            do_sample=True, pad_token_id=self.tokenizer.eos_token_id)
        with torch.no_grad():
            out = self.model.generate(**inputs, generation_config=cfg)
        response = self.tokenizer.decode(
            out[0, inputs['input_ids'].shape[1]:].cpu(),
            skip_special_tokens=True).strip()
        self._history.extend(
            ['User: ' + user_input, 'Assistant: ' + response])
        return response

    def reset(self):
        self._history = []
