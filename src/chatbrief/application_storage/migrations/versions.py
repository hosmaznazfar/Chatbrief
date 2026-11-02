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
        ON export_jobs(state, last_claimed_at, created_at, id)
        """,
    ),
)

MIGRATIONS = (INITIAL_EXPORT_MIGRATION, FAIR_EXPORT_CLAIM_MIGRATION)
