import sys
import os
import argparse

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import json, copy
from PyPDF2 import PdfReader
from invoke import invoke_with_rotation
from prompts import text_generator




def ai_generator(pages_text, module, submodule, section, prev_sec, next_sec,theory):
    # determine page indexes
    p = section.get("page", 0)
    start = max(p - 1, 0)
    end   = min(p + 2, len(pages_text))   # slice excludes end index
    before, current, after = pages_text[start:p], pages_text[p:p+1], pages_text[p+1:end]

    # stitch your info string
    info = (
        f"Module: {module['name']}\n"
        f"Submodule: {submodule['name']}\n"
        f"Section: {section['name']}\n"
        f"Previous section: {prev_sec['name'] if prev_sec else 'None'}\n"
        f"Next section: {next_sec['name'] if next_sec else 'None'}\n"
    )

    # build the prompt

    inp = text_generator.format(
        info=info,
        before="".join(before),
        current="".join(current),
        after="".join(after),
    )

    # invoke the LLM
    generated = invoke_with_rotation(inp,model_size="small")

    # return keys to merge into your theory dict
    return {
        "text": generated.content,
        "id": theory["page"], 
        "page": theory["page"] 
    }

def process_all_theory(modules, func, pages_text):
    for mod in modules:
        for sub in mod.get("submodules", []):
            secs = sub.get("sections", [])
            for idx, sec in enumerate(secs):
                prev_sec = secs[idx-1] if idx > 0 else None
                next_sec = secs[idx+1] if idx < len(secs)-1 else None
                for theory in sec.get("theory", []):
                    updates = func(pages_text,mod, sub, sec, prev_sec, next_sec, theory)
                    if isinstance(updates, dict):
                        theory.update(updates)
    return modules



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

    with open(f"data/index/json/{FILENAME}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Read your PDF file.
    pdf_path = f"data/pdf/{FILENAME}.pdf"
    pdf_reader = PdfReader(pdf_path)
    # Preprocess all the pages into a list.
    pages_text = [page.extract_text() for page in pdf_reader.pages]

    schema = copy.deepcopy(data["modules"])
    result = process_all_theory(copy.deepcopy(schema), ai_generator, pages_text)


    with open(f"data/course/json/{FILENAME}.json","w",encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()