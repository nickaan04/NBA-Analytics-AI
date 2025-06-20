from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from api.model import PostParlayRequest, PostParlayResponse, ParlayLegProbability
from model.parlay_evaluator import ParlayEvaluator
from data.download import get_player_ids_from_rosters
from data.player_dataset import PlayerDataset

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
        
        TEAMS = ["IND", "OKC"]
        
        @self.router.get("/players/")
        def get_players():
          """
          Return a JSON object with a "players" key that is a list of
          { "name": <playerName>, "id": <playerId> } dictionaries.
          This allows the frontend to autocomplete on valid names and
          know which ID to use for images.
          """
          player_map = get_player_ids_from_rosters(TEAMS)
          return { "players": [
              {"name": name, "id": pid}
              for name, pid in player_map.items()
          ] }

        @self.router.get("/player_stats/{player_id}")
        def get_player_stats(player_id: str):
          """
          Return JSON:
            {
              "career": { "pts": 24.3, "reb": 5.1, ... },
              "recent": { "pts": 26.2, "reb": 6.2, ... }
            }
          Career averages cover seasons 2022–2025; recent covers last 5 games.
          """
          try:
              ds = PlayerDataset(player_id)
              career = ds.get_career_averages()
              recent = ds.get_recent_averages()
              return {"career": career, "recent": recent}
          except FileNotFoundError:
              raise HTTPException(
                  status_code=404,
                  detail=f"No combined CSV found for player_id={player_id}"
              )
          except Exception as e:
              raise HTTPException(status_code=500, detail=str(e))

    def start_server(self):
        app = FastAPI()
                # Add CORS middleware so that requests from http://localhost:5173 are allowed
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],   # <-- React dev server
            allow_methods=["*"],
            allow_headers=["*"],
        )

        app.include_router(self.router)
        return app

