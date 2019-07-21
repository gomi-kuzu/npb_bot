from flask import Flask, render_template, request
import os
import slack

app = Flask(__name__)

client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])

@app.route('/', methods=['POST'])
def hello():

    text = request.form['text']

    if request.method == 'POST':
        
        if text == "A":
            name = ""
            response = client.chat_postMessage(channel = '#チャットボットかいはつ',text = "testやで")
            return name
        elif text == "B":
            name = "bbb"

        else:
            name = "ccc"

    else:
        name = "?"

    return name


@app.route('/good')
def good():
    name = "Good"
    return name

## おまじない
if __name__ == "__main__":
    app.run(debug=True)
