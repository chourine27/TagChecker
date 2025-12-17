import os
import sys

# Make `src` importable when running this script from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("nfc_available_rest.app:app", host="0.0.0.0", port=6543, reload=True)
