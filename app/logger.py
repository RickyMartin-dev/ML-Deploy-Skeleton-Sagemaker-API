import json, time
from aws_embedded_metrics import metric_scope

def json_log(msg, **kwargs):
    print(json.dumps({"msg": msg, "ts": time.time(), **kwargs}), flush=True)

@metric_scope
def put_latency_metric(metrics, latency_ms: float):
    metrics.set_namespace("Titanic/Inference")
    metrics.put_dimensions({"Service": "AsyncEndpoint"})
    metrics.put_metric("LatencyMs", latency_ms, "Milliseconds")
    metrics.set_property("component", "inference")