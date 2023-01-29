import json
import requests
import time
import json
from generation_metrics import *
import codecs

testsets = ["KonwConv"]  # "Diamante", "DuSinc", "DuConv", "kdconv", "NaturalConv", 
model = "GLM_Finetune"  # GLM_Finetune
URL = {
        "CDial_GPT": "http://mzy:10003/cdial-gpt",
        "GLM10B": "http://mzy:8001/glm-10b",
        "GLM130B": "http://mzy:8001/glm-130b",
        "EVA": "http://mzy:8001/eva",
        "XDAI": "http://aigc.aminer.cn/test/xd/v2/query",
        "GLM_Finetune": "http://36.103.203.210:8008/generate",
    }


def evaluate(results):
    """Evaluation."""

    metric = Metric(None)

    generation_res = None
    metric_res = {}

    generation_res = []
    # print("results = ", results)
    for ctx, lab, gen in results:  # context, reference, generation
        metric.forstr([lab], gen)
        
        generation_res.append({
            'context': ctx,
            'response': lab,
            'generation': gen,
        })

    metric_res, *_ = metric.close()

    return metric_res, generation_res


def post(chat_list, cnt):
    # time.sleep(0.5)
    if model == "XDAI":
        msgList = []
        for i in range(0, len(chat_list) - 2, 2):
            msgList.append({
                'talker': 'user',
                'text': chat_list[i]
            })
            msgList.append({
                'talker': 'bot',
                'text': chat_list[i + 1]
            })
        msgList.append({
            'talker': 'user',
            'text': chat_list[cnt - 2]
        })
        # print(msgList)
        data = {  # 构造传输的数据
            "xdid": "#xd小呆6836",
            "platform": "automatic-eval",
            "platform_id": "lny",
            "requestId": 'automatic-eval' + str(time.time()),
            "msgList": msgList
        }
        res = requests.post(url='http://aigc.aminer.cn/test/xd/v2/query', json=data).json()
        print(res['data']['reply'])
        return res['data']['reply']
    else:    
        data = {  # 构造传输的数据
            "content": chat_list[0 : cnt - 1]  # [0, cnt - 1)
        }
        time.sleep(1)
        res = requests.post(url=URL[model], json=data)
        print(res)
        res = res.json()
        print(res)
        return res['data']


if __name__ == "__main__":
    num = 0
    for testset in testsets:
        results = []
        with open(r'data/' + testset + r'/test.txt', 'r', encoding='utf-8') as datafile:
            with open(r"results/" + model + '/' + testset + r"/generation.json", "a", encoding='utf-8') as datafile2:
                for line in datafile:
                    num += 1
                    if(num <= 683):
                        continue
                    # if(num > 11440):
                    #     exit(0)

                    chat_list = []
                    cnt = 0
                    dialogue = line.split('\t')
                    if(dialogue[-1] == '\n'):  # 丢弃最后的换行符
                        dialogue.pop()
                    if model == "CDial_GPT": # 最多传递最后2轮对话历史
                        if len(dialogue) >= 4:
                            chat_list.extend(dialogue[-4:])
                            cnt = 4
                        else:
                            chat_list.extend(dialogue)
                            cnt = len(dialogue)
                    elif model == "GLM10B":
                        if len(dialogue) >= 6:
                            if len(dialogue) % 2 == 0:
                                chat_list.extend(dialogue[-6:])
                                cnt = 6
                            else:
                                chat_list.extend(dialogue[-5:])
                                cnt = 5
                        else:
                            chat_list.extend(dialogue)
                            cnt = len(dialogue)
                    elif model == "GLM_Finetune":
                        if len(dialogue) >= 10:
                            chat_list.extend(dialogue[-10:])
                            cnt = 10
                        else:
                            chat_list.extend(dialogue)
                            cnt = len(dialogue)
                    else:
                        # for conv in dialogue:
                        #     chat_list.append(conv)
                        #     cnt += 1
                        chat_list.extend(dialogue)
                        cnt = len(dialogue)
                    print(chat_list)
                    generation = post(chat_list, cnt)
                    json.dump((chat_list[0 : cnt - 1], chat_list[cnt - 1], generation), datafile2, ensure_ascii=False, indent=2)
                    datafile2.write(",\n")
            datafile2.close()
        datafile.close()    
