'''
AWS Lambda function that serves as an example for how to automate data egress
from the Voxel51 Platform.

| Copyright 2017-2020, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
'''
import base64
import boto3
from botocore.exceptions import ClientError
import json
import os

import eta.core.data as etad
import eta.core.storage as etas
import eta.core.video as etav

from voxel51.users.api import API
from voxel51.users.auth import Token

BUCKET = os.environ["BUCKET_NAME"]


def get_secret():
    '''Retrieves a secret from Secrets Manager.

    Returns:
        a secret string
    '''
    secret_arn = os.environ["SECRET_ARN"]

    client = boto3.client("secretsmanager")

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_arn)
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text using the
            # provided KMS key. Deal with the exception here, and/or rethrow at
            # your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            # You provided a parameter value that is not valid for the current
            # state of the resource. Deal with the exception here, and/or
            # rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these
        # fields will be populated.
        secret = decoded_binary_secret = None
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response["SecretBinary"]
            )

    return secret or decoded_binary_secret


def lambda_handler(event, context):
    '''Lambda function entrypoint, defined in the SAM `template.yaml` handler.

    This function should parse POST body data for the message from the API's
    webhook request, which is structured as:
    ```
    {
        "id": <id of Platform object>
        "event": <event>
        "msg": <misc string data about event>
    }
    ```

    The event key in the request object should only be one of the events this
    webhook was subscribed to.

    Args:
        event: the event dictionary with the Platform API request stored in the
            `body` key
        context: the context

    Returns:
        a dictionary with `statusCode` key
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
        api = API(token=Token.from_str(get_secret()))

        # Download the output to local disk
        api.download_job_output(job_id, job_output_path)

        # ############# Process Label Data ##############
        # Read the file in as an ETA VideoLabels object
        video_labels = etav.VideoLabels.from_json(job_output_path)

        # Translate to your label data format here!

        # Example of manipulating the VideoLabels!
        video_labels.add_video_attribute(
            etad.CategoricalAttribute("Video-Quality", "Amazing"))

        # # ############# Upload to Storage ##############
        path_on_bucket = "s3://{}/labels/{}.json".format(BUCKET, job_id)
        client = etas.S3StorageClient()
        # video_labels is already in memory so use upload_bytes
        client.upload_bytes(video_labels.to_str(pretty_print=False),
                            path_on_bucket, content_type="application/json")

        # Or you can upload the file on disk
        # client.upload(job_output_path, path_on_bucket,
        #               content_type="application/json")

        # For debug and CloudWatch logs
        print({"msg": msg, "event_type": event_type})

        # Return 200 on success!
        return {"statusCode": 200}

    except Exception as e:
        # If anything goes wrong return 500 and view logs for error
        print(e)
        return {"statusCode": 500}
