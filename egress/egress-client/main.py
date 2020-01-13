'''
Egress Client Example for the Voxel51 Platform API Webhook Handler.

| Copyright 2017-2020, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
'''
from voxel51.users.api import API
from voxel51.users.auth import Token
import eta.core.video as etav
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
    ''' Lambda function entry point, defined in the SAM template.yaml "Handler"
    This function should parse POST body data for the message from the API's
    webhook request, which is structured as:
    {
        "id":<id of Platform object>
        "event":<event>
        "msg":<misc str data about event>
    }
    The event key in the request object should only be one of the events this
    webhook was subscribed to.

    Args:
        event: object with request data, Platform API request is on event.body
        context:
    Returns:
        Object with "statusCode"
    '''
    try:
        # ############# Process Request ##############
        # Make sure request has a body
        body = event.get("body")
        if not body:
            print("POST missing body!")
            return {"statusCode": 400}

        # Check for required keys on json body
        body = json.loads(body)
        job_id = body.get("id")
        event_type = body.get("event")
        msg = body.get("msg")
        if not job_id:
            print("POST body missing jobId param")
            return {"statusCode": 400}

        # For this example, we are listening to job_complete events.
        # Only after this event fires can job output be downloaded.
        if "job_complete" != event_type:
            print("Wrong event type: {}".format(event_type))
            return {"statusCode": 400}

        # ############# Retrieve Output from API ##############
        # AWS Lambda note: the /tmp directory is the only writable part of the
        # virtual file system during lambda's runtime

        # For this example, we are assuming job outputs are video-labels jsons
        job_output_path = os.path.join("/tmp", job_id + ".json")

        # Create an authenticated connection to the API with your token
        api = API(token=Token(token_dict))
        # Download the output to local disk
        api.download_job_output(job_id, job_output_path)

        # ############# Process Label Data ##############
        # Read the file in as an ETA VideoLabels object
        video_labels = etav.VideoLabels.from_json(job_output_path)
        print(video_labels)

        # Translate to your label data format here!

        # ############# Upload to Storage ##############
        with open(job_output_path, "rb") as read_stream:

            # Upload to S3 bucket for storage
            path_on_bucket = "labels/" + job_id + ".json"
            client = boto3.client("s3")
            client.put_object(Body=read_stream,
                              Bucket="v51-test-egress-268586343424",
                              Key=path_on_bucket)

        # For debug and CloudWatch logs
        print({"msg": msg, "event_type": event_type})
        # Return 200 on success!
        return {"statusCode": 200}

    except Exception as e:
        # If anything goes wrong return 500, and view logs for error
        print(e)
        return {"statusCode": 500}
