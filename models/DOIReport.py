from pydantic import BaseModel


class DOIRequest(BaseModel):
    doiUrl: str