import sys

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

import streamlit as st
# -------------------------------------------------------------------------
# Your other imports and main application code will go AFTER this block.
# For example:
# from langchain_community.document_loaders import TextLoader
# import chromadb
# ... etc.

import os
from dotenv import load_dotenv
load_dotenv()
import zipfile # Keep this import as it's used for the download button functionality

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI # Use langchain_openai for newer versions

# Make sure to import the wrapped tools, including the new zip tools
from tools import (
    code_docs_search_tool, # Ensure this is defined in your tools.py
    code_interpreter_tool,
    composio_tools,
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
    scrape_website_tool,
    website_search_tool,
    xml_search_tool,
    youtube_channel_search_tool,
    youtube_video_search_tool,
    create_zip_archive_tool_function,   # UPDATED: Import the function directly
    extract_zip_archive_tool_function    # UPDATED: Import the function directly
)

# Consolidate all tools into a list for agents
tools = [
    code_docs_search_tool,
    code_interpreter_tool,
    *composio_tools, # Unpack composio_tools if it returns a list of tools
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
    scrape_website_tool,
    website_search_tool,
    xml_search_tool,
    youtube_channel_search_tool,
    youtube_video_search_tool,
    create_zip_archive_tool_function,   # UPDATED: Add the function to the list
    extract_zip_archive_tool_function   # UPDATED: Add the function to the list
]

# Ensure OPENAI_API_KEY is set in your environment
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7) # Use gpt-3.5-turbo

# === AGENTS ===
briefing_agent = Agent(
    role="Creative Strategist",
    goal="Understand product intent and search for relevant competitors",
    backstory="Knows how to position a brand for impact",
    tools=tools, # Pass the comprehensive tools list
    llm=llm,
    verbose=True
)

designer_agent = Agent(
    role="Web Designer",
    goal="Define structure, layout, and visual tokens",
    backstory="Expert at UX and turning ideas into screens",
    tools=tools, # Pass the comprehensive tools list
    llm=llm,
    verbose=True
)

copywriter_agent = Agent(
    role="Content Marketer",
    goal="Write copy with real-world context and references",
    backstory="Ties writing to live content and user needs",
    tools=tools, # Pass the comprehensive tools list
    llm=llm,
    verbose=True
)

developer_agent = Agent(
    role="Frontend Coder",
    goal="Build clean, responsive HTML/CSS code from design and content, and *save the final code to 'autosite/index.html' using the file_write_tool*.", # Emphasize saving
    backstory="Can go from wireframe to production code",
    tools=tools, # Pass the comprehensive tools list
    llm=llm,
    verbose=True
)

analyst_agent = Agent(
    role="SQL Analyst",
    goal="Retrieve key structured info about customers or product behavior",
    backstory="Data-first decision maker",
    tools=tools, # Pass the comprehensive tools list
    llm=llm,
    verbose=True
)

# === STREAMLIT UI ===
st.title("🧠 Auto Website Builder with CrewAI")

prompt = st.text_input("Enter your website idea or prompt", placeholder="e.g. A landing page for a smart fitness mirror")

uploaded_file = st.file_uploader("Upload your design or data file (CSV, TXT, etc.)", type=["csv", "txt", "pdf"])
if uploaded_file is not None:
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success(f"Uploaded {uploaded_file.name}")

if st.button("🚀 Run AI Website Builder"):
    if not prompt:
        st.warning("Please enter a prompt before running the builder.")
    else:
        st.write("Running CrewAI Agents... Please wait.")

        # === TASKS ===
        # Add a placeholder for the generated HTML if needed, or let the developer agent handle it
        # For now, let's assume the developer agent will write directly to the expected path.

        tasks = [
            Task(
                description=f"Analyze the prompt: '{prompt}' and use Web Search to find related products and trends. Summarize them into a brand brief.",
                expected_output="Brand goals, competitors, user insights.",
                agent=briefing_agent
            ),
            Task(
                description="Use the brand brief to define sections, layout, and a simple color palette. Refer to design.csv if needed.",
                expected_output="Wireframe layout + design tokens (text-based)",
                agent=designer_agent
            ),
            Task(
                description="Write persuasive and contextual content for each section. Include a hero title, subtext, CTA, and footer.",
                expected_output="SEO copywriting for the full homepage.",
                agent=copywriter_agent
            ),
            Task(
                description="Use layout, copy, and design tokens provided by previous agents to write clean, responsive HTML/CSS code for a full homepage. **Crucially, save this complete HTML/CSS code directly to a file named 'index.html' within the 'autosite/' directory using the 'Write File Tool'.** Ensure it's a complete, well-formed HTML document.",
                expected_output="Complete and syntactically correct HTML + CSS saved as 'autosite/index.html'.",
                agent=developer_agent,
            ),
            Task(
                description="Query user_feedback table and summarize most common feature requests and complaints.",
                expected_output="Data-driven insights to improve design/copy.",
                agent=analyst_agent
            )
        ]

        crew = Crew(agents=[briefing_agent, designer_agent, copywriter_agent, developer_agent, analyst_agent], tasks=tasks, verbose=True)
        result = crew.kickoff()
        st.success("Website generation process completed!")
        st.text_area("CrewAI Process Summary Output", value=result, height=300)

        # Create autosite folder - this should be done *before* the agent writes to it, or be robust.
        # It's better to ensure it exists before the agent tries to write.
        os.makedirs("autosite", exist_ok=True)

        # Check if index.html was actually created by the agent
        generated_html_path = "autosite/index.html"
        if os.path.exists(generated_html_path) and os.path.getsize(generated_html_path) > 0:
            st.success(f"Generated HTML found at {generated_html_path}")
            # Instead of writing a placeholder, read the content the agent generated
            with open(generated_html_path, "r") as f:
                st.code(f.read(), language="html") # Display the generated HTML
        else:
            st.warning(f"No HTML file found or it's empty at {generated_html_path}. The developer agent might not have saved it correctly.")
            # Fallback to a placeholder if the agent failed to write
            with open(generated_html_path, "w") as f:
                f.write("<html><body><h1>Generated Website (Placeholder)</h1><p>The AI agent did not produce the expected HTML output.</p></body></html>")


        # Zip the folder (this zips the *actual* generated index.html or the placeholder for download)
        zip_filename = "autosite_package.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for root, _, files in os.walk("autosite"):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, arcname=os.path.relpath(file_path, "autosite"))

        with open(zip_filename, "rb") as zip_file:
            st.download_button("📦 Download Website ZIP", data=zip_file, file_name=zip_filename, mime="application/zip")
