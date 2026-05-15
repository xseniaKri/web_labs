import sys
from pathlib import Path

from asgiref.wsgi import WsgiToAsgi


if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.factory import create_app


app = create_app()
asgi_app = WsgiToAsgi(app)


if __name__ == "__main__":
    app.run(debug=True)
