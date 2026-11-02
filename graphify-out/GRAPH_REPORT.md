# Graph Report - ChatBrief  (2026-11-02)

## Corpus Check
- 112 files · ~120,628 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 8, .example 2, .toml 1)

## Summary
- 2543 nodes · 5798 edges · 137 communities (95 shown, 42 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 1168 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `eb52e97f`
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
- Config
- with
- AsyncContextManager
- .transition_job
- CommandStatus
- unittest_mock
- asyncio
- delivery.py
- unit
- ._build_extractor_prompt
- config/models.py
- english_config
- TelegramBot
- test_ui_strings.py
- telebrief
- _quality_gate_filter
- ._build_group_definitions
- test_message_source.py
- DefaultComposer
- attributes
- unit
- feature_request.yml
- ApplicationDatabase
- validation.py
- .summarize_all
- CommandResult
- ExportWorker
- .group_summaries
- ._format_date
- test_grouper.py
- .create_digest
- OllamaProvider
- capture
- ChannelConfig
- ._create_header
- test_cleanup_old_digests_success
- unit
- ._create_channel_section
- escape_xml_delimiters
- ._extract_bullets_from_channel
- test_run_without_application
- hooks
- AGENTS.md
- test_application_delivery.py
- Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader
- ExportCleanupRepository
- test_mcp_config_rejects_invalid
- _build_grouped_parts
- conftest.py
- .test_classifies_flat_bullets_into_groups
- Summarizer
- README.md
- Personal data export — detailed approved design
- .send_channel_messages_with_tracking
- grouper.py
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
- load_class
- TelegramMessageSender
- Current status — 2026-11-02 (authoritative update)
- config/loader.py
- Chatbrief — AI-assisted development workflow
- Implementation sequence
- create_session.sh script
- _strip_channel_summary_noise
- os
- Phase 1 export persistence migration proposal — approved for implementation
- Contributor Covenant Code of Conduct
- Implementation Steps
- ._enforce_length_limit
- Chatbrief — AI development guide
- Export JSON root shape — approved (Option A)
- ui_strings.py
- Chatbrief — persistent project context
- Export schema: top-level document and section shapes — recommended defaults
- Export schema: shared metadata, references, timestamps, and ordering — recommended defaults
- Graphify — local CLI and Git-shared code graph
- test_send_summary_message_error
- 📊 Example Output
- Chatbrief implementation checklist
- Export report v1 semantics and media-only message handling — recommended defaults
- TestBuildGroupDefinitions
- Pull Request
- Security Policy
- chatbrief
- Digest scheduling, incremental windows, and one-time requests
- build_server
- Chatbrief-side image limits before provider upload — approved
- ._create_statistics
- ADR 0002: Stored Message History Is Not Proof of Collection Completeness
- TokenBudgetExhaustedError
- Platform
- current.md
- parse_application_storage_config
- McpConfig
- Export report and media manifest validation details — recommended defaults
- test_verify_instruction_removed_from_user_prompt
- test_cleanup_old_digests_deletion_failure
- test_load_config_unsupported_provider
- test_load_config_digest_groups_non_string_fields
- test_load_config_duplicate_channel_names

## God Nodes (most connected - your core abstractions)
1. `load_config()` - 99 edges
2. `Current status — 2026-11-02 (authoritative update)` - 85 edges
3. `Message` - 65 edges
4. `Summarizer` - 64 edges
5. `Config` - 58 edges
6. `TelegramBot` - 58 edges
7. `TelegramMessageSender` - 55 edges
8. `ChannelConfig` - 53 edges
9. `DigestFormatter` - 53 edges
10. `MessageSource` - 44 edges

## Surprising Connections (you probably didn't know these)
- `Validation commands` --references--> `ExportWorker`  [INFERRED]
  AI_README.md → src/chatbrief/application_storage/worker.py
- `Current project status — 2026-11-02` --references--> `ExportWorker`  [INFERRED]
  CHATGPT_CONTEXT.md → src/chatbrief/application_storage/worker.py
- `Negative / Risks` --references--> `ChannelConfig`  [INFERRED]
  docs/adr/0001-extensibility-architecture.md → src/chatbrief/config/models.py
- `Config schema additions (all optional)` --references--> `ChannelConfig`  [INFERRED]
  docs/plans/completed/20260430-extensibility-architecture.md → src/chatbrief/config/models.py
- `Task 1: ADR document` --references--> `ChannelConfig`  [INFERRED]
  docs/plans/completed/20260430-extensibility-architecture.md → src/chatbrief/config/models.py

## Import Cycles
- None detected.

## Communities (137 total, 42 thin omitted)

### Community 0 - "SQLiteBackend"
Cohesion: 0.07
Nodes (30): Phase 1 export persistence migration proposal — approved for implementation, Task 10: Extend StorageBackend Protocol, Context (from discovery), Development Approach, Implementation Steps, Overview, Post-Completion, Progress Tracking (+22 more)

### Community 1 - "test_filters.py"
Cohesion: 0.11
Nodes (38): ADR 0001: Extensibility Architecture — Filters, Prompts, Storage Read API, Plugin Loader, Alternatives Rejected, Consequences, Context, Decision, Migration, Negative / Risks, Option B: Subclass Extension (+30 more)

### Community 2 - "test_summarizer.py"
Cohesion: 0.11
Nodes (12): _make_messages(), test_default_template_path_points_to_existing_file(), test_format_messages_prompt_always_includes_at_least_one(), test_format_messages_prompt_no_truncation_within_budget(), test_format_messages_prompt_truncation_keeps_recent(), test_format_messages_prompt_warns_on_truncation(), test_summarizer_custom_composer_constructor_type_error(), test_summarizer_custom_composer_invalid_interface() (+4 more)

### Community 3 - "TelegramBot"
Cohesion: 0.07
Nodes (36): Package/platform refactor status, TelegramBot, _make_command_service(), _make_update(), test_cleanup_rate_limited(), test_handle_cleanup_exception(), test_handle_cleanup_failure(), test_handle_cleanup_messages_use_output_language() (+28 more)

### Community 4 - "grouper.py"
Cohesion: 0.07
Nodes (21): main(), clear_digest_message_ids(), get_digest_message_ids(), get_lookback_time(), save_digest_message_ids(), setup_logging(), split_message(), test_cleanup_old_digests_message_not_found() (+13 more)

### Community 5 - "GroupedPoint"
Cohesion: 0.16
Nodes (5): english_config(), test_format_group_message_empty_points(), test_format_group_message_no_source(), test_format_group_message_no_truncation(), test_format_group_message_output()

### Community 6 - "load_config"
Cohesion: 0.07
Nodes (48): load_config(), _storage_config_file(), test_application_storage_path_can_be_configured(), test_application_storage_path_defaults_to_application_database(), test_channel_group_field_parsed(), test_channel_group_localized_other_accepted(), test_channel_group_none_by_default(), test_channel_group_null_yaml_is_none() (+40 more)

### Community 7 - "._summarize_channel"
Cohesion: 0.07
Nodes (15): test_language_instruction_only_in_system_prompt(), test_summarize_channel_detects_output_over_3500_chars(), test_summarize_channel_double_budget_exhaustion_propagates(), test_summarize_channel_error(), test_summarize_channel_length_retry_exception_falls_through_to_truncation(), test_summarize_channel_no_retry_on_success(), test_summarize_channel_no_retry_when_under_limit(), test_summarize_channel_passes_max_prompt_chars_to_formatter() (+7 more)

### Community 8 - "test_scheduler.py"
Cohesion: 0.21
Nodes (17): make_scheduler(), test_get_next_run_time_job_without_next_run(), test_get_next_run_time_when_not_running(), test_get_next_run_time_with_job(), test_get_next_run_time_without_job(), test_init(), test_parse_schedule_time(), test_parse_schedule_time_invalid() (+9 more)

### Community 9 - "with"
Cohesion: 0.06
Nodes (41): name, needs, runs-on, steps, jobs, build, lint, security (+33 more)

### Community 10 - "test_digest.py"
Cohesion: 0.13
Nodes (31): collect_messages(), _resolve_channel(), _configure_channel_builder(), _configure_group_builder(), _make_sender(), _make_source(), test_apply_filters_empty_specs_preserve_messages(), test_build_digest_disconnects_when_collection_fails() (+23 more)

### Community 11 - "pytest"
Cohesion: 0.06
Nodes (22): test_application_storage_path_rejects_blank_value(), test_channel_unknown_group_error_lists_bad_channel(), test_channel_unknown_group_raises(), test_digest_group_prompt_extra_non_string_raises(), test_filter_spec_channel_invalid_class_path_raises(), test_filter_spec_missing_class_path_raises(), test_filter_spec_non_dict_config_raises(), test_filter_spec_non_mapping_item_raises() (+14 more)

### Community 12 - "test_telegram.py"
Cohesion: 0.11
Nodes (38): make_source(), test_connect_dialog_cache_failure(), test_connect_missing_session(), test_connect_success(), test_connect_unauthorized(), test_disconnect(), test_fetch_channel_messages_error(), test_fetch_channel_messages_private_entity() (+30 more)

### Community 13 - ".format_group_summary_message"
Cohesion: 0.17
Nodes (4): test_format_group_summary_message(), test_format_group_summary_message_russian(), test_pick_group_emoji_default(), test_pick_group_emoji_known_groups()

### Community 14 - "test_mcp_server.py"
Cohesion: 0.09
Nodes (17): message_source(), server(), test_get_channel_messages_defaults(), test_get_channel_messages_renders_messages(), test_get_channel_messages_reports_empty_result(), test_get_channel_messages_surfaces_unknown_channel(), test_get_digest_defaults_to_24_hours(), test_get_digest_rejects_out_of_range_hours() (+9 more)

### Community 15 - "message.py"
Cohesion: 0.16
Nodes (6): Running Tests and Checks, Testing conventions, mock_env_vars(), mock_logger(), sample_messages(), temp_config_file()

### Community 16 - "CommandService"
Cohesion: 0.11
Nodes (15): english_config(), _make_command_service(), test_cleanup_failure(), test_cleanup_rate_limited(), test_cleanup_success(), test_digest_exception(), test_digest_failure(), test_digest_rate_limited() (+7 more)

### Community 17 - "Config"
Cohesion: 0.09
Nodes (9): Config, build_digest_parts(), join_parts(), _order_groups(), write_last_digest(), collect_channel_messages(), build_digest(), generate_and_send_digest() (+1 more)

### Community 18 - "with"
Cohesion: 0.07
Nodes (29): name, permissions, runs-on, steps, env, IMAGE_NAME, REGISTRY, jobs (+21 more)

### Community 19 - "AsyncContextManager"
Cohesion: 0.15
Nodes (11): AnthropicProvider, test_anthropic_provider_accepts_reasoning_effort_param(), test_anthropic_provider_chat_completion(), test_anthropic_provider_empty_content_array_raises(), test_anthropic_provider_error(), test_anthropic_provider_error_body_truncated(), test_anthropic_provider_logs_response_metadata(), test_anthropic_provider_max_tokens_empty_content_raises_with_guidance() (+3 more)

### Community 20 - ".transition_job"
Cohesion: 0.14
Nodes (22): Step 3a — export-job repository and atomic state transitions, Step 3c — worker claims and lease-generation fencing, ExportJob, ExportJobState, ExportRepository, _job_from_row(), _utc_now(), _validate_transition() (+14 more)

### Community 21 - "CommandStatus"
Cohesion: 0.13
Nodes (5): CommandStatus, test_handle_digest_error_message_uses_output_language(), test_handle_digest_rate_limited(), test_handle_digest_success_message_uses_output_language(), test_handle_digest_unauthorized()

### Community 22 - "unittest_mock"
Cohesion: 0.12
Nodes (7): test_create_bot_injects_command_service_and_sets_up_application(), test_create_bot_rejects_unimplemented_bale(), test_create_services_rejects_unimplemented_bale(), test_create_services_uses_telegram_adapters(), test_initialize_fails_closed_when_application_database_fails(), initialize(), test_initialize_sets_up_application_database_before_platform()

### Community 23 - "asyncio"
Cohesion: 0.13
Nodes (13): OpenAIProvider, test_openai_provider_chat_completion(), test_openai_provider_empty_string_content_raises(), test_openai_provider_falls_back_to_max_tokens_after_reasoning_effort_retry(), test_openai_provider_falls_back_to_max_tokens_without_reasoning_effort(), test_openai_provider_falls_back_when_reasoning_effort_rejected(), test_openai_provider_length_empty_content_raises_with_guidance(), test_openai_provider_length_with_content_returns_truncated() (+5 more)

### Community 24 - "delivery.py"
Cohesion: 0.13
Nodes (14): Step 3b — delivery-attempt and cleanup-task repositories, _attempt_from_row(), DeliveryAttemptOutcome, DeliveryDocumentKind, ExportDeliveryAttempt, ExportDeliveryRepository, _utc_now(), _validate_delivery_identifiers() (+6 more)

### Community 25 - "unit"
Cohesion: 0.09
Nodes (11): create_provider(), OllamaProvider, test_create_provider_anthropic_missing_key(), test_create_provider_case_insensitive(), test_create_provider_ollama(), test_create_provider_openai(), test_create_provider_openai_missing_key(), test_create_provider_unknown() (+3 more)

### Community 26 - "._build_extractor_prompt"
Cohesion: 0.10
Nodes (3): TestPromptInjectionMitigation, TestStripChannelHeader, TestStripSectionTwo

### Community 29 - "TelegramBot"
Cohesion: 0.05
Nodes (18): Architecture guardrails, Current implementation status, Architectural decisions to preserve, Current refactor status (2026-10-30), Chatbrief-specific guardrails, Current architecture, Current lifecycle and boundaries, Phase 1 — Inspect current storage and digest lifecycle (+10 more)

### Community 31 - "test_ui_strings.py"
Cohesion: 0.14
Nodes (9): get_ui_strings(), test_all_required_keys_present_for_each_language(), test_digest_group_keys_english_values(), test_digest_group_keys_present_for_each_language(), test_get_ui_strings_english(), test_get_ui_strings_returns_dict(), test_get_ui_strings_russian(), test_get_ui_strings_unknown_language_falls_back_to_english() (+1 more)

### Community 32 - "telebrief"
Cohesion: 0.10
Nodes (20): build, container_name, env_file, environment, healthcheck, image, logging, restart (+12 more)

### Community 33 - "_quality_gate_filter"
Cohesion: 0.10
Nodes (6): _dedup_extracted(), ExtractedBullet, _qg_has_concrete_entity(), _quality_gate_filter(), TestDedupExtracted, TestQualityGateFilter

### Community 35 - "test_message_source.py"
Cohesion: 0.10
Nodes (9): main(), async_messages(), message_source(), test_fetch_channel_messages_empty_without_media(), test_fetch_channel_messages_media_only(), test_fetch_channel_messages_sorts_messages(), test_fetch_channel_messages_stops_at_lookback(), test_fetch_channel_messages_text() (+1 more)

### Community 36 - "DefaultComposer"
Cohesion: 0.19
Nodes (18): 🔌 Extensibility, Group binding, Prompts, Storage queries, DefaultComposer, _channel(), _group(), test_base_only_no_group_no_channel_extra() (+10 more)

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
Nodes (25): Application-state database and export persistence foundation, Next steps, Scope, Step 1 — database foundation, Step 2 — application lifecycle integration, Step 2 — local verification, Step 3d — fair per-user claim scheduling, Step 3e — delivery-attempt lease fencing (+17 more)

### Community 42 - "validation.py"
Cohesion: 0.19
Nodes (9): PromptsConfig, parse_channel_entry(), parse_channels(), parse_filter_specs(), parse_prompts_config(), validate_channel_group(), validate_channel_id_name(), validate_channel_lookback() (+1 more)

### Community 43 - ".summarize_all"
Cohesion: 0.14
Nodes (4): test_summarize_all_empty(), test_summarize_all_partial_failure(), test_summarize_all_success(), test_summarizer_custom_output_language()

### Community 45 - "ExportWorker"
Cohesion: 0.10
Nodes (13): ExportLeaseLostError, ExportWorker, _create_jobs(), test_shutdown_cancels_handler_after_grace_and_releases_lease(), test_stop_waits_for_active_handlers_to_finish(), handler(), test_worker_cancels_handler_when_lease_is_lost(), test_worker_dispatches_claimed_phase_and_releases_lease() (+5 more)

### Community 47 - "._format_date"
Cohesion: 0.14
Nodes (5): DigestFormatter, main(), test_format_date_english_month_names(), test_format_date_russian_month_names(), test_format_summary_message_uses_output_language()

### Community 48 - "test_grouper.py"
Cohesion: 0.12
Nodes (6): config_with_groups(), config_with_other_group(), grouper(), grouper_english(), TestFallbackGroup, TestGrouperTemperatureOverride

### Community 49 - ".create_digest"
Cohesion: 0.25
Nodes (3): test_create_digest(), test_formatter_without_stats(), test_overview_section_label_uses_output_language()

### Community 50 - "OllamaProvider"
Cohesion: 0.08
Nodes (14): _redact_url(), AsyncContextManager, test_ollama_provider_accepts_reasoning_effort_param(), test_ollama_provider_chat_completion(), test_ollama_provider_debug_logging(), test_ollama_provider_empty_content_raises(), test_ollama_provider_error(), test_ollama_provider_error_body_truncated() (+6 more)

### Community 51 - "capture"
Cohesion: 0.10
Nodes (8): test_channel_with_group_uses_base_group_and_channel_prompt_extra(), test_channel_without_group_uses_base_and_channel_prompt_extra(), test_summarize_channel_applies_prompt_extra(), test_summarize_channel_includes_truncation_note(), test_summarize_channel_prompt_instructs_two_tier_format(), capture(), test_summarize_channel_unknown_channel_uses_default_prompt(), test_summarize_channel_wraps_messages_in_xml_delimiters()

### Community 52 - "ChannelConfig"
Cohesion: 0.11
Nodes (23): Export schema v1 message/source/media defaults — working recommendations, Context (from discovery), Phase 2 — Filter Protocol + Chain, Task 4: FilterConfig parsing, Task 5: Filter chain wiring in core, Task 8: Group binding in config, Archive purpose, Export schema v1 message, source, media, and portability defaults — working recommendations (+15 more)

### Community 53 - "._create_header"
Cohesion: 0.25
Nodes (3): test_create_header(), test_create_header_russian_month_name(), test_create_header_uses_output_language()

### Community 55 - "unit"
Cohesion: 0.08
Nodes (17): test_cleanup_old_digests_default_user_id(), test_cleanup_old_digests_no_messages(), test_cleanup_old_digests_partial_failure(), test_cleanup_old_digests_unauthorized(), test_send_digest_default_user_id(), test_send_digest_error(), test_send_digest_markdown_fallback(), test_send_digest_success() (+9 more)

### Community 58 - "._extract_bullets_from_channel"
Cohesion: 0.11
Nodes (3): _run(), TestExtractAllBullets, TestExtractBulletsFromChannel

### Community 60 - "hooks"
Cohesion: 0.18
Nodes (10): exclude, additional_dependencies, args, exclude, files, id, repos, hooks (+2 more)

### Community 62 - "test_application_delivery.py"
Cohesion: 0.30
Nodes (13): _leased_packaging_job(), _packaging_job(), test_attempt_cannot_be_finished_twice_or_with_started_outcome(), test_cleanup_task_retry_and_terminal_update_are_compare_and_set(), test_cleanup_task_survives_job_deletion_and_can_be_completed(), test_cleanup_tasks_are_created_only_for_owned_jobs(), test_cleanup_tasks_cover_telegram_and_staging_resources(), test_delivery_attempts_are_owner_scoped() (+5 more)

### Community 63 - "Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader"
Cohesion: 0.12
Nodes (14): Config schema additions (all optional), Development Approach, Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader, Filter chain insertion point, Overview, Plugin loader semantics, Post-Completion, Progress Tracking (+6 more)

### Community 64 - "ExportCleanupRepository"
Cohesion: 0.14
Nodes (6): Step 3b implementation update — delivery attempts and cleanup tasks, _cleanup_from_row(), CleanupTaskState, CleanupTaskType, ExportCleanupRepository, ExportCleanupTask

### Community 65 - "test_mcp_config_rejects_invalid"
Cohesion: 0.20
Nodes (6): _mcp_config_file(), test_filter_spec_invalid_dotted_path_raises(), test_mcp_config_explicit(), test_mcp_config_missing_block_defaults(), test_mcp_config_rejects_invalid(), test_prompts_composer_invalid_dotted_path_raises()

### Community 66 - "_build_grouped_parts"
Cohesion: 0.18
Nodes (6): _build_channel_parts(), _build_grouped_parts(), _filter_valid_summaries(), _format_group_messages(), _get_channel_urls(), _summarize_channels()

### Community 67 - "conftest.py"
Cohesion: 0.22
Nodes (9): Code of Conduct, Code Style, Commit Messages, Contributing to Telebrief, Development Setup, Pull Request Process, Questions, Reporting Bugs (+1 more)

### Community 69 - "Summarizer"
Cohesion: 0.13
Nodes (7): Summarizer, test_format_messages_for_prompt(), test_format_messages_includes_link(), test_format_messages_truncate_long(), test_truncate_at_sentence_boundary_hard_truncates_without_punctuation(), test_truncate_at_sentence_boundary_returns_short_text(), test_truncate_at_sentence_boundary_uses_last_sentence()

### Community 70 - "README.md"
Cohesion: 0.09
Nodes (19): Chatbrief — new chat starter, AI-assisted development workflow, 🤖 Bot Commands, 🤝 Contributing, 🙏 Credits, 🛠️ Development & Testing, 🐳 Docker Deployment, ❓ FAQ (+11 more)

### Community 71 - "Personal data export — detailed approved design"
Cohesion: 0.08
Nodes (24): Archive structure, Automatic Telegram delivery retry limits, Cancellation and cleanup, Configurable worker concurrency, Database-backed worker claims and leases, Explicit recovery from ambiguous delivery, Export behavior on account deletion, Export invalidation when included source data is removed — approved (Option A) (+16 more)

### Community 72 - ".send_channel_messages_with_tracking"
Cohesion: 0.14
Nodes (7): test_orphaned_summary_delete_failure(), test_orphaned_summary_deleted_when_all_channels_fail(), test_send_channel_messages_with_tracking(), test_send_channel_messages_with_tracking_default_user_id(), test_send_channel_messages_with_tracking_no_summary(), test_send_channel_messages_with_tracking_unauthorized(), test_summary_sent_before_channel_messages()

### Community 73 - "grouper.py"
Cohesion: 0.14
Nodes (4): DigestGroupConfig, DigestGrouper, GroupedPoint, _normalize_point()

### Community 74 - "contact_links"
Cohesion: 0.33
Nodes (5): blank_issues_enabled, contact_links, about, name, url

### Community 75 - ".__init__"
Cohesion: 0.13
Nodes (8): Task 9: Wire composer into Summarizer, __getattr__(), _load_base_template(), test_load_base_template_contains_language_placeholder(), test_load_base_template_custom_path(), test_load_base_template_default_path_returns_nonempty(), test_load_base_template_missing_file_raises(), test_system_prompt_template_loaded_from_file()

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
Cohesion: 0.12
Nodes (9): Implementation update — application-state database foundation and startup lifecycle, ActiveExportExistsError, ExportMediaOutcome, InvalidExportTransitionError, _normalize_updates(), _require_confirmed_primary_delivery(), _transition_in_transaction(), _validate_worker_id() (+1 more)

### Community 83 - "Telegram Hybrid Ingestion and Multi-User Support"
Cohesion: 0.22
Nodes (9): Acceptance criteria, Documentation and decision tracking, Goal, Important constraints and risks, Manual pending-digest recovery command — approved, Message content privacy in personal exports — approved, Non-goals, Preference, subscription, and source field allowlist — recommended defaults (+1 more)

### Community 84 - "load_class"
Cohesion: 0.24
Nodes (9): load_class(), test_load_class_function_not_class(), test_load_class_missing_attribute(), test_load_class_missing_module(), test_load_class_no_dot_raises(), test_load_class_non_class_attribute(), test_load_class_returns_type(), test_load_class_stdlib_class() (+1 more)

### Community 85 - "TelegramMessageSender"
Cohesion: 0.11
Nodes (7): TelegramMessageSender, test_send_channel_messages_default_user_id(), test_send_channel_messages_long_message(), test_send_channel_messages_success(), test_send_channel_messages_unauthorized(), test_send_channel_messages_with_failure(), test_send_message_with_tracking_markdown_fallback()

### Community 86 - "Current status — 2026-11-02 (authoritative update)"
Cohesion: 0.03
Nodes (79): Account-deletion confirmation flow — approved, AI image-analysis failure behavior — approved, Application-state database validation — developer-reported results, Current status — 2026-11-02 (authoritative update), Daylight-saving schedule behavior — approved, Delivery recovery and diagnostics decisions — consolidated handover, Deterministic image selection at the per-digest limit — approved, Digest behavior and scheduling requirements (+71 more)

### Community 87 - "config/loader.py"
Cohesion: 0.15
Nodes (5): _load_and_validate_env_vars(), parse_digest_settings(), parse_storage_config(), resolve_ai_settings(), validate_channel_groups()

### Community 88 - "Chatbrief — AI-assisted development workflow"
Cohesion: 0.12
Nodes (16): Bug fixing, Chat workflow conventions, Chatbrief — AI-assisted development workflow, Complete the graph artifacts, Feature work — required developer workflow, Goals, Handover contract, How AI assistants should use GitHub (+8 more)

### Community 89 - "Implementation sequence"
Cohesion: 0.17
Nodes (12): Application-state database foundation — implementation status, Configuration and identity constraints, Current persistence behavior, Implementation sequence, Migration proposal — design direction, not an approved schema, Phase 1 findings — verified 2026-10-31, Phase 1 verification scope, Phase 2 — Establish a normalized ingestion boundary (+4 more)

### Community 93 - "Phase 1 export persistence migration proposal — approved for implementation"
Cohesion: 0.18
Nodes (11): Constraints and indexes, Existing constraints, Explicitly out of scope for this migration, `export_cleanup_tasks`, `export_delivery_attempts`, `export_jobs`, Legacy data and compatibility, Migration order and acceptance checks (+3 more)

### Community 94 - "Contributor Covenant Code of Conduct"
Cohesion: 0.17
Nodes (12): 1. Correction, 2. Warning, 3. Temporary Ban, 4. Permanent Ban, Attribution, Contributor Covenant Code of Conduct, Enforcement, Enforcement Guidelines (+4 more)

### Community 95 - "Implementation Steps"
Cohesion: 0.18
Nodes (11): Implementation Steps, Phase 1 — Skeleton + ADR + Plugin Loader, Phase 3 — Prompt Composer + Group Binding, Phase 4 — Storage Read API, Phase 5 — Verification + Documentation, Task 11: Verify acceptance criteria, Task 12: Update documentation, Task 1: ADR document (+3 more)

### Community 96 - "._enforce_length_limit"
Cohesion: 0.20
Nodes (3): test_enforce_length_limit_minor_overage_truncates_at_sentence_boundary(), test_enforce_length_limit_retry_failure_keeps_original_summary(), test_enforce_length_limit_retry_returns_short_summary()

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

### Community 105 - "📊 Example Output"
Cohesion: 0.50
Nodes (4): Channel mode (`digest_mode: "channel"` — default), `dedup_topics` — cross-channel deduplication, 📊 Example Output, Topic mode (`digest_mode: "digest"`)

### Community 106 - "Chatbrief implementation checklist"
Cohesion: 0.15
Nodes (12): Application-state database foundation — steps 1–2, Chatbrief implementation checklist, Completion and handover, Export persistence — Step 3a: job repository and atomic transitions, Export persistence — Step 3b: delivery attempts and cleanup tasks, Export persistence — Step 3c: worker claims and lease fencing, Export persistence — Step 3d: fair per-user claim scheduling, Export persistence — Step 3e: delivery-attempt lease fencing (+4 more)

### Community 107 - "Export report v1 semantics and media-only message handling — recommended defaults"
Cohesion: 0.40
Nodes (5): Export report v1 semantics and media-only message handling — recommended defaults, Message record v1 content rules, Omission records and result, Report counts, Warnings

### Community 109 - "Pull Request"
Cohesion: 0.40
Nodes (4): Checklist, Pull Request, What, Why

### Community 110 - "Security Policy"
Cohesion: 0.40
Nodes (4): Reporting a Vulnerability, Scope Notes, Security Policy, Supported Versions

### Community 114 - "Digest scheduling, incremental windows, and one-time requests"
Cohesion: 0.50
Nodes (4): Digest scheduling, incremental windows, and one-time requests, One-time digest requests, Raw collection mode (no AI summarization), Scheduled digest configuration

### Community 117 - "build_server"
Cohesion: 0.14
Nodes (12): Enabling it, 🔗 MCP Server, Reading a single channel, Security, Tools, read_last_digest(), build_server(), get_channel_messages() (+4 more)

### Community 123 - "ADR 0002: Stored Message History Is Not Proof of Collection Completeness"
Cohesion: 0.40
Nodes (4): ADR 0002: Stored Message History Is Not Proof of Collection Completeness, Consequences, Context, Decision

### Community 129 - "Export report and media manifest validation details — recommended defaults"
Cohesion: 0.67
Nodes (3): Export report and media manifest validation details — recommended defaults, Media manifest integrity and archive paths, Report result, counts, and omission codes

## Knowledge Gaps
- **1 isolated node(s):** `chatbrief`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1218 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **42 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Message` connect `SQLiteBackend` to `test_filters.py`, `test_summarizer.py`, `._summarize_channel`, `message.py`, `Config`, `config/models.py`, `TelegramBot`, `test_message_source.py`, `unit`, `.summarize_all`, `._format_date`, `.create_digest`, `ChannelConfig`, `Summarizer`, `Decisions`, `Current status — 2026-11-02 (authoritative update)`, `os`, `build_server`, `._create_statistics`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Are the 77 inferred relationships involving `load_config()` (e.g. with `main()` and `.initialize()`) actually correct?**
  _`load_config()` has 77 INFERRED edges - model-reasoned connections that need verification._
- **What connects `chatbrief` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `SQLiteBackend` be split into smaller, more focused modules?**
  _Cohesion score 0.07228327228327229 - nodes in this community are weakly interconnected._
- **Why does `Config` connect `Config` to `SQLiteBackend`, `.__init__`, `TelegramBot`, `grouper.py`, `.__init__`, `load_config`, `test_digest.py`, `CommandStatus`, `config/models.py`, `TelegramBot`, `test_ui_strings.py`, `CommandResult`, `._format_date`, `ChannelConfig`, `Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader`, `_build_grouped_parts`, `Summarizer`, `grouper.py`, `.__init__`, `TelegramMessageSender`, `config/loader.py`, `Implementation sequence`, `os`, `ui_strings.py`, `build_server`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `Message` (e.g. with `Architecture guardrails` and `Architectural decisions to preserve`) actually correct?**
  _`Message` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_filters.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1085972850678733 - nodes in this community are weakly interconnected._