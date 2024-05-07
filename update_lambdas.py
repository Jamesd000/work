import boto3

def list_lambdas_to_update(region_name, runtime_check, version_threshold=None):
    lambda_client = boto3.client('lambda', region_name=region_name)
    paginator = lambda_client.get_paginator('list_functions')
    functions_to_update = []

    for page in paginator.paginate():
        for function in page['Functions']:
            runtime = function.get('Runtime', None)
            if runtime and runtime_check in runtime:
                if version_threshold:
                    # For Node.js, remove non-numeric parts and check version
                    version_num = runtime.replace(runtime_check, '').replace('.x', '')
                    if version_num.isdigit() and int(version_num) < version_threshold:
                        functions_to_update.append(function['FunctionName'])
                else:
                    # For Python, no version threshold check needed
                    functions_to_update.append(function['FunctionName'])
    return functions_to_update


def update_lambda_function(region_name, function_name, new_runtime):
    lambda_client = boto3.client('lambda', region_name=region_name)
    try:
        updated_function = lambda_client.update_function_configuration(
            FunctionName=function_name,
            Runtime=new_runtime
        )
        print(f"Updated {function_name} to {new_runtime} in {region_name}")
    except Exception as e:
        print(f"Failed to update {function_name} in {region_name}: {str(e)}")

def confirm_and_update(functions, region, new_runtime):
    if not functions:
        print("No functions to update.")
        return

    print("The following functions will be updated:")
    for function in functions:
        print(f"- {function}")

    confirmation = input("Do you want to proceed with the update? (yes/no): ")
    if confirmation.lower() == 'yes':
        for function in functions:
            update_lambda_function(region, function, new_runtime)
    else:
        print("Update cancelled.")

# List potential updates
python_functions = list_lambdas_to_update('eu-west-1', 'python3.6')
nodejs_functions = list_lambdas_to_update('us-east-1', 'nodejs', 18)

# Confirm and update Python functions
confirm_and_update(python_functions, 'eu-west-1', 'python3.9')

# Confirm and update Node.js functions
confirm_and_update(nodejs_functions, 'us-east-1', 'nodejs18.x')
