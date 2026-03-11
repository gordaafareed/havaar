from flask import Flask
from server.config import Config
from server.routes.auth   import auth_bp
from server.routes.twilio import twilio_bp
from server.routes.api    import api_bp
from server.routes.views  import views_bp


def create_app(config=Config):
    app = Flask(__name__, static_folder=None)
    app.secret_key = config.SECRET_KEY
    app.config.from_object(config)
    config.RECORDINGS_IN.mkdir(parents=True, exist_ok=True)
    config.RECORDINGS_OUT.mkdir(parents=True, exist_ok=True)
    app.register_blueprint(auth_bp)
    app.register_blueprint(twilio_bp, url_prefix="/twilio")
    app.register_blueprint(api_bp,    url_prefix="/api")
    app.register_blueprint(views_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    print(f"\n  havaar → http://localhost:{Config.PORT}\n")
    app.run(host="0.0.0.0", port=Config.PORT, debug=False)


# for flask dev server / hot reload
app = create_app()
