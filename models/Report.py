from pydantic import BaseModel

from models.Argument import Argument
from models.Relation import Relation
from models.Summary import Summary

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
    arguments: list[ArgumentModel]
    relations: list[RelationModel]
    summary: dict[str, dict[str, int]]