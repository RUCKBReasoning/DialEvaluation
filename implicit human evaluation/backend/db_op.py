from bson import ObjectId
from pymongo import MongoClient

client = MongoClient("", 27017, username="", password="").racetrack


def update_access_token(plato_account_id, access_token):
    """ 更新指定plato账号的access token """
    client.plato_account.update_one({'_id': plato_account_id}, {'$set': {'access_token': access_token}})


def update_session_content(session_id, openid, doc):
    if session_id == '':
        result = client.session.insert_one({
            'openid': openid,
            'content': [doc]
        })
        session_id = str(result.inserted_id)
    else:
        content = client.session.find_one({'_id': ObjectId(session_id)})['content']
        content.append(doc)
        client.session.update_one(
            {'_id': ObjectId(session_id)},
            {'$set': {'content': content}}
        )
    return session_id


def update_session_choose(session_id, chosen_msg_index):
    content = client.session.find_one({'_id': ObjectId(session_id)})['content']
    for i in range(len(content[-1]['bot'])):
        content[-1]['bot'][i]['chosen'] = False
    content[-1]['bot'][chosen_msg_index]['chosen'] = True
    client.session.update_one(
        {'_id': ObjectId(session_id)},
        {'$set': {'content': content}}
    )


def get_plato_account_all():
    """ 获取所有的plato账号 """
    return [doc for doc in client.plato_account.find()]


def get_prompt():
    """ 获取作为提示的起始语句 """
    prompt = [doc['content'] for doc in client.start_utterance.aggregate([{"$sample": {"size": 1}}])][0]
    return prompt


def get_bot_name_all():
    """ 获取所有chatbot的姓名 """
    return [doc['bot_name'] for doc in client.chatbot.find({'is_online': True})]


def get_bot_all():
    """ 获取所有bot的信息（不含id） """
    return [doc for doc in client.chatbot.find({'is_online': True}, {'_id': 0})]


def get_bot_order(session_id):
    """ 获取当前session的chatbot顺序 """
    bot_order = []
    content = client.session.find_one({'_id': ObjectId(session_id)})['content']
    for msg in content:
        bot_order.append([bot['name'] if bot['name'] != 'GLM-Finetune' else 'Finetune' for bot in msg['bot']])
    return bot_order


def get_chosen_num_all(bot_name):
    """ 获取全部时间内指定chatbot被选中的数量 """
    chosen_num = 0
    content_list = [doc['content'] for doc in client.session.find()]
    for content in content_list:
        for msg_list in content:
            for bot in msg_list['bot']:
                if bot['name'] == bot_name:
                    if bot['chosen']:
                        chosen_num += 1
                    break
    return chosen_num


def get_chosen_num_session(bot_name, session_id):
    """ 获取session内指定chatbot被选中的数量 """
    chosen_num = 0
    content = client.session.find_one({'_id': ObjectId(session_id)})['content']
    for msg_list in content:
        for bot in msg_list['bot']:
            if bot['name'] == bot_name:
                if bot['chosen']:
                    chosen_num += 1
                break
    return chosen_num


def get_rank(session_id):
    """ 获取全时间排行榜列表 """
    rank_list = []
    bot_name_list = get_bot_name_all()
    for bot_name in bot_name_list:
        rank_list.append({
            'bot_name': bot_name if bot_name != 'GLM-Finetune' else 'Finetune',
            'chosen_num': get_chosen_num_all(bot_name) if session_id == ''
            else get_chosen_num_session(bot_name, session_id)
        })
    rank_list.sort(key=lambda k: (k.get('chosen_num', 0)), reverse=True)
    return rank_list
