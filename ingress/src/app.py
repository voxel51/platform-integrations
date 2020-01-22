'''
AWS Lambda function that serves as an example for how to automate data ingress
to the Voxel51 Platform.

| Copyright 2017-2020, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
'''
import base64
from datetime import datetime, timedelta
import json
import mimetypes
import os
import urllib

import boto3
from botocore.exceptions import ClientError

from voxel51.users.api import API
from voxel51.users.auth import Token
from voxel51.users.jobs import JobRequest, JobComputeMode


def get_analytic_names():
    '''Retrieve names of analytics to run on data.

    Returns:
        the list of analytic names
    '''
    analytic_names = os.getenv("ANALYTIC_NAMES", "")
    return analytic_names.split(",") if analytic_names else []


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


def create_presigned_url(bucket_name, object_key, expiration=3600):
    '''Generates a presigned URL with GET access to an S3 object.

    Args:
        bucket_name: the name of the bucket
        object_key: the object key
        expiration: the time in seconds for the presigned URL to remain valid

    Returns:
        url: the presigned URL string
        expiration_date: a datetime describing the expiration date of the URL
    '''
    # Generate a presigned URL for the S3 object.
    s3_client = boto3.client("s3")
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        raise e

    # The response contains the presigned URL.
    expiration_date = (
        datetime.now() + timedelta(seconds=expiration)).isoformat()
    return response, expiration_date


def lambda_handler(event, context):
    '''Main handler that automatically uploads S3 objects to the Voxel51
    Platform as signed URLs and runs the configured analytic(s) on them.

    Args:
        event: the event dictionary
        context: the context

    Returns:
        a list of metadata describing the executed jobs
    '''
    # Get the object from the event.
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    object_key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"])
    object_size = event["Records"][0]["s3"]["object"]["size"]

    try:
        # Authenticate to Voxel51 Platform.
        api = API(Token.from_str(get_secret()))

        # Post data as URL.
        url, expiration_date = create_presigned_url(bucket_name, object_key)
        mime_type = mimetypes.guess_type(object_key)[0]
        metadata = api.post_data_as_url(
            url, object_key, mime_type, object_size, expiration_date
        )

        # Upload job request(s) on specified analytics to platform.
        data_id = metadata["id"]
        version = None
        compute_mode = JobComputeMode.BEST
        job_metadata = []

        for analytic in get_analytic_names():
            job_request = JobRequest(
                analytic, version=version, compute_mode=compute_mode
            )
            job_request.set_input("video", data_id=data_id)
            job_name = "{}-{}".format(object_key, analytic)
            job_metadata += [
                api.upload_job_request(
                    job_request, job_name, auto_start=True
                )
            ]

        return job_metadata

    except Exception as e:
        print(
            "Error processing object {} from bucket {}. Event {}".format(
                object_key, bucket_name, json.dumps(event, indent=2)
            )
        )
        raise e
