import sys
import os
import zipfile
import streamlit as st
from dotenv import load_dotenv

# This section ensures that 'pysqlite3' is used whenever 'sqlite3' is imported.
# This is crucial for libraries like ChromaDB that might default to the built-in sqlite3,
# which is too old on your system.
try:
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    # If pysqlite3-binary somehow isn't available, fall back to the standard sqlite3.
    # (Note: if this happens, ChromaDB will likely still fail due to old version).
    pass

# Load environment variables at the very beginning
load_dotenv()

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Make sure to import all tools you intend to use.
# It's good practice to be explicit about which tools each agent gets.
from tools import (
    code_docs_search_tool,
    code_interpreter_tool,
    composio_tools, # This is a list of tools from ComposioToolSet
    csv_search_tool,
    exa_search_tool,
    file_read_tool,
    firecrawl_search_tool,
    firecrawl_crawl_website_tool,
    firecrawl_scrape_website_tool,
    github_search_tool,
    serper_dev_tool,
    txt_search_tool,
    json_search_tool,
    mdx_search_tool,
    pdf_search_tool,
    rag_tool,
    scrape_element_from_website_tool,
    scrape_website_tool, # Used for general page scraping (doesn't need css_element)
    website_search_tool,
    xml_search_tool,
    youtube_channel_search_tool,
    youtube_video_search_tool,
    create_zip_archive_tool_function,
    extract_zip_archive_tool_function
)

# --- IMPORTANT: SQL Database Tool Setup (If you intend to query a database) ---
# Your logs indicated 'analyst_agent' tried to query a 'user_feedback table'
# with 'CodeDocsSearchTool', which is incorrect.
# To query a SQL database, you need to properly set up SQLDatabase and QuerySQLDataBaseTool.
# This part assumes you have a database connection string (e.g., in your .env).

# from langchain_community.utilities import SQLDatabase
# from langchain_community.tools import QuerySQLDataBaseTool

# sql_query_tool = None # Initialize to None
# try:
#     # Replace with your actual database connection string
#     DB_URI = os.getenv("DATABASE_URL", "sqlite:///./data/user_feedback.db") # Example for SQLite
#     if not DB_URI:
#         st.error("DATABASE_URL environment variable is not set for SQL database access.")
#     else:
#         # Ensure your database is accessible and has the 'user_feedback' table.
#         # You might need to adjust the directory for 'data/user_feedback.db'
#         # You may need to create the 'data' directory and an empty 'user_feedback.db' file initially
#         sql_database = SQLDatabase.from_uri(DB_URI)
#         sql_query_tool = QuerySQLDataBaseTool(database=sql_database)
#         st.info(f"SQL Database Tool initialized for {DB_URI}")
# except Exception as e:
#     st.error(f"Error initializing SQL Database Tool: {e}. Check your DATABASE_URL and database file.")

# --- Consolidated Tool Lists (Tailored for each agent) ---
# Instead of giving all agents all tools, provide only what they need.
# This reduces the LLM's 'cognitive load' and potential for misusing tools.

# General Web Search & File Reading tools for initial research
briefing_agent_tools = [
    serper_dev_tool,
    exa_search_tool,
    file_read_tool,
    firecrawl_search_tool,
    firecrawl_crawl_website_tool,
    firecrawl_scrape_website_tool, # Use this if you need full page content
    website_search_tool,
    csv_search_tool, # If it might read uploaded CSVs
    txt_search_tool, # If it might read uploaded TXTs
    pdf_search_tool, # If it might read uploaded PDFs
]
# Add scrape_element_from_website_tool ONLY if this agent is expected to extract specific CSS elements
# briefing_agent_tools.append(scrape_element_from_website_tool)

# Designer and Copywriter might need general web search for inspiration/context
designer_copywriter_tools = [
    serper_dev_tool,
    exa_search_tool,
    file_read_tool,
    scrape_website_tool, # For general website content to inform design/copy
    csv_search_tool, # If they might refer to design.csv
    txt_search_tool,
    json_search_tool,
]

# Developer needs code interpretation, file read/write, and potentially Github search
developer_agent_tools = [
    code_interpreter_tool,
    file_read_tool,
    # Assuming 'Write File Tool' is implied/handled by CrewAI's Task output,
    # but if there's an explicit WriteFileTool, add it here.
    # If the custom zip functions are needed for developer output:
    create_zip_archive_tool_function,
    extract_zip_archive_tool_function,
    github_search_tool,
]

