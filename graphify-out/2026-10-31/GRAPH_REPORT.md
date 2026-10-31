# Graph Report - ChatBrief  (2026-10-31)

## Corpus Check
- 104 files · ~76,379 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 8, .example 2, .toml 2)

## Summary
- 2117 nodes · 4790 edges · 114 communities (81 shown, 33 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 911 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3856ba55`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SQLiteBackend
- _channel
- grouper.py
- TelegramMessageSource
- test_utils.py
- _make_update
- load_config
- StorageBackend
- test_scheduler.py
- with
- test_digest.py
- pytest
- test_telegram.py
- Platform
- test_mcp_server.py
- validation.py
- CommandService
- digest/builder.py
- with
- AsyncContextManager
- Summarizer
- test_telegram_bot.py
- DefaultComposer
- asyncio
- test_summarizer.py
- unit
- telegram_sender.py
- CommandResult
- unit
- Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader
- test_ui_strings.py
- telebrief
- ExtractedBullet
- TestParseGroupedResponse
- main.py
- ChannelConfig
- attributes
- feature_request.yml
- TelegramBot
- _make_command_service
- summarizer.py
- escape_xml_delimiters
- Message
- load_class
- unit
- ._extract_bullets_from_channel
- OllamaProvider
- utils.py
- unit
- DigestScheduler
- package.json
- asyncio
- test_grouper.py
- .format_group_summary_message
- hooks
- AGENTS.md
- build_server
- Storage Layer: SQLite (default) + Postgres (advanced)
- Telebrief Landing Page
- test_mcp_config_rejects_invalid
- ._format_date
- create_session.py
- Config
- config/models.py
- README.md
- ._create_header
- .format_channel_message
- test_load_config_invalid_output_language
- contact_links
- tsconfig.json
- ._create_channel_section
- test_run_without_application
- test_load_config_digest_groups_non_string_fields
- test_handle_cleanup_messages_use_output_language
- test_handle_cleanup_rate_limited
- test_handle_digest_exception
- index.astro
- test_handle_status_unauthorized
- test_handle_status_displays_command_service_result
- test_handle_help_unauthorized
- Chatbrief — current project handover
- DigestFormatter
- Chatbrief — AI-assisted development workflow
- unit
- create_session.sh script
- Deployment Guide for Telebrief Landing Page
- Contributor Covenant Code of Conduct
- Chatbrief — AI development guide
- Chatbrief — persistent project context
- test_formatter.py
- Graphify — local CLI and Git-shared code graph
- Chatbrief implementation checklist
- If the hook produced a new graph diff, review and commit it.
- Pull Request
- Security Policy
- chatbrief
- 📊 Example Output
- 🗄️ Persistent Storage
- TelegramMessageSender

## God Nodes (most connected - your core abstractions)
1. `load_config()` - 96 edges
2. `Summarizer` - 65 edges
3. `Message` - 57 edges
4. `TelegramBot` - 57 edges
5. `Config` - 56 edges
6. `TelegramMessageSender` - 54 edges
7. `ChannelConfig` - 51 edges
8. `DigestFormatter` - 50 edges
9. `MessageSource` - 42 edges
10. `_make_command_service()` - 40 edges

## Surprising Connections (you probably didn't know these)
- `Task 3: MessageFilter Protocol + builtins` --references--> `MessageFilter`  [INFERRED]
  docs/plans/completed/20260430-extensibility-architecture.md → src/chatbrief/extensions/filters.py
- `Negative / Risks` --references--> `ChannelConfig`  [INFERRED]
  docs/adr/0001-extensibility-architecture.md → src/chatbrief/config/models.py
- `Config schema additions (all optional)` --references--> `ChannelConfig`  [INFERRED]
  docs/plans/completed/20260430-extensibility-architecture.md → src/chatbrief/config/models.py
- `Task 7: PromptComposer Protocol + DefaultComposer` --references--> `PromptComposer`  [INFERRED]
  docs/plans/completed/20260430-extensibility-architecture.md → src/chatbrief/extensions/prompts.py
- `Option B: Subclass Extension` --references--> `Summarizer`  [INFERRED]
  docs/adr/0001-extensibility-architecture.md → src/chatbrief/summarizer.py

## Import Cycles
- None detected.

## Communities (114 total, 33 thin omitted)

### Community 0 - "SQLiteBackend"
Cohesion: 0.10
Nodes (17): Task 10: Extend StorageBackend Protocol, Implementation Steps, Task 1: Add StorageConfig to config_loader.py, Task 2: Create src/storage.py, Task 3: Wire storage into _collect_messages(), Task 4: Update requirements.txt and config.yaml.example, Task 5: Add Postgres tests (env-gated) and tighten coverage, Task 6: Verify acceptance criteria (+9 more)

### Community 1 - "_channel"
Cohesion: 0.26
Nodes (15): KeywordFilter, MinLengthFilter, _channel(), _make_message(), test_keyword_empty_input(), test_keyword_exclude_removes_message(), test_keyword_include_and_exclude(), test_keyword_include_case_insensitive() (+7 more)

### Community 2 - "grouper.py"
Cohesion: 0.09
Nodes (6): validate_channel_groups(), _format_group_messages(), _order_groups(), _qg_has_concrete_entity(), get_month_names(), get_ui_strings()

### Community 3 - "TelegramMessageSource"
Cohesion: 0.06
Nodes (10): main(), TelegramMessageSource, async_messages(), message_source(), test_fetch_channel_messages_empty_without_media(), test_fetch_channel_messages_media_only(), test_fetch_channel_messages_sorts_messages(), test_fetch_channel_messages_stops_at_lookback() (+2 more)

### Community 4 - "test_utils.py"
Cohesion: 0.10
Nodes (13): split_message(), test_clear_digest_message_ids_no_file(), test_get_digest_message_ids_invalid_json(), test_get_digest_message_ids_no_file(), test_get_lookback_time(), test_save_and_get_digest_message_ids(), test_save_digest_message_ids_multiple_users(), test_setup_logging_debug_level() (+5 more)

### Community 5 - "_make_update"
Cohesion: 0.14
Nodes (7): _make_update(), test_handle_digest_rate_limited(), test_handle_digest_success_message_uses_output_language(), test_handle_help_without_message(), test_handle_help_without_user(), test_handle_status_uses_output_language(), test_handle_status_without_user()

### Community 6 - "load_config"
Cohesion: 0.08
Nodes (45): load_config(), _storage_config_file(), test_channel_group_field_parsed(), test_channel_group_localized_other_accepted(), test_channel_group_none_by_default(), test_channel_group_null_yaml_is_none(), test_channel_group_other_accepted(), test_digest_group_config_equality_with_prompt_extra() (+37 more)

### Community 7 - "StorageBackend"
Cohesion: 0.10
Nodes (17): ADR 0001: Extensibility Architecture — Filters, Prompts, Storage Read API, Plugin Loader, Alternatives Rejected, Consequences, Context, Decision, Migration, Negative / Risks, Option B: Subclass Extension (+9 more)

### Community 8 - "test_scheduler.py"
Cohesion: 0.07
Nodes (33): Code of Conduct, Code Style, Commit Messages, Contributing to Telebrief, Development Setup, Pull Request Process, Questions, Reporting Bugs (+25 more)

### Community 9 - "with"
Cohesion: 0.05
Nodes (49): name, needs, runs-on, steps, jobs, build, lint, security (+41 more)

### Community 10 - "test_digest.py"
Cohesion: 0.07
Nodes (51): Filter chain insertion point, Phase 2 — Filter Protocol + Chain, Task 3: MessageFilter Protocol + builtins, Task 4: FilterConfig parsing, Task 5: Filter chain wiring in core, FilterSpec, StorageConfig, _apply_filters() (+43 more)

### Community 11 - "pytest"
Cohesion: 0.06
Nodes (22): test_channel_unknown_group_error_lists_bad_channel(), test_channel_unknown_group_raises(), test_digest_group_prompt_extra_non_string_raises(), test_filter_spec_channel_invalid_class_path_raises(), test_filter_spec_missing_class_path_raises(), test_filter_spec_non_dict_config_raises(), test_filter_spec_non_mapping_item_raises(), test_filter_spec_non_string_class_path_raises() (+14 more)

### Community 12 - "test_telegram.py"
Cohesion: 0.10
Nodes (38): make_source(), test_connect_dialog_cache_failure(), test_connect_missing_session(), test_connect_success(), test_connect_unauthorized(), test_disconnect(), test_fetch_channel_messages_error(), test_fetch_channel_messages_private_entity() (+30 more)

### Community 13 - "Platform"
Cohesion: 0.25
Nodes (5): Platform, test_create_bot_injects_command_service_and_sets_up_application(), test_create_bot_rejects_unimplemented_bale(), test_create_services_rejects_unimplemented_bale(), test_create_services_uses_telegram_adapters()

### Community 14 - "test_mcp_server.py"
Cohesion: 0.09
Nodes (17): message_source(), server(), test_get_channel_messages_defaults(), test_get_channel_messages_renders_messages(), test_get_channel_messages_reports_empty_result(), test_get_channel_messages_surfaces_unknown_channel(), test_get_digest_defaults_to_24_hours(), test_get_digest_rejects_out_of_range_hours() (+9 more)

### Community 15 - "validation.py"
Cohesion: 0.10
Nodes (16): McpConfig, PromptsConfig, parse_channel_entry(), parse_channels(), parse_digest_settings(), parse_filter_specs(), parse_mcp_config(), parse_platform() (+8 more)

### Community 16 - "CommandService"
Cohesion: 0.10
Nodes (16): CommandStatus, english_config(), _make_command_service(), test_cleanup_failure(), test_cleanup_rate_limited(), test_cleanup_success(), test_digest_exception(), test_digest_failure() (+8 more)

### Community 17 - "digest/builder.py"
Cohesion: 0.09
Nodes (5): _build_grouped_parts(), _filter_valid_summaries(), DigestGrouper, GroupedPoint, TestGroupSummaries

### Community 18 - "with"
Cohesion: 0.07
Nodes (29): name, permissions, runs-on, steps, env, IMAGE_NAME, REGISTRY, jobs (+21 more)

### Community 19 - "AsyncContextManager"
Cohesion: 0.14
Nodes (11): AnthropicProvider, AsyncContextManager, test_anthropic_provider_accepts_reasoning_effort_param(), test_anthropic_provider_chat_completion(), test_anthropic_provider_empty_content_array_raises(), test_anthropic_provider_error(), test_anthropic_provider_error_body_truncated(), test_anthropic_provider_logs_response_metadata() (+3 more)

### Community 20 - "Summarizer"
Cohesion: 0.07
Nodes (8): Task 9: Wire composer into Summarizer, AIProvider, _summarize_channels(), main(), Summarizer, test_enforce_length_limit_retry_failure_keeps_original_summary(), test_summarizer_custom_composer_constructor_type_error(), test_summarizer_custom_composer_invalid_interface()

### Community 21 - "test_telegram_bot.py"
Cohesion: 0.12
Nodes (5): english_config(), test_handle_digest_without_user(), test_rate_limit_message_uses_configured_language(), test_stop_running_application(), test_stop_without_updater()

### Community 22 - "DefaultComposer"
Cohesion: 0.24
Nodes (14): DefaultComposer, _channel(), _group(), test_base_only_no_group_no_channel_extra(), test_base_plus_channel_extra(), test_base_plus_group_extra(), test_base_plus_group_plus_channel_ordering(), test_default_composer_is_prompt_composer() (+6 more)

### Community 23 - "asyncio"
Cohesion: 0.13
Nodes (13): OpenAIProvider, test_openai_provider_chat_completion(), test_openai_provider_empty_string_content_raises(), test_openai_provider_falls_back_to_max_tokens_after_reasoning_effort_retry(), test_openai_provider_falls_back_to_max_tokens_without_reasoning_effort(), test_openai_provider_falls_back_when_reasoning_effort_rejected(), test_openai_provider_length_empty_content_raises_with_guidance(), test_openai_provider_length_with_content_returns_truncated() (+5 more)

### Community 24 - "test_summarizer.py"
Cohesion: 0.03
Nodes (46): TokenBudgetExhaustedError, _make_messages(), test_channel_without_group_uses_base_and_channel_prompt_extra(), test_default_template_path_points_to_existing_file(), test_enforce_length_limit_minor_overage_truncates_at_sentence_boundary(), test_enforce_length_limit_retry_returns_short_summary(), test_format_messages_for_prompt(), test_format_messages_includes_link() (+38 more)

### Community 25 - "unit"
Cohesion: 0.10
Nodes (10): create_provider(), test_create_provider_anthropic(), test_create_provider_anthropic_missing_key(), test_create_provider_case_insensitive(), test_create_provider_ollama(), test_create_provider_openai(), test_create_provider_openai_missing_key(), test_create_provider_unknown() (+2 more)

### Community 27 - "CommandResult"
Cohesion: 0.13
Nodes (4): CommandResult, CommandServiceProtocol, test_handle_cleanup_unauthorized(), test_handle_digest_error_message_uses_output_language()

### Community 28 - "unit"
Cohesion: 0.13
Nodes (7): test_cleanup_rate_limited(), test_handle_cleanup_exception(), test_handle_status_without_message(), test_help_not_rate_limited(), test_run_application_initialization_failure(), test_setup_application(), test_status_not_rate_limited()

### Community 29 - "Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader"
Cohesion: 0.13
Nodes (13): Config schema additions (all optional), Context (from discovery), Development Approach, Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader, Plugin loader semantics, Post-Completion, Progress Tracking, Prompt composition order (+5 more)

### Community 31 - "test_ui_strings.py"
Cohesion: 0.15
Nodes (8): test_all_required_keys_present_for_each_language(), test_digest_group_keys_english_values(), test_digest_group_keys_present_for_each_language(), test_get_ui_strings_english(), test_get_ui_strings_returns_dict(), test_get_ui_strings_russian(), test_get_ui_strings_unknown_language_falls_back_to_english(), test_no_empty_strings_for_any_language()

### Community 32 - "telebrief"
Cohesion: 0.10
Nodes (20): build, container_name, env_file, environment, healthcheck, image, logging, restart (+12 more)

### Community 33 - "ExtractedBullet"
Cohesion: 0.10
Nodes (6): _dedup_extracted(), ExtractedBullet, _normalize_point(), _quality_gate_filter(), TestDedupExtracted, TestQualityGateFilter

### Community 34 - "TestParseGroupedResponse"
Cohesion: 0.08
Nodes (3): TestBuildGroupDefinitions, TestDeterministicDedup, TestParseGroupedResponse

### Community 36 - "ChannelConfig"
Cohesion: 0.12
Nodes (13): Implementation Steps, Phase 1 — Skeleton + ADR + Plugin Loader, Phase 3 — Prompt Composer + Group Binding, Phase 4 — Storage Read API, Phase 5 — Verification + Documentation, Task 11: Verify acceptance criteria, Task 12: Update documentation, Task 1: ADR document (+5 more)

### Community 37 - "attributes"
Cohesion: 0.12
Nodes (16): description, label, options, placeholder, render, value, body, attributes (+8 more)

### Community 40 - "feature_request.yml"
Cohesion: 0.12
Nodes (15): description, label, options, placeholder, body, attributes, id, type (+7 more)

### Community 41 - "TelegramBot"
Cohesion: 0.10
Nodes (13): Architecture guardrails, Current implementation status, Architectural decisions to preserve, Current refactor status (2026-10-30), Chatbrief-specific guardrails, Current architecture, Package/platform refactor status, CommandService (+5 more)

### Community 42 - "_make_command_service"
Cohesion: 0.17
Nodes (6): _make_command_service(), test_handle_cleanup_without_user(), test_handle_digest_processing_message_uses_output_language(), test_handle_digest_unauthorized(), test_setup_bot_menu_uses_output_language(), test_setup_bot_menu_without_application()

### Community 43 - "summarizer.py"
Cohesion: 0.10
Nodes (10): DigestGroupConfig, PromptComposer, __getattr__(), _load_base_template(), test_channel_with_group_uses_base_group_and_channel_prompt_extra(), test_load_base_template_contains_language_placeholder(), test_load_base_template_custom_path(), test_load_base_template_default_path_returns_nonempty() (+2 more)

### Community 44 - "escape_xml_delimiters"
Cohesion: 0.06
Nodes (6): _strip_channel_summary_noise(), escape_xml_delimiters(), TestStripBroaderNoise, TestStripChannelHeader, TestStripSectionTwo, TestEscapeXmlDelimiters

### Community 45 - "Message"
Cohesion: 0.17
Nodes (12): MessageFilter, RegexFilter, Message, test_keyword_filter_is_message_filter(), test_min_length_filter_is_message_filter(), test_regex_default_mode_is_include(), test_regex_empty_input(), test_regex_exclude_mode_removes_matching() (+4 more)

### Community 47 - "load_class"
Cohesion: 0.24
Nodes (10): load_class(), _SampleClass, test_load_class_function_not_class(), test_load_class_missing_attribute(), test_load_class_missing_module(), test_load_class_no_dot_raises(), test_load_class_non_class_attribute(), test_load_class_returns_type() (+2 more)

### Community 48 - "unit"
Cohesion: 0.09
Nodes (16): test_cleanup_old_digests_default_user_id(), test_cleanup_old_digests_no_messages(), test_cleanup_old_digests_unauthorized(), test_send_digest_default_user_id(), test_send_digest_error(), test_send_digest_markdown_fallback(), test_send_digest_success(), test_send_digest_unauthorized() (+8 more)

### Community 49 - "._extract_bullets_from_channel"
Cohesion: 0.07
Nodes (5): _run(), TestClassifyBullets, TestExtractAllBullets, TestExtractBulletsFromChannel, TestGrouperMissingChannelWarning

### Community 50 - "OllamaProvider"
Cohesion: 0.07
Nodes (16): OllamaProvider, _redact_url(), test_ollama_provider_accepts_reasoning_effort_param(), test_ollama_provider_chat_completion(), test_ollama_provider_debug_logging(), test_ollama_provider_empty_content_raises(), test_ollama_provider_error(), test_ollama_provider_error_body_truncated() (+8 more)

### Community 51 - "utils.py"
Cohesion: 0.12
Nodes (9): clear_digest_message_ids(), get_digest_message_ids(), get_lookback_time(), save_digest_message_ids(), test_cleanup_old_digests_deletion_failure(), test_cleanup_old_digests_message_not_found(), test_cleanup_old_digests_partial_failure(), test_cleanup_old_digests_success() (+1 more)

### Community 52 - "unit"
Cohesion: 0.19
Nodes (5): test_formatter_initialization(), test_formatter_without_emojis(), test_pick_emoji_crypto(), test_pick_emoji_default(), test_pick_emoji_tech()

### Community 55 - "package.json"
Cohesion: 0.18
Nodes (10): astro, dependencies, astro@^4.0.0, description, name, scripts, build, dev (+2 more)

### Community 57 - "asyncio"
Cohesion: 0.15
Nodes (6): test_handle_cleanup_failure(), test_handle_cleanup_without_message(), test_handle_digest_without_message(), test_handle_help_uses_output_language(), test_setup_bot_menu_exception(), test_stop_without_application()

### Community 58 - "test_grouper.py"
Cohesion: 0.10
Nodes (7): config_with_groups(), config_with_other_group(), grouper(), grouper_english(), TestFallbackGroup, TestGrouperTemperatureOverride, TestPromptInjectionMitigation

### Community 59 - ".format_group_summary_message"
Cohesion: 0.17
Nodes (4): test_format_group_summary_message(), test_format_group_summary_message_russian(), test_pick_group_emoji_default(), test_pick_group_emoji_known_groups()

### Community 60 - "hooks"
Cohesion: 0.18
Nodes (10): exclude, additional_dependencies, args, exclude, files, id, repos, hooks (+2 more)

### Community 62 - "build_server"
Cohesion: 0.12
Nodes (12): Enabling it, 🔗 MCP Server, Reading a single channel, Security, Tools, build_digest(), build_server(), get_channel_messages() (+4 more)

### Community 63 - "Storage Layer: SQLite (default) + Postgres (advanced)"
Cohesion: 0.20
Nodes (9): Context (from discovery), Development Approach, Overview, Post-Completion, Progress Tracking, Storage Layer: SQLite (default) + Postgres (advanced), Technical Details, Testing Strategy (+1 more)

### Community 64 - "Telebrief Landing Page"
Cohesion: 0.08
Nodes (23): Browser Support, Build, Cloudflare Pages, Colors, Content, Customization, Deployment, Design Features (+15 more)

### Community 65 - "test_mcp_config_rejects_invalid"
Cohesion: 0.20
Nodes (6): _mcp_config_file(), test_filter_spec_invalid_dotted_path_raises(), test_mcp_config_explicit(), test_mcp_config_missing_block_defaults(), test_mcp_config_rejects_invalid(), test_prompts_composer_invalid_dotted_path_raises()

### Community 66 - "._format_date"
Cohesion: 0.20
Nodes (3): test_format_date_english_month_names(), test_format_date_russian_month_names(), test_format_summary_message_uses_output_language()

### Community 68 - "Config"
Cohesion: 0.10
Nodes (5): Config, _build_channel_parts(), build_digest_parts(), _get_channel_urls(), _channel_from_storage()

### Community 69 - "config/models.py"
Cohesion: 0.11
Nodes (5): join_parts(), read_last_digest(), write_last_digest(), generate_and_send_digest(), validate_hours()

### Community 70 - "README.md"
Cohesion: 0.10
Nodes (15): Chatbrief — new chat starter, AI-assisted development workflow, 🤖 Bot Commands, 🤝 Contributing, 🙏 Credits, 🛠️ Development & Testing, 🐳 Docker Deployment, ❓ FAQ (+7 more)

### Community 71 - "._create_header"
Cohesion: 0.25
Nodes (3): test_create_header(), test_create_header_russian_month_name(), test_create_header_uses_output_language()

### Community 72 - ".format_channel_message"
Cohesion: 0.25
Nodes (3): test_format_channel_message_includes_channel_link(), test_format_channel_message_stats_uses_output_language(), test_truncation_message_uses_output_language()

### Community 74 - "contact_links"
Cohesion: 0.33
Nodes (5): blank_issues_enabled, contact_links, about, name, url

### Community 75 - "tsconfig.json"
Cohesion: 0.33
Nodes (5): astro/tsconfigs/strict, compilerOptions, jsx, jsxImportSource, extends

### Community 86 - "Chatbrief — current project handover"
Cohesion: 0.29
Nodes (6): Chatbrief — current project handover, Graphify state, Immediate next action, Product purpose, Remaining before the refactor can be declared complete, Workflow and safety rules

### Community 87 - "DigestFormatter"
Cohesion: 0.17
Nodes (7): DigestFormatter, main(), test_create_digest(), test_create_statistics(), test_create_statistics_uses_output_language(), test_formatter_without_stats(), test_overview_section_label_uses_output_language()

### Community 88 - "Chatbrief — AI-assisted development workflow"
Cohesion: 0.12
Nodes (16): Bug fixing, Chat workflow conventions, Chatbrief — AI-assisted development workflow, Complete the graph artifacts, Feature work — required developer workflow, Goals, Handover contract, How AI assistants should use GitHub (+8 more)

### Community 89 - "unit"
Cohesion: 0.11
Nodes (9): test_orphaned_summary_delete_failure(), test_orphaned_summary_deleted_when_all_channels_fail(), test_send_channel_messages_with_tracking(), test_send_channel_messages_with_tracking_default_user_id(), test_send_channel_messages_with_tracking_no_summary(), test_send_channel_messages_with_tracking_unauthorized(), test_send_summary_message_error(), test_send_summary_message_markdown_fallback() (+1 more)

### Community 91 - "Deployment Guide for Telebrief Landing Page"
Cohesion: 0.14
Nodes (13): Build succeeds but site doesn't update, Build Verification, Cloudflare Pages Deployment, Configuration in Cloudflare Dashboard, Deployment Checklist, Deployment Guide for Telebrief Landing Page, Error: "Expected output file at workers-site/index.js", GitHub Pages Deployment (+5 more)

### Community 94 - "Contributor Covenant Code of Conduct"
Cohesion: 0.17
Nodes (12): 1. Correction, 2. Warning, 3. Temporary Ban, 4. Permanent Ban, Attribution, Contributor Covenant Code of Conduct, Enforcement, Enforcement Guidelines (+4 more)

### Community 97 - "Chatbrief — AI development guide"
Cohesion: 0.18
Nodes (11): Chat workflow conventions, Chatbrief — AI development guide, End-of-session handover, Git and change safety, Graph-assisted development (Graphify), Graphify artifact completion and hook verification, Project facts and stack, Project workflow helper (+3 more)

### Community 100 - "Chatbrief — persistent project context"
Cohesion: 0.22
Nodes (8): Chatbrief — persistent project context, Development workflow contract, Graphify — local CLI, pj automation, and Git-shared graph, Product and stack, Project-local workflow, Read first, Safety, Tooling and commands

### Community 101 - "test_formatter.py"
Cohesion: 0.16
Nodes (5): english_config(), test_format_group_message_empty_points(), test_format_group_message_no_source(), test_format_group_message_no_truncation(), test_format_group_message_output()

### Community 103 - "Graphify — local CLI and Git-shared code graph"
Cohesion: 0.25
Nodes (8): Build the initial graph, Git automation, Graphify — local CLI and Git-shared code graph, Install the standalone CLI, Query the local graph, Recommended source-to-GitHub cycle, Update and synchronize, What is shared through Git

### Community 106 - "Chatbrief implementation checklist"
Cohesion: 0.33
Nodes (5): Chatbrief implementation checklist, Completion and handover, Implementation, Inspect and decide before implementation, Validation

### Community 108 - "If the hook produced a new graph diff, review and commit it."
Cohesion: 0.40
Nodes (5): Complete the report and visualization, How ChatGPT uses the graph from GitHub, If the hook produced a new graph diff, review and commit it., Official references, pj graph command reference

### Community 109 - "Pull Request"
Cohesion: 0.40
Nodes (4): Checklist, Pull Request, What, Why

### Community 110 - "Security Policy"
Cohesion: 0.40
Nodes (4): Reporting a Vulnerability, Scope Notes, Security Policy, Supported Versions

### Community 121 - "📊 Example Output"
Cohesion: 0.50
Nodes (4): Channel mode (`digest_mode: "channel"` — default), `dedup_topics` — cross-channel deduplication, 📊 Example Output, Topic mode (`digest_mode: "digest"`)

### Community 123 - "🗄️ Persistent Storage"
Cohesion: 0.50
Nodes (4): 🗄️ Persistent Storage, PostgreSQL (optional backend), Schema, SQLite (default backend)

### Community 131 - "TelegramMessageSender"
Cohesion: 0.11
Nodes (7): TelegramMessageSender, test_send_channel_messages_default_user_id(), test_send_channel_messages_long_message(), test_send_channel_messages_success(), test_send_channel_messages_unauthorized(), test_send_channel_messages_with_failure(), test_send_message_with_tracking_markdown_fallback()

## Knowledge Gaps
- **2 isolated node(s):** `chatbrief`, `astro/tsconfigs/strict`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 981 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Config` connect `Config` to `SQLiteBackend`, `grouper.py`, `main.py`, `ChannelConfig`, `config/models.py`, `load_config`, `TelegramMessageSource`, `test_scheduler.py`, `TelegramBot`, `test_digest.py`, `summarizer.py`, `validation.py`, `digest/builder.py`, `Summarizer`, `DigestScheduler`, `telegram_sender.py`, `Extensibility Architecture: Filters, Prompts, Storage Read API, Plugin Loader`, `build_server`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 73 inferred relationships involving `load_config()` (e.g. with `.initialize()` and `test_channel_group_field_parsed()`) actually correct?**
  _`load_config()` has 73 INFERRED edges - model-reasoned connections that need verification._
- **What connects `chatbrief`, `astro/tsconfigs/strict` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `SQLiteBackend` be split into smaller, more focused modules?**
  _Cohesion score 0.10062111801242236 - nodes in this community are weakly interconnected._
- **Why does `Summarizer` connect `Summarizer` to `ChannelConfig`, `config/models.py`, `Config`, `StorageBackend`, `summarizer.py`, `Message`, `DefaultComposer`, `test_summarizer.py`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 52 inferred relationships involving `Summarizer` (e.g. with `Option B: Subclass Extension` and `Task 9: Wire composer into Summarizer`) actually correct?**
  _`Summarizer` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Should `grouper.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0873015873015873 - nodes in this community are weakly interconnected._