import sys
import os
import argparse

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph
from typing import TypedDict, Dict, List
from PyPDF2 import PdfReader
from invoke import invoke_with_rotation
from prompts import text_index_constructor, summary_of_page


# Define the structure of our state for the graph
class State(TypedDict):
    current_index: str        # The index accumulated so far.
    pages: List[str]          # List of all extracted page texts.
    current_batch_start: int  # Starting index for the current batch.
    batch_size: int           # Number of pages per batch.
    total_pages: int          # Total number of pages in the document.



def construct_batch_text(state: Dict) -> str:
    """
    Construct an aggregated text string for the current batch of pages.
    Each page is labeled with its page number.
    """
    start = state["current_batch_start"]
    end = min(start + state["batch_size"], state["total_pages"])
    batch_lines = []
    for i in range(start, end):
        # Add a marker for each page.
        batch_lines.append(f"Page {i+1}:\n{state['pages'][i]}")
    return "\n\n".join(batch_lines)

def process_batch(state: Dict) -> Dict:
    """
    Process a batch of pages: construct the aggregate prompt from the current batch and invoke the LLM.
    """
    # Construct the aggregated batch text.
    batch_text = construct_batch_text(state)
    # Prepare the prompt using the aggregated text.
    prompt_text = text_index_constructor.format(
        current_index=state["current_index"],
        number_of_pages=state["total_pages"],
        current_text=batch_text
    )
    ai_response = invoke_with_rotation(prompt_text,"small")
    
    return {
        "current_index": ai_response.content,  # Update the index.
        "pages": state["pages"],
        "current_batch_start": state["current_batch_start"],
        "batch_size": state["batch_size"],
        "total_pages": state["total_pages"]
    }

def get_next_batch(state: Dict) -> Dict:
    """
    Update the state pointer to move to the next batch.
    """
    next_start = state["current_batch_start"] + state["batch_size"]
    # If there are more pages, update the pointer.
    return {
        "current_index": state["current_index"],
        "pages": state["pages"],
        "current_batch_start": next_start,
        "batch_size": state["batch_size"],
        "total_pages": state["total_pages"]
    }

def after_process(state: Dict) -> str:
    """
    Determine if another batch needs processing.
    """
    if state["current_batch_start"] + state["batch_size"] < state["total_pages"]:
        return "get_next_batch"
    return "__end__"

def after_next_batch(state: Dict) -> str:
    """
    Return the next action after updating the batch pointer.
    """
    return "process_batch"

# Build the workflow using StateGraph
workflow = StateGraph(State)
workflow.add_node("process_batch", RunnableLambda(process_batch))
workflow.add_node("get_next_batch", RunnableLambda(get_next_batch))

# Connect steps based on the state evaluation.
workflow.add_conditional_edges(
    "process_batch",
    after_process,
    {
        "get_next_batch": "get_next_batch",
        "__end__": "__end__"
    }
)
workflow.add_conditional_edges(
    "get_next_batch",
    after_next_batch,
    {
        "process_batch": "process_batch"
    }
)

# Define entry and finish points.
workflow.set_entry_point("process_batch")

# Compile the workflow.
app = workflow.compile()




def main():
    parser = argparse.ArgumentParser(
        description="Process a file whose path is given by the user."
    )
    parser.add_argument(
        "FILENAME",
        help="Path to the input file"
    )
    args = parser.parse_args()

    FILENAME = args.FILENAME

    # Read your PDF file.
    pdf_path = f"data/pdf/{FILENAME}.pdf"  # Replace with your PDF file path.
    pdf_reader = PdfReader(pdf_path)

    # Preprocess all the pages into a list.
    pages_text = [page.extract_text() for page in pdf_reader.pages]
    #pages_text = [invoke_with_rotation(summary_of_page.format(text),"small").content for text in pages_text ]


    # Set the desired batch size (adjust as needed).
    BATCH_SIZE = 20

    # Initialize the state with all pages loaded.
    initial_state = {
        "current_index": "",
        "pages": pages_text,
        "current_batch_start": 0,
        "batch_size": BATCH_SIZE,
        "total_pages": len(pages_text)
    }

    # Run the indexing process.
    result = app.invoke(initial_state, {"recursion_limit": 100})

    # Print the final index.
    print("\n=== Generated Index ===\n")
    print(result["current_index"])

    # Optionally, save the generated index to a file.
    with open(f"data/index/text/{FILENAME}.txt", "w", encoding="utf-8") as f:
        f.write(result["current_index"])

if __name__ == "__main__":
    main()

