import logging
from typing import List

from .constants import PROVIDER_DEFAULT_MODELS, SUPPORTED_LANGUAGES, SUPPORTED_PROVIDERS
from .models import (
    ChannelConfig,
    DigestGroupConfig,
    FilterSpec,
    McpConfig,
    PromptsConfig,
    StorageConfig,
)


def resolve_ai_settings(settings_dict: dict) -> tuple:
    """Resolve ai_provider and ai_model from settings dict.

    Returns:
        Tuple of (ai_provider, ai_model)

    Raises:
        ValueError: If ai_provider is unsupported
    """
    raw_provider = settings_dict.get("ai_provider", "openai")
    if not isinstance(raw_provider, str):
        raise ValueError(f"ai_provider must be a string, got {type(raw_provider).__name__}")
    ai_provider = raw_provider.lower()

    if ai_provider not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported ai_provider: '{ai_provider}'. "
            f"Supported providers: {', '.join(sorted(SUPPORTED_PROVIDERS))}"
        )

    default_model = PROVIDER_DEFAULT_MODELS[ai_provider]

    # ai_model takes priority; openai_model is only a fallback for the openai provider
    ai_model = settings_dict.get("ai_model") or (
        settings_dict.get("openai_model", default_model)
        if ai_provider == "openai"
        else default_model
    )

    return ai_provider, ai_model


def parse_digest_settings(
    settings_dict: dict,
) -> tuple[str, list[DigestGroupConfig], str]:
    """Parse digest_mode, digest_groups, and output_language from settings.

    Returns:
        Tuple of (digest_mode, digest_groups, output_language)
    """
    digest_mode = settings_dict.get("digest_mode", "channel")
    if digest_mode not in ("channel", "digest"):
        raise ValueError(f"Invalid digest_mode: '{digest_mode}'. Must be 'channel' or 'digest'.")

    digest_groups = []
    raw_groups = settings_dict.get("digest_groups") or []
    for i, g in enumerate(raw_groups):
        if not isinstance(g, dict) or "name" not in g or "description" not in g:
            raise ValueError(
                f"digest_groups[{i}] must be a dict with 'name' and 'description' fields"
            )
        if not isinstance(g["name"], str) or not isinstance(g["description"], str):
            raise ValueError(f"digest_groups[{i}] 'name' and 'description' must be strings")
        group_prompt_extra = g.get("prompt_extra", "")
        if not isinstance(group_prompt_extra, str):
            raise ValueError(
                f"digest_groups[{i}].prompt_extra must be a string, "
                f"got {type(group_prompt_extra).__name__}"
            )
        digest_groups.append(
            DigestGroupConfig(
                name=g["name"],
                description=g["description"],
                prompt_extra=group_prompt_extra,
            )
        )

    output_language = settings_dict.get("output_language", "Russian")
    if output_language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported output_language: '{output_language}'. "
            f"Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
        )

    if digest_mode == "digest" and not digest_groups:
        logger = logging.getLogger("telebrief")
        logger.warning(
            "digest mode enabled but no digest_groups configured — all content will go to 'Other'"
        )

    return digest_mode, digest_groups, output_language


