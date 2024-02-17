import ast
import json
import logging
import os

import boto3
import requests
from botocore.exceptions import ClientError

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Class to retrieve secrets from Secrets Manager

    Attributes:
        secret_name (str): The name of the secret
        region_name (str): The name of the region
        client (boto3.client): The client for Secrets Manager
    """

    def __init__(self, secret_name, region_name):
        self.secret_name = secret_name
        self.region_name = region_name
        self.client = boto3.client(
            service_name='secretsmanager',
            region_name=region_name
        )

    def get_secret(self, key):
        """
        Retrieves the value of a secret based on the provided key.

        Args:
            key (str): The key of the secret to retrieve.

        Returns:
            str: The value of the secret.

        Raises:
            ClientError: If there is an error retrieving the secret.
        """
        try:
            get_secret_value_response = self.client.get_secret_value(
                SecretId=self.secret_name
            )
        except ClientError as e:
            raise e

        secret_data = get_secret_value_response['SecretString']
        secret = ast.literal_eval(secret_data)

        return secret[key]


secrets_manager = SecretsManager(
    secret_name=os.environ.get("SECRET_NAME"),
    region_name=os.environ.get("REGION_NAME")
)

BACKLOG_API_KEY = secrets_manager.get_secret("BacklogApiKey")
BACKLOG_BASE_URL = secrets_manager.get_secret("BacklogBaseURL")


def truncate(text, length):
    """
    Truncate the given text to the given length.

    Args:
        text (str): The text to truncate.
        length (int): The length to truncate the text to.

    Returns:
        str: The truncated text.
    """
    if len(text) > length:
        return text[:length] + '...'
    return text


def issue_search(parameters):
    """
    Search for issues in the Backlog API based on the given parameters.

    Args:
        parameters (list): A list of dictionaries containing the parameter name
        (sort, summary, keyword, and etc.) and value.

    Returns:
        object: The response object from the Backlog API.
    """
    params = {p['name']: p['value'] for p in parameters}

    response = requests.get(
        f"{BACKLOG_BASE_URL}/api/v2/issues?apiKey={BACKLOG_API_KEY}&count=10",
        params=params
    )
    issues = json.loads(response.text)
    extracted_issues = []

    for issue in issues:
        extracted_issue = {
            'issueKey': issue['issueKey'],
            'summary': issue['summary'],
            'status': issue['status']['name'] if issue['status'] else None,
            'assignee': issue['assignee']['name'] if issue['assignee'] else None,
            'dueDate': issue['dueDate'] if issue['status'] else None,
        }
        extracted_issues.append(extracted_issue)
    return {'issues': extracted_issues}


def wiki_search(parameters):
    """
    Search for wikis in the Backlog API based on the given parameters.

    Args:
        parameters (list): A list of dictionaries containing the parameter name
        (keyword, projectIdOrKey) and value.

    Returns:
        object: The response object from the Backlog API.
    """
    params = {p['name']: p['value'] for p in parameters}

    response = requests.get(
        f"{BACKLOG_BASE_URL}/api/v2/wikis?apiKey={BACKLOG_API_KEY}",
        params=params
    )
    wikis = json.loads(response.text)
    extracted_issues = []

    for issue in wikis:
        extracted_issue = {
            'name': issue['name'],
            'content': truncate(issue['content'], 100)
        }
        extracted_issues.append(extracted_issue)
    return {'issues': extracted_issues}


def lambda_handler(event, context):
    """
    Handles the Lambda function invocation.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object passed to the Lambda function.

    Returns:
        dict: The API response containing the action group, API path,
        HTTP method, HTTP status code, and response body.
    """

    print(event)

    parameters = event["parameters"]
    api_path = event["apiPath"]
    body = {}

    if api_path == "/issues":
        body = issue_search(parameters)

    elif api_path == "/wikis":
        body = wiki_search(parameters)

    response_body = {"application/json": {"body": json.dumps(body)}}

    action_response = {
        "actionGroup": event["actionGroup"],
        "apiPath": event["apiPath"],
        "httpMethod": event["httpMethod"],
        "httpStatusCode": 200,
        "responseBody": response_body,
    }
    api_response = {"messageVersion": "1.0", "response": action_response}
    return api_response
