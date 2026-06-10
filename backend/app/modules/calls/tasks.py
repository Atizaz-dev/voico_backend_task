"""Background tasks for the calls module."""

import asyncio
import logging
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.db import async_session
from app.modules.calls.repository import CallRepository

logger = logging.getLogger(__name__)


async def run_stale_call_expiry_loop() -> None:
    while True:
        try:
            async with async_session() as session:
                repo = CallRepository(session)
                threshold = datetime.utcnow() - timedelta(
                    minutes=settings.stale_call_threshold_minutes
                )
                count = await repo.expire_stale_calls(threshold)
                logger.info("Expired %d stale in_progress call(s)", count)
        except Exception:
            logger.exception("Stale call expiry job failed")
        await asyncio.sleep(settings.stale_call_check_interval_minutes * 60)
