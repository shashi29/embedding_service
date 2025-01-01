import uvicorn
import multiprocessing
import os
import typer
from typing import Optional

app = typer.Typer()

def get_workers_count(workers: Optional[int] = None) -> int:
    """Calculate number of workers based on input or environment"""
    if workers is not None:
        return workers
    
    if os.getenv("WORKERS"):
        return int(os.getenv("WORKERS"))
    
    cores = multiprocessing.cpu_count()
    return min((2 * cores) + 1, 8)  # Cap at 8 workers

@app.command()
def start_server(
    host: str = os.getenv("HOST", "0.0.0.0"),
    port: int = int(os.getenv("PORT", "8123")),
    workers: Optional[int] = None,
    reload: bool = os.getenv("RELOAD", "").lower() == "true",
    env: str = os.getenv("ENVIRONMENT", "development")
):
    """Start the FastAPI server with environment-aware configuration"""
    
    workers_count = get_workers_count(workers)
    
    # Development settings
    if env == "development":
        reload = True
        workers_count = 1  # Use single worker with reload
        access_log = True
    else:
        reload = False
        access_log = False
    
    config = uvicorn.Config(
        "app:app",
        host=host,
        port=port,
        workers=workers_count,
        reload=reload,
        log_level="info" if env == "development" else "warning",
        loop="auto",
        http="auto",
        ws="auto",
        timeout_keep_alive=30,
        access_log=access_log,
        use_colors=True
    )
    
    server = uvicorn.Server(config)
    server.run()

if __name__ == "__main__":
    app()