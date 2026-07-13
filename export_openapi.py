import json
from src.api_router import app

with open('openapi.json', 'w') as f:
    json.dump(app.openapi(), f, indent=2)

print("Regenerated openapi.json with updated responses.")
