Development mode (single worker with reload):
python server.py --env development
Production mode (multiple workers):
python server.py --env production --workers 4
Or using environment variables:
bashCopyENVIRONMENT=production WORKERS=4 python server.py
Remember that when using multiple workers:

Each worker is a separate process with its own memory space
Use external caching/state management (like Redis) for shared state
Configure logging appropriately to handle multiple processes
Monitor memory usage as each worker consumes its own memory
The reload flag only works with a single worker, so it's typically used in development