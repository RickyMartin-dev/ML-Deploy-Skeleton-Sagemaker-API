import os, json, time, uuid
import boto3
from botocore.exceptions import ClientError

from dotenv import load_dotenv
load_dotenv()


AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BUCKET = os.getenv("BUCKET")
ENDPOINT_NAME = os.getenv("ENDPOINT_NAME", "titanic-async")

assert BUCKET, "BUCKET env var required"

runtime = boto3.client("sagemaker-runtime", region_name=AWS_REGION)
s3 = boto3.client("s3", region_name=AWS_REGION)

REQ = {
    "instances": [
        {"Pclass": 3, "Sex": "male", "Age": 22, "SibSp": 1, "Parch": 0, "Fare": 7.25, "Embarked": "S"}
    ]
}

# 1) Upload request with proper ContentType so FastAPI sees JSON
input_key = f"inference/input/{uuid.uuid4()}.json"
s3.put_object(
    Bucket=BUCKET,
    Key=input_key,
    Body=json.dumps(REQ).encode(),
    ContentType="application/json"  # IMPORTANT
)

# 2) Invoke async
resp = runtime.invoke_endpoint_async(
    EndpointName=ENDPOINT_NAME,
    InputLocation=f"s3://{BUCKET}/{input_key}",
    # You can also pass InferenceId=str(uuid.uuid4()) if you want to correlate
)
outloc = resp["OutputLocation"]
print("OutputLocation:", outloc)

bucket = outloc.split("/", 3)[2]
key = outloc.split("/", 3)[3]

# 3) Poll with backoff and show helpful diagnostics on failure
deadline = time.time() + 300  # 5 min timeout
sleep = 1.0
while True:
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj["Body"].read().decode()
        print("RESULT:", body)
        break
    except s3.exceptions.NoSuchKey:
        if time.time() > deadline:
            raise TimeoutError(f"Timed out waiting for {outloc}")
        print("waiting...")
        time.sleep(sleep)
        sleep = min(sleep * 1.5, 10)
    except ClientError as e:
        # AccessDenied usually means model role can't write to S3OutputPath
        print("S3 error while fetching output:", e)
        raise
