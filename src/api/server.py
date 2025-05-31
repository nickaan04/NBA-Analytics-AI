from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse
from api.model import *
from model.parlay_evaluator import ParlayEvaluator

class parlaiApi:
    def __init__(self, evaluator: ParlayEvaluator):
        self.evaluator = evaluator
        self.router = APIRouter(prefix="/api")
        self._setup_routes()
    
    def _setup_routes(self):
        @self.router.post("/parlay/", response_model=PostParlayResponse)
        def post_parlay(request: PostParlayRequest):
          parlay_leg_responses: List[ParlayLegProbability] = []
          overall_probability = 1
          for parlayLeg in request.parlayLegs:
            evaluated = self.evaluator.evaluate_leg(parlayLeg)

            parlay_leg_responses.append(evaluated)
            overall_probability *= evaluated.probability

          return PostParlayResponse(
            parlayLegProbabilities=parlay_leg_responses,
            overallProbability=overall_probability
          )

    def start_server(self):
        app = FastAPI()
        app.include_router(self.router)
        return app