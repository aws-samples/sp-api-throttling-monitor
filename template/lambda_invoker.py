import boto3
import argparse
import time
parser = argparse.ArgumentParser()
parser.add_argument('region', type=str, help='region of the Lambda function')
parser.add_argument('function_name', type=str, help='name of the Lambda function')
parser.add_argument('num_invocations', type=int, help='number of invocations to make')
parser.add_argument('interval', type=float, help='interval in seconds between invocations')

args = parser.parse_args()
client = boto3.client('lambda',region_name=args.region)
for i in range(args.num_invocations):
    response = client.invoke(
        FunctionName=args.function_name,
        InvocationType='RequestResponse',
        Payload='{}'
    )
    print(response['Payload'].read().decode('utf-8'))
    time.sleep(args.interval)