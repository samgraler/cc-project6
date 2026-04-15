import os
import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import google.cloud.dialogflow_v2 as dialogflow

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-not-for-production")

# CONFIGURATION
PROJECT_ID = os.environ.get("DIALOGFLOW_PROJECT_ID", "intro-to-cc-project-6")
SESSION_ID = os.environ.get("DIALOGFLOW_SESSION_ID", "chatbot-session")

@app.route("/")
def index():
    if session.get("user"):
        return redirect(url_for("chat"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        first_name = (request.form.get("first_name") or "").strip()
        last_name = (request.form.get("last_name") or "").strip()
        email = (request.form.get("email") or "").strip()

        if not first_name or not last_name or not email:
            return render_template(
                "login.html",
                error="Please enter your first name, last name, and email address.",
                values={"first_name": first_name, "last_name": last_name, "email": email},
            )

        session["user"] = {"first_name": first_name, "last_name": last_name, "email": email}
        # Create a per-user Dialogflow session id so contexts/parameters
        # are isolated between different people using the app.
        session["dialogflow_session_id"] = str(uuid.uuid4())
        return redirect(url_for("chat"))

    return render_template("login.html", error=None, values=None)

@app.route("/chat")
def chat():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    return render_template("index.html", user=user)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/ask", methods=["POST"])
def ask():
    user = session.get("user")
    if not user:
        return jsonify({"reply": "Please log in first."}), 401
    text_input = request.json.get("message")

    # Connect to Dialogflow
    # session_client = dialogflow.SessionsClient.from_service_account_json("key.json")
    session_client = dialogflow.SessionsClient()
    df_session_id = session.get("dialogflow_session_id") or SESSION_ID
    df_session_path = session_client.session_path(PROJECT_ID, df_session_id)

    # Pass user info to Dialogflow using a context with parameters.
    # Can be referenced in Dialogflow responses as:
    #   #user_profile.first_name, #user_profile.last_name, #user_profile.email
    user_profile_context = dialogflow.Context(
        name=f"{df_session_path}/contexts/user_profile",
        lifespan_count=50,
        parameters={
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", ""),
            "email": user.get("email", ""),
        },
    )
    query_params = dialogflow.QueryParameters(contexts=[user_profile_context])
    text_query = dialogflow.TextInput(text=text_input, language_code="en-US")
    query_input = dialogflow.QueryInput(text=text_query)

    response = session_client.detect_intent(
        request={"session": df_session_path, "query_input": query_input, "query_params": query_params}
    )
    return jsonify({"reply": response.query_result.fulfillment_text})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
