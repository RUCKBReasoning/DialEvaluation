import json
import codecs


def Diamante():
    with open(r'Diamante/test_unprocessed.txt', 'r', encoding='utf-8') as datafile:
        with open(r'Diamante/test.txt', 'w', encoding='utf-8') as datafile2:
            for line in datafile:
                dialogue = json.loads(line)  # {id: dialogue-00000, conversation: [{}, {}]}
                tmp = ""
                for conv in dialogue["conversation"]:
                    tmp += conv["utterance"] + "\t"
                datafile2.write(tmp + "\n")
        datafile2.close()
    datafile.close()    


def NaturalConv():
    dialog_list = json.loads(codecs.open(r"NaturalConv/dialog_release.json", "r", "utf-8").read())
    with open(r'NaturalConv/test.txt', 'w', encoding='utf-8') as datafile:
        for dialog in dialog_list:
            # json.dump(dialog, datafile, ensure_ascii=False)
            tmp = ""
            cnt = 0
            for word in dialog["content"]:
                tmp += word + "\t"
                cnt += 1
            if(cnt > 1):  # 至少一轮(2句)对话
                datafile.write(tmp + "\n")
    datafile.close()


def DuSinc():
    with open(r'DuSinc_release_test_B/test_dial_2.txt', 'r', encoding='utf-8') as datafile:
        with open(r'DuSinc_release_test_B/test.txt', 'w', encoding='utf-8') as datafile2:
            for line in datafile:
                dialogue = json.loads(line)  # {conversation: [{}, {}]}
                tmp = ""
                cnt = 0
                for conv in dialogue["conversation"]:
                    if(conv["utterance"] != ""):
                        tmp += conv["utterance"].replace(' ', '') + "\t"
                        cnt += 1
                if(cnt > 1):  # 至少一轮(2句)对话
                    datafile2.write(tmp + "\n")
        datafile2.close()
    datafile.close()   


def DuConv():
    with open(r'DuConv/test_1.txt', 'r', encoding='utf-8') as datafile:
        with open(r'DuConv/test_2.txt', 'r', encoding='utf-8') as datafile2:
            with open(r'DuConv/test.txt', 'w', encoding='utf-8') as datafile3:
                for line in datafile:
                    dialogue = json.loads(line)
                    tmp = ""
                    for conv in dialogue["history"]:
                        tmp += conv.replace(' ', '') + "\t"
                    if "response" in dialogue and dialogue["history"] != []:
                        tmp += dialogue["response"].replace(' ', '') + "\t"
                    if tmp != "":
                        datafile3.write(tmp + "\n")
                for line in datafile2:
                    dialogue = json.loads(line)
                    tmp = ""
                    for conv in dialogue["history"]:
                        tmp += conv.replace(' ', '') + "\t"
                    if "response" in dialogue and dialogue["history"] != []:
                        tmp += dialogue["response"].replace(' ', '') + "\t"
                    if tmp != "":
                        datafile3.write(tmp + "\n")
            datafile3.close()
        datafile2.close()
    datafile.close() 


def KnowVonc():
    with open(r'KonwConv/konw_conv_1204.json', 'r', encoding='utf-8') as datafile:
        with open(r'KonwConv/test.txt', 'w', encoding='utf-8') as datafile2:
            for line in datafile:
                dialogue = json.loads(line)  # {utterance: [, ]}
                tmp = ""
                cnt = 0
                for conv in dialogue["utterance"]:
                    if(conv != ""):
                        tmp += conv.replace(' ', '').replace('\n', '') + "\t"
                        cnt += 1
                if(cnt > 1):  # 至少一轮(2句)对话
                    datafile2.write(tmp + "\n")
        datafile2.close()
    datafile.close()   


if __name__ == "__main__":
    # Diamante()
    # NaturalConv()
    # DuSinc()
    # DuConv()
    KnowVonc()
