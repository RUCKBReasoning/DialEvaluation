## API Format

Request method：POST

URL：Your URL

Parameters：

|  Param   |  Type  |  Illustration  |
|  :-:  | :-:  |  :-:  |
| content  | array | you need to input the context and request |


python example:
```
import requests

data = {
	"content": [
		"你喜欢看什么类型的小说",
		"科幻小说",
		"为什么"
	]
}

response = requests.post(url=URL, json=data).json()

print(response['data'])
```

