#coding=utf-8
import json
import json
from generation_metrics import *

testsets = ["Diamante", "DuConv", "DuSinc_release", "DuSinc_release_test_B", "kdconv", "NaturalConv"]  # 
model = "CDial_GPT"


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


if __name__ == "__main__":
    for testset in testsets:
        with open("results/" + model + "/" + testset + "/generation.json", "r", encoding='utf-8') as datafile:
            results = json.load(datafile)
            metrics, generation = evaluate(results)
            log_string = "Eval result: "
            for key, value in metrics.items():
                log_string += " {}: {:.5} | ".format(key, value)
            with open("results/" + model + "/" + testset + "/metrics.json", "w", encoding='utf-8') as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)
        datafile.close()    
