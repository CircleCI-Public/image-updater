import requests
import json
import sys
import base64
from ruamel.yaml import YAML
from pathlib import Path

# Configuration
api_org = ""  # The organization you'll be scanning.
api_key = ""  # Personal Access Token
new_branch_name = ""  # Make sure this is unique.

# If any of the configuration elements up top are not filled in,
# ask for them here.

while api_org == "":
    api_org = input("Organization you wish to scan for repos:")

while api_key == "":
    api_key = input("Personal Access Token:")

while new_branch_name == "":
    new_branch_name = input("New branch name. Ensure it is unique:")

# Relevant but unlikely to change definitions here.
api_url = "https://api.github.com/"
headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}

yaml = YAML()

default_android_tag = ""
default_win19_tag = ""
default_win22_tag = ""
default_focal_tag = ""
default_jammy_tag = ""
default_docker_tag = ""

set_defaults = input("would you like to set default tags for each image family? (y/n) ")

if set_defaults == "y":
    default_android_tag = input("What tag would you like to default android tags to? (press enter to skip)\n")
    default_win19_tag = input("What tag would you like to default windows 2019 tags to? (press enter to skip)\n")
    default_win22_tag = input("What tag would you like to default windows 2022 tags to? (press enter to skip)\n")
    default_focal_tag = input("What tag would you like to default ubuntu 20.04 tags to? (press enter to skip)\n")
    default_jammy_tag = input("What tag would you like to default ubuntu 22.04 tags to? (press enter to skip)\n")
    default_docker_tag = input("What tag would you like to default remote docker tags to? (press enter to skip)\n")

deprecated_images = [
    # android images #
    "android:202102-01", "android:2021.12.1", "android:2022.01.1", "android:2022.03.1", "android:2022.04.1", "android:2022.06.1", "android:2022.06.2",
    "android:2022.07.1", "android:2022.08.1", "android:2022.09.1", "android:2023.03.1", "android:2023.04.1", "android:2023.06.1", "android:2023.07.1", "android:2023.09.1",
    "android:2023.11.1",

    # windows 2019 images #
    "windows-server-2019:201908-06", "windows-server-2019:201908-08", "windows-server-2019-vs2019:201908-02", "windows-server-2019-vs2019:201908-06",
    "windows-server-2019-vs2019:201909-25", "windows-server-2019-vs2019:201911-06",

    # windows gpu images #
    "windows-server-2019-nvidia:201908-28", "windows-server-2019-nvidia:201909-25", "windows-server-2019-nvidia:201911-06",

    # windows 2022 images #
    "windows-server-2022-gui:2022.04.1", "windows-server-2022-gui:2022.07.1", "windows-server-2022-gui:2022.08.1", "windows-server-2022-gui:2022.09.1",
    "windows-server-2022-gui:2023.03.1", "windows-server-2022-gui:2023.04.1", "windows-server-2022-gui:2023.06.1", "windows-server-2022-gui:2023.07.1",
    "windows-server-2022-gui:2023.09.1", "windows-server-2022-gui:2023.11.1",

    # 20.04 images #
    "ubuntu-2004:202008-01", "ubuntu-2004:202011-01", "ubuntu-2004:202101-01", "ubuntu-2004:202104-01", "ubuntu-2004:202107-01", "ubuntu-2004:202107-02", "ubuntu-2004:202111-01",
    "ubuntu-2004:202201-01", "ubuntu-2004:202201-02", "ubuntu-2004:2022.04.1", "ubuntu-2004:2023.04.1", "ubuntu-2004:2022.04.2", "ubuntu-2004:2022.07.1",

    # 22.04 #
    "ubuntu-2204:2022.04.1", "ubuntu-2204:2022.04.2", "ubuntu-2204:2022.07.1", "ubuntu-2204:2022.07.2", "ubuntu-2204:2023.04.1",
    "ubuntu-2204:2023.07.2", "ubuntu-2204:2022.10.1",

    # remote docker images #
    "docker-17.05.0-ce", "docker-17.06.0-ce", "docker-17.06.1-ce", "docker-17.07.0-ce", "docker-17.09.0-ce", "docker-17.10.0-ce", "docker-17.11.0-ce",
    "docker-17.12.0-ce", "docker-17.12.1-ce", "docker-18.01.0-ce", "docker-18.02.0-ce", "docker-18.03.0-ce", "docker-18.03.1-ce", "docker-18.04.0-ce",
    "docker-18.05.0-ce", "docker-18.06.0-ce", "docker-18.09.3", "docker-19.03.8", "docker-17.03.0-ce", "docker-19.03.12", "docker-19.03.13",
    "docker-19.03.14", "docker-20.10.2", "docker-20.10.6", "docker-20.10.7", "docker-20.10.11", "docker-20.10.12", "docker-20.10.14", "docker-20.10.17",
    "docker-20.10.18", "docker-20.10.23"
]

