from pymongo import MongoClient

client = MongoClient("", 27017, username="", password="").racetrack


def insert_self_chat(document):
    """ 向 self chat 表中插入一个文档 """
    client.chat_record.insert_one(document)


def insert_annotator(name, password, role):
    """  插入一个新的 annotator 信息 """
    client.annotator.insert_one({'name': name, 'password': password, 'role': role})


def insert_chat_annotation(chat_record_id, annotator_id):
    client.chat_annotation.insert_one({
        'chat_record_id': chat_record_id,
        'annotator_id': annotator_id,
        'annotation': {}
    })


def insert_chat_annotation_many(doc):
    client.chat_annotation.insert_many(doc)


def insert_chat_record(bot_name, chat_content, chat_type, topic_type):
    client.chat_record.insert_one({
        'bot_name': bot_name,
        'chat_content': chat_content,
        'chat_type': chat_type,
        'topic_type': topic_type
    })


def insert_chat_generation(annotator_id, chat_record_id):
    client.chat_generation.insert_one({
        'annotator_id': annotator_id,
        'chat_record_id': chat_record_id,
        'state': 'unfinished'
    })


def get_all_annotator_id(role):
    """ 获取所有标注人员的 id """
    return [str(annotator['_id']) for annotator in client.annotator.find({'role': role})]


def get_annotator_account(role):
    """ 获取标注人员的账号信息 """
    return [doc for doc in client.annotator.find({'role': role})]


def get_chat_record_id_between(start, end):
    """ 获取所有start开始的对话的 id """
    a = [str(chat_record['_id']) for chat_record in client.chat_record.find()]
    return a[start:end]