# Analyst needs specific tools for data querying.
# This is where the main "correction" for the database issue goes.
analyst_agent_tools = [
    # If you enabled the SQL_QUERY_TOOL above, uncomment this:
    # sql_query_tool,
    code_interpreter_tool, # Can be used to run Python code for data analysis/DB interaction
    csv_search_tool,
    json_search_tool,
    file_read_tool,
    # Do NOT include code_docs_search_tool here if it's for local documentation.
    # It caused errors trying to resolve external URLs for database queries.
]
# Filter out None if sql_query_tool wasn't initialized
analyst_agent_tools = [tool for tool in analyst_agent_tools if tool is not None]


# Ensure OPENAI_API_KEY is set in your environment
llm = ChatOpenAI(model="gpt-4o", temperature=0.7) # Recommended: Use a more capable model like gpt-4o for complex tasks

# === AGENTS ===
briefing_agent = Agent(
    role="Creative Strategist",
    goal="Understand product intent and search for relevant competitors and market trends using web search. Summarize findings into a comprehensive brand brief.",
    backstory="An expert in market analysis and brand positioning, adept at synthesizing information for strategic insights.",
    tools=briefing_agent_tools, # Assign specific tools
    llm=llm,
    verbose=True,
    allow_delegation=True # Allow delegation for complex research tasks
)

designer_agent = Agent(
    role="Web Designer",
    goal="Define the website's structure, layout, and visual design tokens (colors, typography, spacing). Incorporate best UX practices and refer to design resources.",
    backstory="A seasoned UX/UI designer who excels at translating abstract ideas into intuitive and aesthetically pleasing web interfaces.",
    tools=designer_copywriter_tools, # Assign specific tools
    llm=llm,
    verbose=True,
    allow_delegation=True
)

copywriter_agent = Agent(
    role="Content Marketer",
    goal="Write compelling and contextual copy for each website section, including hero title, subtext, CTA, and footer. Ensure SEO optimization and a clear brand voice.",
    backstory="A master storyteller and wordsmith, capable of crafting engaging content that resonates with target audiences and drives action.",
    tools=designer_copywriter_tools, # Assign specific tools
    llm=llm,
    verbose=True,
    allow_delegation=True
)

developer_agent = Agent(
    role="Frontend Coder",
    goal="Translate the design and content into clean, responsive, and functional HTML/CSS code for a full homepage. **The final output must be saved as a complete, well-formed HTML document to 'autosite/index.html' using the appropriate file writing tool.**",
    backstory="A meticulous and efficient frontend developer who transforms visual designs and content into high-quality, production-ready web code.",
    tools=developer_agent_tools, # Assign specific tools
    llm=llm,
    verbose=True,
    allow_delegation=True
)

analyst_agent = Agent(
    role="Database Analyst", # Changed role for clarity
    goal="Retrieve and summarize the most common feature requests and complaints from the 'user_feedback' database table to provide data-driven insights for design and copy improvements.",
    backstory="A data-first decision maker with expertise in querying and interpreting structured database information.",
    tools=analyst_agent_tools, # Assign specific tools (should include sql_query_tool if enabled)
    llm=llm,
    verbose=True,
    allow_delegation=True
)


# === STREAMLIT UI ===
st.title("🧠 Auto Website Builder with CrewAI")

prompt = st.text_input("Enter your website idea or prompt", placeholder="e.g. A landing page for a smart fitness mirror")

uploaded_file = st.file_uploader("Upload your design or data file (CSV, TXT, PDF, ZIP)", type=["csv", "txt", "pdf", "zip"])
if uploaded_file is not None:
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success(f"Uploaded {uploaded_file.name}")

    # NEW: Handle ZIP file extraction upon upload
    if uploaded_file.type == "application/zip":
        st.info(f"Extracting '{uploaded_file.name}'...")
        try:
            # Use the custom tool function directly, or let an agent handle it if more complex logic is needed
            # For direct extraction, ensure the function is importable and callable.
            extract_zip_archive_tool_function(file_path, "uploads/extracted_zip")
            st.success(f"Successfully extracted '{uploaded_file.name}' to 'uploads/extracted_zip'.")
        except Exception as e:
            st.error(f"Failed to extract zip file: {e}")


