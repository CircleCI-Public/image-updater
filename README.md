# Image Updater

NOTE: This is currently in ALPHA, and we are looking into improving experience for customers.

A script to determine which deprecated machine images need to be changed within repositories across an entire organization.

Limitations:
* Only supports GitHub lookups
* Will not find orb specific changes without being pointed at that specific orb config

## Usage

1. Run Golang locally or within container to execute this script.
2. [Create a Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token) with permissions to read from your repositories.
3. Run: `export GITHUB_TOKEN={INSERT_YOUR_GITHUB_TOKEN}`
4. Run: `go build -o image-updater cmd/main.go && ./image-updater -org={INSERT_YOUR_ORG_NAME}`

## 2024 Deprecation Notices - TODO: Update with latest docs when exist

* [Linux](https://discuss.circleci.com/t/linux-image-deprecations-and-eol-for-2024/50177)
* [Android](https://discuss.circleci.com/t/android-image-deprecations-and-eol-for-2024/50180)
* [Remote Docker](https://discuss.circleci.com/t/remote-docker-image-deprecations-and-eol-for-2024/50176)
* [Windows](https://discuss.circleci.com/t/windows-image-deprecations-and-eol-for-2024/50179)
