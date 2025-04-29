from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse
from api.model import *

router = APIRouter(prefix="/api")

@router.get("/")
def root():
  html_content = """
    <html>
        <head>
            <title>ParlAI</title>
        </head>
        <body>
            <h1>ParlAI</h1>
        </body>
    </html>
    """
  return HTMLResponse(content=html_content, status_code=200)

@router.post("/parlay/", response_model=PostParlayResponse)
def post_parlay(request: PostParlayRequest):
  return PostParlayResponse(**{
    "parlayLegProbabilities": [
        {
            "player": "Stephen Curry",
            "prop": "pts",
            "value": 25.5,
            "overUnder": "over",
            "probability": 0.42
        }
    ],
    "overallProbability": 0.42
})

app = FastAPI()
app.include_router(router)