from flask import Flask, redirect
import os

app = Flask(__name__)

REDIRECT_URL = os.getenv("REDIRECT_URL", "https://impatika.com")

@app.route("/<qr_id>")
def track(qr_id):
    return redirect(f"{REDIRECT_URL}/login?qr={qr_id}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)