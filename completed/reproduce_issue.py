import sys
import os
import logging

# Add project root to sys.path
sys.path.append(os.getcwd())

from openqabot.loader import repohash
from openqabot.loader import gitea

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Data derived from analysis of log for incident 1964
project = "SLFO"
arch = "x86_64"
# repo structure: (product, version, product_version)
# based on log: SUSE:SLFO:1.2:PullRequest:1964:SLES
repo_tuple = ("SUSE:SLFO", "1.2:PullRequest:1964:SLES", "16.0")

print(f"Checking revision for {repo_tuple}")

try:
    # We pass None for options, so product_name defaults to SLES (from repo[1])
    # and product_version is taken from repo[2] (16.0)
    rev = repohash.get_max_revision([repo_tuple], arch, project)
    print(f"Revision: {rev}")
except Exception as e:
    print(f"Error: {e}")
