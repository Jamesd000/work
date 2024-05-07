#!/bin/bash

# Define the time period in milliseconds since the epoch
start_time=$(date -d "2024-05-04 07:00:00" +%s%3N)
end_time=$(date -d "2024-05-04 12:00:00" +%s%3N)

# AWS CLI command to list all Lambda log groups and store them in an array
log_groups=($(aws logs describe-log-groups --log-group-name-prefix '/aws/lambda/' --query 'logGroups[*].logGroupName' --output text))

# Batch size (Manage how many you want per batch, considering CLI limits and practicality)
batch_size=20

# Total number of log groups
total_log_groups=${#log_groups[@]}

# How many full batches
full_batches=$(($total_log_groups / $batch_size))

# Remaining log groups for the last batch
remainder=$(($total_log_groups % $batch_size))

# Function to query a batch of log groups and check for errors
query_log_groups() {
  local start=$1
  local end=$2
  echo "Querying from $start to $end log groups..."
  group_names=""
  for (( i=start; i<end; i++ )); do
    group_names+="${log_groups[$i]} "
  done

  # Start a query and store the query ID
  query_id=$(aws logs start-query \
    --log-group-names $group_names \
    --start-time "$start_time" \
    --end-time "$end_time" \
    --query-string "fields @timestamp, @logStream, @message | filter @message like /ERROR/" \
    --output text --query 'queryId')

  # Wait for the query to complete and get the results
  status="Running"
  while [ "$status" = "Running" ]; do
    result=$(aws logs get-query-results --query-id $query_id --output text)
    status=$(echo $result | awk '{print $1}')
    sleep 1
  done

  # Check if there are any results (errors)
  if [[ "$result" != *"No logs matched"* ]]; then
    echo "Errors found in the following log groups between $start_time and $end_time:"
    echo $group_names
  fi
}

# Query each batch
for (( i=0; i<$full_batches; i++ )); do
  start=$(($i * $batch_size))
  end=$(($start + $batch_size))
  query_log_groups $start $end
done

# Query remaining log groups if any
if [ $remainder -ne 0 ]; then
  start=$(($full_batches * $batch_size))
  end=$(($start + $remainder))
  query_log_groups $start $end
fi
