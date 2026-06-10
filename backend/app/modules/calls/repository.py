import math
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import update
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.calls.schema import Call, CallLabel, CallStatus

SORT_COLUMNS: dict[str, object] = {
    "phone_number": Call.phone_number,
    "caller_name": Call.caller_name,
    "status": Call.status,
    "label": Call.label,
    "duration_seconds": Call.duration_seconds,
    "started_at": Call.started_at,
}


class CallRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, call_id: uuid.UUID) -> Optional[Call]:
        result = await self.session.exec(select(Call).where(Call.id == call_id))
        return result.first()

    def _apply_filters(
        self,
        stmt,
        *,
        status: Optional[CallStatus] = None,
        caller_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        label: Optional[CallLabel] = None,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
    ):
        if status is not None:
            stmt = stmt.where(Call.status == status)
        if caller_name:
            stmt = stmt.where(Call.caller_name.ilike(f"%{caller_name}%"))
        if phone_number:
            stmt = stmt.where(Call.phone_number.ilike(f"%{phone_number}%"))
        if label is not None:
            stmt = stmt.where(Call.label == label)
        if min_duration is not None:
            stmt = stmt.where(Call.duration_seconds >= min_duration)
        if max_duration is not None:
            stmt = stmt.where(Call.duration_seconds <= max_duration)
        return stmt

    def _apply_sort(self, stmt, sort_by: Optional[str], sort_order: str):
        if sort_by and sort_by in SORT_COLUMNS:
            column = SORT_COLUMNS[sort_by]
            if sort_order == "asc":
                return stmt.order_by(column.asc())  # type: ignore[attr-defined]
            return stmt.order_by(column.desc())  # type: ignore[attr-defined]
        return stmt.order_by(Call.created_at.desc())  # type: ignore[attr-defined]

    async def list_calls(
        self,
        status: Optional[CallStatus],
        page: int,
        page_size: int,
        caller_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        label: Optional[CallLabel] = None,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> tuple[list[Call], int, int, dict[str, int]]:
        query = select(Call)
        count_query = select(func.count()).select_from(Call)

        query = self._apply_filters(
            query,
            status=status,
            caller_name=caller_name,
            phone_number=phone_number,
            label=label,
            min_duration=min_duration,
            max_duration=max_duration,
        )
        count_query = self._apply_filters(
            count_query,
            status=status,
            caller_name=caller_name,
            phone_number=phone_number,
            label=label,
            min_duration=min_duration,
            max_duration=max_duration,
        )

        count_result = await self.session.exec(count_query)
        total = count_result.one()

        counts: dict[str, int] = {}
        for s in CallStatus:
            c = (
                await self.session.exec(
                    select(func.count()).select_from(Call).where(Call.status == s)
                )
            ).one()
            counts[s.value] = c

        offset = (page - 1) * page_size
        query = self._apply_sort(query, sort_by, sort_order).offset(offset).limit(page_size)
        result = await self.session.exec(query)
        calls = list(result.all())

        total_pages = math.ceil(total / page_size) if total > 0 else 1
        return calls, total, total_pages, counts

    async def update(self, call: Call) -> Call:
        self.session.add(call)
        await self.session.flush()
        await self.session.refresh(call)
        return call

    async def expire_stale_calls(self, threshold: datetime) -> int:
        stmt = (
            update(Call)
            .where(Call.status == CallStatus.in_progress)
            .where(Call.started_at < threshold)
            .values(status=CallStatus.failed, updated_at=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount or 0
