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


def get_self_chat_from_glm_130b(topic_type, starting_utterance, chat_rounds):
    """ 从 GLM-130B 获取 self chat 记录 """
    cr = chat_rounds * 2 - 1
    doc = {
        "bot_name": 'GLM-130B',
        "chat_type": "bot-bot",
        "topic_type": topic_type,
        "chat_content": [starting_utterance],
    }
    data = {
        "prompt": '请开始一段A和B的对话，由A先开始，你进行续写。A:' + starting_utterance + '',
        'sampling_strategy': 'BaseStrategy',
        'temperature': 0.9,
        'top_k': 40,
        'top_p': 0,
        'max_tokens': 512
    }
    while True:
        res = requests.post(url='http://36.103.203.210:8001/test', json=data)
        if res.status_code == 200:
            text = res.json()['text'][0][0]
            dialog = res.json()['text'][0][0].split(' ')
            if len(dialog) >= cr:
                for i in dialog[:cr]:
                    doc['chat_content'].append(i[2:])
                break
            else:
                print('token length is not enough')
                for i in dialog:
                    doc['chat_content'].append(i[2:])
                break
        else:
            print(res.status_code)
            time.sleep(2)
            exit(0)
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


def get_self_chat_from_xdai(topic_type, starting_utterance, chat_rounds):
    doc = {
        "bot_name": "XDAI",
        "chat_type": "bot-bot",
        "topic_type": topic_type,
        "chat_content": [starting_utterance],
    }
    data = {
        "xdid": "#xd小呆6836",
        "platform": "annotation",
        "platform_id": "mzy",
        "requestId": '',
        "msgList": []
    }
    for i in range(2 * chat_rounds - 1):
        data["requestId"] = "annotation-" + str(time.time())
        data['msgList'] = []
        t = 0 if len(doc["chat_content"]) % 2 == 1 else 1
        for j in range(len(doc["chat_content"])):
            data['msgList'].append({
                "talker": "user" if j % 2 == t else "bot",
                "text": doc["chat_content"][j]
            })
        res = requests.post(url='http://aigc.aminer.cn/test/xd/v2/query', json=data).json()['data']['reply']
        doc["chat_content"].append(res)
    return doc


if __name__ == '__main__':
    # EVA http://36.103.203.210:8001/eva
    # CDial-GPT http://36.103.203.210:8001/cdial-gpt
    # GLM-10B http://36.103.203.210:8001/glm-10b
    # GLM-130B http://36.103.203.210:8001/glm-130b
    # GLM-Finetune http://36.103.203.210:8008/generate

    topic_type = 'knowledge'
    # with open('starting-utterance-{}.txt'.format(topic_type)) as fp:
    #     su_list = fp.readlines()
    #
    # cnt = 1
    # for su in su_list:
    #     if cnt <= 63:
    #         cnt += 1
    #         continue
    #     document = get_self_chat_from_glm_130b(topic_type, su.rstrip('\n'), 5)
    #     insert_self_chat(document)
    #     print(cnt)
    #     cnt += 1

    su_list = [
        '世界富豪榜的前20位中有多少个中国人？',
    ]
    a_list = []
    for su in su_list:
        a = get_self_chat_from_deployed_model('GLM-Finetune', 'http://36.103.203.210:8008/generate', topic_type, su, 5)
        a_list.append(a)
    with open('tmp.txt', 'w') as fp:
        for a in a_list:
            fp.write(str(a['chat_content']))
            fp.write('\n')
