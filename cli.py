#!/usr/bin/env python3

import typer
import uvicorn

app = typer.Typer()

@app.command()
def run():
    """Run the FastAPI application"""
    typer.echo("Starting FastAPI server...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    app()