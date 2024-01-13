import uvicorn
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

if __name__ == "__main__":
    uvicorn.run("source.app:app", host="web", port=8000, log_level="info", reload=True)