def validate_dotted_path(value: str, label: str) -> str:
    """Validate a YAML-string dotted path (e.g. 'pkg.module.ClassName').

    Returns the stripped value. Raises ValueError if the value is not a non-empty
    string or does not parse as ≥2 dot-separated identifier segments.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string, got {value!r}")
    stripped = value.strip()
    segments = stripped.split(".")
    if len(segments) < 2 or not all(seg.isidentifier() for seg in segments):
        raise ValueError(
            f"{label} must be a dotted path (e.g. 'pkg.module.ClassName'), got {value!r}"
        )
    return stripped


def parse_filter_specs(raw_list: object, path_label: str) -> list[FilterSpec]:
    """Parse and validate a list of filter specs from YAML.

    Raises:
        ValueError: If the list or any entry has wrong type or missing required fields.
    """
    if not isinstance(raw_list, list):
        raise ValueError(f"'{path_label}' must be a list, got {type(raw_list).__name__}")
    specs: list[FilterSpec] = []
    for i, item in enumerate(raw_list):
        if not isinstance(item, dict):
            raise ValueError(f"{path_label}[{i}] must be a mapping, got {type(item).__name__}")
        if "class_path" not in item:
            raise ValueError(f"{path_label}[{i}] missing required field 'class_path'")
        class_path = validate_dotted_path(item["class_path"], f"{path_label}[{i}].class_path")
        config = item.get("config", {})
        if not isinstance(config, dict):
            raise ValueError(
                f"{path_label}[{i}].config must be a mapping, got {type(config).__name__}"
            )
        specs.append(FilterSpec(class_path=class_path, config=config))
    return specs


def validate_channel_lookback(i: int, ch: dict) -> int | None:
    lookback_hours = ch.get("lookback_hours")
    if lookback_hours is None:
        return None
    if not isinstance(lookback_hours, int) or isinstance(lookback_hours, bool):
        raise ValueError(
            f"channels[{i}].lookback_hours must be an int, got {type(lookback_hours).__name__}"
        )
    if lookback_hours <= 0:
        raise ValueError(f"channels[{i}].lookback_hours must be positive, got {lookback_hours}")
    return lookback_hours


def validate_channel_group(i: int, ch: dict) -> str | None:
    group = ch.get("group")
    if group is None:
        return None
    if not isinstance(group, str) or not group.strip():
        raise ValueError(f"channels[{i}].group must be a non-empty string or null, got {group!r}")
    return group.strip()


def validate_channel_id_name(i: int, ch: dict) -> None:
    for required in ("id", "name"):
        if required not in ch:
            raise ValueError(f"channels[{i}] missing required field '{required}'")
    if not isinstance(ch["name"], str) or not ch["name"].strip():
        raise ValueError(f"channels[{i}].name must be a non-empty string, got {ch['name']!r}")
    if not isinstance(ch["id"], (str, int)) or isinstance(ch["id"], bool):
        raise ValueError(f"channels[{i}].id must be a string or int, got {type(ch['id']).__name__}")


def parse_channel_entry(i: int, ch: object) -> ChannelConfig:
    """Parse and validate a single channel entry from YAML.

    Raises:
        ValueError: If the entry has wrong type, missing required fields, or invalid values
    """
    if not isinstance(ch, dict):
        raise ValueError(f"channels[{i}] must be a mapping, got {type(ch).__name__}")
    validate_channel_id_name(i, ch)
    lookback_hours = validate_channel_lookback(i, ch)
    prompt_extra = ch.get("prompt_extra", "")
    if not isinstance(prompt_extra, str):
        raise ValueError(
            f"channels[{i}].prompt_extra must be a string, got {type(prompt_extra).__name__}"
        )
    raw_filters = ch.get("filters")
    channel_filters: list[FilterSpec] | None = None
    if raw_filters is not None:
        channel_filters = parse_filter_specs(raw_filters, f"channels[{i}].filters")
    return ChannelConfig(
        id=ch["id"],
        name=ch["name"],
        lookback_hours=lookback_hours,
        prompt_extra=prompt_extra,
        filters=channel_filters,
        group=validate_channel_group(i, ch),
    )


def parse_storage_config(yaml_config: dict) -> StorageConfig:
    """Parse and validate the optional top-level storage: block.

    Raises:
        ValueError: If any field has wrong type or invalid value.
    """
    raw = yaml_config.get("storage")
    if raw is None:
        return StorageConfig()
    if not isinstance(raw, dict):
        raise ValueError(f"'storage' must be a mapping, got {type(raw).__name__}")

    enabled = raw.get("enabled", False)
    if not isinstance(enabled, bool):
        raise ValueError(f"storage.enabled must be a bool, got {type(enabled).__name__}")

    backend = raw.get("backend", "sqlite")
    if not isinstance(backend, str):
        raise ValueError(f"storage.backend must be a string, got {type(backend).__name__}")
    if backend not in ("sqlite", "postgres"):
        raise ValueError(f"storage.backend must be 'sqlite' or 'postgres', got {backend!r}")

    path = raw.get("path", "data/messages.db")
    if backend == "sqlite" and (not isinstance(path, str) or not path.strip()):
        raise ValueError("storage.path must be a non-empty string when backend is 'sqlite'")

    url = raw.get("url", "")
    if not isinstance(url, str):
        raise ValueError(f"storage.url must be a string, got {type(url).__name__}")
    if backend == "postgres" and enabled and not url.strip():
        raise ValueError("storage.url must be set when backend is 'postgres' and enabled is true")

    return StorageConfig(enabled=enabled, backend=backend, path=path, url=url)


def parse_mcp_config(yaml_config: dict) -> McpConfig:
    """Parse and validate the optional top-level mcp: block.

    Raises:
        ValueError: If any field has wrong type or invalid value.
    """
    raw = yaml_config.get("mcp")
    if raw is None:
        return McpConfig()
    if not isinstance(raw, dict):
        raise ValueError(f"'mcp' must be a mapping, got {type(raw).__name__}")

    enabled = raw.get("enabled", False)
    if not isinstance(enabled, bool):
        raise ValueError(f"mcp.enabled must be a bool, got {type(enabled).__name__}")

    host = raw.get("host", "127.0.0.1")
    if not isinstance(host, str) or not host.strip():
        raise ValueError("mcp.host must be a non-empty string")

    port = raw.get("port", 8765)
    if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535:
        raise ValueError(f"mcp.port must be an int in 1..65535, got {port!r}")

    path = raw.get("path", "/mcp")
    if not isinstance(path, str) or not path.startswith("/"):
        raise ValueError(f"mcp.path must be a string starting with '/', got {path!r}")

    return McpConfig(enabled=enabled, host=host.strip(), port=port, path=path)


def parse_prompts_config(yaml_config: dict) -> PromptsConfig:
    """Parse and validate the optional top-level prompts: block.

    Raises:
        ValueError: If any field has wrong type or invalid value.
    """
    raw = yaml_config.get("prompts")
    if raw is None:
        return PromptsConfig()
    if not isinstance(raw, dict):
        raise ValueError(f"'prompts' must be a mapping, got {type(raw).__name__}")

    base_template = raw.get("base_template", "src/prompts/base_summary.txt")
    if not isinstance(base_template, str) or not base_template.strip():
        raise ValueError("prompts.base_template must be a non-empty string")
    base_template = base_template.strip()

    composer = raw.get("composer", "")
    if not isinstance(composer, str):
        raise ValueError(f"prompts.composer must be a string, got {type(composer).__name__}")
    if composer.strip():
        composer = validate_dotted_path(composer, "prompts.composer")
    else:
        composer = ""

    return PromptsConfig(base_template=base_template, composer=composer)


def validate_channel_groups(
    channels: List[ChannelConfig],
    digest_groups: list[DigestGroupConfig],
    output_language: str,
) -> None:
    """Cross-validate that channels[*].group references a known group name.

    Valid values: any digest_groups[*].name, the literal "Other", or the
    localized group_other string for the current output_language.

    Raises:
        ValueError: listing all channels with invalid group references.
    """
    from src.ui_strings import get_ui_strings

    ui = get_ui_strings(output_language)
    localized_other = ui.get("group_other", "Other")
    valid_names = {g.name for g in digest_groups} | {"Other", localized_other}

    bad: list[str] = []
    for ch in channels:
        if ch.group is not None and ch.group not in valid_names:
            bad.append(f"channel {ch.name!r}: group {ch.group!r}")

    if bad:
        raise ValueError(
            "Unknown group references in channels config:\n"
            + "\n".join(f"  {b}" for b in bad)
            + f"\nValid groups: {', '.join(sorted(valid_names))}"
        )


def parse_channels(yaml_config: dict) -> List[ChannelConfig]:
    """Parse and validate channel configs from YAML.

    Raises:
        ValueError: If channels list is empty, entries are invalid, or names are duplicated
    """
    if not isinstance(yaml_config, dict):
        raise ValueError(
            f"config.yaml must contain a top-level mapping, got {type(yaml_config).__name__}"
        )
    channels_value = yaml_config.get("channels", [])
    if not isinstance(channels_value, list):
        raise ValueError(
            f"config.yaml field 'channels' must be a list, got {type(channels_value).__name__}"
        )
    channels = [parse_channel_entry(i, ch) for i, ch in enumerate(channels_value)]

    if not channels:
        raise ValueError("No channels configured in config.yaml")

    seen: set[str] = set()
    duplicates: set[str] = set()
    for c in channels:
        if c.name in seen:
            duplicates.add(c.name)
        seen.add(c.name)
    if duplicates:
        raise ValueError(f"Duplicate channel names in config.yaml: {', '.join(sorted(duplicates))}")

    return channels
