import boto3
import json
import os

def is_valid_json(policy_document):
    """ Validate JSON format """
    try:
        json_object = json.loads(policy_document)  # Load JSON from string
        print("JSON validation successful.")
        return json_object
    except ValueError as e:
        print(f"Invalid JSON: {e}")
        return None

def load_policy_from_file(filename):
    """ Load policy JSON from a specified file """
    try:
        with open(filename, 'r') as file:
            policy_document = file.read()
            return policy_document
    except IOError as e:
        print(f"Error reading file: {e}")
        return None

# Initialize the IAM client
iam = boto3.client('iam')

# Input role and policy name
role_name = input("Enter the role name: ")
policy_name = input("Enter the policy name for the role: ")

# Retrieve the policy ARN (assuming there is only one match)
response = iam.list_policies(Scope='Local', PolicyUsageFilter='PermissionsPolicy')
policy_arn = next((p['Arn'] for p in response['Policies'] if p['PolicyName'] == policy_name), None)

if not policy_arn:
    raise ValueError(f"No policy found with the name {policy_name}")

# Ask user for the JSON file name
filename = input("Enter the JSON policy file name: ")

# Load the policy document from the specified file
policy_document = load_policy_from_file(filename)
if policy_document is None:
    exit()

# Validate JSON format
policy_json = is_valid_json(policy_document)
if policy_json is None:
    exit()

# Ask for confirmation
confirmation = input(f"Do you wish to update role {role_name} with new policy? (yes/no): ")

if confirmation.lower() == 'yes':
    # Update the policy by creating a new version
    iam.create_policy_version(
        PolicyArn=policy_arn,
        PolicyDocument=json.dumps(policy_json),
        SetAsDefault=True
    )
    print(f"Policy {policy_name} updated successfully.")
else:
    print("Update cancelled.")
