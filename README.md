# NBA-Analytics-AI

## Project Structure
#### Packages
- `data/` to extract, transform, and clean our datasets.
- `model/` to train and run inference from our ML models.
- `api/` to define Pydantic data models and our backend service with FastApi.

## Installing dependencies
Set up the virtual environment:
```sh
python3.10 -m venv venv
source venv/bin/activate
pip install .
```

## Run the backend

```sh
python3 src/main.py
```

## Run the frontend

```sh
cd frontend
npm install
npm run dev
```
