import os
from src import *
from src.app import app

if os.environ.get("ENVIRONMENT") == "dev":
    app.run(host='0.0.0.0', port=5000, debug=True)
