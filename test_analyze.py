from analyze import AnalyzeRepo

def get_res():
    openai_key = ""
    currentPageLink = "https://github.com/tegridydev/auto-md"

    
        # Call AnalyzeRepo and get detailed summary
    summary_generator = AnalyzeRepo(openai_key, currentPageLink)
    result = summary_generator.run()

    return result


if __name__ == "__main__":
    print(get_res())













# import os
# import requests
# import nbformat
# from nbconvert import PythonExporter


# def download_file(url, target_path):
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()
#     with open(target_path, "wb") as f:
#         f.write(response.content)

# def is_allowed_filetype(filename):
#     allowed_extensions = ['.py', '.txt', '.js', '.tsx', '.ts', '.md', '.cjs', '.html', '.json', '.ipynb', '.h', '.localhost', '.sh', '.yaml', '.example']
# #    allowed_extensions = ['.md']
#     return any(filename.endswith(ext) for ext in allowed_extensions)

# def escape_xml(text):
#     return (
#         str(text)
#         .replace("&", "&amp;")
#         .replace("<", "&lt;")
#         .replace(">", "&gt;")
#         # Remove the following lines to stop converting apostrophes and quotes
#         # .replace("\"", "&quot;")
#         # .replace("'", "&apos;")
#     )

# def process_ipynb_file(temp_file):
#     with open(temp_file, "r", encoding='utf-8', errors='ignore') as f:
#         notebook_content = f.read()

#     exporter = PythonExporter()
#     python_code, _ = exporter.from_notebook_node(nbformat.reads(notebook_content, as_version=4))
#     return python_code

# TOKEN = ""
# # if TOKEN == 'default_token_here':
# #     raise EnvironmentError("GITHUB_TOKEN environment variable not set.")

# headers = {"Authorization": f"token {TOKEN}"}




# def process_github_repo(repo_url):
#     api_base_url = "https://api.github.com/repos/"
#     repo_url_parts = repo_url.split("https://github.com/")[-1].split("/")
#     repo_name = "/".join(repo_url_parts[:2])

#     subdirectory = ""
#     if len(repo_url_parts) > 4 and repo_url_parts[2] == "tree":
#         subdirectory = "/".join(repo_url_parts[4:])

#     contents_url = f"{api_base_url}{repo_name}/contents"
#     if subdirectory:
#         contents_url = f"{contents_url}/{subdirectory}"

#     repo_content = [f'<source type="github_repository" url="{repo_url}">']

#     def process_directory(url, repo_content):
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#         files = response.json()

#         for file in files:
#             if file["type"] == "file" and is_allowed_filetype(file["name"]):
#                 print(f"Processing {file['path']}...")

#                 temp_file = f"temp_{file['name']}"
#                 download_file(file["download_url"], temp_file)

#                 repo_content.append(f'<file name="{escape_xml(file["path"])}">') 

#                 if file["name"].endswith(".ipynb"):
#                     repo_content.append(escape_xml(process_ipynb_file(temp_file)))
#                 else:
#                     with open(temp_file, "r", encoding='utf-8', errors='ignore') as f:
#                         repo_content.append(escape_xml(f.read()))

#                 repo_content.append('</file>')
#                 os.remove(temp_file)
#             elif file["type"] == "dir":
#                 process_directory(file["url"], repo_content)

#     process_directory(contents_url, repo_content)
#     repo_content.append('</source>')
#     print("All files processed.")

#     return "\n".join(repo_content)

# if __name__ == "__main__":
#     # api_type = "groq"  # or "openai"
#     # api_key = ""
#     repo_url = "https://github.com/tegridydev/auto-md"

#     summary = process_github_repo(repo_url)
#     if summary:
#         print(summary)






# # import requests
# # import json

# # def analyze_github_repo(api_type, api_key, repo_url):
# #     """
# #     Function to send a request to the Flask app and get the analysis summary.
# #     """
# #     url = "http://localhost:8000/"
# #     data = {
# #         "apiType": api_type,
# #         "apiKey": api_key,
# #         "currentPageLink": repo_url
# #     }
# #     headers = {
# #         "Content-Type": "application/json"
# #     }

# #     try:
# #         response = requests.post(url, data=json.dumps(data), headers=headers)
# #         response.raise_for_status()
# #         return response.text
# #     except requests.exceptions.RequestException as e:
# #         print(f"Error: {e}")
# #         return None

# # if __name__ == "__main__":
# #     api_type = "groq"  # or "openai"
# #     api_key = ""
# #     repo_url = "https://github.com/tegridydev/auto-md"

# #     summary = analyze_github_repo(api_type, api_key, repo_url)
# #     if summary:
# #         print(summary)