import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List


class GIFPLite:
    """
    Generative Identity Fingerprint Protocol (Lite) v2.

    Tracks behavioural consistency across turns using TF-IDF cosine
    similarity against recent response history, with a hard penalty
    for explicit self-contradiction phrases.

    Consistency score range: 0.0 (inconsistent) to 1.0 (perfectly stable).
    """

    def __init__(self, role: str = 'helpful assistant with persistent memory'):
        self.role_definition = role
        self.constraints: List[str] = []
        self.behavior_history: List[str] = []

    def set_constraints(self, constraints: List[str]):
        self.constraints = constraints

    def get_identity_prompt(self) -> str:
        prompt = f'You are a {self.role_definition}.\n'
        if self.constraints:
            prompt += '\nBehavioural guidelines:\n'
            for c in self.constraints:
                prompt += f'- {c}\n'
        prompt += '\nMaintain consistency across all interactions.\n'
        return prompt

    def check_consistency(self, output: str) -> float:
        hard_contradictions = [
            'never mind', 'scratch that', 'i was wrong', 'i made an error'
        ]
        penalty = sum(
            0.15 for phrase in hard_contradictions
            if phrase in output.lower())

        if len(self.behavior_history) < 3:
            return max(0.2, 1.0 - penalty)

        try:
            corpus = self.behavior_history[-6:] + [output]
            vec = TfidfVectorizer(stop_words='english', max_features=300)
            tfidf = vec.fit_transform(corpus)
            sims = cosine_similarity(tfidf[-1:], tfidf[:-1])[0]
            scaled = min(1.0, float(np.mean(sims)) * 2.0 + 0.3)
            return max(0.1, scaled - penalty)
        except Exception:
            return max(0.2, 0.75 - penalty)

    def record_behavior(self, output: str):
        if output and len(output) > 10:
            self.behavior_history.append(output[:300])
        if len(self.behavior_history) > 20:
            self.behavior_history = self.behavior_history[-20:]
