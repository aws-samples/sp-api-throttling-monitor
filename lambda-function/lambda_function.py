import requests
import boto3
from requests_aws4auth.aws4auth import AWS4Auth


def lambda_handler(event, context):
    client = boto3.client('sts')
    iam_role = ''
    response = client.assume_role(
        RoleArn=iam_role,
        RoleSessionName='SPAPIRoleSession'
    )
    AccessKeyId = response['Credentials']['AccessKeyId']
    SecretAccessKey = response['Credentials']['SecretAccessKey']
    SessionToken = response['Credentials']['SessionToken']
    client_id = ''
    client_secret = ''
    refresh_token = ''
    payload = {'grant_type': 'refresh_token', 'client_id': client_id, 'client_secret': client_secret,
               'refresh_token': refresh_token}
    lwa = requests.post("https://api.amazon.com/auth/o2/token", data=payload)
    access_token = lwa.json()['access_token']
    headers = {'content-type': 'application/json', 'Accept': 'application/json', 'x-amz-access-token': access_token}
    auth = AWS4Auth(AccessKeyId, SecretAccessKey, 'us-east-1', 'execute-api',
                    session_token=SessionToken)
    sellersResponse = requests.get("https://sellingpartnerapi-na.amazon.com/sellers/v1/marketplaceParticipations",
                                   headers=headers, auth=auth)

    result = sellersResponse.json()
    result["code"] = sellersResponse.status_code
    if sellersResponse.status_code == 429:
        print("API limit exceeded")
        # Publish alarm to CloudWatch
        cloudwatch = boto3.client('cloudwatch')
        cloudwatch.put_metric_data(
            MetricData=[{
                'MetricName': 'API Error',
                'Dimensions': [{
                    'Name': 'FunctionName',
                    'Value': context.function_name
                }],
                'Unit': 'Count',
                'Value': 1
            }],
            Namespace='Custom'
        )
        return {
            "statusCode": result["code"],
            "body": "Too many requests"
        }
    else:
        print(sellersResponse.json())
        return {
            "statusCode": result["code"],
            "body": "Succeed"
        }
