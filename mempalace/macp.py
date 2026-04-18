from dataclasses import dataclass
from typing import List


@dataclass
class ReasoningStep:
    step_id: int
    input_context: str
    model_output: str
    confidence: float
    next_action: str


class MACPLite:
    """
    Multi-Agent Continuity Protocol (Lite).

    Maintains a structured reasoning chain across inference turns.
    Each turn records input context, model output, confidence score,
    and the recommended next action — enabling auditable continuity.
    """

    def __init__(self):
        self.reasoning_chain: List[ReasoningStep] = []
        self.current_step = 0
        self.context_buffer = ''

    def start_chain(self, initial_input: str):
        self.context_buffer = initial_input

    def add_step(self, input_ctx: str, output: str,
                 confidence: float, next_action: str):
        self.reasoning_chain.append(ReasoningStep(
            self.current_step,
            input_ctx[:200],
            output[:300],
            confidence,
            next_action,
        ))
        self.current_step += 1
        self.context_buffer = output

    def get_chain_summary(self) -> str:
        if not self.reasoning_chain:
            return 'No reasoning chain yet.'
        lines = ['[REASONING CHAIN]']
        for s in self.reasoning_chain[-5:]:
            lines.append(
                f'  Step {s.step_id} (conf={s.confidence:.2f}): '
                f'{s.model_output[:80]}...')
        return '\n'.join(lines)

    def reset(self):
        self.reasoning_chain = []
        self.current_step = 0
        self.context_buffer = ''
