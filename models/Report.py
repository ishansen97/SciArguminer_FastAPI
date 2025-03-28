from pydantic import BaseModel

class ArgumentModel(BaseModel):
    text: str
    start: int
    end: int
    type: str

class RelationModel(BaseModel):
    head: ArgumentModel
    tail: ArgumentModel
    relation: str

class ReportModel(BaseModel):
    reportName: str
    authorNames: str
    arguments: list[ArgumentModel]
    relations: list[RelationModel]
    summary: dict[str, dict[str, int]]