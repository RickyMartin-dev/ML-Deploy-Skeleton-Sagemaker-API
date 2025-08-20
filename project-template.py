# Imports
import os
from pathlib import Path
import logging

# Define Logging Format
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s')

# specify files to create
list_of_files = [
    ".env", # Local development of ENVIRONMENT vatiables
    ".github/workflows/.gitkeep", # temp file for github CICD
    # "experiments/testing.py", # for testing files if needed
    "requirements.txt", # for package versions for API
    "Dockerfile", # API Docker File
    "tests/__init__.py", # creation of testing folder

    "app/__init__.py", # Main folder for app code
    "app/app.py", # Main folder for app code
    "app/model_loader.py", # loads from /opt/ml/model
    "app/logger.py", # JSON logger + CW embedded metrics
    "app/schema.py", # same pydantic schema
    "app/serve.sh", # bash command to serve application 

    "scripts/__init__.py", # scripts folder for jobs that need to be completed
    "scripts/create_model_and_endpoint.py", # python script to create model and endpoint
    "scripts/invoke_async.py", # python script to invoke model
]

# Go through list and create folders/files
for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    # logic for directory
    if filedir != "":
        # create directory
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory; {filedir} for the file: {filename}")

    # Create the files
    # check if file exists I do not want to replace
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, "w") as f:
            pass
            logging.info(f"Creating empty file: {filepath}")
    else: # if file already exists
        logging.info(f"{filename} already exists")