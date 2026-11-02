# Graph Report - ChatBrief  (2026-11-02)

## Corpus Check
- 110 files · ~117,404 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 8, .example 2, .toml 1)

## Summary
- 2486 nodes · 5641 edges · 115 communities (87 shown, 28 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 1126 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b08019b1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SQLiteBackend
- test_filters.py
- test_summarizer.py
- TelegramBot
- grouper.py
- GroupedPoint
- load_config
- ._summarize_channel
- test_scheduler.py
- with
- test_digest.py
- pytest
- test_telegram.py
- .format_group_summary_message
- test_mcp_server.py
- message.py
- CommandService
- mcp_server.py
- with
- AsyncContextManager
- .transition_job
- ExportDeliveryRepository
- unittest_mock
- asyncio
- delivery.py
- unit
- escape_xml_delimiters
- test_config.py
- TelegramMessageSender
- test_ui_strings.py
- telebrief
- _quality_gate_filter
- ._build_group_definitions
- telegram_source.py
- ._enforce_length_limit
- attributes
- unit
- feature_request.yml
- ApplicationDatabase
- validation.py
- Summarizer
- CommandResult
- TelegramMessageSender
- current.md
- ._format_date
- DigestFormatter
- OllamaProvider
- test_summarizer_uses_composer_output
- _save_to_storage
- ._create_header
- capture
- test_channel_with_group_uses_base_group_and_channel_prompt_extra
- ._create_channel_section
- test_load_config_anthropic_provider_missing_key
- test_grouper.py
- load_class
- hooks
- AGENTS.md
- test_application_delivery.py
- Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader
- test_application_storage.py
- test_mcp_config_rejects_invalid
- Config
- conftest.py
- runner.py
- _apply_filters
- README.md
- Personal data export — detailed approved design
- test_load_config_invalid_digest_mode
- test_load_config_invalid_output_language
- contact_links
- .__init__
- ai_providers.py
- test_formatter.py
- If the hook produced a new graph diff, review and commit it.
- Decisions
- Chatbrief-side image limits before provider upload — approved
- Delivery status and diagnostics command — approved
- exports.py
- Telegram Hybrid Ingestion and Multi-User Support
- test_load_config_invalid_lookback_hours_value
- Current status — 2026-11-02 (authoritative update)
- Chatbrief — AI-assisted development workflow
- Implementation sequence
- create_session.sh script
- Phase 1 export persistence migration proposal — approved for implementation
- Contributor Covenant Code of Conduct
- Chatbrief — AI development guide
- Export JSON root shape — approved (Option A)
- Config
- Chatbrief — persistent project context
- Export schema: top-level document and section shapes — recommended defaults
- Export schema: shared metadata, references, timestamps, and ordering — recommended defaults
- Graphify — local CLI and Git-shared code graph
- 📊 Example Output
- Chatbrief implementation checklist
- test_load_config_invalid_lookback_hours_type
- Pull Request
- Security Policy
- chatbrief
- test_load_config_missing_env_vars
- Chatbrief-side image limits before provider upload — approved
- TelegramBot
- ADR 0002: Stored Message History Is Not Proof of Collection Completeness

## God Nodes (most connected - your core abstractions)
1. `load_config()` - 99 edges
2. `Current status — 2026-11-02 (authoritative update)` - 84 edges
3. `Message` - 65 edges
4. `Summarizer` - 64 edges
5. `Config` - 58 edges
6. `TelegramBot` - 58 edges
7. `TelegramMessageSender` - 55 edges
8. `ChannelConfig` - 53 edges
9. `DigestFormatter` - 53 edges
10. `MessageSource` - 44 edges

## Surprising Connections (you probably didn't know these)
- `Config schema additions (all optional)` --references--> `ChannelConfig`  [INFERRED]
  docs/plans/completed/20260430-extensibility-architecture.md → src/chatbrief/config/models.py
- `Task 1: ADR document` --references--> `ChannelConfig`  [INFERRED]
  docs/plans/completed/20260430-extensibility-architecture.md → src/chatbrief/config/models.py
- `5. Separate chat access, subscriptions, and digest organization` --references--> `DigestGroupConfig`  [INFERRED]
  docs/plans/telegram-hybrid-ingestion.md → src/chatbrief/config/models.py
- `Migration proposal — design direction, not an approved schema` --references--> `Config`  [INFERRED]
  docs/plans/telegram-hybrid-ingestion.md → src/chatbrief/config/models.py
- `Decision` --references--> `collect_channel_messages()`  [INFERRED]
  docs/adr/0002-storage-completeness.md → src/chatbrief/digest/collector.py

## Import Cycles
- None detected.

## Communities (115 total, 28 thin omitted)

### Community 0 - "SQLiteBackend"
Cohesion: 0.08
Nodes (28): Phase 1 export persistence migration proposal — approved for implementation, Task 10: Extend StorageBackend Protocol, Context (from discovery), Development Approach, Implementation Steps, Overview, Post-Completion, Progress Tracking (+20 more)

### Community 1 - "test_filters.py"
Cohesion: 0.06
Nodes (62): ADR 0001: Extensibility Architecture — Filters, Prompts, Storage Read API, Plugin Loader, Alternatives Rejected, Consequences, Context, Decision, Migration, Negative / Risks, Option B: Subclass Extension (+54 more)

### Community 2 - "test_summarizer.py"
Cohesion: 0.08
Nodes (17): _make_messages(), test_default_template_path_points_to_existing_file(), test_format_messages_for_prompt(), test_format_messages_includes_link(), test_format_messages_prompt_always_includes_at_least_one(), test_format_messages_prompt_no_truncation_within_budget(), test_format_messages_prompt_truncation_keeps_recent(), test_format_messages_prompt_warns_on_truncation() (+9 more)

### Community 3 - "TelegramBot"
Cohesion: 0.11
Nodes (8): Package/platform refactor status, TelegramBot, test_run_without_application(), test_setup_bot_menu_exception(), test_setup_bot_menu_uses_output_language(), test_stop_running_application(), test_stop_without_application(), test_stop_without_updater()

### Community 4 - "grouper.py"
Cohesion: 0.07
Nodes (18): write_last_digest(), clear_digest_message_ids(), get_digest_message_ids(), get_lookback_time(), split_message(), test_clear_digest_message_ids(), test_clear_digest_message_ids_no_file(), test_get_digest_message_ids_invalid_json() (+10 more)

### Community 5 - "GroupedPoint"
Cohesion: 0.16
Nodes (5): english_config(), test_format_group_message_empty_points(), test_format_group_message_no_source(), test_format_group_message_no_truncation(), test_format_group_message_output()

### Community 6 - "load_config"
Cohesion: 0.06
Nodes (32): load_config(), test_application_storage_path_can_be_configured(), test_application_storage_path_defaults_to_application_database(), test_channel_group_field_parsed(), test_channel_group_none_by_default(), test_channel_group_null_yaml_is_none(), test_channel_group_other_accepted(), test_digest_group_config_equality_with_prompt_extra() (+24 more)

### Community 7 - "._summarize_channel"
Cohesion: 0.08
Nodes (12): test_summarize_channel_applies_prompt_extra(), test_summarize_channel_detects_output_over_3500_chars(), test_summarize_channel_double_budget_exhaustion_propagates(), test_summarize_channel_error(), test_summarize_channel_length_retry_exception_falls_through_to_truncation(), test_summarize_channel_no_retry_on_success(), test_summarize_channel_passes_max_prompt_chars_to_formatter(), test_summarize_channel_retries_on_token_budget_exhausted() (+4 more)

### Community 8 - "test_scheduler.py"
Cohesion: 0.21
Nodes (17): make_scheduler(), test_get_next_run_time_job_without_next_run(), test_get_next_run_time_when_not_running(), test_get_next_run_time_with_job(), test_get_next_run_time_without_job(), test_init(), test_parse_schedule_time(), test_parse_schedule_time_invalid() (+9 more)

### Community 9 - "with"
Cohesion: 0.06
Nodes (41): name, needs, runs-on, steps, jobs, build, lint, security (+33 more)

### Community 10 - "test_digest.py"
Cohesion: 0.16
Nodes (27): collect_messages(), _configure_channel_builder(), _configure_group_builder(), _make_sender(), _make_source(), test_build_digest_disconnects_when_collection_fails(), test_build_digest_uses_injected_source_and_formats_channel_output(), test_channel_mode_does_not_instantiate_topic_grouper() (+19 more)

### Community 11 - "pytest"
Cohesion: 0.07
Nodes (19): test_application_storage_path_rejects_blank_value(), test_channel_unknown_group_error_lists_bad_channel(), test_channel_unknown_group_raises(), test_digest_group_prompt_extra_non_string_raises(), test_filter_spec_channel_invalid_class_path_raises(), test_filter_spec_missing_class_path_raises(), test_filter_spec_non_dict_config_raises(), test_filter_spec_non_mapping_item_raises() (+11 more)

### Community 12 - "test_telegram.py"
Cohesion: 0.10
Nodes (38): make_source(), test_connect_dialog_cache_failure(), test_connect_missing_session(), test_connect_success(), test_connect_unauthorized(), test_disconnect(), test_fetch_channel_messages_error(), test_fetch_channel_messages_private_entity() (+30 more)

### Community 13 - ".format_group_summary_message"
Cohesion: 0.17
Nodes (4): test_format_group_summary_message(), test_format_group_summary_message_russian(), test_pick_group_emoji_default(), test_pick_group_emoji_known_groups()

### Community 14 - "test_mcp_server.py"
Cohesion: 0.09
Nodes (17): message_source(), server(), test_get_channel_messages_defaults(), test_get_channel_messages_renders_messages(), test_get_channel_messages_reports_empty_result(), test_get_channel_messages_surfaces_unknown_channel(), test_get_digest_defaults_to_24_hours(), test_get_digest_rejects_out_of_range_hours() (+9 more)

### Community 15 - "message.py"
Cohesion: 0.19
Nodes (4): mock_env_vars(), mock_logger(), sample_messages(), temp_config_file()

### Community 16 - "CommandService"
Cohesion: 0.11
Nodes (15): english_config(), _make_command_service(), test_cleanup_failure(), test_cleanup_rate_limited(), test_cleanup_success(), test_digest_exception(), test_digest_failure(), test_digest_rate_limited() (+7 more)

### Community 17 - "mcp_server.py"
Cohesion: 0.09
Nodes (17): Enabling it, 🔗 MCP Server, Reading a single channel, Security, Tools, read_last_digest(), collect_channel_messages(), _resolve_channel() (+9 more)

### Community 18 - "with"
Cohesion: 0.07
Nodes (29): name, permissions, runs-on, steps, env, IMAGE_NAME, REGISTRY, jobs (+21 more)

### Community 19 - "AsyncContextManager"
Cohesion: 0.14
Nodes (11): AnthropicProvider, test_anthropic_provider_accepts_reasoning_effort_param(), test_anthropic_provider_chat_completion(), test_anthropic_provider_empty_content_array_raises(), test_anthropic_provider_error(), test_anthropic_provider_error_body_truncated(), test_anthropic_provider_logs_response_metadata(), test_anthropic_provider_max_tokens_empty_content_raises_with_guidance() (+3 more)

### Community 20 - ".transition_job"
Cohesion: 0.13
Nodes (23): Step 3a — export-job repository and atomic state transitions, Step 3c — worker claims and lease-generation fencing, ExportJob, ExportJobState, ExportRepository, _job_from_row(), _normalize_lease_timestamp(), _utc_now() (+15 more)

### Community 21 - "ExportDeliveryRepository"
Cohesion: 0.20
Nodes (5): Step 3b — delivery-attempt and cleanup-task repositories, _attempt_from_row(), DeliveryDocumentKind, ExportDeliveryAttempt, ExportDeliveryRepository

### Community 22 - "unittest_mock"
Cohesion: 0.12
Nodes (7): test_create_bot_injects_command_service_and_sets_up_application(), test_create_bot_rejects_unimplemented_bale(), test_create_services_rejects_unimplemented_bale(), test_create_services_uses_telegram_adapters(), test_initialize_fails_closed_when_application_database_fails(), initialize(), test_initialize_sets_up_application_database_before_platform()

### Community 23 - "asyncio"
Cohesion: 0.12
Nodes (12): OpenAIProvider, test_openai_provider_chat_completion(), test_openai_provider_empty_string_content_raises(), test_openai_provider_falls_back_to_max_tokens_without_reasoning_effort(), test_openai_provider_falls_back_when_reasoning_effort_rejected(), test_openai_provider_length_empty_content_raises_with_guidance(), test_openai_provider_length_with_content_returns_truncated(), test_openai_provider_logs_response_metadata() (+4 more)

### Community 24 - "delivery.py"
Cohesion: 0.11
Nodes (13): Step 3b implementation update — delivery attempts and cleanup tasks, _cleanup_from_row(), CleanupTaskState, CleanupTaskType, DeliveryAttemptOutcome, ExportCleanupRepository, ExportCleanupTask, _utc_now() (+5 more)

### Community 25 - "unit"
Cohesion: 0.08
Nodes (14): create_provider(), test_create_provider_anthropic(), test_create_provider_anthropic_missing_key(), test_create_provider_case_insensitive(), test_create_provider_ollama(), test_create_provider_openai(), test_create_provider_openai_missing_key(), test_create_provider_unknown() (+6 more)

### Community 26 - "escape_xml_delimiters"
Cohesion: 0.06
Nodes (6): _strip_channel_summary_noise(), escape_xml_delimiters(), TestStripBroaderNoise, TestStripChannelHeader, TestStripSectionTwo, TestEscapeXmlDelimiters

### Community 27 - "test_config.py"
Cohesion: 0.16
Nodes (16): _storage_config_file(), test_channel_group_localized_other_accepted(), test_filter_spec_defaults_to_empty_global(), test_filter_spec_global_parsed(), test_prompts_config_explicit_values(), test_prompts_config_strips_whitespace(), test_storage_config_empty_path_raises(), test_storage_config_enabled_not_bool_raises() (+8 more)

### Community 29 - "TelegramMessageSender"
Cohesion: 0.05
Nodes (19): Architecture guardrails, Current implementation status, Architectural decisions to preserve, Current refactor status (2026-10-30), Chatbrief-specific guardrails, Current architecture, Current lifecycle and boundaries, Phase 1 — Inspect current storage and digest lifecycle (+11 more)

### Community 31 - "test_ui_strings.py"
Cohesion: 0.15
Nodes (8): test_all_required_keys_present_for_each_language(), test_digest_group_keys_english_values(), test_digest_group_keys_present_for_each_language(), test_get_ui_strings_english(), test_get_ui_strings_returns_dict(), test_get_ui_strings_russian(), test_get_ui_strings_unknown_language_falls_back_to_english(), test_no_empty_strings_for_any_language()

### Community 32 - "telebrief"
Cohesion: 0.10
Nodes (20): build, container_name, env_file, environment, healthcheck, image, logging, restart (+12 more)

### Community 33 - "_quality_gate_filter"
Cohesion: 0.10
Nodes (6): _dedup_extracted(), ExtractedBullet, _qg_has_concrete_entity(), _quality_gate_filter(), TestDedupExtracted, TestQualityGateFilter

### Community 34 - "._build_group_definitions"
Cohesion: 0.08
Nodes (3): TestBuildGroupDefinitions, TestDeterministicDedup, TestParseGroupedResponse

### Community 35 - "telegram_source.py"
Cohesion: 0.13
Nodes (8): async_messages(), message_source(), test_fetch_channel_messages_empty_without_media(), test_fetch_channel_messages_media_only(), test_fetch_channel_messages_sorts_messages(), test_fetch_channel_messages_stops_at_lookback(), test_fetch_channel_messages_text(), test_fetch_messages_success()

### Community 36 - "._enforce_length_limit"
Cohesion: 0.20
Nodes (3): test_enforce_length_limit_minor_overage_truncates_at_sentence_boundary(), test_enforce_length_limit_retry_failure_keeps_original_summary(), test_enforce_length_limit_retry_returns_short_summary()

### Community 37 - "attributes"
Cohesion: 0.12
Nodes (16): description, label, options, placeholder, render, value, body, attributes (+8 more)

### Community 38 - "unit"
Cohesion: 0.25
Nodes (3): test_format_channel_message_includes_channel_link(), test_format_channel_message_stats_uses_output_language(), test_truncation_message_uses_output_language()

### Community 40 - "feature_request.yml"
Cohesion: 0.12
Nodes (15): description, label, options, placeholder, body, attributes, id, type (+7 more)

### Community 41 - "ApplicationDatabase"
Cohesion: 0.06
Nodes (16): Implementation update — application-state database foundation and startup lifecycle, Application-state database and export persistence foundation, Next steps, Scope, Step 1 — database foundation, Step 2 — application lifecycle integration, Step 2 — local verification, Tests added (+8 more)

### Community 42 - "validation.py"
Cohesion: 0.06
Nodes (26): Context (from discovery), Task 4: FilterConfig parsing, Task 8: Group binding in config, Task 1: Add StorageConfig to config_loader.py, ApplicationStorageConfig, DigestGroupConfig, McpConfig, PromptsConfig (+18 more)

### Community 43 - "Summarizer"
Cohesion: 0.11
Nodes (8): Summarizer, test_summarize_all_empty(), test_summarize_all_partial_failure(), test_summarize_all_success(), test_summarizer_custom_output_language(), test_truncate_at_sentence_boundary_hard_truncates_without_punctuation(), test_truncate_at_sentence_boundary_returns_short_text(), test_truncate_at_sentence_boundary_uses_last_sentence()

### Community 45 - "TelegramMessageSender"
Cohesion: 0.05
Nodes (38): main(), TelegramMessageSender, save_digest_message_ids(), test_cleanup_old_digests_default_user_id(), test_cleanup_old_digests_deletion_failure(), test_cleanup_old_digests_message_not_found(), test_cleanup_old_digests_no_messages(), test_cleanup_old_digests_partial_failure() (+30 more)

### Community 47 - "._format_date"
Cohesion: 0.18
Nodes (3): test_format_date_english_month_names(), test_format_date_russian_month_names(), test_format_summary_message_uses_output_language()

### Community 49 - "DigestFormatter"
Cohesion: 0.14
Nodes (7): DigestFormatter, main(), test_create_digest(), test_create_statistics(), test_create_statistics_uses_output_language(), test_formatter_without_stats(), test_overview_section_label_uses_output_language()

### Community 50 - "OllamaProvider"
Cohesion: 0.11
Nodes (13): OllamaProvider, _redact_url(), AsyncContextManager, test_ollama_provider_accepts_reasoning_effort_param(), test_ollama_provider_chat_completion(), test_ollama_provider_debug_logging(), test_ollama_provider_empty_content_raises(), test_ollama_provider_error() (+5 more)

### Community 52 - "_save_to_storage"
Cohesion: 0.29
Nodes (5): Filter chain insertion point, Phase 2 — Filter Protocol + Chain, Task 3: MessageFilter Protocol + builtins, Task 5: Filter chain wiring in core, _save_to_storage()

### Community 53 - "._create_header"
Cohesion: 0.25
Nodes (3): test_create_header(), test_create_header_russian_month_name(), test_create_header_uses_output_language()

### Community 54 - "capture"
Cohesion: 0.10
Nodes (8): test_channel_without_group_uses_base_and_channel_prompt_extra(), test_language_instruction_only_in_system_prompt(), test_summarize_channel_includes_truncation_note(), test_summarize_channel_prompt_instructs_two_tier_format(), capture(), test_summarize_channel_retry_includes_shorten_instruction(), test_summarize_channel_unknown_channel_uses_default_prompt(), test_summarize_channel_wraps_messages_in_xml_delimiters()

### Community 58 - "test_grouper.py"
Cohesion: 0.03
Nodes (16): DigestGrouper, _run(), GroupedPoint, _normalize_point(), config_with_groups(), config_with_other_group(), grouper(), grouper_english() (+8 more)

### Community 59 - "load_class"
Cohesion: 0.24
Nodes (9): load_class(), test_load_class_function_not_class(), test_load_class_missing_attribute(), test_load_class_missing_module(), test_load_class_no_dot_raises(), test_load_class_non_class_attribute(), test_load_class_returns_type(), test_load_class_stdlib_class() (+1 more)

### Community 60 - "hooks"
Cohesion: 0.18
Nodes (10): exclude, additional_dependencies, args, exclude, files, id, repos, hooks (+2 more)

### Community 62 - "test_application_delivery.py"
Cohesion: 0.31
Nodes (11): _packaging_job(), test_attempt_cannot_be_finished_twice_or_with_started_outcome(), test_cleanup_task_retry_and_terminal_update_are_compare_and_set(), test_cleanup_task_survives_job_deletion_and_can_be_completed(), test_cleanup_tasks_are_created_only_for_owned_jobs(), test_cleanup_tasks_cover_telegram_and_staging_resources(), test_delivery_attempts_are_owner_scoped(), test_failed_delivery_can_retry_with_a_new_attempt_number() (+3 more)

### Community 63 - "Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader"
Cohesion: 0.08
Nodes (23): Config schema additions (all optional), Development Approach, Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader, Implementation Steps, Overview, Phase 1 — Skeleton + ADR + Plugin Loader, Phase 3 — Prompt Composer + Group Binding, Phase 4 — Storage Read API (+15 more)

### Community 64 - "test_application_storage.py"
Cohesion: 0.28
Nodes (7): _connected(), test_applied_migration_checksum_drift_is_rejected(), test_failed_migration_rolls_back_schema_and_version_record(), test_foreign_key_constraints_reject_orphaned_delivery_attempts(), test_foreign_keys_are_enabled_on_every_database_connection(), test_initial_migration_creates_export_schema_and_is_idempotent(), test_partial_unique_index_allows_only_one_blocking_job_per_user()

### Community 65 - "test_mcp_config_rejects_invalid"
Cohesion: 0.20
Nodes (6): _mcp_config_file(), test_filter_spec_invalid_dotted_path_raises(), test_mcp_config_explicit(), test_mcp_config_missing_block_defaults(), test_mcp_config_rejects_invalid(), test_prompts_composer_invalid_dotted_path_raises()

### Community 66 - "Config"
Cohesion: 0.11
Nodes (11): _build_channel_parts(), build_digest_parts(), _build_grouped_parts(), _filter_valid_summaries(), _format_group_messages(), _get_channel_urls(), join_parts(), _order_groups() (+3 more)

### Community 67 - "conftest.py"
Cohesion: 0.18
Nodes (11): Code of Conduct, Code Style, Commit Messages, Contributing to Telebrief, Development Setup, Pull Request Process, Questions, Reporting Bugs (+3 more)

### Community 69 - "_apply_filters"
Cohesion: 0.18
Nodes (9): FilterSpec, _apply_filters(), test_apply_filters_empty_specs_preserve_messages(), test_channel_empty_filter_list_overrides_global_filters(), test_channel_filter_list_replaces_global_filter_chain(), test_filter_chain_applies_in_order(), test_filter_exception_is_isolated_from_following_filters(), test_filter_initialization_failure_is_logged_and_skipped() (+1 more)

### Community 70 - "README.md"
Cohesion: 0.09
Nodes (19): Chatbrief — new chat starter, AI-assisted development workflow, 🤖 Bot Commands, 🤝 Contributing, 🙏 Credits, 🛠️ Development & Testing, 🐳 Docker Deployment, ❓ FAQ (+11 more)

### Community 71 - "Personal data export — detailed approved design"
Cohesion: 0.08
Nodes (24): Archive structure, Automatic Telegram delivery retry limits, Cancellation and cleanup, Configurable worker concurrency, Database-backed worker claims and leases, Explicit recovery from ambiguous delivery, Export behavior on account deletion, Export invalidation when included source data is removed — approved (Option A) (+16 more)

### Community 74 - "contact_links"
Cohesion: 0.33
Nodes (5): blank_issues_enabled, contact_links, about, name, url

### Community 75 - ".__init__"
Cohesion: 0.12
Nodes (9): Task 9: Wire composer into Summarizer, __getattr__(), _load_base_template(), _ProviderSettings, test_load_base_template_contains_language_placeholder(), test_load_base_template_custom_path(), test_load_base_template_default_path_returns_nonempty(), test_load_base_template_missing_file_raises() (+1 more)

### Community 77 - "test_formatter.py"
Cohesion: 0.19
Nodes (5): test_formatter_initialization(), test_formatter_without_emojis(), test_pick_emoji_crypto(), test_pick_emoji_default(), test_pick_emoji_tech()

### Community 78 - "If the hook produced a new graph diff, review and commit it."
Cohesion: 0.40
Nodes (5): Complete the report and visualization, How ChatGPT uses the graph from GitHub, If the hook produced a new graph diff, review and commit it., Official references, pj graph command reference

### Community 79 - "Decisions"
Cohesion: 0.12
Nodes (16): 0.1 Optional Telethon account-linking constraints, 0. Chatbrief user identity and registration, 10.1 Message edits, deletions, and overlapping backfill, 10. Telethon scope: explicit historical backfill only, 11. Central bot access loss and restoration, 1. Retain the current libraries and implementation, 2. Separate ingestion from digest generation, 3. Central Bot API is the default (+8 more)

### Community 80 - "Chatbrief-side image limits before provider upload — approved"
Cohesion: 0.12
Nodes (16): Account-deletion confirmation flow — approved, Chatbrief-side image limits before provider upload — approved, Image selection when the per-digest limit is reached — approved, Include retained media in personal exports — approved (Option B), Initial Chatbrief-side image-limit defaults — approved, Initial image formats for AI analysis — approved, Media access authorization at every operation — approved, Media deletion failure and recovery — approved (+8 more)

### Community 81 - "Delivery status and diagnostics command — approved"
Cohesion: 0.13
Nodes (15): AI image-analysis failures and omissions — approved, Delivery status and diagnostics command — approved, Duplicate JSON object keys — approved (Option A), Explicit null values in versioned export documents — approved (Option A), JSON document root shape — approved (Option A), JSON object member-name case sensitivity — approved (Option A), JSON object member-name Unicode handling — approved (Option A), JSON object member-name whitespace handling — approved default (Option A) (+7 more)

### Community 82 - "exports.py"
Cohesion: 0.18
Nodes (7): ExportMediaOutcome, InvalidExportTransitionError, _normalize_updates(), _require_confirmed_primary_delivery(), _transition_in_transaction(), _validate_worker_id(), _validate_worker_lease()

### Community 83 - "Telegram Hybrid Ingestion and Multi-User Support"
Cohesion: 0.10
Nodes (21): Acceptance criteria, Digest scheduling, incremental windows, and one-time requests, Documentation and decision tracking, Export report and media manifest validation details — recommended defaults, Export report v1 semantics and media-only message handling — recommended defaults, Goal, Important constraints and risks, Manual pending-digest recovery command — approved (+13 more)

### Community 86 - "Current status — 2026-11-02 (authoritative update)"
Cohesion: 0.03
Nodes (79): Account-deletion confirmation flow — approved, AI image-analysis failure behavior — approved, Application-state database validation — developer-reported results, Current status — 2026-11-02 (authoritative update), Daylight-saving schedule behavior — approved, Delivery recovery and diagnostics decisions — consolidated handover, Deterministic image selection at the per-digest limit — approved, Digest behavior and scheduling requirements (+71 more)

### Community 88 - "Chatbrief — AI-assisted development workflow"
Cohesion: 0.12
Nodes (16): Bug fixing, Chat workflow conventions, Chatbrief — AI-assisted development workflow, Complete the graph artifacts, Feature work — required developer workflow, Goals, Handover contract, How AI assistants should use GitHub (+8 more)

### Community 89 - "Implementation sequence"
Cohesion: 0.18
Nodes (11): Configuration and identity constraints, Current persistence behavior, Implementation sequence, Migration proposal — design direction, not an approved schema, Phase 1 findings — verified 2026-10-31, Phase 1 verification scope, Phase 2 — Establish a normalized ingestion boundary, Phase 3 — Add central Bot API ingestion (+3 more)

### Community 93 - "Phase 1 export persistence migration proposal — approved for implementation"
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

### Community 99 - "Config"
Cohesion: 0.06
Nodes (6): main(), Config, Platform, get_month_names(), get_ui_strings(), setup_logging()

### Community 100 - "Chatbrief — persistent project context"
Cohesion: 0.10
Nodes (21): Approved target direction: hybrid Telegram ingestion, Chatbrief — persistent project context, Current project status — 2026-11-02, Development workflow contract, Export JSON document shapes — working defaults, Export preference/source field allowlist — working defaults, Export report and media-only message semantics — working defaults, Export report and media validation — working defaults (+13 more)

### Community 101 - "Export schema: top-level document and section shapes — recommended defaults"
Cohesion: 0.40
Nodes (5): Cross-document validation and empty-section behavior, `export.json`, `export-report.json`, Export schema: top-level document and section shapes — recommended defaults, `media-manifest.json`

### Community 102 - "Export schema: shared metadata, references, timestamps, and ordering — recommended defaults"
Cohesion: 0.40
Nodes (5): Deterministic ordering, Export schema: shared metadata, references, timestamps, and ordering — recommended defaults, Export-scoped relationship references, Shared document metadata, Timestamp representation

### Community 103 - "Graphify — local CLI and Git-shared code graph"
Cohesion: 0.25
Nodes (8): Build the initial graph, Git automation, Graphify — local CLI and Git-shared code graph, Install the standalone CLI, Query the local graph, Recommended source-to-GitHub cycle, Update and synchronize, What is shared through Git

### Community 105 - "📊 Example Output"
Cohesion: 0.50
Nodes (4): Channel mode (`digest_mode: "channel"` — default), `dedup_topics` — cross-channel deduplication, 📊 Example Output, Topic mode (`digest_mode: "digest"`)

### Community 106 - "Chatbrief implementation checklist"
Cohesion: 0.20
Nodes (9): Application-state database foundation — steps 1–2, Chatbrief implementation checklist, Completion and handover, Export persistence — Step 3a: job repository and atomic transitions, Export persistence — Step 3b: delivery attempts and cleanup tasks, Export persistence — Step 3c: worker claims and lease fencing, Implementation, Inspect and decide before implementation (+1 more)

### Community 109 - "Pull Request"
Cohesion: 0.40
Nodes (4): Checklist, Pull Request, What, Why

### Community 110 - "Security Policy"
Cohesion: 0.40
Nodes (4): Reporting a Vulnerability, Scope Notes, Security Policy, Supported Versions

### Community 122 - "TelegramBot"
Cohesion: 0.06
Nodes (35): CommandStatus, english_config(), _make_command_service(), _make_update(), test_cleanup_rate_limited(), test_handle_cleanup_exception(), test_handle_cleanup_failure(), test_handle_cleanup_messages_use_output_language() (+27 more)

### Community 123 - "ADR 0002: Stored Message History Is Not Proof of Collection Completeness"
Cohesion: 0.40
Nodes (4): ADR 0002: Stored Message History Is Not Proof of Collection Completeness, Consequences, Context, Decision

## Knowledge Gaps
- **1 isolated node(s):** `chatbrief`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1197 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Config` connect `Config` to `Config`, `TelegramBot`, `_apply_filters`, `load_config`, `validation.py`, `test_digest.py`, `Summarizer`, `TelegramMessageSender`, `.__init__`, `.__init__`, `mcp_server.py`, `DigestFormatter`, `_save_to_storage`, `Implementation sequence`, `test_grouper.py`, `TelegramMessageSender`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **Are the 77 inferred relationships involving `load_config()` (e.g. with `main()` and `.initialize()`) actually correct?**
  _`load_config()` has 77 INFERRED edges - model-reasoned connections that need verification._
- **What connects `chatbrief` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `SQLiteBackend` be split into smaller, more focused modules?**
  _Cohesion score 0.07578659370725034 - nodes in this community are weakly interconnected._
- **Why does `Message` connect `TelegramMessageSender` to `SQLiteBackend`, `test_filters.py`, `test_summarizer.py`, `Config`, `Chatbrief — persistent project context`, `telegram_source.py`, `unit`, `._summarize_channel`, `_apply_filters`, `Summarizer`, `Decisions`, `message.py`, `mcp_server.py`, `DigestFormatter`, `Current status — 2026-11-02 (authoritative update)`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `Message` (e.g. with `Architecture guardrails` and `Architectural decisions to preserve`) actually correct?**
  _`Message` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_filters.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06094627105052125 - nodes in this community are weakly interconnected._