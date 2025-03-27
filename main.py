import logging
from datetime import datetime
from http import HTTPStatus

from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.seed_async import init_db
from logic.fileOperations import save_upload_file, process_pdf_file
from models.Report import ReportModel
from service.ReportService import ReportService
from service.historyService import HistoryService

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()


# Add CORS middleware
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL (adjust as needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.on_event("startup")
async def startup_event():
    """Run async database initialization on app startup."""
    await init_db()
    logger.info("Database initialization complete.")

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/api/v1/file")
async def upload_file(file: UploadFile = File(...)):
    startTime = datetime.now()
    # Attempt to decode the file content safely
    file_name_components = file.filename.split('.')
    file_name, extension = file_name_components[0], file_name_components[1]
    if extension != 'pdf':
        return {
            "status": HTTPStatus.BAD_REQUEST,
            "message": "Uploaded file is not PDF.",
        }

    # save the file
    file_path = save_upload_file(file)
    sections, arguments, relations, summary = process_pdf_file(file_path)

    endTime = datetime.now()
    processedTime = endTime - startTime

    # logs the time elapsed
    logger.info(f"Processed PDF '{file.filename}' | File size: {file.size} bytes | Duration: {processedTime}")

    return {
        "status": HTTPStatus.OK,
        "message": f"File uploaded successfully. Filename: {file_name}",
        "sections": sections,
        "arguments": arguments,
        "relations": relations,
        "summary": summary
    }

@app.get("/api/v1/history")
async def get_history(fromDate: str, toDate: str, db: AsyncSession = Depends(get_db) ):
    historyService = HistoryService()
    records = await historyService.get_all_history(fromDate, toDate, db)
    return {
        "status": HTTPStatus.OK,
        "records": records
    }

@app.post("/api/v1/report", response_model=None)
async def save_report(report: ReportModel, db: AsyncSession = Depends(get_db)):
    reportService = ReportService(db)
    logger.info(f"Processing report '{report.reportName}'")
    await reportService.save_report(report)
    return {
        "status": HTTPStatus.OK,
        "message": f"Report saved successfully. ReportName: {report.reportName}",
    }

@app.get("/api/v1/reports")
async def get_report(fromDate: str, toDate: str, db: AsyncSession = Depends(get_db)):
    reportService = ReportService(db)
    logger.info(f"Accessing reports")
    reports = await reportService.get_all_reports(fromDate, toDate)

    return {
        "status": HTTPStatus.OK if reports is not None else HTTPStatus.NOT_FOUND,
        "records": reports
    }

@app.get("/api/v1/report/{reportId}")
async def get_report(reportId: int, db: AsyncSession = Depends(get_db)):
    reportService = ReportService(db)
    logger.info(f"Accessing report '{type(reportId)}'")
    report = await reportService.get_report(reportId)

    return {
        "status": HTTPStatus.OK if report is not None else HTTPStatus.NOT_FOUND,
        "summary": report
    }