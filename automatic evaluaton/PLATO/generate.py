#coding=utf-8
import json
import requests
import time
import json
from generation_metrics import *
import codecs
import urllib3
urllib3.disable_warnings()

testsets = ["NaturalConv"]  # "Diamante", "DuConv", "DuSinc_release", "DuSinc_release_test_B", "kdconv", 
bot_id = []
API_key = [] # api key is obtained from baidu open platform
secret_key = []
access_token = ""
id = 0


def update_access_token():
    global access_token
    # get access token
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + API_key[id] + '&client_secret=' + secret_key[id]
    access_token = requests.get(host).json()['access_token']


def evaluate(results):
    """Evaluation."""

    metric = Metric(None)

    generation_res = None
    metric_res = {}

    generation_res = []
    for ctx, lab, gen in results:
        metric.forstr([lab], gen)
        
        generation_res.append({
            'context': ctx,
            'response': lab,
            'generation': gen,
        })

    metric_res, *_ = metric.close()

    return metric_res, generation_res


results = []
def post(chat_list, cnt):
    global id, access_token
    data = {
        'version': '3.0',
        'service_id': bot_id[id],
        'session_id': '',
        'log_id': bot_id[id] + str(int(time.time())),
        'request': {
            'query': chat_list[cnt - 2],
            'terminal_id': ''
        },
        "context": {
            "SYS_REMEMBERED_SKILLS": [],
            "SYS_CHAT_HIST": chat_list[0 : cnt - 1]
        }
    }      
    res = requests.post(
            url='https://aip.baidubce.com/rpc/2.0/unit/service/v3/chat?access_token=' + access_token, 
            json=data,
            headers={'Connection':'close'},
            verify=False
        ).json()

    time.sleep(0.3)
    if 'context' in res['result']:
        print('"' + res['result']['context']['SYS_PRESUMED_HIST'][-1] + '"')
        return res['result']['context']['SYS_PRESUMED_HIST'][-1]
    else:
        print("ERROR: 'context' not in res['result']")
        id += 1
        update_access_token()
        res = requests.post(
            url='https://aip.baidubce.com/rpc/2.0/unit/service/v3/chat?access_token=' + access_token, 
            json=data,
            headers={'Connection':'close'},
            verify=False
        ).json()


if __name__ == "__main__":
    update_access_token()
    num = 0
    for testset in testsets:
        results = []
        with open(r'../data/' + testset + r'/test.txt', 'r', encoding='utf-8') as datafile:
            with open(r"../results/PLATO/" + testset + r"/generation.json", "a", encoding='utf-8') as datafile2:
                for line in datafile:
                    num += 1
                    if(num <= 17327):
                        continue
                    # if(num > 11440):
                    #     exit(0)

                    chat_list = []
                    cnt = 0
                    dialogue = line.split('\t')
                    if(dialogue[-1] == '\n'):
                        dialogue.pop()
                    if len(dialogue) >= 14:
                            chat_list.extend(dialogue[-14:])
                            cnt = 14
                    else:
                        chat_list.extend(dialogue)
                        cnt = len(dialogue)
                    # for conv in dialogue:
                    #     chat_list.append(conv)
                    #     cnt += 1
                    #     if(cnt >= 14):
                    #         break
                    print(chat_list[0 : cnt - 1])
                    print('"' + chat_list[cnt - 1] + '"')
                    generation = post(chat_list, cnt)
                    json.dump((chat_list[0 : cnt - 1], chat_list[cnt - 1], generation), datafile2, ensure_ascii=False, indent=2)
                    datafile2.write(",\n")

            # metrics, generation = evaluate(results)
            # log_string = "Eval result: "
            # for key, value in metrics.items():
            #     log_string += " {}: {:.5} | ".format(key, value)
            # with open("results/" + testset + "/metrics.json", "w") as f:
            #     json.dump(metrics, f, ensure_ascii=False, indent=2)
            datafile2.close()
        datafile.close()    
