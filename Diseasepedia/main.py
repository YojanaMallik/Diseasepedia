

from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
import openai
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import os

mongo_uri = os.environ.get("MONGO_URI")
api_key = os.environ.get("OPENAI_API_KEY")


app = Flask(__name__)
app.config["MONGO_URI"] = mongo_uri
mongo = PyMongo(app)

@app.route("/")
def home():
    chats = mongo.db.chats.find({})
    myChats = [chat for chat in chats]
    return render_template("index.html", myChats=myChats)

@app.route("/api", methods=["GET", "POST"])
def qa():
    if request.method == "POST":
        question = request.form.get("question") or request.json.get("question")
        chat = mongo.db.chats.find_one({"question": question})
        if chat:
            chat['_id'] = str(chat['_id'])  # Convert ObjectId to string
            return jsonify(chat)
        else:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=question,
                temperature=0.7,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            data = {"question": question, "answer": response["choices"][0]["text"]}
            result = mongo.db.chats.insert_one(data)
            data['_id'] = str(result.inserted_id)  # Convert ObjectId to string
            return jsonify(data)

    data = {"result": "Thank you! I'm just a machine learning model designed to respond to questions and generate text based on my training data. Is there anything specific you'd like to ask or discuss?"}
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
