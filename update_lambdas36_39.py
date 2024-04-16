import boto3

def update_lambdas_to_python_39():
    lambda_client = boto3.client('lambda', region_name='eu-west-2')

    # Paginator for handling more than 50 Lambdas
    paginator = lambda_client.get_paginator('list_functions')

    updated_functions = []

    # Iterate through the Lambda functions
    for page in paginator.paginate():
        for function in page['Functions']:
            # Safely get the 'Runtime' value with a default of None if not present
            runtime = function.get('Runtime', None)
            if runtime == 'python3.6':
                try:
                    # Update the runtime to Python 3.9
                    updated_function = lambda_client.update_function_configuration(
                        FunctionName=function['FunctionName'],
                        Runtime='python3.9'
                    )
                    updated_functions.append(updated_function['FunctionName'])
                    print(f"Updated {function['FunctionName']} to Python 3.9")
                except Exception as e:
                    print(f"Failed to update {function['FunctionName']}: {str(e)}")

    return updated_functions

# Update all Python 3.6 Lambda functions to Python 3.9
updated_functions = update_lambdas_to_python_39()
print(f"Updated {len(updated_functions)} Lambda functions to Python 3.9.")
