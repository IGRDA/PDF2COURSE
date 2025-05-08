import sys
import os
import argparse

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from typing import List
from pydantic import BaseModel, Field
import argparse
from prompts import text_to_json,structured_output
from invoke import invoke_with_rotation



class Theory(BaseModel):
    id: str = Field(description="unique ID for the theory section")
    text: str = Field(description="exact section title or text")
    page: str = Field(description="page number")

class Section(BaseModel):
    id: str = Field(description="unique ID for the section")
    name: str = Field(description="section title string")
    theory: List[Theory] = Field(description="list of theory entries")

class Submodule(BaseModel):
    id: str = Field(description="unique ID for the submodule")
    name: str = Field(description="submodule title string")
    sections: List[Section] = Field(description="list of sections")

class Module(BaseModel):
    id: str = Field(description="unique ID for the module")
    name: str = Field(description="module title string")
    submodules: List[Submodule] = Field(description="list of submodules")

class ModuleList(BaseModel):
    modules: List[Module] = Field(description="list of modules")


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

    with open(f"data/index/text/{FILENAME}.txt", "r", encoding="utf-8") as file:
        current_index = file.read()
    
    prompt_text = text_to_json.format(
        current_index=current_index
    )


    json_text = invoke_with_rotation(prompt_text,"small").content


    prompt_text = structured_output.format(
        json_text=json_text
    )

    json_object = invoke_with_rotation(prompt_text,"medium",ModuleList)

    with open(f"data/index/json/{FILENAME}.json", "w", encoding="utf-8") as f:
        f.write(json_object.model_dump_json(indent=2))

if __name__ == "__main__":
    main()


