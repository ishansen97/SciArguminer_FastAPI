import logging
from datetime import datetime

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Report
from logic import utils
from models.Report import ReportModel
import json

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def save_report(self, report: ReportModel):
        serialized_report = {
            'arguments': [argument.model_dump() for argument in report.arguments],
            'relations': [relation.model_dump() for relation in report.relations],
            'summary': report.summary
        }

        db_report = Report(
            paper=report.reportName,
            created=datetime.now(),
            structure=json.dumps(serialized_report)
        )

        self.db.add(db_report)
        await self.db.commit()

    async def get_all_reports(self, fromDate: str = None, toDate: str = None):
        fromText = fromDate if fromDate not in [None, "null", ""] else None
        toText = toDate if toDate not in [None, "null", ""] else None
        executable = select(Report)
        fromDateStr = utils.get_datetime(fromText)
        toDateStr = utils.get_datetime(toText)
        history = None
        if fromDateStr is not None and toDateStr is not None:
            executable = executable.where(Report.created.between(fromDateStr, toDateStr))
        if fromDateStr is not None and toDateStr is None:
            executable = executable.where(Report.created.between(fromDateStr, datetime.now()))
        if fromDateStr is None and toDateStr is not None:
            executable = executable.where(Report.created <= toDateStr)

        executable = executable.order_by(Report.created)
        query = await self.db.execute(executable)
        result = query.scalars().all()
        reports = [utils.get_report_models(res) for res in result]
        return reports

    async def get_report(self, reportId: int):
        executable = select(Report).where(Report.id == reportId)
        query = await self.db.execute(executable)
        report = query.scalar_one()
        deserialized: dict = json.loads(report.structure)
        logger.info(f"Report {reportId} was deserializated: {deserialized.keys()}")
        return deserialized['summary']  if list(deserialized.keys()) == ['arguments', 'relations', 'summary'] else None