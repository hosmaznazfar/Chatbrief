# Graph Report - ChatBrief  (2026-10-31)

## Corpus Check
- 96 files · ~70,237 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 7, .example 2, .toml 1)

## Summary
- 2041 nodes · 4828 edges · 104 communities (70 shown, 34 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 1013 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6f2ead88`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SQLiteBackend
- Message
- Config
- TelegramMessageSource
- test_utils.py
- test_handle_help_unauthorized
- load_config
- test_summarizer.py
- test_scheduler.py
- with
- test_digest.py
- pytest
- test_telegram.py
- Platform
- test_mcp_server.py
- validation.py
- CommandService
- ._classify_bullets
- with
- AsyncContextManager
- Summarizer
- test_telegram_bot.py
- DefaultComposer
- asyncio
- ._summarize_channel
- unit
- escape_xml_delimiters
- ._extract_bullets_from_channel
- unit
- capture
- test_ui_strings.py
- telebrief
- ExtractedBullet
- TestParseGroupedResponse
- test_config.py
- ._enforce_length_limit
- attributes
- CommandResult
- feature_request.yml
- TelegramBot
- _make_command_service
- summarizer.py
- test_grouper.py
- Contributing to Telebrief
- ai_providers.py
- load_class
- unit
- .group_summaries
- OllamaProvider
- test_cleanup_old_digests_success
- CommandStatus
- TelegramBot
- ._truncate_at_sentence_boundary
- test_send_summary_message_error
- ⚙️ Per-Channel Configuration
- ._build_fallback_group
- hooks
- AGENTS.md
- build_server
- test_language_instruction_only_in_system_prompt
- test_summarizer_uses_composer_output
- test_mcp_config_rejects_invalid
- test_cleanup_old_digests_deletion_failure
- telegram_source.py
- config/models.py
- README.md
- test_load_config_no_channels
- test_load_config_anthropic_provider_missing_key
- test_load_config_invalid_output_language
- contact_links
- test_load_config_null_ai_provider
- test_load_config_invalid_digest_mode
- test_load_config_invalid_lookback_hours_type
- test_load_config_invalid_lookback_hours_value
- test_load_config_missing_env_vars
- Chatbrief — current project handover
- DigestFormatter
- Chatbrief — AI-assisted development workflow
- unit
- create_session.sh script
- Contributor Covenant Code of Conduct
- Chatbrief — AI development guide
- Chatbrief — persistent project context
- english_config
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
3. `Message` - 60 edges
4. `Config` - 58 edges
5. `TelegramBot` - 57 edges
6. `TelegramMessageSender` - 55 edges
7. `DigestFormatter` - 53 edges
8. `ChannelConfig` - 51 edges
9. `MessageSource` - 42 edges
10. `_make_command_service()` - 42 edges

## Surprising Connections (you probably didn't know these)
- `Task 3: MessageFilter Protocol + builtins` --references--> `MessageFilter`  [INFERRED]
  docs/plans/completed/20260430-extensibility-architecture.md → src/chatbrief/extensions/filters.py
- `Option B: Subclass Extension` --references--> `Summarizer`  [INFERRED]
  docs/adr/0001-extensibility-architecture.md → src/chatbrief/summarizer.py
- `Context` --references--> `AIProvider`  [INFERRED]
  docs/adr/0001-extensibility-architecture.md → src/chatbrief/ai_providers.py
- `Overview` --references--> `AIProvider`  [INFERRED]
  docs/plans/completed/20260430-extensibility-architecture.md → src/chatbrief/ai_providers.py
- `Package/platform refactor status` --references--> `CommandService`  [INFERRED]
  docs/handover/current.md → src/chatbrief/commands/service.py

## Import Cycles
- None detected.

## Communities (104 total, 34 thin omitted)

### Community 0 - "SQLiteBackend"
Cohesion: 0.08
Nodes (27): Task 10: Extend StorageBackend Protocol, Context (from discovery), Development Approach, Implementation Steps, Overview, Post-Completion, Progress Tracking, Storage Layer: SQLite (default) + Postgres (advanced) (+19 more)

### Community 1 - "Message"
Cohesion: 0.05
Nodes (65): ADR 0001: Extensibility Architecture — Filters, Prompts, Storage Read API, Plugin Loader, Alternatives Rejected, Consequences, Context, Decision, Migration, Negative / Risks, Option B: Subclass Extension (+57 more)

### Community 2 - "Config"
Cohesion: 0.07
Nodes (15): Config, _build_channel_parts(), build_digest_parts(), _build_grouped_parts(), _filter_valid_summaries(), _format_group_messages(), _get_channel_urls(), join_parts() (+7 more)

### Community 3 - "TelegramMessageSource"
Cohesion: 0.08
Nodes (10): main(), TelegramMessageSource, async_messages(), message_source(), test_fetch_channel_messages_empty_without_media(), test_fetch_channel_messages_media_only(), test_fetch_channel_messages_sorts_messages(), test_fetch_channel_messages_stops_at_lookback() (+2 more)

### Community 4 - "test_utils.py"
Cohesion: 0.07
Nodes (21): main(), clear_digest_message_ids(), get_digest_message_ids(), get_lookback_time(), save_digest_message_ids(), setup_logging(), split_message(), test_cleanup_old_digests_message_not_found() (+13 more)

### Community 5 - "test_handle_help_unauthorized"
Cohesion: 0.15
Nodes (5): test_handle_help_unauthorized(), test_handle_help_uses_output_language(), test_handle_help_without_message(), test_handle_help_without_user(), test_help_not_rate_limited()

### Community 6 - "load_config"
Cohesion: 0.07
Nodes (30): load_config(), test_channel_group_field_parsed(), test_channel_group_none_by_default(), test_channel_group_null_yaml_is_none(), test_channel_group_other_accepted(), test_digest_group_prompt_extra_defaults_empty(), test_digest_group_prompt_extra_parsed(), test_filter_spec_channel_empty_list_explicit_noop() (+22 more)

### Community 7 - "test_summarizer.py"
Cohesion: 0.09
Nodes (15): _make_messages(), test_default_template_path_points_to_existing_file(), test_format_messages_for_prompt(), test_format_messages_includes_link(), test_format_messages_prompt_always_includes_at_least_one(), test_format_messages_prompt_no_truncation_within_budget(), test_format_messages_prompt_truncation_keeps_recent(), test_format_messages_prompt_warns_on_truncation() (+7 more)

### Community 8 - "test_scheduler.py"
Cohesion: 0.09
Nodes (26): Running Tests and Checks, Testing conventions, Task 4: FilterConfig parsing, Settings, mock_env_vars(), mock_logger(), sample_config(), sample_messages() (+18 more)

### Community 9 - "with"
Cohesion: 0.06
Nodes (41): name, needs, runs-on, steps, jobs, build, lint, security (+33 more)

### Community 10 - "test_digest.py"
Cohesion: 0.06
Nodes (51): Filter chain insertion point, Phase 2 — Filter Protocol + Chain, Task 3: MessageFilter Protocol + builtins, Task 5: Filter chain wiring in core, FilterSpec, _apply_filters(), _channel_from_storage(), collect_channel_messages() (+43 more)

### Community 11 - "pytest"
Cohesion: 0.09
Nodes (16): test_channel_unknown_group_error_lists_bad_channel(), test_channel_unknown_group_raises(), test_digest_group_prompt_extra_non_string_raises(), test_filter_spec_channel_invalid_class_path_raises(), test_filter_spec_missing_class_path_raises(), test_filter_spec_non_dict_config_raises(), test_filter_spec_non_mapping_item_raises(), test_filter_spec_non_string_class_path_raises() (+8 more)

### Community 12 - "test_telegram.py"
Cohesion: 0.11
Nodes (38): make_source(), test_connect_dialog_cache_failure(), test_connect_missing_session(), test_connect_success(), test_connect_unauthorized(), test_disconnect(), test_fetch_channel_messages_error(), test_fetch_channel_messages_private_entity() (+30 more)

### Community 13 - "Platform"
Cohesion: 0.25
Nodes (5): Platform, test_create_bot_injects_command_service_and_sets_up_application(), test_create_bot_rejects_unimplemented_bale(), test_create_services_rejects_unimplemented_bale(), test_create_services_uses_telegram_adapters()

### Community 14 - "test_mcp_server.py"
Cohesion: 0.09
Nodes (17): message_source(), server(), test_get_channel_messages_defaults(), test_get_channel_messages_renders_messages(), test_get_channel_messages_reports_empty_result(), test_get_channel_messages_surfaces_unknown_channel(), test_get_digest_defaults_to_24_hours(), test_get_digest_rejects_out_of_range_hours() (+9 more)

### Community 15 - "validation.py"
Cohesion: 0.09
Nodes (16): McpConfig, PromptsConfig, parse_channel_entry(), parse_channels(), parse_digest_settings(), parse_filter_specs(), parse_mcp_config(), parse_platform() (+8 more)

### Community 16 - "CommandService"
Cohesion: 0.11
Nodes (15): english_config(), _make_command_service(), test_cleanup_failure(), test_cleanup_rate_limited(), test_cleanup_success(), test_digest_exception(), test_digest_failure(), test_digest_rate_limited() (+7 more)

### Community 18 - "with"
Cohesion: 0.07
Nodes (29): name, permissions, runs-on, steps, env, IMAGE_NAME, REGISTRY, jobs (+21 more)

### Community 19 - "AsyncContextManager"
Cohesion: 0.13
Nodes (11): AnthropicProvider, AsyncContextManager, test_anthropic_provider_accepts_reasoning_effort_param(), test_anthropic_provider_chat_completion(), test_anthropic_provider_empty_content_array_raises(), test_anthropic_provider_error(), test_anthropic_provider_error_body_truncated(), test_anthropic_provider_logs_response_metadata() (+3 more)

### Community 20 - "Summarizer"
Cohesion: 0.12
Nodes (7): Task 9: Wire composer into Summarizer, main(), Summarizer, test_summarize_all_empty(), test_summarize_all_partial_failure(), test_summarize_all_success(), test_summarizer_custom_output_language()

### Community 21 - "test_telegram_bot.py"
Cohesion: 0.12
Nodes (10): english_config(), _make_update(), test_cleanup_rate_limited(), test_handle_cleanup_exception(), test_handle_cleanup_failure(), test_handle_cleanup_messages_use_output_language(), test_handle_cleanup_rate_limited(), test_handle_cleanup_unauthorized() (+2 more)

### Community 22 - "DefaultComposer"
Cohesion: 0.25
Nodes (14): DefaultComposer, _channel(), _group(), test_base_only_no_group_no_channel_extra(), test_base_plus_channel_extra(), test_base_plus_group_extra(), test_base_plus_group_plus_channel_ordering(), test_default_composer_is_prompt_composer() (+6 more)

### Community 23 - "asyncio"
Cohesion: 0.13
Nodes (13): OpenAIProvider, test_openai_provider_chat_completion(), test_openai_provider_empty_string_content_raises(), test_openai_provider_falls_back_to_max_tokens_after_reasoning_effort_retry(), test_openai_provider_falls_back_to_max_tokens_without_reasoning_effort(), test_openai_provider_falls_back_when_reasoning_effort_rejected(), test_openai_provider_length_empty_content_raises_with_guidance(), test_openai_provider_length_with_content_returns_truncated() (+5 more)

### Community 24 - "._summarize_channel"
Cohesion: 0.08
Nodes (14): test_summarize_channel_applies_prompt_extra(), test_summarize_channel_detects_output_over_3500_chars(), test_summarize_channel_double_budget_exhaustion_propagates(), test_summarize_channel_error(), test_summarize_channel_length_retry_exception_falls_through_to_truncation(), test_summarize_channel_no_retry_on_success(), test_summarize_channel_no_retry_when_under_limit(), test_summarize_channel_passes_max_prompt_chars_to_formatter() (+6 more)

### Community 25 - "unit"
Cohesion: 0.11
Nodes (12): create_provider(), test_create_provider_anthropic(), test_create_provider_anthropic_missing_key(), test_create_provider_case_insensitive(), test_create_provider_ollama(), test_create_provider_openai(), test_create_provider_openai_missing_key(), test_create_provider_unknown() (+4 more)

### Community 27 - "._extract_bullets_from_channel"
Cohesion: 0.10
Nodes (3): _strip_channel_summary_noise(), TestExtractBulletsFromChannel, TestStripBroaderNoise

### Community 28 - "unit"
Cohesion: 0.14
Nodes (7): test_handle_status_displays_command_service_result(), test_handle_status_unauthorized(), test_handle_status_uses_output_language(), test_handle_status_without_message(), test_handle_status_without_user(), test_setup_application(), test_status_not_rate_limited()

### Community 29 - "capture"
Cohesion: 0.10
Nodes (8): test_channel_with_group_uses_base_group_and_channel_prompt_extra(), test_channel_without_group_uses_base_and_channel_prompt_extra(), test_summarize_channel_includes_truncation_note(), test_summarize_channel_prompt_instructs_two_tier_format(), capture(), test_summarize_channel_retry_includes_shorten_instruction(), test_summarize_channel_unknown_channel_uses_default_prompt(), test_summarize_channel_wraps_messages_in_xml_delimiters()

### Community 31 - "test_ui_strings.py"
Cohesion: 0.15
Nodes (8): test_all_required_keys_present_for_each_language(), test_digest_group_keys_english_values(), test_digest_group_keys_present_for_each_language(), test_get_ui_strings_english(), test_get_ui_strings_returns_dict(), test_get_ui_strings_russian(), test_get_ui_strings_unknown_language_falls_back_to_english(), test_no_empty_strings_for_any_language()

### Community 32 - "telebrief"
Cohesion: 0.10
Nodes (20): build, container_name, env_file, environment, healthcheck, image, logging, restart (+12 more)

### Community 33 - "ExtractedBullet"
Cohesion: 0.10
Nodes (6): _dedup_extracted(), ExtractedBullet, _qg_has_concrete_entity(), _quality_gate_filter(), TestDedupExtracted, TestQualityGateFilter

### Community 34 - "TestParseGroupedResponse"
Cohesion: 0.08
Nodes (3): TestBuildGroupDefinitions, TestDeterministicDedup, TestParseGroupedResponse

### Community 35 - "test_config.py"
Cohesion: 0.16
Nodes (16): _storage_config_file(), test_channel_group_localized_other_accepted(), test_digest_group_config_equality_with_prompt_extra(), test_filter_spec_channel_null_uses_global(), test_prompts_config_explicit_values(), test_prompts_config_strips_whitespace(), test_storage_config_empty_path_raises(), test_storage_config_enabled_not_bool_raises() (+8 more)

### Community 36 - "._enforce_length_limit"
Cohesion: 0.14
Nodes (3): test_enforce_length_limit_minor_overage_truncates_at_sentence_boundary(), test_enforce_length_limit_retry_failure_keeps_original_summary(), test_enforce_length_limit_retry_returns_short_summary()

### Community 37 - "attributes"
Cohesion: 0.12
Nodes (16): description, label, options, placeholder, render, value, body, attributes (+8 more)

### Community 40 - "feature_request.yml"
Cohesion: 0.12
Nodes (15): description, label, options, placeholder, body, attributes, id, type (+7 more)

### Community 41 - "TelegramBot"
Cohesion: 0.08
Nodes (14): Architecture guardrails, Current implementation status, Architectural decisions to preserve, Current refactor status (2026-10-30), Chatbrief-specific guardrails, Current architecture, ChatbriefApp, main() (+6 more)

### Community 42 - "_make_command_service"
Cohesion: 0.14
Nodes (11): _make_command_service(), test_handle_digest_error_message_uses_output_language(), test_handle_digest_exception(), test_handle_digest_processing_message_uses_output_language(), test_handle_digest_rate_limited(), test_handle_digest_success_message_uses_output_language(), test_handle_digest_unauthorized(), test_handle_digest_without_message() (+3 more)

### Community 43 - "summarizer.py"
Cohesion: 0.10
Nodes (13): Phase 3 — Prompt Composer + Group Binding, Task 6: Extract base prompt template, Task 7: PromptComposer Protocol + DefaultComposer, Task 8: Group binding in config, DigestGroupConfig, PromptComposer, __getattr__(), _load_base_template() (+5 more)

### Community 44 - "test_grouper.py"
Cohesion: 0.08
Nodes (7): config_with_groups(), config_with_other_group(), grouper(), grouper_english(), TestPromptInjectionMitigation, TestStripChannelHeader, TestStripSectionTwo

### Community 45 - "Contributing to Telebrief"
Cohesion: 0.22
Nodes (9): Code of Conduct, Code Style, Commit Messages, Contributing to Telebrief, Development Setup, Pull Request Process, Questions, Reporting Bugs (+1 more)

### Community 46 - "ai_providers.py"
Cohesion: 0.15
Nodes (3): AIProvider, TokenBudgetExhaustedError, test_ollama_provider_length_empty_content_raises_with_guidance()

### Community 47 - "load_class"
Cohesion: 0.24
Nodes (10): load_class(), _SampleClass, test_load_class_function_not_class(), test_load_class_missing_attribute(), test_load_class_missing_module(), test_load_class_no_dot_raises(), test_load_class_non_class_attribute(), test_load_class_returns_type() (+2 more)

### Community 48 - "unit"
Cohesion: 0.08
Nodes (17): test_cleanup_old_digests_default_user_id(), test_cleanup_old_digests_no_messages(), test_cleanup_old_digests_partial_failure(), test_cleanup_old_digests_unauthorized(), test_send_digest_default_user_id(), test_send_digest_error(), test_send_digest_markdown_fallback(), test_send_digest_success() (+9 more)

### Community 49 - ".group_summaries"
Cohesion: 0.08
Nodes (5): _run(), TestExtractAllBullets, TestGrouperMissingChannelWarning, TestGrouperTemperatureOverride, TestGroupSummaries

### Community 50 - "OllamaProvider"
Cohesion: 0.10
Nodes (13): OllamaProvider, _redact_url(), test_ollama_provider_accepts_reasoning_effort_param(), test_ollama_provider_chat_completion(), test_ollama_provider_debug_logging(), test_ollama_provider_empty_content_raises(), test_ollama_provider_error(), test_ollama_provider_error_body_truncated() (+5 more)

### Community 53 - "TelegramBot"
Cohesion: 0.10
Nodes (9): Package/platform refactor status, TelegramBot, test_run_without_application(), test_setup_bot_menu_exception(), test_setup_bot_menu_uses_output_language(), test_setup_bot_menu_without_application(), test_stop_running_application(), test_stop_without_application() (+1 more)

### Community 54 - "._truncate_at_sentence_boundary"
Cohesion: 0.25
Nodes (3): test_truncate_at_sentence_boundary_hard_truncates_without_punctuation(), test_truncate_at_sentence_boundary_returns_short_text(), test_truncate_at_sentence_boundary_uses_last_sentence()

### Community 57 - "⚙️ Per-Channel Configuration"
Cohesion: 0.67
Nodes (3): `lookback_hours` — per-channel lookback window, ⚙️ Per-Channel Configuration, `prompt_extra` — per-channel AI instructions

### Community 60 - "hooks"
Cohesion: 0.18
Nodes (10): exclude, additional_dependencies, args, exclude, files, id, repos, hooks (+2 more)

### Community 62 - "build_server"
Cohesion: 0.14
Nodes (11): Enabling it, 🔗 MCP Server, Reading a single channel, Security, Tools, build_server(), get_channel_messages(), get_digest() (+3 more)

### Community 65 - "test_mcp_config_rejects_invalid"
Cohesion: 0.20
Nodes (6): _mcp_config_file(), test_filter_spec_invalid_dotted_path_raises(), test_mcp_config_explicit(), test_mcp_config_missing_block_defaults(), test_mcp_config_rejects_invalid(), test_prompts_composer_invalid_dotted_path_raises()

### Community 69 - "config/models.py"
Cohesion: 0.11
Nodes (3): read_last_digest(), write_last_digest(), validate_hours()

### Community 70 - "README.md"
Cohesion: 0.12
Nodes (12): Chatbrief — new chat starter, AI-assisted development workflow, 🤖 Bot Commands, 🤝 Contributing, 🙏 Credits, 🛠️ Development & Testing, 🐳 Docker Deployment, ❓ FAQ (+4 more)

### Community 74 - "contact_links"
Cohesion: 0.33
Nodes (5): blank_issues_enabled, contact_links, about, name, url

### Community 86 - "Chatbrief — current project handover"
Cohesion: 0.25
Nodes (7): Chatbrief — current project handover, Graphify state, Immediate next action, Product purpose, Python-only modernization (2026-10-31), Remaining before the refactor can be declared complete, Workflow and safety rules

### Community 87 - "DigestFormatter"
Cohesion: 0.05
Nodes (32): DigestFormatter, main(), GroupedPoint, test_channel_section_includes_channel_link(), test_channel_section_without_url_omits_link(), test_create_digest(), test_create_header(), test_create_header_russian_month_name() (+24 more)

### Community 88 - "Chatbrief — AI-assisted development workflow"
Cohesion: 0.12
Nodes (16): Bug fixing, Chat workflow conventions, Chatbrief — AI-assisted development workflow, Complete the graph artifacts, Feature work — required developer workflow, Goals, Handover contract, How AI assistants should use GitHub (+8 more)

### Community 89 - "unit"
Cohesion: 0.14
Nodes (7): test_orphaned_summary_delete_failure(), test_orphaned_summary_deleted_when_all_channels_fail(), test_send_channel_messages_with_tracking(), test_send_channel_messages_with_tracking_default_user_id(), test_send_channel_messages_with_tracking_no_summary(), test_send_channel_messages_with_tracking_unauthorized(), test_summary_sent_before_channel_messages()

### Community 94 - "Contributor Covenant Code of Conduct"
Cohesion: 0.17
Nodes (12): 1. Correction, 2. Warning, 3. Temporary Ban, 4. Permanent Ban, Attribution, Contributor Covenant Code of Conduct, Enforcement, Enforcement Guidelines (+4 more)

### Community 97 - "Chatbrief — AI development guide"
Cohesion: 0.18
Nodes (11): Chat workflow conventions, Chatbrief — AI development guide, End-of-session handover, Git and change safety, Graph-assisted development (Graphify), Graphify artifact completion and hook verification, Project facts and stack, Project workflow helper (+3 more)

### Community 100 - "Chatbrief — persistent project context"
Cohesion: 0.25
Nodes (8): Chatbrief — persistent project context, Development workflow contract, Graphify — local CLI, pj automation, and Git-shared graph, Product and stack, Project-local workflow, Read first, Safety, Tooling and commands

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
- **1 isolated node(s):** `chatbrief`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 923 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Config` connect `Config` to `SQLiteBackend`, `Message`, `TelegramMessageSender`, `test_utils.py`, `TelegramMessageSource`, `load_config`, `test_scheduler.py`, `test_digest.py`, `validation.py`, `Summarizer`, `CommandResult`, `TelegramBot`, `summarizer.py`, `CommandStatus`, `TelegramBot`, `.__init__`, `build_server`, `telegram_source.py`, `.__init__`, `config/models.py`, `DigestFormatter`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Are the 73 inferred relationships involving `load_config()` (e.g. with `.initialize()` and `test_channel_group_field_parsed()`) actually correct?**
  _`load_config()` has 73 INFERRED edges - model-reasoned connections that need verification._
- **What connects `chatbrief` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `SQLiteBackend` be split into smaller, more focused modules?**
  _Cohesion score 0.08244076598506979 - nodes in this community are weakly interconnected._
- **Why does `Message` connect `Message` to `SQLiteBackend`, `Config`, `telegram_source.py`, `TelegramMessageSource`, `config/models.py`, `test_summarizer.py`, `test_scheduler.py`, `TelegramBot`, `test_digest.py`, `summarizer.py`, `Summarizer`, `DigestFormatter`, `._summarize_channel`, `build_server`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Are the 52 inferred relationships involving `Summarizer` (e.g. with `Option B: Subclass Extension` and `Task 9: Wire composer into Summarizer`) actually correct?**
  _`Summarizer` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Should `Message` be split into smaller, more focused modules?**
  _Cohesion score 0.05002337540906966 - nodes in this community are weakly interconnected._