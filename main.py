import model
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Literal, Annotated

app = FastAPI()

# For allowing our backend to interact with any port may be where the front end would be running, we use middle ware
# Here CORSmiddleware - Cross-origin resource sharing
# To validate incoming data - pydantic object

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                # All ports are allowed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve /static/* (images, css, js) and open index.html in browser
app.mount("/static", StaticFiles(directory="static_frontend"), name="static")

class UserInput(BaseModel):

    email_text: Annotated[str, Field(..., description="The text from the email")]
    original_text: Annotated[str, Field(...,description="Original clauses for comparison, JSW'S original")]

@app.post('/compare')
def compare_texts(data: UserInput):
    output_html = model.run_comparison_engine(data.email_text, data.original_text)

    return HTMLResponse(status_code=200, content = output_html)

@app.get("/")
async def read_index():
    return FileResponse('static_frontend/index.html')      # Basically to run on any API (0.0.0.0) and to run on port 8080 there
