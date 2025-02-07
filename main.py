from http import HTTPStatus

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from logic.fileOperations import save_upload_file, process_pdf_file

app = FastAPI()


# Add CORS middleware
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL (adjust as needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/api/v1/file")
async def upload_file(file: UploadFile = File(...)):
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
    sections, arguments = process_pdf_file(file_path)

    return {
        "status": HTTPStatus.OK,
        "message": f"File uploaded successfully. Filename: {file_name}",
        "sections": sections,
        "arguments": arguments
    }
