# Import necessary modules
import base64
import csv
import json
import logging
import sys
from pathlib import Path

import requests
from ruamel.yaml import YAML

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Configuration
api_org = input("Github Organization you wish to scan for repos:")
api_key = input("Github Personal Access Token:")
new_branch_name = "hotfix/enable-circleci-known-ip-ranges"


# API setup
api_url = "https://api.github.com/"
headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}

# Define a mapping from machine images to Docker images
machine_to_docker_image_map = {
    "ubuntu-2004:current": "ubuntu:20.04",
    # Add more mappings as needed
}

yaml = YAML()


# Function to scan repositories for .circleci/config.yaml or .circleci/config.yml
def repo_scan(repo):
    """
    Scans a given repository for the .circleci/config.yaml or .circleci/config.yml file.

    Args:
        repo (dict): A dictionary containing repository information.

    Returns:
        dict or bool: Returns a dictionary with file content and SHA if found, otherwise False.
    """
    file_names = ["config.yaml", "config.yml"]
    for file_name in file_names:
        call_url = api_url + "repos/" + api_org + "/" + repo["name"] + "/contents/.circleci/" + file_name
        result = requests.get(call_url, headers=headers)

        if result.status_code == 200:
            data = json.loads(result.content)
            yaml_file = requests.get(data["download_url"], headers=headers)
            return_data = dict()
            return_data["content"] = str(yaml_file.content)
            return_data["sha"] = data["sha"]
            return_data["extension"] = file_name.split(".")[-1]  # Store the file extension
            return return_data

    logging.info("No .circleci/config.yaml or .circleci/config.yml file found.")
    return False


def fetch_repos():
    """
    Fetches repositories for the specified organization.

    Returns:
        list: A list of repositories.
    """
    call_url = api_url + f"orgs/{api_org}/repos?per_page=100"
    res = requests.get(call_url, headers=headers)
    if res.status_code != 200:
        logging.error(
            "Organization %s is not valid, or you don't have access to it. Confirm your API Key is correct as well.",
            api_org,
        )
        sys.exit(1)

    repos = res.json()
    while "next" in res.links.keys():
        res = requests.get(res.links["next"]["url"], headers=headers)
        if res.status_code != 200:
            break
    return repos


# Fetch repositories
repos = fetch_repos()
pr_info_list = []
logging.info("Found %s repos", len(repos))
# Process each repository
for r in repos:
    logging.info("====== Working on Repo: " + r["name"] + " ======")
    result = repo_scan(r)
    if result is False:
        continue

    result_text = result["content"]
    result_text = result_text.replace(r"---", "")
    result_text = result_text.replace(r"\n", "\n")
    result_text = result_text[2:-1]

    yaml.preserve_quotes = False
    result_yaml = yaml.load(result_text)
    change_made = False

    logging.info(" Enabling CircleCI IP Ranges ")

    # Add circleci_ip_ranges: true to each job and switch machine jobs to docker
    for job_name, job_details in result_yaml["jobs"].items():
        if "machine" in job_details:
            # Extract the image name from the machine job
            machine_image = job_details["machine"]["image"]
            # Get the corresponding Docker image from the mapping
            docker_image = machine_to_docker_image_map.get(machine_image, machine_image)
            # Replace machine with a docker image using the mapped image name
            job_details.pop("machine")
            job_details["docker"] = [{"image": docker_image}]
        job_details["circleci_ip_ranges"] = True
        change_made = True

    if not change_made:
        logging.info("No changes made, moving to next repo.")
        continue

    logging.info(" Writing file locally ")
    file_extension = result["extension"]
    local_file_name = f"{r['name']}.{file_extension}"
    with open(local_file_name, "w") as file:
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.default_style = None
        yaml.dump(result_yaml, file)
        logging.info("Output for updated config saved in file: " + local_file_name)

    # Prepare URLs for API Calls
    base_repo_url = api_url + "repos/" + api_org + "/" + r["name"]
    ref_head_url = base_repo_url + "/git/refs/heads"
    create_branch_url = base_repo_url + "/git/refs"
    update_url = base_repo_url + f"/contents/.circleci/config.{file_extension}"
    create_pr_url = base_repo_url + "/pulls"

    # Check if the branch exists
    logging.info(" Checking if Branch Exists ")
    branches = requests.get(ref_head_url, headers=headers).json()
    branch_exists = any(branch["ref"] == f"refs/heads/{new_branch_name}" for branch in branches)

    if branch_exists:
        logging.info(" Branch exists, deleting it ")
        delete_branch_url = base_repo_url + f"/git/refs/heads/{new_branch_name}"
        delete_branch_res = requests.delete(delete_branch_url, headers=headers)
        if delete_branch_res.status_code != 204:
            logging.error("Error when attempting to delete branch: %s", delete_branch_res.status_code)
            continue
        logging.info("Branch deleted.")

    # Create a new branch
    logging.info(" Creating Branch ")
    branch, sha = branches[-1]["ref"], branches[-1]["object"]["sha"]
    branch_create_res = requests.post(
        create_branch_url,
        headers=headers,
        data=json.dumps({"ref": "refs/heads/" + new_branch_name, "sha": sha}),
    )
    if branch_create_res.status_code != 201 and branch_create_res.status_code != 200:
        logging.error("Error when attempting to create branch: ", branch_create_res.status_code)
        continue
    logging.info("Branch created.")

    # Fetch the latest SHA for the file to ensure no conflicts
    latest_file_info = requests.get(update_url, headers=headers).json()

    # Check if the request was successful
    if "sha" not in latest_file_info:
        logging.error("Failed to fetch the latest file information.")
        continue

    latest_sha = latest_file_info["sha"]
    logging.info("Latest SHA: %s", latest_sha)

    # Update the config file with the latest SHA
    logging.info(" Updating Config ")
    file_content = Path(local_file_name).read_text()
    file_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")  # Ensure correct encoding

    put_data = {
        "message": "Enable CircleCI IP Ranges feature.",
        "content": file_content,
        "sha": latest_sha,  # Use the latest SHA
        "branch": new_branch_name,
    }

    put_result = requests.put(update_url, headers=headers, data=json.dumps(put_data))

    if put_result.status_code != 201 and put_result.status_code != 200:
        logging.error("Error when attempting to update config file: %s", put_result.status_code)
        logging.error("Response: %s", put_result.json())
        continue

    logging.info("Config updated.")

    # Create a pull request
    logging.info(" Creating Pull Request ")
    pr_data = {
        "title": "Enable CircleCI IP Ranges",
        "head": new_branch_name,
        "base": r["default_branch"],
        "body": "This PR enables the CircleCI IP Ranges feature in the pipeline configuration.",
    }

    pr_result = requests.post(create_pr_url, headers=headers, data=json.dumps(pr_data))

    if pr_result.status_code != 201:
        logging.error(f"Error creating pull request: {pr_result.status_code}")
        continue

    # Collect information about the pull request
    pr_info = {"repo_name": r["name"], "pr_url": pr_result.json()["html_url"], "pr_number": pr_result.json()["number"]}
    pr_info_list.append(pr_info)

    logging.info("=========*      Success!      *=========")
    logging.info("Pull request opened, URL: " + pr_info["pr_url"])

# After the loop, write the collected information to a CSV file
with open("pr_summary.csv", "w", newline="") as csvfile:
    fieldnames = ["repo", "pull_request_url", "pull_request_number"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for info in pr_info_list:
        writer.writerow(
            {"repo": info["repo_name"], "pull_request_url": info["pr_url"], "pull_request_number": info["pr_number"]}
        )
