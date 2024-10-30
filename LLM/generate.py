import groq
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import LLMChain, ReduceDocumentsChain, MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

class GroqLLM:
    def __init__(self, groq_api_key, model_name):
        self.groq_client = groq.Groq(api_key=groq_api_key)
        self.model_name = model_name

    def __call__(self, prompt):
        response = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model_name
        )
        return response.choices.message.content

class GroqFunctionCaller:
    def __init__(self, groq_llm):
        self.groq_llm = groq_llm

    def define_function(self, function_name, function_description, arguments):
        # Example function definition
        return {
            "name": function_name,
            "description": function_description,
            "arguments": arguments
        }

    def invoke_function(self, function_name, arguments):
        # Generate the prompt for invoking the function
        prompt = f"Invoke the {function_name} function with the following arguments: {arguments}"
        return self.groq_llm(prompt)

class LLM_Summarize:
    def __init__(self, groq_api_key, repo_url):
        self.groq_llm = GroqLLM(groq_api_key, "llama3-70b-8192")
        self.function_caller = GroqFunctionCaller(self.groq_llm)
        self.repo_url = repo_url

        self.code_summary_prompt = """You are an elite programmer who can understand Github Repository code given to you in text very well and summarize what is written in it.

                                    Code : {codes}

                                    Summarize the above list of codes present between delimiters in 50-70 words each and in paragraph.
                                    Store it in a list."""
        self.all_summary_prompt = """You are great at understanding the bigger picture of a codebase by looking at the summary of different code files. Given the following summaries, you have to tell in detail what the project does.

                                    Summaries : {summary_list}

                                    Limit final summary to 2000 words. Provide an elegant answer highlighting its purpose, main features, and key technologies used. Include 2-3 emojis."""
        self.format_response = """
                                Given the below text, modify it in HTML format for <p> tag. Use proper spacing, replace all space and line break with required HTML tags. Highlight main words by using proper tags. Include headings if required.

                                Text : {text} 
                                """

    def summarize_repo(self, code_list):
        # Map
        MAP_PROMPT = PromptTemplate.from_template(template=self.code_summary_prompt)
        map_chain = LLMChain(llm=self.groq_llm, prompt=MAP_PROMPT)

        # Reduce
        REDUCE_PROMPT = PromptTemplate.from_template(template=self.all_summary_prompt)
        reduce_chain = LLMChain(llm=self.groq_llm, prompt=REDUCE_PROMPT)

        # Combine documents chain
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain, document_variable_name="summary_list"
        )
        reduce_documents_chain = ReduceDocumentsChain(
            combine_documents_chain=combine_documents_chain,
            collapse_documents_chain=combine_documents_chain,
            token_max=4000,
        )

        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=map_chain,
            reduce_documents_chain=reduce_documents_chain,
            document_variable_name="codes",
            return_intermediate_steps=False,
        )

        # Split text
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000, chunk_overlap=0
        )
        split_docs = text_splitter.split_documents([Document(page_content=code) for code in code_list])

        # logger.info("Running LLM")
        result = map_reduce_chain.run(split_docs)

        # Change response from LLM to HTML format
        FORMAT_PROMPT = ChatPromptTemplate.from_template(self.format_response)
        FORMAT_MSG = FORMAT_PROMPT.format_messages(text=result)
        response = self.groq_llm(FORMAT_MSG)

        # logger.info("Result Generated")

        return response

# if __name__ == "__main__":
#     groq_api_key = "your_groq_api_key_here"
#     repo_url = "https://github.com/tegridydev/auto-md"
#     summarize_llm = LLM_Summarize(groq_api_key, repo_url)

#     # Example code list
#     code_list = [
#         "def hello_world():\n    print('Hello, World')",
#         "class Calculator:\n    def add(self, a, b):\n        return a + b"
#     ]

#     summary = summarize_llm.summarize_repo(code_list)
#     if summary:
#         print(summary)