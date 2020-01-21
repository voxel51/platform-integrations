'''
AWS Lambda function that serves as an example for how to automate data egress
from the Voxel51 Platform.

| Copyright 2017-2020, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
'''
import json
import os

import eta.core.data as etad
import eta.core.storage as etas
import eta.core.video as etav

from voxel51.users.api import API
from voxel51.users.auth import Token


BUCKET = os.environ["BUCKET_NAME"]


TOKEN_DICT = {
    "access_token": {
        "private_key": os.environ["API_PRIV_KEY"],
        "created_at": "nobodycares",
        "token_id": os.environ["API_TOKEN_ID"],
        "base_api_url": os.environ["API_BASE_URL"]
    }
}


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
        api = API(token=Token(TOKEN_DICT))

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
