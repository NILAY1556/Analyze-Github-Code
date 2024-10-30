import logging
from LLM.scrap import process_github_repo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AnalyzeRepo")


class AnalyzeRepo:
    """
    Main Class to perform all analyzing and summary operations
    """

    def __init__(self, token, url):
        self.llm_token = token


        self.repo_url = url
        # parsed_url = url.split("/")  # Split URL based on /
        # self.github_owner = parsed_url[-2]  # Get the owner
        # self.github_repo_name = parsed_url[-1]  # Get the repo name
        # logger.info("Necessary variables set")

    def run(self):
        result = process_github_repo(self.repo_url , self.llm_token)
        logger.info("Final summary ready!")

        return result
