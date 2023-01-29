import requests
import time
from random import shuffle
from db_op import *


def get_msg_from_xdai(msg_send):
    """ 获取小呆的回复 """
    data = {
        "xdid": "#xd小呆6836",
        "platform": "annotation",
        "platform_id": "mzy",
        "requestId": "annotation-" + str(time.time()),
        "msgList": []
    }
    for i in range(len(msg_send)):
        data['msgList'].append({"talker": "user" if i % 2 == 0 else "bot", "text": msg_send[i]})
    res = requests.post(url='http://aigc.aminer.cn/test/xd/v2/query', json=data)
    if res.status_code == 200:
        return res.json()['data']['reply']
    else:
        return ''


def get_msg_from_plato(msg_send):
    """ 获取plato的回复 """
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
    """ 获取已部署模型的回复 """
    res = requests.post(
        url='http://36.103.203.210:8001/' + model_name.lower(),
        json={'content': msg_send}
    )
    if res.status_code == 200:
        return res.json()['data']
    else:
        return ''


def get_msg_from_chatbot(bot_name, msg_send, bot_msg):
    """ 路由功能，获取chatbot的回复 """
    if bot_name == 'XDAI':
        msg_received = get_msg_from_xdai(msg_send)
    elif bot_name == 'PLATO-2':
        msg_received = get_msg_from_plato(msg_send)
    elif bot_name == 'GLM-Finetune':
        res = requests.post(url='http://36.103.203.210:8008/generate',
                            json={'content': msg_send})
        if res.status_code == 200:
            msg_received = res.json()['data']
            bot_msg.append({
                'name': bot_name,
                'value': msg_received,
                'chosen': False,
                'query_key': res.json()['query_key'],
                'knowledge': res.json()['knowledge'],
            })
        else:
            msg_received = ''
    else:
        msg_received = get_msg_from_deployed_model(bot_name, msg_send)
    if msg_received != '' and bot_name != 'GLM-Finetune':
        bot_msg.append({
            'name': bot_name,
            'value': msg_received,
            'chosen': False
        })
