# Course Generator from PDF

This repository processes a PDF document into a structured course through three steps: `index_txt`, `index_json`, and `course_json`.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Usage

Run any main script from the src folder with the document title (without .pdf):

```bash
python3 src/course_json/main.py gestion_negocios_online
```


