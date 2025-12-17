import os
import shutil
from git import Repo
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RepoCloner:
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.repo_name = repo_url.split("/")[-1].replace(".git", "")
        self.repo_path = os.path.join(settings.REPO_STORAGE_PATH, self.repo_name)

    def clone_repo(self) -> str:
        """
        Clones the repository to the local storage.
        If it already exists, it pulls the latest changes.
        Returns the path to the cloned repository.
        """
        if os.path.exists(self.repo_path):
            logger.info(f"Repository {self.repo_name} already exists. Pulling latest changes...")
            try:
                repo = Repo(self.repo_path)
                repo.remotes.origin.pull()
            except Exception as e:
                logger.error(f"Error pulling repo: {e}")
                # Optional: delete and re-clone if pull fails
                shutil.rmtree(self.repo_path)
                Repo.clone_from(self.repo_url, self.repo_path)
        else:
            logger.info(f"Cloning repository {self.repo_name}...")
            Repo.clone_from(self.repo_url, self.repo_path)
        
        return self.repo_path