if st.button("🚀 Run AI Website Builder"):
    if not prompt:
        st.warning("Please enter a prompt before running the builder.")
    else:
        st.write("Running CrewAI Agents... Please wait.")

        # === TASKS ===
        tasks = [
            Task(
                description=f"Analyze the prompt: '{prompt}'. Use web search tools to find and summarize related products, competitors, and current market trends. Deliver a concise brand brief.",
                expected_output="A brief outlining brand goals, key competitors, and relevant user/market insights.",
                agent=briefing_agent,
            ),
            Task(
                description="Based on the brand brief, define the website's structure (e.g., header, hero, features, CTA, footer), a clear layout, and a consistent visual design token system (color palette, typography, spacing). Reference uploaded design files if available (e.g., 'design.csv').",
                expected_output="A text-based wireframe layout description and a list of design tokens.",
                agent=designer_agent,
            ),
            Task(
                description="Draft persuasive and SEO-friendly content for each section of the website. Include a catchy hero title, compelling subtext, a clear call-to-action (CTA), and a functional footer. Ensure the tone aligns with the brand brief and target audience.",
                expected_output="Complete and contextual copywriting for the entire homepage.",
                agent=copywriter_agent,
            ),
            Task(
                description=(
                    "Using the detailed layout, content, and design tokens from previous agents, write clean, semantic, and responsive HTML and CSS code for the entire homepage. "
                    "**Crucially, after generating the complete HTML and CSS, save it as a single, well-formed HTML document named 'index.html' inside the 'autosite/' directory. "
                    "You must use the available file writing tool to perform this save operation.**"
                ),
                expected_output="A complete and syntactically correct HTML/CSS file saved as 'autosite/index.html'.",
                agent=developer_agent,
            ),
            Task(
                description=(
                    "Access the 'user_feedback' database table and retrieve the most common feature requests and complaints. "
                    "Use the SQL query tool to extract relevant data. "
                    "Summarize these findings into actionable insights for improving the website's design and copy. "
                    "If the SQL tool isn't available, state that and explain how you would hypothetically achieve this if it were."
                ),
                expected_output="A summary of data-driven insights from user feedback, including common requests/complaints, presented clearly for design/copy improvement.",
                agent=analyst_agent,
            )
        ]

        # Use an appropriate model, e.g., "gpt-4o" for better performance in complex tasks
        crew = Crew(
            agents=[briefing_agent, designer_agent, copywriter_agent, developer_agent, analyst_agent],
            tasks=tasks,
            verbose=True,
            # Uncomment below for higher verbosity to debug agent thought process
            # manager_llm=llm # Add a manager_llm if you have a hierarchical crew setup
        )
        result = crew.kickoff()
        st.success("Website generation process completed!")
        st.text_area("CrewAI Process Summary Output", value=result, height=300)

        # Ensure 'autosite' directory exists before checking for the file or zipping
        os.makedirs("autosite", exist_ok=True)

        generated_html_path = "autosite/index.html"
        if os.path.exists(generated_html_path) and os.path.getsize(generated_html_path) > 0:
            st.success(f"Generated HTML found at {generated_html_path}")
            with open(generated_html_path, "r") as f:
                st.code(f.read(), language="html") # Display the generated HTML
        else:
            st.warning(f"No HTML file found or it's empty at {generated_html_path}. The developer agent might not have saved it correctly or encountered an issue.")
            # Provide a placeholder if generation failed
            with open(generated_html_path, "w") as f:
                f.write("<html><body><h1>Generated Website (Placeholder)</h1><p>The AI agent did not produce the expected HTML output.</p></body></html>")


        # Create a ZIP archive of the 'autosite' directory
        zip_filename = "autosite_package.zip"
        try:
            # Using the custom tool function directly here for the download button,
            # assuming it's reliable for this purpose outside of an agent's direct call.
            # Alternatively, an agent could be tasked to create this zip.
            create_zip_archive_tool_function("autosite", zip_filename)
            st.success(f"Website package zipped to '{zip_filename}'.")
            with open(zip_filename, "rb") as zip_file:
                st.download_button("📦 Download Website ZIP", data=zip_file, file_name=zip_filename, mime="application/zip")
        except Exception as e:
            st.error(f"Error creating zip for download: {e}")