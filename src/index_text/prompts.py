
from langchain.prompts import PromptTemplate


summary_of_page = PromptTemplate.from_template("""
Extract the index of this page, enumerate the module, submodule and sections. Don write plain tex. Just section names. Be short: {text}
""")



text_index_constructor= PromptTemplate.from_template("""
You are an assistant that incrementally builds a three‑level index for an educational document of {number_of_pages} pages. You’ll be called in sequence with:

• current_index: the index built so far  
• current_text: text from the next batch of pages  

Your job:
1. Extract only headings from current_text that are new and relevant.
2. If current_index already covers current_text, return it unchanged.  
3. If current_index itself contains a full, coherent index, return that instead.
4. Merge the new current_text information into current_index, ensuring:
5. Preserve a three‑level structure:
   – MODULE (ALL CAPS, “1”, “2”, …)  
   – Submodule (“1.1”, “1.2”, …)  
   – Section (“1.1.1”, “1.1.2”, …)  
6. Balance the number of items across modules, submodules, and sections.
7. Output **only** the updated index tree—no extra commentary.
8. Ensure pages are correct

Example output:
1. MODULE ONE  … page 1  
   1.1 COURSE OVERVIEW … page 2  
      1.1.1 Learning Objectives … page 3  
      1.1.2 Course Schedule … page 4  
   1.2 INSTRUCTOR INFO … page 5  
2. MODULE TWO … page 6  
   2.1 …  
   
<<<
**Previous Index:**
{current_index}

**New Content:**
{current_text}
>>>

Return the updated combined index.
""")




