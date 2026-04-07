import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    # FLASK_HOST defaults to 127.0.0.1 for local dev; set to 0.0.0.0 in docker so nginx can reach flask across containers
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    app.run(debug=True, host=host, port=5000)
