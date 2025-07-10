import os
import zipfile  # NEW: Added for zip functionality
from dotenv import load_dotenv

# Load environment variables from .env file at the very beginning
load_dotenv()

# --- Langchain Tools (Fixing Deprecation Warnings) ---
# These imports are now updated to use langchain_community as per deprecation warnings.
# They are included if you intend to use them, even if not directly wrapped as CrewAI tools.
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_community.tools import ReadFileTool as LangchainReadFileTool # Renamed to avoid conflict
from langchain_community.tools import WriteFileTool as LangchainWriteFileTool # Renamed to avoid conflict

# --- Composio Toolset Import ---
# Used for integrating with Composio for various app actions (e.g., GitHub).
from composio_crewai import ComposioToolSet, App, Action

from crewai.tools import tool

# --- CrewAI Tools Imports ---
# These are the core tools from crewai_tools that will be instantiated.
from crewai_tools import (
    CodeDocsSearchTool,
    CodeInterpreterTool,
    CSVSearchTool,
    EXASearchTool,
    FileReadTool,
    FirecrawlSearchTool,
    FirecrawlCrawlWebsiteTool,
    FirecrawlScrapeWebsiteTool,
    GithubSearchTool,
    SerperDevTool,
    TXTSearchTool,
    JSONSearchTool,
    MDXSearchTool,
    PDFSearchTool,
    RagTool,
    ScrapeElementFromWebsiteTool,
    ScrapeWebsiteTool,
    WebsiteSearchTool,
    XMLSearchTool,
    YoutubeChannelSearchTool,
    YoutubeVideoSearchTool,
     # NEW: Ensure Tool is imported for custom tools
)

