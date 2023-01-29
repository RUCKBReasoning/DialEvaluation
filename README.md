# Automatic Evaluation

##  1 Data Processing

To prepare the data, You need to create a directory under the path `data/`, which contains `train.txt`, `valid.txt`, and `test.txt`. 

The functions that process datasets are located in the file `data/data_process.py`. After the processing, each line in the files should be a dialogue sample. Different utterances are separated with `\t` and the last utterance is the response that the model needs to generate. 

```
你好，知道北京市规划展览馆在什么地方吗？	嗯呢，地址在北京市东城区前门东大街20号（老北京火车站东侧），电话你要不？	不用了，我已经知道了，电话是010-67017074，帮我查一下这里可以玩多久好了？	大概可以我1小时 - 2小时，知道这里啥时间开放吗？	周一闭馆，周二-周日9:00-17:00，16:00停止入馆，门票贵不？	免费开放，凭有效证件领票入场。	挺好呀，该景点周边有没有其他好玩的地方啊？	好多呢，比如故宫，天安门广场，恭王府等，都是历史遗留的产物。	我想去恭王府看看，能把详细地址发给我吗？	可以，地址在北京市西城区柳荫街甲14号，电话你有没？	有的，电话是010-83288149，这里能够玩多久呀？	差不多能玩2小时 - 4小时吧，门票贵不？	
```



## 2 RUN

All the python scripts to run is in `src/`.

* `generate.py`: Invoke the API of the model and generate the response.
* `metric.py`: Calculate metrics according to the generated responses.
* `generation_metrics.py`: Include utility functions used to calculate metrics.

Before running the code, please change `model` in the script according to the `URL`. The results can be found in `results/{{model}}/{{testset}}`.

