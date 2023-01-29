import bson.errors
from bson import ObjectId
from pymongo import MongoClient

client = MongoClient("", 27017, username="", password="").racetrack


def check_auth(annotator_id, password):
    """ 检查指定 id 和密码的账户是否存在 """
    try:
        annotator = client.annotator.find_one({'_id': ObjectId(annotator_id), 'password': password})
    except bson.errors.InvalidId:
        return {'annotator_name': ''}
    if annotator is None or annotator['role'] != 'evaluation' and annotator['role'] != 'generation':
        return {'annotator_name': ''}
    else:
        return {'annotator_name': annotator['name'], 'annotator_role': annotator['role']}


def get_chat_record_not_annotate(annotator_id):
    """ 获取下一段待标注对话 """
    chat_num = client.chat_annotation.count_documents({
        'annotator_id': annotator_id,
        'annotation': {},
    })
    if chat_num == 0:
        return {
            'chat_num': 0
        }
    chat_annotation = client.chat_annotation.find_one({
        'annotator_id': annotator_id,
        'annotation': {},
    })
    chat_record = client.chat_record.find_one({
        '_id': ObjectId(chat_annotation['chat_record_id'])
    })
    return {
        'chat_num': chat_num,
        'chat_annotation_id': str(chat_annotation['_id']),
        'chat_record': chat_record['chat_content']
    }


def update_chat_annotation(chat_annotation_id, annotation):
    """ 更新对话的标注信息 """
    try:
        client.chat_annotation.update_one(
            {'_id': ObjectId(chat_annotation_id)},
            {'$set': {'annotation': annotation}}
        )
    except bson.errors.InvalidId:
        return {'status': 'fail'}
    return {'status': 'success'}


def get_chat_record_not_generate(annotator_id):
    """ 获取下一段待生成对话 """
    chat_num = client.chat_generation.count_documents({
        'annotator_id': annotator_id,
        'state': 'unfinished'
    })
    if chat_num == 0:
        return {
            'chat_num': 0
        }
    chat_generation = client.chat_generation.find_one({
        'annotator_id': annotator_id,
        'state': 'unfinished'
    })
    chat_record = client.chat_record.find_one({
        '_id': ObjectId(chat_generation['chat_record_id'])
    })
    return {
        'chat_num': chat_num,
        'chat_generation_id': str(chat_generation['_id']),
        'chat_record': chat_record['chat_content']
    }


def get_chat_generation_by_id(chat_generation_id):
    chat_generation = client.chat_generation.find_one({
        '_id': ObjectId(chat_generation_id)
    })
    return chat_generation


def get_bot_name_by_id(chat_record_id):
    bot_name = client.chat_record.find_one({
        '_id': ObjectId(chat_record_id)
    })['bot_name']
    return bot_name


def get_plato_account_all():
    """ 获取所有可用的plato账号 """
    return [doc for doc in client.plato_account.find({'can_use': True})]


def update_access_token(plato_account_id, access_token):
    """ 更新指定plato账号的access token """
    client.plato_account.update_one({'_id': plato_account_id}, {'$set': {'access_token': access_token}})


def update_chat_record(chat_generation_id, chat_content):
    """ 存储生成的对话 """
    client.chat_generation.update_one({
        '_id': ObjectId(chat_generation_id)
    }, {'$set': {'state': 'finished'}})
    chat_record_id = client.chat_generation.find_one({
        '_id': ObjectId(chat_generation_id)
    })['chat_record_id']
    client.chat_record.update_one({
        '_id': ObjectId(chat_record_id)
    }, {'$set': {'chat_content': chat_content}})
    return {'state': 'success'}
