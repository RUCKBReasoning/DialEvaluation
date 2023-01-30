import pymongo

# 1. create mongdb
client = pymongo.MongoClient("mongodb://YOUR_IP:27017/")
db = client['racetrack']

# 2. create collections and insert sample data to show the structure
col = db['annotator']
col.insert_one({
    'name': 'name',
    'password': 'password',
    'role': 'role',
})
col = db['chat_annotation']
col.insert_one({
    'annotation': 'annotation',
    'annotator_id': 'annotator_id',
    'chat_record_id': 'chat_record_id',
})
col = db['chat_generation']
col.insert_one({
    'annotator_id': 'annotator_id',
    'chat_record_id': 'chat_record_id',
    'state': 'unfinish'
})
col = db['chat_record']
col.insert_one({
    'bot_name': 'bot_name',
    'chat_content': 'chat_content',
    'chat_type': 'chat_type',
    'topic_type': 'topic_type'
})
