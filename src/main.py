import uvicorn

from api.server import *
from api.model import *
from data import *
from model import *


api = parlaiApi(
  evaluator=ParlayEvaluator()
)

uvicorn.run(
  api.start_server()
)
