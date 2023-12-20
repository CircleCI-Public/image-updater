# Image Updater
An update script for updating deprecated machine images quickly and automatically across entire orgs.

## Usage

1. Install the required Python packages with `pip install -r requirements.txt`
2. Run using `py ./image-updater.py`
3. Either edit the main.py file to insert your API Key and Organization name, or input them when prompted.

When the script has run, branches shuold have been created with the name `Deprecated CircleCI Image Update` (unless edited) and a Pull Request created as well. Also, during this, local copies of the config.yml files will be created. These can safely be deleted, but you may want to check them out for debugging purposes.

If the script fails due to a branch creation error, ensure the branch does not exist already. If you ran the script once, it already exists, and thus needs to be deleted.