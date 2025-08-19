from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
import os, time, pandas as pd, uuid, json, datetime
import boto3

from app.schema import BatchRequest
from app.model_loader import load_artifacts
from app.logger import json_log, put_latency_metric

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Globals populated at startup
pre = None
model = None
schema = None

@app.on_event("startup")
def _load():
    global pre, model, schema
    pre, model, schema = load_artifacts()
    json_log("startup_loaded_artifacts")

@app.get("/ping")
def ping():
    try:
        _ = getattr(model, "predict_proba", None)
        return PlainTextResponse("ok", status_code=200)
    except Exception as e:
        return PlainTextResponse(str(e), status_code=500)

@app.post("/invocations")
def invocations(req: BatchRequest, request: Request):
    t0 = time.time()
    try:
        rows = [r.model_dump() for r in req.instances]
        df = pd.DataFrame(rows)

        # Simple imputations mirroring training assumptions
        if "Age" in df: df["Age"] = df["Age"].fillna(df["Age"].median())
        if "Embarked" in df: df["Embarked"] = df["Embarked"].fillna("S")

        X = df[["Pclass","Sex","Age","SibSp","Parch","Fare","Embarked"]]
        Xtr = pre.transform(X)
        proba = model.predict_proba(Xtr)[:, 1]
        pred  = (proba >= 0.5).astype(int)

        result = [{"proba": float(p), "pred": int(c)} for p, c in zip(proba, pred)]
        latency = (time.time() - t0) * 1000.0
        put_latency_metric(latency_ms=latency)
        json_log("inference_ok", n=len(result), latency_ms=latency)
        # Optional: store recent features for drift checks
        bucket = os.getenv("BUCKET")
        if bucket:
            s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
            key = f"drift/recent/{datetime.date.today().isoformat()}/{uuid.uuid4()}.json"
            s3.put_object(Bucket=bucket, Key=key, Body=df.to_json(orient="records").encode())

        return JSONResponse({"predictions": result}, status_code=200)

    except Exception as e:
        json_log("inference_error", error=str(e))
        return JSONResponse({"error": str(e)}, status_code=500)
