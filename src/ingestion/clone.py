import os
import shutil
from git import Repo
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class RepoCloner:
    def __init__(self, repo_url: str, temp_dir: str = None):
        self.repo_url = repo_url
        self.repo_name = repo_url.split("/")[-1].replace(".git", "")
        # Use temp_dir if provided, else default to settings.REPO_STORAGE_PATH
        if temp_dir:
            self.repo_path = os.path.join(temp_dir, self.repo_name)
        else:
            self.repo_path = os.path.join(settings.REPO_STORAGE_PATH, self.repo_name)

    def clone_repo(self, cleanup_existing: bool = False) -> str:
        """
        Clones the repository to the local storage (temp folder).
        If it already exists, it pulls the latest changes or optionally cleans up and reclones.
        Returns the path to the cloned repository.
        """
        if os.path.exists(self.repo_path):
            logger.info(f"Repository {self.repo_name} already exists at {self.repo_path}.")
            if cleanup_existing:
                logger.info("Cleanup enabled. Removing existing repo...")
                shutil.rmtree(self.repo_path)
                Repo.clone_from(self.repo_url, self.repo_path)
            else:
                try:
                    repo = Repo(self.repo_path)
                    repo.remotes.origin.pull()
                except Exception as e:
                    logger.error(f"Error pulling repo: {e}")
                    shutil.rmtree(self.repo_path)
                    Repo.clone_from(self.repo_url, self.repo_path)
        else:
            logger.info(f"Cloning repository {self.repo_name} to {self.repo_path}...")
            Repo.clone_from(self.repo_url, self.repo_path)
        return self.repo_path
