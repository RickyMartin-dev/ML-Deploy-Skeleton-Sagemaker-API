import json, time

def json_log(msg, **kwargs):
    print(json.dumps({"msg": msg, "ts": time.time(), **kwargs}), flush=True)

def put_latency_metric(latency_ms: float):
    # CloudWatch EMF payload
    emf = {
      "_aws": {
        "Timestamp": int(time.time() * 1000),
        "CloudWatchMetrics": [{
          "Namespace": "Titanic/Inference",
          "Dimensions": [["Service"]],
          "Metrics": [{"Name": "LatencyMs", "Unit": "Milliseconds"}]
        }]
      },
      "Service": "AsyncEndpoint",
      "LatencyMs": latency_ms,
      "component": "inference"
    }
    print(json.dumps(emf), flush=True)


# import json, time
# from aws_embedded_metrics import metric_scope

# def json_log(msg, **kwargs):
#     print(json.dumps({"msg": msg, "ts": time.time(), **kwargs}), flush=True)

# @metric_scope
# def put_latency_metric(metrics, latency_ms: float):
#     metrics.set_namespace("Titanic/Inference")
#     metrics.put_dimensions({"Service": "AsyncEndpoint"})
#     metrics.put_metric("LatencyMs", latency_ms, "Milliseconds")
#     metrics.set_property("component", "inference")

# import json, time, asyncio
# from aws_embedded_metrics.logger.metrics_logger import create_metrics_logger

# def json_log(msg, **kwargs):
#     print(json.dumps({"msg": msg, "ts": time.time(), **kwargs}), flush=True)

# def _ensure_event_loop():
#     try:
#         asyncio.get_running_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)

# def put_latency_metric(latency_ms: float):
#     _ensure_event_loop()
#     m = create_metrics_logger()
#     m.set_namespace("Titanic/Inference")
#     m.put_dimensions({"Service": "AsyncEndpoint"})
#     m.put_metric("LatencyMs", latency_ms, "Milliseconds")
#     m.set_property("component", "inference")
#     # flush() is sync in this path
#     m.flush()