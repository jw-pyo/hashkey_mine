from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import argparse

from api.order import order_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie", "SEARCH_N_DISCOVERY_SESSION"],
)
app.include_router(order_router)

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Run the FastAPI server')
    # parser.add_argument('--scheduling', action='store_true', help='Enable the scheduler')
    # args = parser.parse_args()

    uvicorn.run(app=app, host="0.0.0.0", port=5555, workers=1)