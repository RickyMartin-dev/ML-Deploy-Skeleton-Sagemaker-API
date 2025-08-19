import os, json, pickle

MODEL_DIR = os.getenv("MODEL_DIR", "/opt/ml/model")

def load_artifacts():
    with open(f"{MODEL_DIR}/preprocessor.pkl", "rb") as f:
        pre = pickle.load(f)
    with open(f"{MODEL_DIR}/model.pkl", "rb") as f:
        model = pickle.load(f)
    with open(f"{MODEL_DIR}/schema.json","r") as f:
        schema = json.load(f)
    return pre, model, schema