"""Application startup and shutdown lifecycle tests."""

# pylint: disable=unused-argument

from unittest.mock import MagicMock

import pytest

from chatbrief.application_storage import MigrationError
from main import ChatbriefApp


@pytest.mark.asyncio
async def test_initialize_sets_up_application_database_before_platform(
    sample_config,
    monkeypatch,
):
    events = []

    class FakeApplicationDatabase:
        def __init__(self, path):
            events.append(("database_constructed", path))

        async def initialize(self):
            events.append("database_initialized")

    class FakePlatformBuilder:
        def __init__(self, config, logger):
            events.append("platform_builder_constructed")

        def create_services(self):
            events.append("platform_services_created")
            return MagicMock(), MagicMock()

        def create_bot(self, command_service):
            events.append("bot_created")
            return MagicMock()

    class FakeScheduler:
        def __init__(self, **kwargs):
            events.append("scheduler_created")

    class FakeCommandService:
        def __init__(self, **kwargs):
            events.append("command_service_created")

    monkeypatch.setattr("main.load_config", lambda: sample_config)
    monkeypatch.setattr("main.setup_logging", lambda _level: MagicMock())
    monkeypatch.setattr("main.ApplicationDatabase", FakeApplicationDatabase)
    monkeypatch.setattr("main.PlatformBuilder", FakePlatformBuilder)
    monkeypatch.setattr("main.DigestScheduler", FakeScheduler)
    monkeypatch.setattr("main.CommandService", FakeCommandService)

    app = ChatbriefApp()

    assert await app.initialize() is True
    assert events[0] == ("database_constructed", sample_config.application_storage.path)
    assert events.index("database_initialized") < events.index("platform_builder_constructed")
    assert events.index("database_initialized") < events.index("platform_services_created")
    assert app.application_database is not None


@pytest.mark.asyncio
async def test_initialize_fails_closed_when_application_database_fails(
    sample_config,
    monkeypatch,
):
    class FailingApplicationDatabase:
        def __init__(self, path):
            self.path = path

        async def initialize(self):
            raise MigrationError("migration failed")

    class UnexpectedPlatformBuilder:
        def __init__(self, config, logger):
            pytest.fail("Platform services must not be created after database failure")

    monkeypatch.setattr("main.load_config", lambda: sample_config)
    monkeypatch.setattr("main.setup_logging", lambda _level: MagicMock())
    monkeypatch.setattr("main.ApplicationDatabase", FailingApplicationDatabase)
    monkeypatch.setattr("main.PlatformBuilder", UnexpectedPlatformBuilder)

    app = ChatbriefApp()

    assert await app.initialize() is False
    assert app.application_database is None
    assert app.source is None
    assert app.bot is None
