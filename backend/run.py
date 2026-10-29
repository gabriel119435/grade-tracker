import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # FLASK_HOST is 127.0.0.1 for local dev, docker sets 0.0.0.0 so nginx can reach flask across containers
    host = os.environ.get("FLASK_HOST") or "127.0.0.1"
    # app.run reads FLASK_DEBUG to enable reloader and debugger; on by default, docker sets 0
    os.environ["FLASK_DEBUG"] = os.environ.get("FLASK_DEBUG") or "1"
    app.run(host=host, port=5000)
