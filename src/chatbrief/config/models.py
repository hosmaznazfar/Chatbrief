from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Platform(StrEnum):
    """Supported messaging platforms."""

    TELEGRAM = "telegram"
    BALE = "bale"


@dataclass
class FilterSpec:
    """Specification for a single message filter in a filter chain."""

    class_path: str
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChannelConfig:
    """Configuration for a single messaging-platform channel."""

    id: str | int  # str for @username, int for numeric channel ID
    name: str
    lookback_hours: int | None = None  # None = use global settings.lookback_hours
    prompt_extra: str = ""  # appended to system prompt when summarizing this channel
    filters: list[FilterSpec] | None = None  # None=use global, []=explicit no-op
    group: str | None = None  # must reference digest_groups[*].name, "Other", or None


@dataclass
class DigestGroupConfig:
    """Configuration for a single digest topic group."""

    name: str
    description: str
    prompt_extra: str = ""  # appended to system prompt for channels in this group


@dataclass
class PromptsConfig:
    """Configuration for prompt template and composer."""

    base_template: str = "src/chatbrief/prompts/base_summary.txt"
    composer: str = ""  # empty = DefaultComposer; otherwise dotted class path


@dataclass
class StorageConfig:
    """Configuration for the persistent message storage backend."""

    enabled: bool = False
    backend: str = "sqlite"  # "sqlite" | "postgres"
    path: str = "data/messages.db"
    url: str = field(
        default="", repr=False
    )  # postgres only; repr=False prevents credential exposure in logs


@dataclass
class ApplicationStorageConfig:
    """Configuration for the required application-state database."""

    path: str = "data/application.db"


@dataclass
class McpConfig:
    """Configuration for the built-in MCP server."""

    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 8765
    path: str = "/mcp"


@dataclass
class Settings:  # pylint: disable=too-many-instance-attributes
    """Application settings."""

    schedule_time: str
    timezone: str
    lookback_hours: int
    openai_model: str
    openai_temperature: float
    temperature: float = 0.7
    max_tokens_per_summary: int = 1500
    use_emojis: bool = True
    include_statistics: bool = True
    target_user_id: int = 0
    auto_cleanup_old_digests: bool = True
    max_messages_per_channel: int = 500
    max_prompt_chars: int = 8000
    api_timeout: int = 30
    ai_provider: str = "openai"
    ai_model: str = ""
    ollama_base_url: str = "http://localhost:11434"
    output_language: str = "Russian"
    digest_mode: str = "channel"
    digest_groups: list[DigestGroupConfig] = field(default_factory=list)
    filters: list[FilterSpec] = field(default_factory=list)
    dedup_topics: bool = False


@dataclass
class Config:  # pylint: disable=too-many-instance-attributes
    """Complete application configuration."""

    platform: Platform
    channels: list[ChannelConfig]
    settings: Settings

    # Environment variables
    telegram_api_id: int
    telegram_api_hash: str
    telegram_bot_token: str
    openai_api_key: str
    log_level: str
    anthropic_api_key: str = ""
    storage: StorageConfig = field(default_factory=StorageConfig)
    prompts: PromptsConfig = field(default_factory=PromptsConfig)
    mcp: McpConfig = field(default_factory=McpConfig)
    application_storage: ApplicationStorageConfig = field(default_factory=ApplicationStorageConfig)