# --- Custom Zip Functions (NEW) ---
@tool ("zip_creator_tool")
def create_zip_archive_tool_function(source_path: str, output_zip_file: str) -> str:
    """
    Creates a zip archive from a file or folder.

    Args:
        source_path (str): The path to the file or directory to be zipped.
        output_zip_file (str): The desired name and path for the output .zip file.
                                (e.g., 'my_archive.zip', 'output/backup.zip')
    Returns:
        str: A message indicating success or failure.
    """
    try:
        if os.path.isfile(source_path):
            with zipfile.ZipFile(output_zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(source_path, os.path.basename(source_path))
            return f"Successfully created zip archive '{output_zip_file}' from file '{source_path}'."
        elif os.path.isdir(source_path):
            with zipfile.ZipFile(output_zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # arcname is the name of the file inside the zip, relative to the source_path
                        arcname = os.path.relpath(file_path, os.path.dirname(source_path) if os.path.dirname(source_path) else '.')
                        zipf.write(file_path, arcname)
            return f"Successfully created zip archive '{output_zip_file}' from directory '{source_path}'."
        else:
            return f"Error: Source path '{source_path}' does not exist or is not a file/directory."
    except Exception as e:
        return f"Error creating zip archive: {e}"
        
@tool ("zip_extractor_tool")
def extract_zip_archive_tool_function(zip_file_path: str, extract_to_path: str) -> str:
    """
    Extracts all contents from a zip archive to a specified directory.

    Args:
        zip_file_path (str): The path to the .zip file to be extracted.
        extract_to_path (str): The directory where the contents should be extracted.
                                This directory will be created if it doesn't exist.
    Returns:
        str: A message indicating success or failure.
    """
    try:
        if not os.path.exists(zip_file_path):
            return f"Error: Zip file '{zip_file_path}' not found."

        os.makedirs(extract_to_path, exist_ok=True) # Create target directory if it doesn't exist

        with zipfile.ZipFile(zip_file_path, 'r') as zipf:
            zipf.extractall(extract_to_path)
        return f"Successfully extracted contents of '{zip_file_path}' to '{extract_to_path}'."
    except zipfile.BadZipFile:
        return f"Error: '{zip_file_path}' is not a valid zip file."
    except Exception as e:
        return f"Error extracting zip archive: {e}"


# --- Tool Instantiation ---

# CodeDocsSearchTool: Requires a directory to search within.
code_docs_search_tool = CodeDocsSearchTool(directory='./docs') # Ensure './docs' directory exists if used.

# Code Interpreter Tool: Allows agents to execute and interpret code.
code_interpreter_tool = CodeInterpreterTool()

# Composio Toolset: Integrates with various applications via Composio.
# Ensure COMPOSIO_API_KEY is set in your .env file.
composio_key = os.getenv("COMPOSIO_API_KEY")
if not composio_key:
    raise ValueError("COMPOSIO_API_KEY is missing in .env file. Please set it.")
composio_toolset = ComposioToolSet(api_key=composio_key) # Pass the key during instantiation
# Get specific tools from Composio, e.g., GitHub actions.
composio_tools = composio_toolset.get_tools(apps=[App.GITHUB])


# CSV Search Tool: Searches within a CSV file.
# Agents will need to specify the file_path when using this tool if not set here.
csv_search_tool = CSVSearchTool() # Can take file_path='./data.csv' if always same

# EXA Search Tool: For general web search via EXA API.
# Ensure EXA_API_KEY is set in your .env file.
exa_api_key = os.getenv("EXA_API_KEY")
if not exa_api_key:
    raise ValueError("EXA_API_KEY is not set in .env file. EXASearchTool requires it.")
exa_search_tool = EXASearchTool(api_key=exa_api_key) # Pass the API key to the constructor

# File Read Tool: Reads content from a specified file.
# Agents will need to specify the file_path when using this tool.
file_read_tool = FileReadTool() # Can take file_path='./my_file.txt' if always same

# Firecrawl Search Tools: For web crawling and scraping via Firecrawl.
# Ensure FIRECRAWL_API_KEY is set in your .env file if required.
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
# Pass the API key to the constructors if it's available.
firecrawl_search_tool = FirecrawlSearchTool(api_key=firecrawl_api_key) if firecrawl_api_key else FirecrawlSearchTool()
firecrawl_crawl_website_tool = FirecrawlCrawlWebsiteTool(api_key=firecrawl_api_key) if firecrawl_api_key else FirecrawlCrawlWebsiteTool()
firecrawl_scrape_website_tool = FirecrawlScrapeWebsiteTool(api_key=firecrawl_api_key) if firecrawl_api_key else FirecrawlScrapeWebsiteTool()


# GitHub Search Tool: Searches GitHub repositories.
# Ensure GITHUB_TOKEN is set in your .env file.
github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    raise ValueError("GITHUB_TOKEN is not set in .env file. GithubSearchTool requires it.")
github_search_tool = GithubSearchTool(
    gh_token=github_token,
    # You can set a default repo_url here if most searches are for one repo:
    # repo_url='https://github.com/crewAI/crewAI'
)

# Serper Dev Tool: Provides structured search results from Google via Serper API.
# Ensure SERPER_API_KEY is set in your .env file.
serper_api_key = os.getenv("SERPER_API_KEY")
if not serper_api_key:
    raise ValueError("SERPER_API_KEY is not set in .env file. SerperDevTool requires it.")
serper_dev_tool = SerperDevTool(api_key=serper_api_key) # Pass the API key to the constructor


# TXT Search Tool: Searches within a plain text file.
# Agents will need to specify the file_path when using this tool.
txt_search_tool = TXTSearchTool() # Can take file_path='./notes.txt' if always same

# JSON Search Tool: Searches within a JSON file.
# Agents will need to specify the file_path when using this tool.
json_search_tool = JSONSearchTool() # Can take file_path='./data.json' if always same

# MDX Search Tool: Searches within an MDX file.
# Agents will need to specify the file_path when using this tool.
mdx_search_tool = MDXSearchTool() # Can take file_path='./readme.mdx' if always same

# PDF Search Tool: Searches within a PDF file.
# Agents will need to specify the file_path when using this tool.
pdf_search_tool = PDFSearchTool() # Can take file_path='./report.pdf' if always same

# RAG Tool: Retrieval-Augmented Generation tool.
# This typically requires configuration for a knowledge base or retriever to be effective.
# You might need to specify a 'knowledge_base_path' or a 'retriever' here.
# Example: rag_tool = RagTool(knowledge_base_path='./my_knowledge_base_folder')
rag_tool = RagTool()

# Web Scraping Tools: For extracting content from websites.
# These tools typically take the URL as an argument when called by an agent.
scrape_element_from_website_tool = ScrapeElementFromWebsiteTool()
scrape_website_tool = ScrapeWebsiteTool()

# Website Search Tool: A general tool for searching a specific website.
# Agents will need to specify the website_url when using this tool.
website_search_tool = WebsiteSearchTool() # Can take website_url='https://example.com' if always same

# XML Search Tool: Searches within an XML file.
# Agents will need to specify the file_path when using this tool.
xml_search_tool = XMLSearchTool() # Can take file_path='./config.xml' if always same

# Youtube Tools: For searching YouTube channels and videos.
# Ensure YOUTUBE_API_KEY is set in your .env file if using the full API.
youtube_api_key = os.getenv("YOUTUBE_API_KEY") # NEW: Get YouTube API key

# Agents will need to specify channel_id/video_id/search_query when using these tools.
youtube_channel_search_tool = YoutubeChannelSearchTool(youtube_api_key=youtube_api_key) if youtube_api_key else YoutubeChannelSearchTool()
youtube_video_search_tool = YoutubeVideoSearchTool(youtube_api_key=youtube_api_key) if youtube_api_key else YoutubeVideoSearchTool()


# --- Exporting Tools ---
# The __all__ list defines what gets imported when someone does 'from tools import *'
# It's good practice to include all public objects you want to expose.
__all__ = [
    "code_docs_search_tool",
    "code_interpreter_tool",
    "composio_tools",
    "csv_search_tool",
    "exa_search_tool",
    "file_read_tool",
    "firecrawl_search_tool",
    "firecrawl_crawl_website_tool",
    "firecrawl_scrape_website_tool",
    "github_search_tool",
    "serper_dev_tool",
    "txt_search_tool",
    "json_search_tool",
    "mdx_search_tool",
    "pdf_search_tool",
    "rag_tool",
    "scrape_element_from_website_tool",
    "scrape_website_tool",
    "website_search_tool",
    "xml_search_tool",
    "youtube_channel_search_tool",
    "youtube_video_search_tool",
    "zip_creator_tool",   # NEW: Added zip creator tool
    "zip_extractor_tool", # NEW: Added zip extractor tool
]
