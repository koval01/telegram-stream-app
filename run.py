import os

from app import app

if __name__ == "__main__":
    app.run(
        "0.0.0.0",
        port=os.getenv('PORT', 3000),
        debug=True if (os.getenv("FLASK_ENV") == "development") else False
    )
