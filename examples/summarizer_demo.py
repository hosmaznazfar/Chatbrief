"""Manual end-to-end summarizer demo.

Run with: uv run python examples/summarizer_demo.py
"""

import asyncio

from chatbrief.config.loader import load_config
from chatbrief.platforms.builder import PlatformBuilder
from chatbrief.summarizer import Summarizer
from chatbrief.utils import setup_logging


async def main() -> None:
    """Run the summarizer against messages collected from the configured platform."""
    config = load_config()
    logger = setup_logging(config.log_level)

    platform_builder = PlatformBuilder(config, logger)
    source, _sender = platform_builder.create_services()

    await source.connect()
    try:
        messages = await source.fetch_messages(hours=24)
    finally:
        await source.disconnect()

    summarizer = Summarizer(config, logger)
    result = await summarizer.summarize_all(messages)

    print("\\n" + "=" * 50)
    print("OVERVIEW:")
    print("=" * 50)
    print(result["overview"])

    print("\\n" + "=" * 50)
    print("CHANNEL SUMMARIES:")
    print("=" * 50)
    for channel, summary in result["channel_summaries"].items():
        print(f"\\n{channel}:")
        print(summary)


if __name__ == "__main__":
    asyncio.run(main())
