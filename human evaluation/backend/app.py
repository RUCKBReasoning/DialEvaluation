from flask import Flask, request

from chatbot_api import get_msg_from_chatbot
from db_op import *

app = Flask(__name__)


@app.route("/login", methods=['POST'])
def login():
    """ login """
    data = request.get_json()
    return check_auth(data['annotator_id'], data['password'])


@app.route("/next-chat", methods=['POST'])
def next_chat():
    """ get next dialog to be annotated """
    data = request.get_json()
    return get_chat_record_not_annotate(data['annotator_id'])


@app.route("/upload-annotation", methods=['POST'])
def upload_annotation():
    """ upload annotation result """
    data = request.get_json()
    return update_chat_annotation(data['chat_annotation_id'], data['annotation'])


@app.route("/next-generate", methods=['POST'])
def next_generate():
    """ get next dialog to be generated """
    data = request.get_json()
    return get_chat_record_not_generate(data['annotator_id'])


@app.route("/get-msg", methods=['POST'])
def get_msg():
    """ get response from chatbot """
    data = request.get_json()
    return get_msg_from_chatbot(data['chat_generation_id'], data['msg_send'])


@app.route("/upload-generate", methods=['POST'])
def upload_generate():
    """ upload generation result """
    data = request.get_json()
    return update_chat_record(data['chat_generation_id'], data['chat_content'])


if __name__ == "__main__":
    app.run('0.0.0.0', port=10000)
