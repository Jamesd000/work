import boto3

def update_lambda_to_python_39(function_name):
    lambda_client = boto3.client('lambda')

    try:
        # Retrieve the current configuration of the specified Lambda function
        response = lambda_client.get_function(FunctionName=function_name)
        current_runtime = response['Configuration']['Runtime']

        # Check if the runtime is Python 3.6
        if current_runtime == 'python3.6':
            # Update the runtime to Python 3.9
            updated_function = lambda_client.update_function_configuration(
                FunctionName=function_name,
                Runtime='python3.9'
            )
            print(f"Updated {function_name} from Python 3.6 to Python 3.9.")
        else:
            print(f"No update needed for {function_name}. Current runtime is {current_runtime}.")

    except lambda_client.exceptions.ResourceNotFoundException:
        print(f"Function named {function_name} does not exist.")
    except Exception as e:
        print(f"Failed to update {function_name}: {str(e)}")

# Specify the function name you want to update
function_name_to_test = "test"
update_lambda_to_python_39(function_name_to_test)
