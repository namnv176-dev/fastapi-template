from collections.abc import Callable


class GuardrailError(Exception):
    """
    Exception raised when a guardrail rule is violated.
    """
    pass


def check_prompt_injection(text: str) -> None:
    """
    Detection for common prompt injection attempts.
    """
    # Simple keyword-based detection
    keywords = [
        "ignore previous instructions",
        "forget everything you were told before",
        "system prompt",
        "from now on you are",
        "as a developer",
        "you are a powerful ai",
    ]
    text_lower = text.lower()
    for k in keywords:
        if k in text_lower:
            raise GuardrailError(f"Potential prompt injection detected: '{k}'")


class LLMGuardrails:
    def __init__(self) -> None:
        self._pre_hooks: list[Callable[[str], None]] = [check_prompt_injection]
        self._post_hooks: list[Callable[[str], None]] = []

    def validate_input(self, text: str) -> None:
        """
        Validate input before sending to LLM.
        """
        for hook in self._pre_hooks:
            hook(text)

    def validate_output(self, text: str) -> None:
        """
        Validate output before returning to user.
        """
        for hook in self._post_hooks:
            hook(text)


guardrails = LLMGuardrails()
