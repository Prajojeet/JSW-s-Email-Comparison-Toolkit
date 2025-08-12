import model
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, computed_field
from typing import Literal, Annotated

app = FastAPI()

# To validate incoming data - pydantic object

class UserInput(BaseModel):

    email_text: Annotated[str, Field(..., description="The text from the email")]
    original_text: Annotated[str, Field(...,description="Original clauses for comparison, JSW'S original")]

@app.post('/compare')
def compare_texts(data: UserInput):
    output_html = model.run_comparison_engine(data.email_text, data.original_text)

    return HTMLResponse(status_code=200, content = output_html)