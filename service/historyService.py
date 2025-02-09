from datetime import datetime

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from logic import utils

from db.database import get_db
from db.models import SampleHistory


class HistoryService:
    def __init__(self):
        pass

    async def get_all_history(self, fromDate: str = None, toDate: str = None, db: AsyncSession = Depends(get_db) ):
        # replace the 'SampleHistory' with 'History'
        fromText = fromDate if fromDate not in [None, "null", ""] else None
        toText = toDate if toDate not in [None, "null", ""] else None
        executable = select(SampleHistory)
        fromDateStr = utils.get_datetime(fromText)
        toDateStr = utils.get_datetime(toText)
        history = None
        if fromDateStr is not None and toDateStr is not None:
            executable = executable.where(SampleHistory.date.between(fromDateStr, toDateStr))
        if fromDateStr is not None and toDateStr is None:
            executable = executable.where(SampleHistory.date.between(fromDateStr, datetime.now()))
        if fromDateStr is None and toDateStr is not None:
            executable = executable.where(SampleHistory.date <= toDateStr)

        executable = executable.order_by(SampleHistory.date)
        query = await db.execute(executable)
        return query.scalars().all()