from langchain.prompts import PromptTemplate

text_to_json = PromptTemplate.from_template("""
You are a txt to JSON convertor. You will be given a plaintext course index with numbered headings and page numbers. Your job is to output a JSON array of module objects, each following this schema:
[{{  
    "id": "moduleId",  
    "name": "moduleName",  
    "submodules": [  
        {{  
            "id": "submoduleId",  
            "name": "submoduleName",  
            "sections":[  
                {{  
                    "id": "sectionId",  
                    "name": "sectionName",  
                    "theory":[  
                        {{  
                            "id": "sectionId",  
                            "text": "",  
                            "page": ""  
                        }}  
                    ]  
                }}  
            ]  
        }}  
    ]  
}},  
{{  
    "id": "moduleId",  
    "name": "moduleName",  
    "submodules": [  
        {{  
            "id": "submoduleId",  
            "name": "submoduleName",  
            "sections":[  
                {{  
                    "id": "sectionId",  
                    "name": "sectionName",  
                    "theory":[  
                        {{  
                            "id": "sectionId",  
                            "text": "",  
                            "page": ""  
                        }}  
                    ]  
                }}  
            ]  
        }}  
    ]  
}}]


The index:
{current_index}
Make sure all you write is in the language of the course. Dont be bias because your are using english.
Make sure al names are textual content and not placeholders.
Leave the text always empty ("text": "").
Make sure the JSON has the schema provided.              
""")


structured_output = PromptTemplate.from_template("Complete and correct the format, schema and missing fields to have the required output format. Leave the text always empty ('text': ''):{json_text}")
