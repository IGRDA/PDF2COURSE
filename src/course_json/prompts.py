from langchain.prompts import PromptTemplate

text_generator = PromptTemplate.from_template("""
You are writing a course.  You have these pieces of info about where you are:

{info}

Here is the text of the page **before** this section:
{before}

Here is the text of the **current** page:
{current}

Here is the text of the page **after** this section:
{after}

Write the plain‐text content (concise, faithful to the source) for _this_ section.

Use the same lenguage in the sections porvided.
""")