
from dotenv import load_dotenv
load_dotenv()
# tools.py
# FIX: Removed the incomplete 'from cr' line
from langchain.tools import Tool as LangchainTool # Rename to avoid conflict
from langchain.utilities import SerpAPIWrapper
from langchain.utilities.sql_database import SQLDatabase
from langchain.tools.sql_database.tool import QuerySQLDataBaseTool
# from langchain.agents.tools import tool # No longer strictly needed if using crewai_tools.Tool for wrapping
# from langchain.agents.agent_toolkits import FileManagementToolkit # Unused, can remove
# from langchain.tools import DuckDBTool # Unused, can remove
from langchain.tools.file_management.read import ReadFileTool as LangchainReadFileTool # Rename
from langchain.tools.file_management.write import WriteFileTool as LangchainWriteFileTool # Rename
import os

print("Loaded COMPOSIO_API_KEY:", os.getenv("COMPOSIO_API_KEY"))  # Bu satırı geçici 

from composio_crewai import ComposioToolSet, App, Action






# Import CrewAI Tool for wrapping Langchain tools
from crewai_tools import (


CodeDocsSearchTool ,

CodeInterpreterTool ,


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
code_docs_search_tool = CodeDocsSearchTool(directory='./docs')
code_interpreter_tool = CodeInterpreterTool()

# Kontrollü kullanım
composio_key = os.getenv("COMPOSIO_API_KEY")
if not composio_key:
    raise ValueError("COMPOSIO_API_KEY is missing in .env file")

composio_toolset = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))
print(os.getenv("COMPOSIO_API_KEY"))
composio_tools = composio_toolset.get_tools(apps=[App.GITHUB])

csv_search_tool = CSVSearchTool(file_path='./data.csv')
exa_search_tool = EXASearchTool(api_key=os.getenv("EXA_API_KEY"))
file_read_tool = FileReadTool(file_path='./my_file.txt')
firecrawl_search_tool = FirecrawlSearchTool()
firecrawl_crawl_website_tool = FirecrawlCrawlWebsiteTool()
firecrawl_scrape_website_tool = FirecrawlScrapeWebsiteTool()
github_search_tool = GithubSearchTool(
    repo_url='https://github.com' ,
    gh_token=os.getenv("GITHUB_TOKEN"))
serper_dev_tool = SerperDevTool()
txt_search_tool = TXTSearchTool(file_path='./notes.txt')
json_search_tool = JSONSearchTool(file_path='./data.json')
mdx_search_tool = MDXSearchTool(file_path='./readme.mdx')
pdf_search_tool = PDFSearchTool(file_path='./report.pdf')
rag_tool = RagTool()
scrape_element_from_website_tool = ScrapeElementFromWebsiteTool()
scrape_website_tool = ScrapeWebsiteTool()
website_search_tool = WebsiteSearchTool(website_url='https://example.com')
xml_search_tool = XMLSearchTool(file_path='./config.xml')
youtube_channel_search_tool = YoutubeChannelSearchTool(channel_id='UC_example_id')
youtube_video_search_tool = YoutubeVideoSearchTool(video_id='example_video_id')


__all__ = [
    "code_docs_search_tool",
    "code_interpreter_tool",
    "composio_tools",
    "csv_search_tool",
]








