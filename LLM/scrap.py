import logging
import os
import requests
import json
from github import Github, GithubException
from retry import retry
import re
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# Configuration
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
HUGGINGFACE_MODEL_NAME = "google/flan-t5-large"  # Or "mosaicml/mpt-7b"


include_extensions = [
    "py", "java", "html", "c", "js", "ipynb", "cpp", "sh", "md", "txt",
]


@retry(tries=3, delay=2, backoff=2, logger=logger)
def summarize_with_huggingface(text):
    """Summarizes text using the Hugging Face Inference API."""
    API_URL = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL_NAME}"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    # Use parameters for better summarization control with Flan-T5
    data = json.dumps({"inputs": text, "parameters": {"max_length": 512, "min_length": 30}}) # min_length for shorter summaries


    try:
        response = requests.post(API_URL, headers=headers, data=data)
        response.raise_for_status()
        output = json.loads(response.content.decode("utf-8"))

        if isinstance(output, list) and isinstance(output[0], dict) and "summary_text" in output[0]: # Correct output format
            return output[0]["summary_text"]
        elif isinstance(output, list) and isinstance(output[0], str):  # Handle string list outputs
            return output[0]
        elif isinstance(output, dict) and "generated_text" in output:  # Handle some models structure output
            return output['generated_text']
        else:
            logger.warning(f"Unexpected output format from Hugging Face API: {output}")
            return "Error during summarization."


    except requests.exceptions.RequestException as e:
        logger.error(f"Error in Hugging Face API call: {e}")
        return "Error during summarization."



def get_repo_language(repo):
    """Gets the primary language of the repository."""
    try:
        return repo.get_languages().most_common(1)[0][0]
    except IndexError:  # Handle cases where language info is unavailable
        return None


@retry(tries=3, delay=2, backoff=2, logger=logger)  # Retry decorator for API calls
def ask_llm_about_next_files(text, language=None):
    """Asks the LLM which files to analyze next."""
    prompt = f"""Based on this information:\n{text}\nWhich files would be most helpful to understand the codebase and its purpose?"""
    if language:
        prompt += f" The primary language used is {language}."

    response = summarize_with_huggingface(prompt)  # Use Hugging Face API directly

    if response.startswith("Error"):  # Handle potential errors from the API call
        return []

    files = extract_filenames_from_response(response)
    return files


def extract_filenames_from_response(llm_response):
    """Extract mentioned filenames from the LLM's response.

    Uses a regular expression to find potential filenames (e.g., setup.py, src/main.java, etc.)"""

    # You'll likely need to improve this regex for your use cases.
    filenames = re.findall(r"([a-zA-Z0-9_\-\.\/]+\.[a-zA-Z0-9]+)", llm_response)
    return filenames




def analyze_repo(readme_content, other_files_content):
    """Analyzes the combined content using the LLM."""
    combined_text = f"README:\n{readme_content}\n\nOther Files:\n{other_files_content}"
    prompt = "Analyze this codebase and describe its purpose, functionality, and technologies used."
    analysis = summarize_with_huggingface(f"{prompt}\n\n{combined_text}")  # Use Hugging Face API

    if analysis.startswith("Error"): # Add error handling.
        return "Error analyzing the repository." # Return an error message

    return analysis


def scrap_repo(github_owner, github_repo_name):

    g = Github(token=GITHUB_TOKEN)
    repo = g.get_repo(f"{github_owner}/{github_repo_name}")
    readMe = ""
    second = ""

    # Get README content and language
    try:
        readme_content = repo.get_contents("README.md")
        readMe = readme_content.decoded_content.decode()

    except GithubException as e: # Catch if the README file is not found
        if e.status == 404: # File Not Found
            logger.warning("README.md not found.  Getting repository language...")
            repo_language = get_repo_language(repo)
            if repo_language:
                readMe = f"No README found. Repository primarily uses {repo_language}."  # Placeholder
            else:
                readMe = "No README found, and language information unavailable."
        else: # Other github exceptions.
            logger.error(f"README.md file error: {e}")
            return "", "" # Return empty strings,


    except Exception as e:  # Other exceptions like decoding errors
        logger.error(f"Error processing README.md: {e}")
        return  "", ""


    # Get files to analyze (either via README analysis or language defaults)
    if readMe.strip():  # Check if readme has content.
        files_to_summarize = ask_llm_about_next_files(readMe)
    else:  # If README is empty or not available
        repo_language = get_repo_language(repo)  # Fallback: get repo language
        if repo_language == "Python":
            files_to_summarize = ["setup.py", "requirements.txt", "main.py"]  # Python defaults
        elif repo_language == "JavaScript":
            files_to_summarize = ["package.json", "index.js"]  # JavaScript defaults
        # ... add more language defaults ...
        else:
            files_to_summarize = []  # Or handle it differently



    # Scrape and summarize other files
    for filename in files_to_summarize:
        try:
            file_content = repo.get_contents(filename)
            file_text = file_content.decoded_content.decode()
            file_summary = summarize_with_huggingface(file_text)  # Call the correct function
            second += f"## {filename}\n{file_summary}\n"
        except GithubException as e:
             if e.status == 404:  # File not found
                logger.warning(f"File not found: {filename}")
             else: # Other Github error
                 logger.error(f"Github error fetching: {filename} : {e}") # Other github exception
        except Exception as e: # Other errors
            logger.error(f"Error processing file: {filename}: {e}")
    


    # Analyze the repo
    repo_analysis = analyze_repo(readMe, second)
    

    return readMe, second, repo_analysis  # Return the analysis as well



if __name__ == "__main__":
    repo_owner = "NILAY1556"
    repo_name = "Analyze-github-repo"
    readme, other_files, repo_analysis = scrap_repo(repo_owner, repo_name)

    print("README Content:\n", readme)
    print("\nOther Files Summary:\n", other_files)
    print("\nRepository Analysis:\n", repo_analysis)