remote_docker_versions = [
    # remote docker images #
    "17.05.0-ce", "17.06.0-ce", "17.06.1-ce", "17.07.0-ce", "17.09.0-ce", "17.10.0-ce", "17.11.0-ce",
    "17.12.0-ce", "17.12.1-ce", "18.01.0-ce", "18.02.0-ce", "18.03.0-ce", "18.03.1-ce", "18.04.0-ce",
    "18.05.0-ce", "18.06.0-ce", "18.09.3", "19.03.8", "17.03.0-ce"

    "19.03.12", "19.03.13", "19.03.14", "20.10.2", "20.10.6", "20.10.7", "20.10.11", "20.10.12",
    "20.10.14", "20.10.17", "20.10.18", "20.10.23"
]


# Get all repos.
def fetch_repos():
    call_url = api_url + f"orgs/{api_org}/repos?per_page=100"
    res = requests.get(call_url, headers=headers)
    if res.status_code != 200:
        print("Organization " + api_org + " is not valid, or you don't have access to it. Confirm your API Key is correct as well.")
        sys.exit(1)

    repos = res.json()
    while 'next' in res.links.keys():
        res = requests.get(res.links['next']['url'], headers=headers)
        if res.status_code != 200:
            print("Organization " + api_org + " is not valid, or you don't have access to it. Confirm your API Key is correct as well.")
            sys.exit(1)
        repos.extend(res.json())
    return repos


# For each repo, investigate for a .circleci/config.yml file being present in the main branch.
def repo_scan(repo):
    call_url = api_url + "repos/" + api_org + "/" + repo["name"] + "/contents/.circleci/config.yml"

    result = requests.get(call_url, headers=headers)

    if result.status_code == 200:
        data = json.loads(result.content)
        yaml_file = requests.get(data["download_url"], headers=headers)

        if str(yaml_file.content).find("machine:") == -1 and str(yaml_file.content).find("setup_remote_docker") == -1:
            print("No entry for \"machine:\" or \"setup_remote_docker\" found")
            return False
        else:
            return_data = dict()
            return_data['content'] = str(yaml_file.content)
            return_data['sha'] = data["sha"]
            return return_data
    else:
        print("No .circleci/config.yml file found.")
        return False


# Determine if there are any machine entries at all.
def machine_check(config: str):
    if config.find("machine:") > -1:
        return True
    return False


# An initial call to get all repos.
repos = fetch_repos()

