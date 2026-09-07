"""
Configuration loader for Telebrief.
Loads settings from config.yaml and environment variables.
"""

import os

import yaml
from dotenv import load_dotenv

from .models import Config, Settings
from .validation import (
    parse_channels,
    parse_digest_settings,
    parse_filter_specs,
    parse_mcp_config,
    parse_prompts_config,
    parse_storage_config,
    resolve_ai_settings,
    validate_channel_groups,
)


def _load_and_validate_env_vars(ai_provider: str) -> dict:
    """Load and validate required environment variables.

    Returns:
        Dict with keys matching Config env var fields.
    """
    telegram_api_id = os.getenv("TELEGRAM_API_ID")
    telegram_api_hash = os.getenv("TELEGRAM_API_HASH")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
    log_level = os.getenv("LOG_LEVEL", "INFO")

    missing_vars = []
    if not telegram_api_id:
        missing_vars.append("TELEGRAM_API_ID")
    if not telegram_api_hash:
        missing_vars.append("TELEGRAM_API_HASH")
    if not telegram_bot_token:
        missing_vars.append("TELEGRAM_BOT_TOKEN")

    if ai_provider == "openai" and not openai_api_key:
        missing_vars.append("OPENAI_API_KEY")
    elif ai_provider == "anthropic" and not anthropic_api_key:
        missing_vars.append("ANTHROPIC_API_KEY")

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please set them in .env file (see .env.example)"
        )

    telegram_api_id = os.environ["TELEGRAM_API_ID"]
    telegram_api_hash = os.environ["TELEGRAM_API_HASH"]
    telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]

    return {
        "telegram_api_id": int(telegram_api_id),
        "telegram_api_hash": telegram_api_hash,
        "telegram_bot_token": telegram_bot_token,
        "openai_api_key": openai_api_key,
        "anthropic_api_key": anthropic_api_key,
        "log_level": log_level,
    }


def load_config(config_path: str = "config.yaml") -> Config:
    """
    Load configuration from YAML file and environment variables.

    Args:
        config_path: Path to config.yaml file

    Returns:
        Config object with all settings

    Raises:
        FileNotFoundError: If config.yaml not found
        ValueError: If required environment variables missing
    """
    # Load environment variables from .env file
    load_dotenv()

    # Load YAML configuration
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        yaml_config = yaml.safe_load(f)

    # Parse channels
    channels = parse_channels(yaml_config)

    # Parse storage config
    storage_config = parse_storage_config(yaml_config)

    # Parse prompts config
    prompts_config = parse_prompts_config(yaml_config)

    # Parse MCP server config
    mcp_config = parse_mcp_config(yaml_config)

    # Parse settings
    settings_dict = yaml_config.get("settings", {})
    ai_provider, ai_model = resolve_ai_settings(settings_dict)
    digest_mode, digest_groups, output_language = parse_digest_settings(settings_dict)
    raw_global_filters = settings_dict.get("filters")
    global_filters = parse_filter_specs(
        raw_global_filters if raw_global_filters is not None else [],
        "settings.filters",
    )

    settings = Settings(
        schedule_time=settings_dict.get("schedule_time", "08:00"),
        timezone=settings_dict.get("timezone", "UTC"),
        lookback_hours=settings_dict.get("lookback_hours", 24),
        openai_model=settings_dict.get("openai_model", "gpt-5-nano"),
        openai_temperature=settings_dict.get("openai_temperature", 0.7),
        temperature=settings_dict.get("temperature", settings_dict.get("openai_temperature", 0.7)),
        max_tokens_per_summary=settings_dict.get("max_tokens_per_summary", 1500),
        use_emojis=settings_dict.get("use_emojis", True),
        include_statistics=settings_dict.get("include_statistics", True),
        target_user_id=settings_dict.get("target_user_id", 0),
        auto_cleanup_old_digests=settings_dict.get("auto_cleanup_old_digests", True),
        max_messages_per_channel=settings_dict.get("max_messages_per_channel", 500),
        max_prompt_chars=settings_dict.get("max_prompt_chars", 8000),
        api_timeout=int(settings_dict.get("api_timeout", 30)),
        ai_provider=ai_provider,
        ai_model=ai_model,
        ollama_base_url=settings_dict.get("ollama_base_url", "http://localhost:11434"),
        output_language=output_language,
        digest_mode=digest_mode,
        digest_groups=digest_groups,
        filters=global_filters,
        dedup_topics=bool(settings_dict.get("dedup_topics", False)),
    )

    if settings.target_user_id == 0:
        raise ValueError(
            "target_user_id not configured in config.yaml. "
            "Get your Telegram user ID from @userinfobot"
        )

    # Cross-validate channel group references against known digest_groups
    validate_channel_groups(channels, digest_groups, output_language)

    env_vars = _load_and_validate_env_vars(ai_provider)

    return Config(
        channels=channels,
        settings=settings,
        storage=storage_config,
        prompts=prompts_config,
        mcp=mcp_config,
        **env_vars,
    )


if __name__ == "__main__":
    # Test configuration loading
    try:
        config = load_config()
        print("✅ Configuration loaded successfully!")
        print(f"Channels: {len(config.channels)}")
        print(f"Target user: {config.settings.target_user_id}")
        print(f"AI provider: {config.settings.ai_provider}, model: {config.settings.ai_model}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
