import os, json, boto3
from dotenv import load_dotenv
load_dotenv()

AWS_REGION=os.getenv("AWS_REGION","us-east-1")
BUCKET=os.getenv("BUCKET")
ACCOUNT=os.getenv("ACCOUNT_ID")
ROLE=os.getenv("SM_ROLE_ARN")
MODEL_NAME=os.getenv("MODEL_NAME","titanic-logreg")
ENDPOINT_NAME=os.getenv("ENDPOINT_NAME","titanic-async")
IMAGE=f"{ACCOUNT}.dkr.ecr.{AWS_REGION}.amazonaws.com/titanic-infer:latest"

s3=boto3.client("s3", region_name=AWS_REGION)
sm=boto3.client("sagemaker", region_name=AWS_REGION)

# Resolve latest registry version
man = s3.get_object(Bucket=BUCKET, Key=f"registry/models/{MODEL_NAME}/MANIFEST.json")
manifest=json.loads(man["Body"].read())
model_data_url = manifest["artifacts"]["model"]  # s3://bucket/..model.tar.gz

container_def = {
  "Image": IMAGE,
  "Mode": "SingleModel",
  "ModelDataUrl": model_data_url,
  "Environment": {"PYTHONPATH": "/opt/ml/code"}
}

smr = sm.create_model(
ModelName=f"{MODEL_NAME}-model",
PrimaryContainer=container_def,
ExecutionRoleArn=ROLE
)
print("Created model:", smr["ModelArn"])

# Async Inference config
output_path=f"s3://{BUCKET}/inference/output/"
cfg_name=f"{ENDPOINT_NAME}-cfg"
try:
    sm.create_endpoint_config(
      EndpointConfigName=cfg_name,
      ProductionVariants=[{
        "VariantName":"v1",
        "ModelName":f"{MODEL_NAME}-model",
        "InitialInstanceCount":1,
        "InstanceType":"ml.m5.large",
        "InitialVariantWeight":1.0
      }],
      AsyncInferenceConfig={
        "OutputConfig":{"S3OutputPath":output_path},
        "ClientConfig":{"MaxConcurrentInvocationsPerInstance": 4}
      }
    )
    print("Created endpoint config", cfg_name)
except sm.exceptions.ResourceInUse:
    print("Config exists; reusing")

# Create or update endpoint
try:
    ep = sm.create_endpoint(EndpointName=ENDPOINT_NAME, EndpointConfigName=cfg_name)
    print("Creating endpoint:", ep["EndpointArn"])
except sm.exceptions.ResourceInUse:
    sm.update_endpoint(EndpointName=ENDPOINT_NAME, EndpointConfigName=cfg_name)
    print("Updating endpoint…")
