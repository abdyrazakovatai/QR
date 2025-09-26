import requests
from flask import Flask, redirect
import os

from flask.cli import load_dotenv

load_dotenv()

app = Flask(__name__)

REDIRECT_URL = os.getenv("REDIRECT_URL", "https://impatika.com")
JAVA_API = os.getenv("JAVA_API")


@app.route("/<qr_id>")
def track(qr_id):
    try:
        requests.post(JAVA_API, json={"qrId": qr_id})
    except Exception as e:
        print("Failed to connect to Java API", e)

    return redirect(f"{REDIRECT_URL}/login?qr={qr_id}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)