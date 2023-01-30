import pymongo

# 1. create mongdb
client = pymongo.MongoClient("mongodb://YOUR_IP:27017/")
db = client['racetrack']

# 2. create collections and insert sample data to show the structure
col = db['chatbot']
col.insert_one({
    'bot_name': 'bot',
    'intro': 'intro',
    'is_online': False,
    'short': 'BT'
})
col = db['plato_account']
col.insert_one({
    'access_token': 'access_token',
    'api_key': 'api_key',
    'bot_id': 'bot_id',
    'can_use': False,
    'secret_key': 'secret_key'
})
col = db['session']
col.insert_one({
    'content': 'content',
    'openid': 'openid'
})
col = db['start_utterance']
col.insert_one({
    'content': '你喜欢看书吗'
})
