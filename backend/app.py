from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

from src.routes.chat_routes import chat_blueprint

def create_app():
    app = Flask(__name__)
    CORS(app, origins="*", supports_credentials=True)
    app.register_blueprint(chat_blueprint, url_prefix="/api")

    @app.route("/health", methods=["GET"])
    def health_check():
        return {"status": "ok", "message": "Medical Chatbot API is running"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "production") == "development"
    print(f"Medical Chatbot API starting on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug)
