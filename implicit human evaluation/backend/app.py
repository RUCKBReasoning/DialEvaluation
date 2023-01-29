from random import shuffle
from threading import Thread
from flask import Flask, request

from db_op import *
from chatbot_api import get_msg_from_chatbot

app = Flask(__name__)


@app.route("/bot", methods=['POST'])
def bot():
    bot_list = get_bot_all()
    return {'bot_list': bot_list}


@app.route("/prompt", methods=['POST'])
def prompt():
    return {'prompt': get_prompt()}


@app.route("/msg", methods=['POST'])
def msg():
    data = request.get_json()
    bot_name_list = get_bot_name_all()
    bot_msg = []
    thread_list = []
    msg_send = data['msg_send'] if len(data['msg_send']) <= 5 else data['msg_send'][-5:]
    for bot_name in bot_name_list:
        thread_list.append(Thread(target=get_msg_from_chatbot,
                                  args=(bot_name, msg_send, bot_msg)))
        thread_list[-1].start()

    # 等待子线程运行完毕
    is_finish = False
    while not is_finish:
        is_finish = True
        for tl in thread_list:
            if tl.is_alive():
                is_finish = False
                break

    # 检查是否有api没有回复消息
    if len(bot_msg) != len(bot_name_list):
        return {'status': 'error'}

    shuffle(bot_msg)
    session_id = update_session_content(data['session_id'], data['openid'],
                                        {'user': data['msg_send'][-1], 'bot': bot_msg})
    return {
        "status": 'success',
        "session_id": session_id,
        "msg_list_received": [i['value'] for i in bot_msg]
    }


@app.route("/order", methods=['POST'])
def order():
    data = request.get_json()
    bot_order = get_bot_order(data['session_id'])
    return {"bot_order": bot_order}


@app.route("/choose", methods=['POST'])
def choose():
    data = request.get_json()
    update_session_choose(data['session_id'], data['chosen_msg_index'])
    return {"status": "success"}


@app.route("/rank", methods=['POST'])
def rank():
    data = request.get_json()
    return {"rank_list": get_rank(data['session_id'])}


if __name__ == "__main__":
    app.run('0.0.0.0', port=10002)
