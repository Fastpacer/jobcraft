from enum import Enum


class GroqReasoningModels(str, Enum):
    LLAMA3_8B = "llama-3.1-8b-instant"
    LLAMA3_70B = "llama-3.3-70b-versatile"
    MIXTRAL_8X7B = "mixtral-8x7b-32768"


class GroqGuardModels(str, Enum):
    LLAMA_GUARD_4_12B = "meta-llama/llama-guard-4-12b"
    PROMPT_GUARD_2_22M = "meta-llama/llama-prompt-guard-2-22m"
    PROMPT_GUARD_2_86M = "meta-llama/llama-prompt-guard-2-86m"