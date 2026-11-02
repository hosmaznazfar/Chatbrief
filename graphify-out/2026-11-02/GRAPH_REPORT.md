# Graph Report - ChatBrief  (2026-11-02)

## Corpus Check
- 99 files · ~105,937 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 8, .example 2, .toml 1)

## Summary
- 2271 nodes · 5071 edges · 122 communities (83 shown, 39 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 1034 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e45032fa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SQLiteBackend
- test_filters.py
- config/models.py
- capture
- test_utils.py
- unit
- load_config
- test_summarizer.py
- test_scheduler.py
- with
- test_digest.py
- pytest
- test_telegram.py
- DigestGroupConfig
- test_mcp_server.py
- validation.py
- CommandService
- Config
- with
- AsyncContextManager
- Summarizer
- _make_command_service
- DefaultComposer
- asyncio
- ._summarize_channel
- unit
- escape_xml_delimiters
- ._extract_bullets_from_channel
- _make_command_service
- MessageSource
- test_ui_strings.py
- telebrief
- _quality_gate_filter
- ._build_group_definitions
- TelegramMessageSource
- ._enforce_length_limit
- attributes
- CommandResult
- feature_request.yml
- ._classify_bullets
- test_telegram_bot.py
- _load_base_template
- _dedup_extracted
- TelegramMessageSender
- ai_providers.py
- load_class
- test_config.py
- unit
- OllamaProvider
- test_format_group_summary_message_russian
- Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader
- Contributing to Telebrief
- Message
- ._create_header
- test_grouper.py
- .create_digest
- hooks
- AGENTS.md
- TelegramBot
- test_format_channel_message_includes_channel_link
- test_mcp_config_rejects_invalid
- .group_summaries
- TestBuildGroupDefinitions
- ._create_channel_section
- current.md
- README.md
- Personal data export — detailed approved design
- 📊 Example Output
- ChannelConfig
- contact_links
- ⚙️ Per-Channel Configuration
- english_config
- english_config
- Decisions
- Chatbrief-side image limits before provider upload — approved
- Delivery status and diagnostics command — approved
- 🔗 MCP Server
- Telegram Hybrid Ingestion and Multi-User Support
- test_redact_url_no_credentials
- test_load_config_no_channels
- Chatbrief — current project handover
- test_formatter.py
- Chatbrief — AI-assisted development workflow
- Implementation sequence
- create_session.sh script
- test_load_config_invalid_digest_mode
- test_load_config_invalid_output_language
- Phase 1 export persistence migration proposal — pending approval
- Contributor Covenant Code of Conduct
- test_load_config_unsupported_provider
- test_load_config_invalid_target_user
- Chatbrief — AI development guide
- Export JSON root shape — approved (Option A)
- ._create_statistics
- Chatbrief — persistent project context
- Export schema: top-level document and section shapes — recommended defaults
- Export schema: shared metadata, references, timestamps, and ordering — recommended defaults
- Graphify — local CLI and Git-shared code graph
- Export report v1 semantics and media-only message handling — recommended defaults
- test_formatter_without_emojis
- Chatbrief implementation checklist
- Digest scheduling, incremental windows, and one-time requests
- test_formatter_initialization
- Pull Request
- Security Policy
- chatbrief
- test_format_group_message_no_truncation
- Chatbrief-side image limits before provider upload — approved
- 🗄️ Persistent Storage

## God Nodes (most connected - your core abstractions)
1. `load_config()` - 95 edges
2. `Current status — 2026-11-02 (authoritative update)` - 79 edges
3. `Message` - 65 edges
4. `Summarizer` - 64 edges
5. `Config` - 58 edges
6. `TelegramBot` - 58 edges
7. `TelegramMessageSender` - 55 edges
8. `ChannelConfig` - 53 edges
9. `DigestFormatter` - 53 edges
10. `MessageSource` - 44 edges

## Surprising Connections (you probably didn't know these)
- `Negative / Risks` --references--> `ChannelConfig`  [INFERRED]
  docs/adr/0001-extensibility-architecture.md → src/chatbrief/config/models.py
- `Config schema additions (all optional)` --references--> `ChannelConfig`  [INFERRED]
  docs/plans/completed/20260430-extensibility-architecture.md → src/chatbrief/config/models.py
- `Task 1: ADR document` --references--> `ChannelConfig`  [INFERRED]
  docs/plans/completed/20260430-extensibility-architecture.md → src/chatbrief/config/models.py
- `5. Separate chat access, subscriptions, and digest organization` --references--> `DigestGroupConfig`  [INFERRED]
  docs/plans/telegram-hybrid-ingestion.md → src/chatbrief/config/models.py
- `Migration proposal — design direction, not an approved schema` --references--> `Config`  [INFERRED]
  docs/plans/telegram-hybrid-ingestion.md → src/chatbrief/config/models.py

## Import Cycles
- None detected.

## Communities (122 total, 39 thin omitted)

### Community 0 - "SQLiteBackend"
Cohesion: 0.07
Nodes (30): Phase 1 export persistence migration proposal — approved for implementation, Context (from discovery), Task 10: Extend StorageBackend Protocol, Context (from discovery), Development Approach, Implementation Steps, Overview, Post-Completion (+22 more)

### Community 1 - "test_filters.py"
Cohesion: 0.25
Nodes (20): MinLengthFilter, _channel(), _make_message(), test_keyword_empty_input(), test_keyword_exclude_removes_message(), test_keyword_include_and_exclude(), test_keyword_include_case_insensitive(), test_keyword_include_match() (+12 more)

### Community 2 - "config/models.py"
Cohesion: 0.05
Nodes (10): create_session(), CommandServiceProtocol, _load_and_validate_env_vars(), parse_digest_settings(), main(), main(), get_month_names(), get_ui_strings() (+2 more)

### Community 3 - "capture"
Cohesion: 0.10
Nodes (8): test_channel_without_group_uses_base_and_channel_prompt_extra(), test_language_instruction_only_in_system_prompt(), test_summarize_channel_applies_prompt_extra(), test_summarize_channel_includes_truncation_note(), test_summarize_channel_prompt_instructs_two_tier_format(), capture(), test_summarize_channel_unknown_channel_uses_default_prompt(), test_summarize_channel_wraps_messages_in_xml_delimiters()

### Community 4 - "test_utils.py"
Cohesion: 0.09
Nodes (16): clear_digest_message_ids(), get_digest_message_ids(), split_message(), test_clear_digest_message_ids(), test_clear_digest_message_ids_no_file(), test_get_digest_message_ids_invalid_json(), test_get_digest_message_ids_no_file(), test_get_lookback_time() (+8 more)

### Community 5 - "unit"
Cohesion: 0.16
Nodes (6): test_handle_help_unauthorized(), test_handle_help_uses_output_language(), test_handle_help_without_message(), test_handle_help_without_user(), test_help_not_rate_limited(), test_setup_application()

### Community 6 - "load_config"
Cohesion: 0.07
Nodes (30): load_config(), test_channel_group_field_parsed(), test_channel_group_none_by_default(), test_channel_group_null_yaml_is_none(), test_channel_group_other_accepted(), test_digest_group_config_equality_with_prompt_extra(), test_digest_group_prompt_extra_defaults_empty(), test_digest_group_prompt_extra_parsed() (+22 more)

### Community 7 - "test_summarizer.py"
Cohesion: 0.07
Nodes (15): _make_messages(), test_default_template_path_points_to_existing_file(), test_format_messages_for_prompt(), test_format_messages_includes_link(), test_format_messages_prompt_always_includes_at_least_one(), test_format_messages_prompt_no_truncation_within_budget(), test_format_messages_prompt_truncation_keeps_recent(), test_format_messages_prompt_warns_on_truncation() (+7 more)

### Community 8 - "test_scheduler.py"
Cohesion: 0.10
Nodes (24): Running Tests and Checks, Testing conventions, mock_env_vars(), mock_logger(), sample_config(), sample_messages(), temp_config_file(), make_scheduler() (+16 more)

### Community 9 - "with"
Cohesion: 0.06
Nodes (41): name, needs, runs-on, steps, jobs, build, lint, security (+33 more)

### Community 10 - "test_digest.py"
Cohesion: 0.07
Nodes (47): ADR 0002: Stored Message History Is Not Proof of Collection Completeness, Consequences, Context, Decision, Task 5: Filter chain wiring in core, FilterSpec, _apply_filters(), collect_channel_messages() (+39 more)

### Community 11 - "pytest"
Cohesion: 0.07
Nodes (19): test_channel_unknown_group_error_lists_bad_channel(), test_channel_unknown_group_raises(), test_digest_group_prompt_extra_non_string_raises(), test_filter_spec_channel_invalid_class_path_raises(), test_filter_spec_missing_class_path_raises(), test_filter_spec_non_dict_config_raises(), test_filter_spec_non_mapping_item_raises(), test_filter_spec_non_string_class_path_raises() (+11 more)

### Community 12 - "test_telegram.py"
Cohesion: 0.10
Nodes (38): make_source(), test_connect_dialog_cache_failure(), test_connect_missing_session(), test_connect_success(), test_connect_unauthorized(), test_disconnect(), test_fetch_channel_messages_error(), test_fetch_channel_messages_private_entity() (+30 more)

### Community 13 - "DigestGroupConfig"
Cohesion: 0.12
Nodes (10): Phase 3 — Prompt Composer + Group Binding, Task 6: Extract base prompt template, Task 7: PromptComposer Protocol + DefaultComposer, Task 8: Group binding in config, Task 9: Wire composer into Summarizer, DigestGroupConfig, validate_channel_groups(), PromptComposer (+2 more)

### Community 14 - "test_mcp_server.py"
Cohesion: 0.09
Nodes (17): message_source(), server(), test_get_channel_messages_defaults(), test_get_channel_messages_renders_messages(), test_get_channel_messages_reports_empty_result(), test_get_channel_messages_surfaces_unknown_channel(), test_get_digest_defaults_to_24_hours(), test_get_digest_rejects_out_of_range_hours() (+9 more)

### Community 15 - "validation.py"
Cohesion: 0.08
Nodes (19): McpConfig, Platform, PromptsConfig, parse_channel_entry(), parse_channels(), parse_filter_specs(), parse_mcp_config(), parse_platform() (+11 more)

### Community 16 - "CommandService"
Cohesion: 0.11
Nodes (15): english_config(), _make_command_service(), test_cleanup_failure(), test_cleanup_rate_limited(), test_cleanup_success(), test_digest_exception(), test_digest_failure(), test_digest_rate_limited() (+7 more)

### Community 17 - "Config"
Cohesion: 0.05
Nodes (23): Tools, Config, _build_channel_parts(), build_digest_parts(), _build_grouped_parts(), _filter_valid_summaries(), _format_group_messages(), _get_channel_urls() (+15 more)

### Community 18 - "with"
Cohesion: 0.07
Nodes (29): name, permissions, runs-on, steps, env, IMAGE_NAME, REGISTRY, jobs (+21 more)

### Community 19 - "AsyncContextManager"
Cohesion: 0.14
Nodes (11): AnthropicProvider, test_anthropic_provider_accepts_reasoning_effort_param(), test_anthropic_provider_chat_completion(), test_anthropic_provider_empty_content_array_raises(), test_anthropic_provider_error(), test_anthropic_provider_error_body_truncated(), test_anthropic_provider_logs_response_metadata(), test_anthropic_provider_max_tokens_empty_content_raises_with_guidance() (+3 more)

### Community 20 - "Summarizer"
Cohesion: 0.11
Nodes (8): Summarizer, test_summarize_all_empty(), test_summarize_all_partial_failure(), test_summarize_all_success(), test_summarizer_custom_output_language(), test_truncate_at_sentence_boundary_hard_truncates_without_punctuation(), test_truncate_at_sentence_boundary_returns_short_text(), test_truncate_at_sentence_boundary_uses_last_sentence()

### Community 21 - "_make_command_service"
Cohesion: 0.14
Nodes (10): _make_update(), test_cleanup_rate_limited(), test_handle_cleanup_exception(), test_handle_cleanup_failure(), test_handle_cleanup_messages_use_output_language(), test_handle_cleanup_rate_limited(), test_handle_cleanup_unauthorized(), test_handle_cleanup_without_message() (+2 more)

### Community 22 - "DefaultComposer"
Cohesion: 0.19
Nodes (18): 🔌 Extensibility, Group binding, Prompts, Storage queries, DefaultComposer, _channel(), _group(), test_base_only_no_group_no_channel_extra() (+10 more)

### Community 23 - "asyncio"
Cohesion: 0.12
Nodes (12): OpenAIProvider, test_openai_provider_chat_completion(), test_openai_provider_empty_string_content_raises(), test_openai_provider_falls_back_to_max_tokens_without_reasoning_effort(), test_openai_provider_falls_back_when_reasoning_effort_rejected(), test_openai_provider_length_empty_content_raises_with_guidance(), test_openai_provider_length_with_content_returns_truncated(), test_openai_provider_logs_response_metadata() (+4 more)

### Community 24 - "._summarize_channel"
Cohesion: 0.07
Nodes (14): test_summarize_channel_detects_output_over_3500_chars(), test_summarize_channel_double_budget_exhaustion_propagates(), test_summarize_channel_error(), test_summarize_channel_length_retry_exception_falls_through_to_truncation(), test_summarize_channel_no_retry_on_success(), test_summarize_channel_no_retry_when_under_limit(), test_summarize_channel_passes_max_prompt_chars_to_formatter(), test_summarize_channel_retries_on_token_budget_exhausted() (+6 more)

### Community 25 - "unit"
Cohesion: 0.08
Nodes (13): create_provider(), test_create_provider_anthropic(), test_create_provider_anthropic_missing_key(), test_create_provider_case_insensitive(), test_create_provider_ollama(), test_create_provider_openai(), test_create_provider_openai_missing_key(), test_create_provider_unknown() (+5 more)

### Community 26 - "escape_xml_delimiters"
Cohesion: 0.05
Nodes (7): _strip_channel_summary_noise(), escape_xml_delimiters(), TestPromptInjectionMitigation, TestStripBroaderNoise, TestStripChannelHeader, TestStripSectionTwo, TestEscapeXmlDelimiters

### Community 27 - "._extract_bullets_from_channel"
Cohesion: 0.12
Nodes (3): _run(), TestExtractAllBullets, TestExtractBulletsFromChannel

### Community 28 - "_make_command_service"
Cohesion: 0.15
Nodes (7): _make_command_service(), test_handle_status_displays_command_service_result(), test_handle_status_unauthorized(), test_handle_status_uses_output_language(), test_handle_status_without_message(), test_handle_status_without_user(), test_status_not_rate_limited()

### Community 29 - "MessageSource"
Cohesion: 0.05
Nodes (20): Architecture guardrails, Current implementation status, Architectural decisions to preserve, Current refactor status (2026-10-30), Chatbrief-specific guardrails, Current architecture, Package/platform refactor status, Current lifecycle and boundaries (+12 more)

### Community 31 - "test_ui_strings.py"
Cohesion: 0.15
Nodes (8): test_all_required_keys_present_for_each_language(), test_digest_group_keys_english_values(), test_digest_group_keys_present_for_each_language(), test_get_ui_strings_english(), test_get_ui_strings_returns_dict(), test_get_ui_strings_russian(), test_get_ui_strings_unknown_language_falls_back_to_english(), test_no_empty_strings_for_any_language()

### Community 32 - "telebrief"
Cohesion: 0.10
Nodes (20): build, container_name, env_file, environment, healthcheck, image, logging, restart (+12 more)

### Community 33 - "_quality_gate_filter"
Cohesion: 0.15
Nodes (4): ExtractedBullet, _qg_has_concrete_entity(), _quality_gate_filter(), TestQualityGateFilter

### Community 35 - "TelegramMessageSource"
Cohesion: 0.15
Nodes (8): async_messages(), message_source(), test_fetch_channel_messages_empty_without_media(), test_fetch_channel_messages_media_only(), test_fetch_channel_messages_sorts_messages(), test_fetch_channel_messages_stops_at_lookback(), test_fetch_channel_messages_text(), test_fetch_messages_success()

### Community 36 - "._enforce_length_limit"
Cohesion: 0.20
Nodes (3): test_enforce_length_limit_minor_overage_truncates_at_sentence_boundary(), test_enforce_length_limit_retry_failure_keeps_original_summary(), test_enforce_length_limit_retry_returns_short_summary()

### Community 37 - "attributes"
Cohesion: 0.12
Nodes (16): description, label, options, placeholder, render, value, body, attributes (+8 more)

### Community 40 - "feature_request.yml"
Cohesion: 0.12
Nodes (15): description, label, options, placeholder, body, attributes, id, type (+7 more)

### Community 42 - "test_telegram_bot.py"
Cohesion: 0.12
Nodes (8): CommandStatus, test_handle_digest_error_message_uses_output_language(), test_handle_digest_exception(), test_handle_digest_processing_message_uses_output_language(), test_handle_digest_rate_limited(), test_handle_digest_success_message_uses_output_language(), test_handle_digest_unauthorized(), test_rate_limit_message_uses_configured_language()

### Community 43 - "_load_base_template"
Cohesion: 0.12
Nodes (8): __getattr__(), _load_base_template(), _ProviderSettings, test_load_base_template_contains_language_placeholder(), test_load_base_template_custom_path(), test_load_base_template_default_path_returns_nonempty(), test_load_base_template_missing_file_raises(), test_system_prompt_template_loaded_from_file()

### Community 44 - "_dedup_extracted"
Cohesion: 0.15
Nodes (3): _dedup_extracted(), _normalize_point(), TestDedupExtracted

### Community 45 - "TelegramMessageSender"
Cohesion: 0.05
Nodes (37): TelegramMessageSender, save_digest_message_ids(), test_cleanup_old_digests_default_user_id(), test_cleanup_old_digests_deletion_failure(), test_cleanup_old_digests_message_not_found(), test_cleanup_old_digests_no_messages(), test_cleanup_old_digests_partial_failure(), test_cleanup_old_digests_success() (+29 more)

### Community 47 - "load_class"
Cohesion: 0.24
Nodes (9): load_class(), test_load_class_function_not_class(), test_load_class_missing_attribute(), test_load_class_missing_module(), test_load_class_no_dot_raises(), test_load_class_non_class_attribute(), test_load_class_returns_type(), test_load_class_stdlib_class() (+1 more)

### Community 48 - "test_config.py"
Cohesion: 0.16
Nodes (16): _storage_config_file(), test_channel_group_localized_other_accepted(), test_filter_spec_channel_null_uses_global(), test_filter_spec_defaults_to_empty_global(), test_prompts_config_explicit_values(), test_prompts_config_missing_block_defaults(), test_storage_config_empty_path_raises(), test_storage_config_enabled_not_bool_raises() (+8 more)

### Community 49 - "unit"
Cohesion: 0.13
Nodes (7): test_format_channel_message_stats_uses_output_language(), test_format_date_english_month_names(), test_format_group_message_output(), test_pick_emoji_crypto(), test_pick_emoji_default(), test_pick_emoji_tech(), test_truncation_message_uses_output_language()

### Community 50 - "OllamaProvider"
Cohesion: 0.11
Nodes (13): OllamaProvider, _redact_url(), AsyncContextManager, test_ollama_provider_accepts_reasoning_effort_param(), test_ollama_provider_chat_completion(), test_ollama_provider_debug_logging(), test_ollama_provider_empty_content_raises(), test_ollama_provider_error() (+5 more)

### Community 52 - "Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader"
Cohesion: 0.09
Nodes (21): Config schema additions (all optional), Development Approach, Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader, Filter chain insertion point, Implementation Steps, Overview, Phase 1 — Skeleton + ADR + Plugin Loader, Phase 4 — Storage Read API (+13 more)

### Community 53 - "Contributing to Telebrief"
Cohesion: 0.22
Nodes (9): Code of Conduct, Code Style, Commit Messages, Contributing to Telebrief, Development Setup, Pull Request Process, Questions, Reporting Bugs (+1 more)

### Community 55 - "Message"
Cohesion: 0.11
Nodes (18): ADR 0001: Extensibility Architecture — Filters, Prompts, Storage Read API, Plugin Loader, Alternatives Rejected, Consequences, Context, Decision, Migration, Negative / Risks, Option B: Subclass Extension (+10 more)

### Community 56 - "._create_header"
Cohesion: 0.25
Nodes (3): test_create_header(), test_create_header_russian_month_name(), test_create_header_uses_output_language()

### Community 58 - "test_grouper.py"
Cohesion: 0.11
Nodes (6): config_with_groups(), config_with_other_group(), grouper(), grouper_english(), TestFallbackGroup, TestGrouperTemperatureOverride

### Community 59 - ".create_digest"
Cohesion: 0.25
Nodes (3): test_create_digest(), test_formatter_without_stats(), test_overview_section_label_uses_output_language()

### Community 60 - "hooks"
Cohesion: 0.18
Nodes (10): exclude, additional_dependencies, args, exclude, files, id, repos, hooks (+2 more)

### Community 63 - "TelegramBot"
Cohesion: 0.11
Nodes (10): TelegramBot, test_handle_digest_without_message(), test_run_application_initialization_failure(), test_run_without_application(), test_setup_bot_menu_exception(), test_setup_bot_menu_uses_output_language(), test_setup_bot_menu_without_application(), test_stop_running_application() (+2 more)

### Community 65 - "test_mcp_config_rejects_invalid"
Cohesion: 0.20
Nodes (6): _mcp_config_file(), test_filter_spec_invalid_dotted_path_raises(), test_mcp_config_explicit(), test_mcp_config_missing_block_defaults(), test_mcp_config_rejects_invalid(), test_prompts_composer_invalid_dotted_path_raises()

### Community 70 - "README.md"
Cohesion: 0.09
Nodes (17): Chatbrief — new chat starter, Complete the report and visualization, How ChatGPT uses the graph from GitHub, If the hook produced a new graph diff, review and commit it., Official references, pj graph command reference, AI-assisted development workflow, 🤖 Bot Commands (+9 more)

### Community 71 - "Personal data export — detailed approved design"
Cohesion: 0.08
Nodes (24): Archive structure, Automatic Telegram delivery retry limits, Cancellation and cleanup, Configurable worker concurrency, Database-backed worker claims and leases, Explicit recovery from ambiguous delivery, Export behavior on account deletion, Export invalidation when included source data is removed — approved (Option A) (+16 more)

### Community 72 - "📊 Example Output"
Cohesion: 0.50
Nodes (4): Channel mode (`digest_mode: "channel"` — default), `dedup_topics` — cross-channel deduplication, 📊 Example Output, Topic mode (`digest_mode: "digest"`)

### Community 73 - "ChannelConfig"
Cohesion: 0.15
Nodes (12): Export schema v1 message/source/media defaults — working recommendations, Phase 2 — Filter Protocol + Chain, Task 3: MessageFilter Protocol + builtins, Task 4: FilterConfig parsing, Archive purpose, Export schema v1 message, source, media, and portability defaults — working recommendations, Media filenames and metadata, Message records (+4 more)

### Community 74 - "contact_links"
Cohesion: 0.33
Nodes (5): blank_issues_enabled, contact_links, about, name, url

### Community 75 - "⚙️ Per-Channel Configuration"
Cohesion: 0.67
Nodes (3): `lookback_hours` — per-channel lookback window, ⚙️ Per-Channel Configuration, `prompt_extra` — per-channel AI instructions

### Community 79 - "Decisions"
Cohesion: 0.12
Nodes (16): 0.1 Optional Telethon account-linking constraints, 0. Chatbrief user identity and registration, 10.1 Message edits, deletions, and overlapping backfill, 10. Telethon scope: explicit historical backfill only, 11. Central bot access loss and restoration, 1. Retain the current libraries and implementation, 2. Separate ingestion from digest generation, 3. Central Bot API is the default (+8 more)

### Community 80 - "Chatbrief-side image limits before provider upload — approved"
Cohesion: 0.12
Nodes (16): Account-deletion confirmation flow — approved, Chatbrief-side image limits before provider upload — approved, Image selection when the per-digest limit is reached — approved, Include retained media in personal exports — approved (Option B), Initial Chatbrief-side image-limit defaults — approved, Initial image formats for AI analysis — approved, Media access authorization at every operation — approved, Media deletion failure and recovery — approved (+8 more)

### Community 81 - "Delivery status and diagnostics command — approved"
Cohesion: 0.13
Nodes (15): AI image-analysis failures and omissions — approved, Delivery status and diagnostics command — approved, Duplicate JSON object keys — approved (Option A), Explicit null values in versioned export documents — approved (Option A), JSON document root shape — approved (Option A), JSON object member-name case sensitivity — approved (Option A), JSON object member-name Unicode handling — approved (Option A), JSON object member-name whitespace handling — approved default (Option A) (+7 more)

### Community 82 - "🔗 MCP Server"
Cohesion: 0.29
Nodes (6): Enabling it, 🔗 MCP Server, Reading a single channel, Security, get_channel_messages(), _format_messages()

### Community 83 - "Telegram Hybrid Ingestion and Multi-User Support"
Cohesion: 0.17
Nodes (12): Acceptance criteria, Documentation and decision tracking, Export report and media manifest validation details — recommended defaults, Goal, Important constraints and risks, Manual pending-digest recovery command — approved, Media manifest integrity and archive paths, Message content privacy in personal exports — approved (+4 more)

### Community 86 - "Chatbrief — current project handover"
Cohesion: 0.03
Nodes (76): Account-deletion confirmation flow — approved, AI image-analysis failure behavior — approved, Current status — 2026-11-02 (authoritative update), Daylight-saving schedule behavior — approved, Delivery recovery and diagnostics decisions — consolidated handover, Deterministic image selection at the per-digest limit — approved, Digest behavior and scheduling requirements, Digest processing modes clarified and approved (+68 more)

### Community 87 - "test_formatter.py"
Cohesion: 0.14
Nodes (6): test_format_date_russian_month_names(), test_format_group_message_empty_points(), test_format_group_message_no_source(), test_format_summary_message_uses_output_language(), test_pick_group_emoji_default(), test_pick_group_emoji_known_groups()

### Community 88 - "Chatbrief — AI-assisted development workflow"
Cohesion: 0.12
Nodes (16): Bug fixing, Chat workflow conventions, Chatbrief — AI-assisted development workflow, Complete the graph artifacts, Feature work — required developer workflow, Goals, Handover contract, How AI assistants should use GitHub (+8 more)

### Community 89 - "Implementation sequence"
Cohesion: 0.18
Nodes (11): Configuration and identity constraints, Current persistence behavior, Implementation sequence, Migration proposal — design direction, not an approved schema, Phase 1 findings — verified 2026-10-31, Phase 1 verification scope, Phase 2 — Establish a normalized ingestion boundary, Phase 3 — Add central Bot API ingestion (+3 more)

### Community 93 - "Phase 1 export persistence migration proposal — pending approval"
Cohesion: 0.18
Nodes (11): Constraints and indexes, Existing constraints, Explicitly out of scope for this migration, `export_cleanup_tasks`, `export_delivery_attempts`, `export_jobs`, Legacy data and compatibility, Migration order and acceptance checks (+3 more)

### Community 94 - "Contributor Covenant Code of Conduct"
Cohesion: 0.17
Nodes (12): 1. Correction, 2. Warning, 3. Temporary Ban, 4. Permanent Ban, Attribution, Contributor Covenant Code of Conduct, Enforcement, Enforcement Guidelines (+4 more)

### Community 97 - "Chatbrief — AI development guide"
Cohesion: 0.18
Nodes (11): Chat workflow conventions, Chatbrief — AI development guide, End-of-session handover, Git and change safety, Graph-assisted development (Graphify), Graphify artifact completion and hook verification, Project facts and stack, Project workflow helper (+3 more)

### Community 98 - "Export JSON root shape — approved (Option A)"
Cohesion: 0.29
Nodes (7): Duplicate JSON object keys — approved (Option A), Export JSON root shape — approved (Option A), JSON object member-name case sensitivity — approved (Option A), JSON object member-name Unicode handling — approved (Option A), JSON object member-name whitespace handling — approved default (Option A), Missing `schema_version` — approved (Option A), `schema_version` value validation — approved (Option A)

### Community 100 - "Chatbrief — persistent project context"
Cohesion: 0.10
Nodes (20): Approved target direction: hybrid Telegram ingestion, Chatbrief — persistent project context, Current project status — 2026-11-02, Development workflow contract, Export JSON document shapes — working defaults, Export preference/source field allowlist — working defaults, Export report and media-only message semantics — working defaults, Export report and media validation — working defaults (+12 more)

### Community 101 - "Export schema: top-level document and section shapes — recommended defaults"
Cohesion: 0.40
Nodes (5): Cross-document validation and empty-section behavior, `export.json`, `export-report.json`, Export schema: top-level document and section shapes — recommended defaults, `media-manifest.json`

### Community 102 - "Export schema: shared metadata, references, timestamps, and ordering — recommended defaults"
Cohesion: 0.40
Nodes (5): Deterministic ordering, Export schema: shared metadata, references, timestamps, and ordering — recommended defaults, Export-scoped relationship references, Shared document metadata, Timestamp representation

### Community 103 - "Graphify — local CLI and Git-shared code graph"
Cohesion: 0.25
Nodes (8): Build the initial graph, Git automation, Graphify — local CLI and Git-shared code graph, Install the standalone CLI, Query the local graph, Recommended source-to-GitHub cycle, Update and synchronize, What is shared through Git

### Community 104 - "Export report v1 semantics and media-only message handling — recommended defaults"
Cohesion: 0.40
Nodes (5): Export report v1 semantics and media-only message handling — recommended defaults, Message record v1 content rules, Omission records and result, Report counts, Warnings

### Community 106 - "Chatbrief implementation checklist"
Cohesion: 0.33
Nodes (5): Chatbrief implementation checklist, Completion and handover, Implementation, Inspect and decide before implementation, Validation

### Community 107 - "Digest scheduling, incremental windows, and one-time requests"
Cohesion: 0.50
Nodes (4): Digest scheduling, incremental windows, and one-time requests, One-time digest requests, Raw collection mode (no AI summarization), Scheduled digest configuration

### Community 109 - "Pull Request"
Cohesion: 0.40
Nodes (4): Checklist, Pull Request, What, Why

### Community 110 - "Security Policy"
Cohesion: 0.40
Nodes (4): Reporting a Vulnerability, Scope Notes, Security Policy, Supported Versions

### Community 123 - "🗄️ Persistent Storage"
Cohesion: 0.50
Nodes (4): 🗄️ Persistent Storage, PostgreSQL (optional backend), Schema, SQLite (default backend)

## Knowledge Gaps
- **1 isolated node(s):** `chatbrief`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1124 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Config` connect `Config` to `SQLiteBackend`, `config/models.py`, `load_config`, `test_scheduler.py`, `test_digest.py`, `_load_base_template`, `.__init__`, `DigestGroupConfig`, `TelegramMessageSender`, `TelegramBot`, `Summarizer`, `Implementation sequence`, `MessageSource`, `.__init__`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Are the 74 inferred relationships involving `load_config()` (e.g. with `main()` and `.initialize()`) actually correct?**
  _`load_config()` has 74 INFERRED edges - model-reasoned connections that need verification._
- **What connects `chatbrief` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `SQLiteBackend` be split into smaller, more focused modules?**
  _Cohesion score 0.07252298263534218 - nodes in this community are weakly interconnected._
- **Why does `Message` connect `Message` to `SQLiteBackend`, `test_filters.py`, `config/models.py`, `._create_statistics`, `TelegramMessageSource`, `test_summarizer.py`, `test_scheduler.py`, `ChannelConfig`, `test_digest.py`, `_load_base_template`, `Decisions`, `Config`, `🔗 MCP Server`, `Summarizer`, `Chatbrief — current project handover`, `._summarize_channel`, `.create_digest`, `MessageSource`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `Message` (e.g. with `Architecture guardrails` and `Architectural decisions to preserve`) actually correct?**
  _`Message` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Should `config/models.py` be split into smaller, more focused modules?**
  _Cohesion score 0.051929824561403506 - nodes in this community are weakly interconnected._