import uvicorn
import os

if __name__ == "__main__":
    # The app is defined in worker_pool_manager.py
    uvicorn.run("Triada.manager.worker_pool_manager:app", host="0.0.0.0", port=8000, reload=True)
