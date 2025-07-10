import os
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
    YoutubeVideoSearchTool
)

# --- Tool Instantiation ---

# CodeDocsSearchTool: Requires a directory to search within.
code_docs_search_tool = CodeDocsSearchTool(directory='./docs') # Ensure './docs' directory exists if used.

# Code Interpreter Tool: Allows agents to execute and interpret code.
code_interpreter_tool = CodeInterpreterTool()

# Composio Toolset: Integrates with various applications via Composio.
# Ensure COMPOSIO_API_KEY is set in your .env file.
composio_key = os.getenv("COMPOSIO_API_KEY")
if not composio_key:
    # This raises the ValueError if the key is missing, as per your original logic.
    raise ValueError("COMPOSIO_API_KEY is missing in .env file. Please set it.")
composio_toolset = ComposioToolSet(api_key=composio_key) # Pass the key during instantiation
# Get specific tools from Composio, e.g., GitHub actions.
# You can specify other apps like [App.SLACK, App.JIRA] etc.
composio_tools = composio_toolset.get_tools(apps=[App.GITHUB])


# CSV Search Tool: Searches within a CSV file.
# Make sure 'data.csv' exists or update the path.
csv_search_tool = CSVSearchTool(file_path='./data.csv')

# EXA Search Tool: For general web search via EXA API.
# Ensure EXA_API_KEY is set in your .env file.
exa_api_key = os.getenv("EXA_API_KEY")
# It's generally better to raise an error if a critical API key is missing
# rather than just printing a warning, as the tool won't function without it.
if not exa_api_key:
    raise ValueError("EXA_API_KEY is not set in .env file. EXASearchTool requires it.")
exa_search_tool = EXASearchTool(api_key=exa_api_key)

# File Read Tool: Reads content from a specified file.
# Make sure 'my_file.txt' exists or update the path.
file_read_tool = FileReadTool(file_path='./my_file.txt')

# Firecrawl Search Tools: For web crawling and scraping via Firecrawl.
# Firecrawl tools often require an API key for full functionality.
# Ensure FIRECRAWL_API_KEY is set in your .env file if required.
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
firecrawl_search_tool = FirecrawlSearchTool(api_key=firecrawl_api_key) # Pass API key if available
firecrawl_crawl_website_tool = FirecrawlCrawlWebsiteTool(api_key=firecrawl_api_key) # Pass API key if available
firecrawl_scrape_website_tool = FirecrawlScrapeWebsiteTool(api_key=firecrawl_api_key) # Pass API key if available


# GitHub Search Tool: Searches GitHub repositories.
# Ensure GITHUB_TOKEN is set in your .env file.
github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    # Raise error if GitHub token is critical for your use case
    raise ValueError("GITHUB_TOKEN is not set in .env file. GithubSearchTool requires it.")
github_search_tool = GithubSearchTool(
    gh_token=github_token,
    # You can set a default repo_url if most searches are for one repo
    # repo_url='https://github.com/crewAI/crewAI'
)

# Serper Dev Tool: Provides structured search results from Google via Serper API.
# Ensure SERPER_API_KEY is set in your .env file.
serper_api_key = os.getenv("SERPER_API_KEY")
if not serper_api_key:
    raise ValueError("SERPER_API_KEY is not set in .env file. SerperDevTool requires it.")
serper_dev_tool = SerperDevTool()


# TXT Search Tool: Searches within a plain text file.
# Make sure 'notes.txt' exists or update the path.
txt_search_tool = TXTSearchTool(file_path='./notes.txt')

# JSON Search Tool: Searches within a JSON file.
# Make sure 'data.json' exists or update the path.
json_search_tool = JSONSearchTool(file_path='./data.json')

# MDX Search Tool: Searches within an MDX file.
# Make sure 'readme.mdx' exists or update the path.
mdx_search_tool = MDXSearchTool(file_path='./readme.mdx')

# PDF Search Tool: Searches within a PDF file.
# Make sure 'report.pdf' exists or update the path.
pdf_search_tool = PDFSearchTool(file_path='./report.pdf')

# RAG Tool: Retrieval-Augmented Generation tool.
# This typically requires configuration for a knowledge base or retriever to be effective.
# You might need to specify a 'knowledge_base_path' or a 'retriever' here.
# Example: RagTool(knowledge_base_path='./my_knowledge_base_folder')
rag_tool = RagTool()

# Web Scraping Tools: For extracting content from websites.
# These tools typically take the URL as an argument when called by an agent.
scrape_element_from_website_tool = ScrapeElementFromWebsiteTool()
scrape_website_tool = ScrapeWebsiteTool()

# Website Search Tool: A general tool for searching a specific website.
# website_url can be set here or passed dynamically by the agent.
website_search_tool = WebsiteSearchTool(website_url='https://example.com') # Example URL

# XML Search Tool: Searches within an XML file.
# Make sure 'config.xml' exists or update the path.
xml_search_tool = XMLSearchTool(file_path='./config.xml')

# Youtube Tools: For searching YouTube channels and videos.
# Replace with actual channel/video IDs or use agents to provide them dynamically.
youtube_channel_search_tool = YoutubeChannelSearchTool(channel_id='UC_example_id') # Replace with actual channel ID
youtube_video_search_tool = YoutubeVideoSearchTool(video_id='example_video_id') # Replace with actual video ID

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
    
]