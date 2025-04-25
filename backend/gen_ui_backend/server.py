import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes

from gen_ui_backend.langgraph.graph import create_graph
from gen_ui_backend.types import ChatInputType

import gen_ui_backend.utils.config

def start() -> None:
    app = FastAPI(
        title="Broken Basket",
        version="1.0",
        description="Broken Basket is a multi-agent LLM based application to help with achieving dietary goals"
    )

    # Configure CORS
    origins = [
        "http://localhost",
        "http://localhost:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    graph = create_graph()

    runnable = graph.with_types(input_type=ChatInputType, output_type=dict)

    add_routes(app, runnable, path="/chat", playground_type="default")
    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
