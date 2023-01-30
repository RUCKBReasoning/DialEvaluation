import time
import requests
from db_op import insert_self_chat


def get_self_chat_from_deployed_model(bot_name, url, topic_type, starting_utterance, chat_rounds):
    """ 从开源模型获取 self chat 记录 """
    doc = {
        "bot_name": bot_name,
        "chat_type": "bot-bot",
        "topic_type": topic_type,
        "chat_content": [starting_utterance],
    }
    for i in range(2 * chat_rounds - 1):
        res = requests.post(url=url, json={"content": doc["chat_content"]})
        if res.status_code == 200:
            doc["chat_content"].append(res.json()['data'])
        else:
            return {}
        time.sleep(1)
    return doc


def get_self_chat_from_plato2(topic_type, starting_utterance, chat_rounds):
    """ 从 PLATO-2 获取 self chat 记录 """
    doc = {
        "bot_name": "PLATO-2",
        "chat_type": "bot-bot",
        "topic_type": topic_type,
        "chat_content": [starting_utterance],
    }
    access_token = ''
    data = {
        'version': '3.0',
        'service_id': '',
        'session_id': '',
        'log_id': '',
        'request': {
            'query': '',
            'terminal_id': ''
        },
        "context": {
            "SYS_REMEMBERED_SKILLS": [],
            "SYS_CHAT_HIST": []
        }
    }
    for i in range(2 * chat_rounds - 1):
        data['log_id'] = '' + str(int(time.time()))
        data['request']['query'] = doc["chat_content"][-1]
        data['context']['SYS_CHAT_HIST'] = doc["chat_content"]
        res = requests.post(url='https://aip.baidubce.com/rpc/2.0/unit/service/v3/chat?access_token='
                                + access_token, json=data).json()
        while 'context' not in res['result']:
            print("exception")
            time.sleep(10)
        doc["chat_content"].append(res['result']['context']['SYS_PRESUMED_HIST'][-1])
    return doc


if __name__ == '__main__':

    topic_type = 'knowledge'
    with open('starting-utterance-{}.txt'.format(topic_type)) as fp:
        su_list = fp.readlines()
    
    cnt = 1
    for su in su_list:
        if cnt <= 63:
            cnt += 1
            continue
        document = get_self_chat_from_glm_130b(topic_type, su.rstrip('\n'), 5)
        insert_self_chat(document)
        print(cnt)
        cnt += 1

