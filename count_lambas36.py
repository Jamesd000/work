import boto3
from datetime import datetime, timezone

def list_and_count_python36_lambdas():
    lambda_client = boto3.client('lambda', region_name='eu-west-2')
    logs_client = boto3.client('logs', region_name='eu-west-2')

    paginator = lambda_client.get_paginator('list_functions')
    python36_lambdas = []
    python36_count = 0  # Counter for Python 3.6 lambdas

    # Iterate through the Lambda functions
    for page in paginator.paginate():
        for function in page['Functions']:
            runtime = function.get('Runtime', None)  # Safely get the 'Runtime'
            if runtime == 'python3.6':
                python36_count += 1
                function_name = function['FunctionName']  # Here we define 'function_name'
                log_group_name = f"/aws/lambda/{function_name}"  # Construct the log group name using 'function_name'
                print (log_group_name)
                # Attempt to retrieve log stream information
                try:
                    streams = logs_client.describe_log_streams(
                        logGroupName=log_group_name,
                        orderBy='LastEventTime',
                        descending=True,
                        limit=1
                    )
                    last_execution_time = None
                    if streams.get('logStreams'):
                        last_event_timestamp = streams['logStreams'][0]['lastEventTimestamp']
                        last_execution_time = datetime.fromtimestamp(last_event_timestamp / 1000.0, timezone.utc)
                except logs_client.exceptions.ResourceNotFoundException:
                    print(f"Log group {log_group_name} does not exist.")
                    last_execution_time = None

                # Append function details including last execution time
                python36_lambdas.append({
                    'FunctionName': function_name,
                    'Runtime': runtime,
                    'LastExecutionTime': last_execution_time
                })

    # Print each Python 3.6 lambda function and its last execution time
    for lambda_function in python36_lambdas:
        print(f"Function Name: {lambda_function['FunctionName']}")
        print(f"Runtime: {lambda_function['Runtime']}")
        print(f"Last Execution Time: {lambda_function['LastExecutionTime']}")
        print('-' * 50)

    # Return count and list of functions
    return python36_count, python36_lambdas

# Example usage of the function
count, lambdas = list_and_count_python36_lambdas()
print(f"Total number of Python 3.6 Lambda functions: {count}")
