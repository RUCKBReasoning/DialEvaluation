import requests
import time
from random import shuffle
from db_op import *


def get_msg_from_xdai(msg_send):
    """ get response from xdao """
    data = {
        "xdid": "#xd小呆6836",
        "platform": "annotation",
        "platform_id": "mzy",
        "requestId": "annotation-" + str(time.time()),
        "msgList": []
    }
    for i in range(len(msg_send)):
        data['msgList'].append({"talker": "user" if i % 2 == 0 else "bot", "text": msg_send[i]})
    res = requests.post(url='http://aigc.aminer.cn/test/xd/v2/query', json=data).json()
    return res['data']['reply']


def get_msg_from_plato(msg_send):
    """ get response from plato """
    data = {
        'version': '3.0',
        'service_id': '',
        'session_id': '',
        'log_id': '',
        'request': {
            'query': msg_send[-1],
            'terminal_id': 'xxx'
        },
        "context": {
            "SYS_REMEMBERED_SKILLS": [],
            "SYS_CHAT_HIST": msg_send[-7:] if len(msg_send) > 7 else msg_send
        }
    }
    plato_account_list = get_plato_account_all()
    shuffle(plato_account_list)
    msg_received = ''
    for plato_account in plato_account_list:
        data['service_id'] = plato_account['bot_id']
        data['log_id'] = plato_account['bot_id'] + str(int(time.time()))
        access_token = plato_account['access_token']
        while msg_received == '':
            res = requests.post(url='https://aip.baidubce.com/rpc/2.0/unit/service/v3/chat?access_token='
                                    + access_token, json=data).json()
            if res['error_code'] == 0:
                msg_received = res['result']['context']['SYS_PRESUMED_HIST'][-1]
            elif res['error_code'] == 100 or res['error_code'] == 110 or res['error_code'] == 111:
                access_token = requests.get('https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&'
                                            'client_id=' + plato_account['api_key'] +
                                            '&client_secret=' + plato_account['secret_key']).json()['access_token']
                update_access_token(plato_account['_id'], access_token)
            else:
                break
        if msg_received != '':
            break
    return msg_received


def get_msg_from_deployed_model(model_name, msg_send):
    """ get response from deployed model """
    res = requests.post(
        url='http://36.103.203.210:8001/' + model_name.lower(),
        json={'content': msg_send}
    ).json()
    return res['data']


def get_msg_from_chatbot(chat_generation_id, msg_send):
    """ get response from chatbot """
    chat_generation = get_chat_generation_by_id(chat_generation_id)
    bot_name = get_bot_name_by_id(chat_generation['chat_record_id'])
    msg_received = ''
    if bot_name == 'XDAI':
        msg_received = get_msg_from_xdai(msg_send)
    elif bot_name == 'PLATO-2':
        msg_received = get_msg_from_plato(msg_send)
    elif bot_name == 'GLM-Finetune':
        res = requests.post(url='http://36.103.203.210:8008/generate',
                            json={'content': msg_send})
        if res.status_code == 200:
            msg_received = res.json()['data']
    else:
        msg_received = get_msg_from_deployed_model(bot_name, msg_send)
    if msg_received != '':
        return {'state': 'success', 'msg_received': msg_received}
    else:
        return {'state': 'error'}
