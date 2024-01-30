# Valohai Metrics Aggregator

## Project Overview

This project is designed to gather metrics from the executions of a specific Valohai task, calculate their averages, and save the results to Valohai. The process runs in an infinite loop, updating the metrics at regular intervals.

**Note: The execution is running in an infinite loop. DO NOT FORGET TO STOP IT!**

## Configuration

### Parameters

1. **task-id:**
   - To get your task-id go to your task page in `app.valohai`, and copy the task-id from the URL: `https://app.valohai.com/p/<your-org>/<your-project>/task/<TASK-ID>/#details`.
2. **sleep_for_seconds:**
   - Set the interval for updating results in seconds (e.g., every 600 seconds).

### Environment Variables

Ensure that you have set the following environment variable in Valohai:

- **VALOHAI_API_TOKEN:** _(you can choose another name - don’t forget to change it in the code)_
  - Go to your profile -> Authentication -> Manage Tokens -> Generate New Token -> Save it.
  - Add the generated token as an environment variable in Valohai. You can add environment variables in a couple of ways in Valohai. 
    - Add the environment variable when creating an execution from the UI (Create Execution -> Environment Variables). The env variable are only available in the execution where it was created. 
    - Add the project environment variable (Project Settings -> "Environment Variables" tab -> Check "Secret" checkbox). In this case, the env variable will be available for all executions of the project.

## Project Workflow

1. **API Calls:**
   - The project makes two API calls:
      - [Get Executions' IDs](https://app.valohai.com/api/v0/tasks/{task_id}/execution_ids/): Obtain execution IDs of the specified task.
      - [Download Metadata CSV](https://app.valohai.com/api/v0/executions/multi_download_metadata_csv/): Get metadata in CSV format from all task executions.

2. **Execution Flow:**
   - The script follows these main steps:
      - Import necessary libraries and modules.
      - Define functions for API calls, data processing, and result calculation.
      - Run the main process in an infinite loop.
      - Gather execution data, process it, calculate averages, and save results to CSV.
      - Dump the metrics to metadata for visualisation and Upload the CSV to Valohai.

3. **Result Files:**
   - A CSV file named `average_metrics_{iterator}.csv` is saved to `/valohai/outputs/` with each iteration, and it is also live-uploaded to Valohai.

## Usage Instructions

1. Add this script to your project and add the step to your `valohai.yaml`.
2. Set the `VALOHAI_API_TOKEN` environment variable in Valohai.
3. Create a task or a pipeline with a task node.
4. Get the task-id
5. Start a separate execution using step `gather`
6. Monitor the console output for updates, the graphs of the avg metrics in the metadata tab and view the live-uploaded CSV files in the Valohai interface.

**Monitoring Note:** 
- Keep in mind that each metadata upload is assigned a unique identifier (`_1`, `_2`, `_3`, and so on). When reviewing the graphs in the metadata tab, ensure you select the relevant features such as `epoch_2` and `accuracy_2`. 
- `epoch_2` does not signify the second epoch; rather, it represents the epochs from the second upload of the metrics.

**Important: Stop the execution when no longer needed to avoid unnecessary API calls and resource usage.**

## Additional Notes

- The script excludes non-metric features specified in the `columns_to_exclude` list.
- Ensure proper handling of environment variables and sensitive information.
- Adjust the sleep interval based on your project requirements.

Happy Valohai-ing!