# Run through each of them.
for r in repos:
    print("\n\n====== Working on Repo: " + r["name"] + " ======")
    result = repo_scan(r)
    if result is False:  # Any error, we leave.
        continue

    result_text = result['content']

    # Split into different variables per newline, and remove leading dashes if they are present.
    result_text = result_text.replace(r"---", "")
    result_text = result_text.replace(r'\n', '\n')
    result_text = result_text[2:-1]

    yaml.preserve_quotes = False
    result_yaml = yaml.load(result_text)
    change_made = False  # If no changes are made, we can quit after this is done.

    print("\n=== Updating image tags ===")

    for attr, value in result_yaml['jobs'].items():
        remote_docker = ""
        for values in value["steps"]:
            if "setup_remote_docker" in values:
                if values == "setup_remote_docker":
                    continue
                if "version" in values["setup_remote_docker"]:
                    remote_docker = values["setup_remote_docker"]['version']

        if "machine" or "executor" in value or remote_docker != "":
            # The image name can be present under machines, or on the same depth as it, so we need to account for both.
            # We first check for the same depth, then, we check under image.
            depth = 0
            old_image = ""
            if "machine" in value:
                if "image" in value:
                    old_image = value["image"]
                elif value["machine"] is True:  # 'machine: true'
                    continue
                elif "image" in value["machine"]:
                    depth = 1
                    old_image = value["machine"]["image"]
                    if '\\' in old_image:
                        old_image.replace('\\', '')
                else:
                    print("Unexpected lack of image tag.")
                    continue
            if remote_docker != "":
                old_image = remote_docker
                image_family = ""
            image = ""
            for i in deprecated_images:
                if i == old_image:
                    if "docker" not in old_image:
                        image_family = old_image.split(":")[0] + ":"
                    else:
                        image_family = "docker"
                    if default_android_tag != "" and image_family == "android:":
                        image = image_family + default_android_tag
                    elif default_win19_tag != "" and image_family == "windows-server-2019-vs2019:":
                        image = image_family + default_win19_tag
                    elif default_win22_tag != "" and image_family == "windows-server-2022-gui:":
                        image = image_family + default_win22_tag
                    elif default_focal_tag != "" and image_family == "ubuntu-2004:":
                        image = image_family + default_focal_tag
                    elif default_jammy_tag != "" and image_family == "ubuntu-2204:":
                        image = image_family + default_jammy_tag
                    elif default_docker_tag != "" and image_family == "docker":
                        image = "docker-" + default_docker_tag
                    else:
                        print("\nDeprecated image: " + old_image + " found")
                        if image_family == "android":
                            image_tag = input("Specify new tag (if you would like default press enter):")
                        else:
                            image_tag = input("Specify new tag (if you would like current press enter):")
                        if image_tag == "":
                            if image_family == "android":
                                image = "android:default"
                            else:
                                image = image_family + "current"
                        else:
                            image = image_family + image_tag
            for i in remote_docker_versions:
                if i in old_image:
                    print("Deprecated remote docker image version '" + old_image + "' found used in a 'setup_remote_docker' step")
                    image_tag = input("Specify new tag (if you would like current press enter):")
                    if image_tag == "":
                        image = "current"
                    else:
                        image = image_tag

            # If the resource variable matches the Resource we started with, no change was made - otherwise, one was made.
            if (image != old_image and image != ""):
                change_made = True
                if remote_docker != "":
                    for values in value["steps"]:
                        if "setup_remote_docker" in values:
                            values["setup_remote_docker"]["version"] = image
                else:
                    if depth == 0:
                        value["image"] = image
                    elif depth == 1:
                        value["machine"]["image"] = image

                    print("Updating from " + old_image + " to " + image)
        else:
            continue

    if change_made is False:
        print("No changes triggered, moving to next repo.")
        continue

    print("\n=== Writing file locally ===")
    # We save the file locally so that a copy is available to view, and so that it's easier to json-ify later.
    with open(r['name'] + ".yml", "w") as file:
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.default_style = None
        yaml.dump(result_yaml, file)
        print("Output for updated config saved in file: " + r['name'] + ".yml")

    # Prepare URLs for API Calls. Very repetitive, but hey.
    base_repo_url = api_url + "repos/" + api_org + "/" + r["name"]
    ref_head_url = base_repo_url + "/git/refs/heads"
    create_branch_url = base_repo_url + "/git/refs"
    update_url = base_repo_url + "/contents/.circleci/config.yml"
    create_pr_url = base_repo_url + "/pulls"

    # Attempt to create a branch. If it already exists, we will assume the script has already been run and move on.
    print("\n=== Creating Branch ===")
    branches = requests.get(ref_head_url, headers=headers).json()
    branch, sha = branches[-1]['ref'], branches[-1]['object']['sha']

    branch_create_res = requests.post(create_branch_url, headers=headers, data=json.dumps({
        "ref": "refs/heads/" + new_branch_name,
        "sha": sha
    }))
    if branch_create_res.status_code != 201 and branch_create_res.status_code != 200:
        print("Error when attempting to create branch: ", branch_create_res.status_code)
        print("Branch " + new_branch_name + " probably already exists, did you run the script before? If so, please delete the old branch.")
        continue

    print("Branch created.")
    print("\n=== Updating Config ===")

    # Open the file created above and encode it.
    file_content = Path(r['name'] + ".yml").read_text()
    file_content = file_content.replace('\n', "\n")
    file_content = str.encode(file_content)
    put_data = {
        "message": "Automatic image update for deprecated images.",
        "content": base64.b64encode(file_content).decode("utf-8"),
        "sha": result['sha'],
        "branch": new_branch_name
    }

    put_result = requests.put(update_url, headers=headers, data=json.dumps(put_data))

    if put_result.status_code != 201 and put_result.status_code != 200:
        print("Error when attempting to update config.yml:", put_result.status_code)
        continue

    print("Config updated.")

    # Successful commit to the branch, now we move on to a PR.
    print("\n=== Creating Pull Request ===")

    pr_data = {
        "title": "Update deprecated image tags",
        "head": new_branch_name,
        "base": r["default_branch"],
        "body": "This PR is opened by a script, designed to help bulk update deprecated image tags."
    }

    pr_result = requests.post(create_pr_url, headers=headers, data=json.dumps(pr_data))

    if pr_result.status_code != 201:
        print("Error creating pull request: ", pr_result.status_code)
        continue
    print("\n\n========================================")
    print("=========*      Success!      *=========")
    print("========================================")
    print("Pull request opened, URL: " + pr_result.json()["html_url"])
