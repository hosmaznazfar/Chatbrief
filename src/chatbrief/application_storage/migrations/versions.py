"""Immutable schema definitions for application-state database migrations."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Migration:
    """One immutable, ordered database migration."""

    version: int
    statements: tuple[str, ...]


INITIAL_EXPORT_MIGRATION = Migration(
    version=1,
    statements=(
        """
        CREATE TABLE export_jobs (
            id TEXT PRIMARY KEY,
            export_id TEXT NOT NULL UNIQUE,
            owner_telegram_user_id INTEGER NOT NULL CHECK (owner_telegram_user_id > 0),
            state TEXT NOT NULL CHECK (state IN (
                'queued', 'collecting', 'packaging', 'ready', 'cancelled',
                'failed', 'invalidated', 'expired'
            )),
            media_outcome TEXT CHECK (media_outcome IS NULL OR media_outcome IN (
                'sent', 'omitted', 'failed', 'delivery_unknown'
            )),
            cutoff_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            primary_delivered_at TEXT,
            expires_at TEXT,
            terminal_at TEXT,
            lease_owner TEXT,
            lease_expires_at TEXT,
            lease_generation INTEGER NOT NULL DEFAULT 0 CHECK (lease_generation >= 0),
            next_run_at TEXT,
            staging_key TEXT,
            report_json TEXT CHECK (report_json IS NULL OR json_valid(report_json)),
            media_manifest_json TEXT CHECK (
                media_manifest_json IS NULL OR json_valid(media_manifest_json)
            ),
            last_error_code TEXT
        )
        """,
        """
        CREATE TABLE export_delivery_attempts (
            id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL REFERENCES export_jobs(id) ON DELETE CASCADE,
            document_kind TEXT NOT NULL CHECK (document_kind IN ('primary', 'media')),
            attempt_number INTEGER NOT NULL CHECK (attempt_number > 0),
            outcome TEXT NOT NULL CHECK (outcome IN (
                'started', 'succeeded', 'failed', 'delivery_unknown'
            )),
            started_at TEXT NOT NULL,
            finished_at TEXT,
            retry_after_at TEXT,
            telegram_chat_id INTEGER,
            telegram_message_id INTEGER,
            telegram_file_id TEXT,
            error_code TEXT,
            retry_after_seconds INTEGER CHECK (
                retry_after_seconds IS NULL OR retry_after_seconds >= 0
            ),
            UNIQUE (job_id, document_kind, attempt_number)
        )
        """,
        """
        CREATE TABLE export_cleanup_tasks (
            id TEXT PRIMARY KEY,
            job_id TEXT REFERENCES export_jobs(id) ON DELETE SET NULL,
            task_type TEXT NOT NULL CHECK (
                task_type IN ('telegram_message_delete', 'staging_delete')
            ),
            state TEXT NOT NULL CHECK (state IN ('pending', 'succeeded', 'abandoned')),
            telegram_chat_id INTEGER,
            telegram_message_id INTEGER,
            staging_key TEXT,
            attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
            next_attempt_at TEXT NOT NULL,
            deadline_at TEXT,
            last_error_code TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            CHECK (
                (task_type = 'telegram_message_delete'
                    AND telegram_chat_id IS NOT NULL
                    AND telegram_message_id IS NOT NULL
                    AND staging_key IS NULL)
                OR
                (task_type = 'staging_delete'
                    AND staging_key IS NOT NULL
                    AND telegram_chat_id IS NULL
                    AND telegram_message_id IS NULL)
            )
        )
        """,
        """
        CREATE UNIQUE INDEX uq_export_jobs_one_blocking_per_user
        ON export_jobs(owner_telegram_user_id)
        WHERE state IN ('queued', 'collecting', 'packaging', 'ready')
        """,
        "CREATE INDEX idx_export_jobs_state_next_run ON export_jobs(state, next_run_at)",
        "CREATE INDEX idx_export_jobs_owner_created ON export_jobs(owner_telegram_user_id, created_at)",
        "CREATE INDEX idx_export_jobs_lease_expiry ON export_jobs(lease_expires_at)",
        "CREATE INDEX idx_export_jobs_ready_expiry ON export_jobs(expires_at) WHERE state = 'ready'",
        "CREATE INDEX idx_export_attempts_job_kind ON export_delivery_attempts(job_id, document_kind)",
        "CREATE INDEX idx_export_cleanup_pending ON export_cleanup_tasks(state, next_attempt_at, deadline_at)",
    ),
)

FAIR_EXPORT_CLAIM_MIGRATION = Migration(
    version=2,
    statements=(
        "ALTER TABLE export_jobs ADD COLUMN last_claimed_at TEXT",
        """
        CREATE INDEX idx_export_jobs_fair_claim
        ON export_jobs(state, last_claimed_at, created_at, owner_telegram_user_id, id)
        """,
    ),
)

DELIVERY_LEASE_FENCING_MIGRATION = Migration(
    version=3,
    statements=(
        "ALTER TABLE export_delivery_attempts ADD COLUMN worker_id TEXT",
        """
        ALTER TABLE export_delivery_attempts
        ADD COLUMN lease_generation INTEGER
        CHECK (lease_generation IS NULL OR lease_generation > 0)
        """,
    ),
)


SHARED_ARCHIVE_MIGRATION = Migration(
    version=4,
    statements=(
        """
        CREATE TABLE users (
            telegram_user_id INTEGER PRIMARY KEY CHECK (telegram_user_id > 0),
            created_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE sources (
            id TEXT PRIMARY KEY,
            platform TEXT NOT NULL CHECK (platform IN ('telegram')),
            platform_chat_id TEXT NOT NULL CHECK (length(platform_chat_id) > 0),
            display_name TEXT NOT NULL CHECK (length(display_name) > 0),
            source_type TEXT NOT NULL CHECK (
                source_type IN ('channel', 'group', 'supergroup')
            ),
            visibility TEXT NOT NULL CHECK (
                visibility IN ('public', 'private', 'unknown')
            ),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE (platform, platform_chat_id)
        )
        """,
        """
        CREATE TABLE source_access (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
            access_method TEXT NOT NULL CHECK (access_method IN ('bot_api', 'telethon')),
            owner_telegram_user_id INTEGER REFERENCES users(telegram_user_id)
                ON DELETE CASCADE,
            state TEXT NOT NULL CHECK (
                state IN ('unknown', 'available', 'inaccessible', 'revoked')
            ),
            verified_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            CHECK (
                (access_method = 'bot_api' AND owner_telegram_user_id IS NULL)
                OR
                (access_method = 'telethon' AND owner_telegram_user_id IS NOT NULL)
            )
        )
        """,
        """
        CREATE UNIQUE INDEX uq_source_access_bot_api
        ON source_access(source_id)
        WHERE access_method = 'bot_api'
        """,
        """
        CREATE UNIQUE INDEX uq_source_access_telethon_user
        ON source_access(source_id, owner_telegram_user_id)
        WHERE access_method = 'telethon'
        """,
        """
        CREATE TABLE source_authorizations (
            source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
            telegram_user_id INTEGER NOT NULL REFERENCES users(telegram_user_id)
                ON DELETE CASCADE,
            granted_by_telegram_user_id INTEGER REFERENCES users(telegram_user_id)
                ON DELETE SET NULL,
            state TEXT NOT NULL CHECK (state IN ('active', 'revoked')),
            granted_at TEXT NOT NULL,
            revoked_at TEXT,
            PRIMARY KEY (source_id, telegram_user_id),
            CHECK (
                (state = 'active' AND revoked_at IS NULL)
                OR
                (state = 'revoked' AND revoked_at IS NOT NULL)
            )
        )
        """,
        """
        CREATE TABLE subscriptions (
            id TEXT PRIMARY KEY,
            telegram_user_id INTEGER NOT NULL REFERENCES users(telegram_user_id)
                ON DELETE CASCADE,
            source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
            state TEXT NOT NULL CHECK (state IN ('active', 'suspended', 'ended')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            ended_at TEXT,
            UNIQUE (telegram_user_id, source_id),
            CHECK (
                (state = 'ended' AND ended_at IS NOT NULL)
                OR
                (state IN ('active', 'suspended') AND ended_at IS NULL)
            )
        )
        """,
        """
        CREATE INDEX idx_subscriptions_source_state
        ON subscriptions(source_id, state)
        """,
        """
        CREATE INDEX idx_subscriptions_user_state
        ON subscriptions(telegram_user_id, state)
        """,
        """
        CREATE TABLE messages (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
            platform_message_id TEXT NOT NULL CHECK (length(platform_message_id) > 0),
            text TEXT NOT NULL DEFAULT '',
            sender_label TEXT,
            source_timestamp TEXT,
            link TEXT,
            has_media INTEGER NOT NULL CHECK (has_media IN (0, 1)),
            media_type TEXT CHECK (
                media_type IS NULL OR media_type IN (
                    'image', 'video', 'document', 'audio', 'other', 'unknown'
                )
            ),
            collected_at TEXT NOT NULL,
            edited_at TEXT,
            deleted_at TEXT,
            UNIQUE (source_id, platform_message_id),
            CHECK (
                (has_media = 0 AND media_type IS NULL)
                OR
                (has_media = 1 AND media_type IS NOT NULL)
            )
        )
        """,
        """
        CREATE INDEX idx_messages_source_timestamp
        ON messages(source_id, source_timestamp)
        """,
        """
        CREATE INDEX idx_messages_retention
        ON messages(source_timestamp)
        """,
        """
        CREATE TABLE source_collection_coverage (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
            ingestion_method TEXT NOT NULL CHECK (
                ingestion_method IN ('bot_api', 'telethon')
            ),
            covered_from TEXT NOT NULL,
            covered_until TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            CHECK (covered_until >= covered_from)
        )
        """,
        """
        CREATE INDEX idx_source_coverage_lookup
        ON source_collection_coverage(
            source_id, ingestion_method, covered_from, covered_until
        )
        """,
    ),
)


MIGRATIONS = (
    INITIAL_EXPORT_MIGRATION,
    FAIR_EXPORT_CLAIM_MIGRATION,
    DELIVERY_LEASE_FENCING_MIGRATION,
    SHARED_ARCHIVE_MIGRATION,
)
