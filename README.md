# Image Updater
An update script for updating deprecated machine images quickly and automatically across entire orgs.

## Usage

1. Install the required Python packages with `pip install -r requirements.txt`
2. Run using `py ./image-updater.py`
3. [Create a Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token) with permissions to read and write to your repositories as well as open pull requests.
4. Either edit the main.py file to insert your Personal Access Token and Organization name, or input them when prompted.

When the script has run, branches should have been created with the name `Deprecated CircleCI Image Update` (unless edited) and a Pull Request created as well. Also, during this, local copies of the config.yml files will be created. These can safely be deleted, but you may want to check them out for debugging purposes.

If the script fails due to a branch creation error, ensure the branch does not exist already. If you ran the script once, it already exists, and thus needs to be deleted.

## 2024 Deprecation Notices

* [Linux](https://discuss.circleci.com/t/linux-image-deprecations-and-eol-for-2024/50177)
* [Android](https://discuss.circleci.com/t/android-image-deprecations-and-eol-for-2024/50180)
* [Remote Docker](https://discuss.circleci.com/t/remote-docker-image-deprecations-and-eol-for-2024/50176)
* [Windows](https://discuss.circleci.com/t/windows-image-deprecations-and-eol-for-2024/50179)
