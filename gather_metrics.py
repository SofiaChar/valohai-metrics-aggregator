import time
from collections import defaultdict
import requests
import json
import valohai
import csv
import os

# Retrieve Valohai API token from environment variable
auth_token = os.environ.get("VALOHAI_API_TOKEN")
HEADERS = {'Authorization': 'Token %s' % auth_token}

# Function to get execution IDs for a given task
def get_execution_ids(task_id):
    url = f'https://app.valohai.com/api/v0/tasks/{task_id}/execution_ids/'
    resp = requests.get(url, headers=HEADERS, json={})

    string_data = resp.content.decode('utf-8')
    return json.loads(string_data)

# Function to download metadata CSV for a list of execution IDs
def download_metadata_csv(executions_list):
    url = 'https://app.valohai.com/api/v0/executions/multi_download_metadata_csv/'
    the_json = {"ids": executions_list}

    resp = requests.get(url, headers=HEADERS, json=the_json)
    data_lines = resp.content.decode('utf-8').replace('\r', '')

    return data_lines

# Function to process data and exclude specified columns
def process_data(data_lines, columns_to_exclude):
    lines = data_lines.strip().split('\n')
    header = lines[0].split(',')
    lines = lines[1:]

    result = []
    for line in lines:
        values = line.split(',')
        data_dict = {}

        for i, value in enumerate(values):
            key = header[i]
            if key == "epoch":
                value = int(value)
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass
            data_dict[key] = value

        result.append(data_dict)

    for i in result:
        for col in columns_to_exclude:
            i.pop(col)

    return result

# Function to group data by epoch and calculate averages
def group_and_calculate_averages(result, i):
    grouped_data = defaultdict(list)
    for entry in result:
        epoch = entry["epoch"]
        grouped_data[epoch].append(entry)

    averages = [
        {f"{key}_{i}": sum(d[key] for d in data_points) / len(data_points) for key in data_points[0]}
        for data_points in grouped_data.values()
    ]

    return averages

# Function to write averages to CSV
def write_to_csv(csv_path, data, i):
    with open(csv_path, 'w', newline='') as csv_file:
        field_names = list(data[0].keys())
        field_names.insert(0, field_names.pop(field_names.index(f'epoch_{i}')))
        csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
        csv_writer.writeheader()
        csv_writer.writerows(data)

# Main process for continuous execution
def main_process(exec_list, to_exclude, iterator):
    print('\n-------Start/restart the main process')

    data_lines = download_metadata_csv(exec_list)
    result = process_data(data_lines, to_exclude)
    averages = group_and_calculate_averages(result, iterator)
    for avg in averages:
        print(json.dumps(avg))

    csv_path = f'/valohai/outputs/average_metrics_{iterator}.csv'
    write_to_csv(csv_path, averages, iterator)
    valohai.outputs().live_upload(f"average_metrics_{iterator}.csv")

    print('\n-------Saved current metrics to csv\n')

# Script execution
if __name__ == "__main__":
    # Get task_id and sleep interval from Valohai parameters
    task_id = valohai.parameters("task_id").value
    sleep_for = valohai.parameters("sleep_for_seconds").value

    # Exclude features that are not metrics
    columns_to_exclude = ['execution_id', '_time', 'execution_title', 'execution_counter']

    # Get execution IDs for the specified task
    executions_list = get_execution_ids(task_id)

    # Continuous execution loop
    iterator_num = 1
    while True:
        main_process(executions_list, columns_to_exclude, iterator_num)
        iterator_num += 1
        print(f'\n-------Waiting {sleep_for} seconds\n')
        time.sleep(sleep_for)
