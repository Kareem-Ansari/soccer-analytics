# Script to start the FastAPI server
# Sets database connection environment variables from Colab Secrets
# Run this cell in Colab to start the API

import os
import uvicorn


def start(db_password: str, host: str = "0.0.0.0", port: int = 8000):
    """
    Start the FastAPI server.
    db_password comes from Colab Secrets, never hardcoded.
    """
    os.environ["DB_HOST"]     = "localhost"
    os.environ["DB_PORT"]     = "5432"
    os.environ["DB_NAME"]     = "soccer_analytics"
    os.environ["DB_USER"]     = "postgres"
    os.environ["DB_PASSWORD"] = db_password

    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    import sys
    password = sys.argv[1] if len(sys.argv) > 1 else ""
    start(password)