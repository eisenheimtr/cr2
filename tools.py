import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Langchain Tools (imported but not directly used as CrewAI tools in this setup) ---
# These imports are kept if you intend to use raw Langchain tools elsewhere,
# but they are not directly wrapped into CrewAI tools in this script.
# If not needed, they can be removed.
from langchain.tools import Tool as LangchainTool # Renamed to avoid conflict
from langchain.utilities import SerpAPIWrapper
from langchain.utilities.sql_database import SQLDatabase
from langchain.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.tools.file_management.read import ReadFileTool as LangchainReadFileTool
from langchain.tools.file_management.write import WriteFileTool as LangchainWriteFileTool

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

# CodeDocsSearchTool: This tool was used but not imported/defined in the provided snippet.
# If it's a custom tool, ensure its definition is present.
# If it's from another library, add the appropriate import statement.
# For now, it's commented out to prevent errors.
code_docs_search_tool = CodeDocsSearchTool(directory='./docs')

# Code Interpreter Tool: Allows agents to execute and interpret code.
code_interpreter_tool = CodeInterpreterTool()

# Composio Toolset: Integrates with various applications via Composio.
# Ensure COMPOSIO_API_KEY is set in your .env file.
composio_key = os.getenv("COMPOSIO_API_KEY")
if not composio_key:
    raise ValueError("COMPOSIO_API_KEY is missing in .env file. Please set it.")
composio_toolset = ComposioToolSet()
# Get specific tools from Composio, e.g., GitHub actions.
composio_tools = composio_toolset.get_tools(apps=[App.GITHUB])

# CSV Search Tool: Searches within a CSV file.
# Consider making file_path configurable via environment variables or arguments.
csv_search_tool = CSVSearchTool(file_path='./data.csv')

# EXA Search Tool: For general web search via EXA API.
# Ensure EXA_API_KEY is set in your .env file.
exa_api_key = os.getenv("EXA_API_KEY")
if not exa_api_key:
    print("Warning: EXA_API_KEY is not set. EXASearchTool may not function.")
exa_search_tool = EXASearchTool(api_key=exa_api_key)

# File Read Tool: Reads content from a specified file.
# Consider making file_path configurable.
file_read_tool = FileReadTool(file_path='./my_file.txt')

# Firecrawl Search Tools: For web crawling and scraping via Firecrawl.
# Firecrawl tools often require an API key for full functionality.
firecrawl_search_tool = FirecrawlSearchTool()
firecrawl_crawl_website_tool = FirecrawlCrawlWebsiteTool()
firecrawl_scrape_website_tool = FirecrawlScrapeWebsiteTool()

# GitHub Search Tool: Searches GitHub repositories.
# Ensure GITHUB_TOKEN is set in your .env file.
github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    print("Warning: GITHUB_TOKEN is not set. GithubSearchTool may not function.")
github_search_tool = GithubSearchTool(
    repo_url='https://github.com', # Default repo, can be overridden when used
    gh_token=github_token
)

# Serper Dev Tool: Provides structured search results from Google via Serper API.
# Ensure SERPER_API_KEY is set in your .env file.
# Now fetch the API key
serper_api_key = os.getenv("SERPER_API_KEY")
if not serper_api_key:
    print("Warning: SERPER_API_KEY is not set. SerperDevTool may not function.")

serper_dev_tool = SerperDevTool()

# TXT Search Tool: Searches within a plain text file.
# Consider making file_path configurable.
txt_search_tool = TXTSearchTool(file_path='./notes.txt')

# JSON Search Tool: Searches within a JSON file.
# Consider making file_path configurable.
json_search_tool = JSONSearchTool(file_path='./data.json')

# MDX Search Tool: Searches within an MDX file.
# Consider making file_path configurable.
mdx_search_tool = MDXSearchTool(file_path='./readme.mdx')

# PDF Search Tool: Searches within a PDF file.
# Consider making file_path configurable.
pdf_search_tool = PDFSearchTool(file_path='./report.pdf')

# RAG Tool: Retrieval-Augmented Generation tool.
# This typically requires configuration for a knowledge base or retriever to be effective.
# Example: RagTool(knowledge_base_path='./my_knowledge_base')
rag_tool = RagTool()

# Web Scraping Tools: For extracting content from websites.
# These tools typically take the URL as an argument when called by an agent.
scrape_element_from_website_tool = ScrapeElementFromWebsiteTool()
scrape_website_tool = ScrapeWebsiteTool()

# Website Search Tool: A general tool for searching a specific website.
# Consider making website_url configurable.
website_search_tool = WebsiteSearchTool(website_url='https://example.com')

# XML Search Tool: Searches within an XML file.
# Consider making file_path configurable.
xml_search_tool = XMLSearchTool(file_path='./config.xml')

# YouTube Search Tools: For searching YouTube channels and videos.
# These tools will need actual channel/video IDs or search queries to be useful.
youtube_channel_search_tool = YoutubeChannelSearchTool(channel_id='UC_example_id') # Replace with actual channel ID
youtube_video_search_tool = YoutubeVideoSearchTool(video_id='example_video_id') # Replace with actual video ID

# --- Exporting Tools ---
# The __all__ list defines what gets imported when someone does 'from tools import *'
# It's good practice to include all public objects you want to expose.
__all__ = [
    # "code_docs_search_tool", # Commented out as it's not defined
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
