import json
import math
import re
from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class MemoryEntry:
    content: str
    timestamp: int
    relevance_score: float = 1.0
    category: str = 'general'


class MemPalaceLite:
    """
    Structured external memory for SLMs.

    Stores episodic history and extracted key facts with temporal decay,
    deduplication, and JSON persistence. Works with any language model —
    pass the model's output and user input; MemPalace handles the rest.

    Decay formula: relevance * exp(-decay_rate * age_in_steps)
    """

    def __init__(self, max_history: int = 10, max_facts: int = 20,
                 decay_rate: float = 0.05):
        self.history: List[MemoryEntry] = []
        self.key_facts: List[MemoryEntry] = []
        self.patterns: List[str] = []
        self.max_history = max_history
        self.max_facts = max_facts
        self.decay_rate = decay_rate
        self.step_counter = 0

    # ------------------------------------------------------------------
    # Core memory operations
    # ------------------------------------------------------------------

    def _decayed_relevance(self, entry: MemoryEntry) -> float:
        age = self.step_counter - entry.timestamp
        return entry.relevance_score * math.exp(-self.decay_rate * age)

    def add_to_history(self, interaction: str, category: str = 'interaction'):
        self.step_counter += 1
        self.history.append(
            MemoryEntry(interaction, self.step_counter, category=category))
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def add_fact(self, fact: str, relevance: float = 1.0):
        fact = fact.strip()
        if not fact or len(fact) < 8:
            return
        for e in self.key_facts:
            if (fact.lower()[:40] in e.content.lower() or
                    e.content.lower()[:40] in fact.lower()):
                return
        self.key_facts.append(
            MemoryEntry(fact, self.step_counter,
                        relevance_score=relevance, category='fact'))
        if len(self.key_facts) > self.max_facts:
            self.key_facts.sort(key=self._decayed_relevance, reverse=True)
            self.key_facts = self.key_facts[:self.max_facts]

    def add_pattern(self, pattern: str):
        if pattern and pattern not in self.patterns:
            self.patterns.append(pattern)

    # ------------------------------------------------------------------
    # Context assembly
    # ------------------------------------------------------------------

    def get_context(self, top_facts: int = 5, top_history: int = 3) -> str:
        parts = []
        if self.key_facts:
            sorted_facts = sorted(
                self.key_facts, key=self._decayed_relevance, reverse=True)
            facts_text = '\n'.join(
                f'  * {f.content}' for f in sorted_facts[:top_facts])
            parts.append(f'[REMEMBERED FACTS]\n{facts_text}')
        if self.history:
            hist_text = '\n'.join(
                f'  {h.content}' for h in self.history[-top_history:])
            parts.append(f'[RECENT CONVERSATION]\n{hist_text}')
        if self.patterns:
            pat_text = '\n'.join(f'  -> {p}' for p in self.patterns[-2:])
            parts.append(f'[REASONING PATTERNS]\n{pat_text}')
        return '\n\n'.join(parts)

    # ------------------------------------------------------------------
    # Fact extraction
    # ------------------------------------------------------------------

    def extract_facts(self, text: str, user_input: str = '') -> List[str]:
        """
        Extract factual sentences from user_input + model text.

        user_input is combined with text so injected personal facts
        ("My name is Jordan") are captured. Question sentences are
        filtered by first-word check to avoid storing distractors.

        Secondary extraction is restricted to user_input only to prevent
        noisy model narration from polluting the fact store.
        """
        QUESTION_STARTERS = (
            'what', 'where', 'when', 'who', 'how', 'why', 'is', 'are',
            'do', 'does', 'did', 'can', 'will', 'could', 'would', 'should'
        )
        PATTERNS = [
            r'my name is ([\w ]+)',
            r'i am (?:a |an )?([\w ]+)',
            r'i work (?:as|at|for) ([\w ]+)',
            r"i(?:'m| am) (?:currently )?(?:studying|working on|researching|building) ([\w ]+)",
            r'i (?:live|am based) (?:in|at) ([\w ,]+)',
        ]

        def _non_question_sentences(src: str) -> List[str]:
            out = []
            for s in re.split(r'[.!?]', src):
                s = s.strip()
                if not s:
                    continue
                first = s.lower().split()[0] if s.split() else ''
                if first not in QUESTION_STARTERS:
                    out.append(s)
            return out

        combined = (user_input + ' ' + text).strip()
        combined_sentences = _non_question_sentences(combined)
        user_sentences = _non_question_sentences(user_input)

        facts = []

        # Primary: regex patterns on combined sentences
        for sent in combined_sentences:
            for p in PATTERNS:
                if re.search(p, sent.lower()) and 8 < len(sent) < 200:
                    facts.append(sent[:200])
                    break

        # Secondary: general facts — user_input sentences only (not model output)
        if len(facts) < 3:
            for sent in user_sentences:
                if 20 < len(sent) < 150:
                    if any(kw in sent.lower()
                           for kw in [' is ', ' are ', ' was ',
                                      'capital', 'located', 'known for']):
                        if sent not in facts:
                            facts.append(sent[:150])

        # Deduplicate
        seen, unique = set(), []
        for f in facts:
            k = f.lower()[:30]
            if k not in seen:
                seen.add(k)
                unique.append(f)
        return unique[:4]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str):
        data = {
            'history': [asdict(h) for h in self.history],
            'key_facts': [asdict(f) for f in self.key_facts],
            'patterns': self.patterns,
            'step_counter': self.step_counter,
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f'Memory saved -> {path}  '
              f'({len(self.key_facts)} facts, {len(self.history)} history)')

    @classmethod
    def load(cls, path: str, **kwargs) -> 'MemPalaceLite':
        inst = cls(**kwargs)
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        inst.history = [MemoryEntry(**h) for h in data['history']]
        inst.key_facts = [MemoryEntry(**f) for f in data['key_facts']]
        inst.patterns = data['patterns']
        inst.step_counter = data.get('step_counter', 0)
        print(f'Memory loaded <- {path}  '
              f'({len(inst.key_facts)} facts, {len(inst.history)} history)')
        return inst

    def to_dict(self) -> Dict:
        return {
            'history': [asdict(h) for h in self.history],
            'key_facts': [asdict(f) for f in self.key_facts],
            'patterns': self.patterns,
        }
