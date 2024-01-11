from haystack import Pipeline
from haystack.components.converters import HTMLToDocument, TextFileToDocument
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack import Document

import requests
from pathlib import Path
import os

def store_from_htmls(document_store, htmls: list):
    """Converts HTML files to documents and stores them in the document store"""
    pipeline = Pipeline()
    pipeline.add_component("converter", HTMLToDocument())
    pipeline.add_component("cleaner", DocumentCleaner())
    pipeline.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=5))
    pipeline.add_component("writer", DocumentWriter(document_store=document_store))
    pipeline.connect("converter", "cleaner")
    pipeline.connect("cleaner", "splitter")
    pipeline.connect("splitter", "writer")
    pipeline.run({"converter": {"sources": htmls}})

def store_from_urls(document_store, urls: list):
    """Downloads the HTML of the page at the given URL and stores it in the document store"""
    for url in urls:
        response = requests.get(url)
        filename = "search\\" + url.split("/")[-1].lower() + ".html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
    htmls = [str(file) for file in list(Path("./search").glob("*.html"))]
    store_from_htmls(document_store, htmls)

    for filename in list(Path("./search").glob("*.html")):
        os.remove(filename)
    
def store_from_txts(document_store, txts: list):
    """Converts text files to documents and stores them in the document store"""
    pipeline = Pipeline()
    pipeline.add_component("converter", TextFileToDocument())
    pipeline.add_component("cleaner", DocumentCleaner())
    pipeline.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=5))
    pipeline.add_component("writer", DocumentWriter(document_store=document_store))
    pipeline.connect("converter", "cleaner")
    pipeline.connect("cleaner", "splitter")
    pipeline.connect("splitter", "writer")
    pipeline.run({"converter": {"sources": txts}})

def store_from_str(document_store, text: str):
    """Converts a string to documents and stores them in the document store"""
    document_store.write_documents([Document(content=text)])


