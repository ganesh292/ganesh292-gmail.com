from flask import Flask, render_template, request
from chatterbot import ChatBot

app = Flask(__name__)

english_bot = ChatBot("Chatterbot",
                      logic_adapters=[{
                                        'import_path': 'logic_adapter.InfoAdapter'
                                        },
                                        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'Sorry. Make sure the State/District/City name is accurate',
            'maximum_similarity_threshold': 0.95
        }])
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(english_bot.get_response(text=userText))


if __name__ == "__main__":
    app.run()
