from datetime import datetime

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Report
from models.Report import ReportModel
import json


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def save_report(self, report: ReportModel):
        serialized_report = {
            'arguments': [dict(argument) for argument in report.arguments],
            'relations': [dict(relation) for relation in report.relations],
            'summary': dict(report.summary)
        }

        db_report = Report(
            paper=report.reportName,
            created=datetime.now(),
            structure=json.dumps(serialized_report)
        )

        self.db.add(db_report)
        await self.db.commit()
