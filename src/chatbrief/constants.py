"""Configuration and digest constants for Chatbrief."""

SUPPORTED_LANGUAGES = (
    "English",
    "Russian",
    "Spanish",
    "German",
    "French",
    "Persian",
)

SUPPORTED_PROVIDERS = {
    "openai",
    "ollama",
    "anthropic",
}

PROVIDER_DEFAULT_MODELS = {
    "openai": "gpt-5-nano",
    "anthropic": "claude-sonnet-4-5-20250929",
    "ollama": "llama3",
}

MAX_DIGEST_HOURS = 168  # one week; guards against a caller asking for a year of history
MAX_CHANNEL_MESSAGES = 500  # guards against a caller pulling a whole archive into the context
