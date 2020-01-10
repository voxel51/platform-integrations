from voxel51.users.api import API
from voxel51.users.auth import Token
import json
import boto3

import os

token_dict = {
    "access_token": {
        "private_key": os.environ["API_PRIV_KEY"],
        "created_at": "nobodycares",
        "token_id": os.environ["API_TOKEN_ID"],
        "base_api_url": os.environ["API_BASE_URL"]
    }
}


def lambda_handler(event, context):
    try:
        body = event.get("body")
        if not body:
            return {
                "statusCode": 400,
                "message": "POST missing body!"
            }
        body = json.loads(body)
        job_id = body.get("id")
        event_type = body.get("event")
        msg = body.get("msg")
        if not job_id:
            return {
                "statusCode": 400,
                "message": "POST body missing jobId param"
            }
        if "job_complete" != event_type:
            return {
                "statusCode": 400,
                "message": "Job is not in the right state",
                "event_type": event_type,
                "msg": msg,
            }
        job_output_path = os.path.join("/tmp", job_id + ".json")
        api = API(token=Token(token_dict))
        api.download_job_output(job_id, job_output_path)
        with open(job_output_path, "rb") as read_stream:
            path_on_bucket = "labels/" + job_id + ".json"
            client = boto3.client("s3")
            client.put_object(Body=read_stream,
                              Bucket="v51-test-egress-268586343424",
                              Key=path_on_bucket)

        print({"msg": msg, "event_type": event_type})
        return {
            "statusCode": 200,
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
        }
