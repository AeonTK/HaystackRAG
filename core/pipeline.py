import os
from haystack import Pipeline
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.document_stores import InMemoryDocumentStore
from haystack.components.generators import GPTGenerator
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.document_stores import InMemoryDocumentStore

from core.search import generate_search_pipeline

PROMPT_TEMPLATE = """
Given these documents, answer the question.
Documents:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}
Question: {{question}}
Answer:
"""

def generate_root_pipeline(document_store):
    root_pipeline = Pipeline()
    root_pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))
    root_pipeline.add_component("prompt_builder", PromptBuilder(template=PROMPT_TEMPLATE))
    root_pipeline.add_component("llm", GPTGenerator(api_key=os.environ.get("OPENAI_API_KEY")))
    root_pipeline.add_component("answer_builder", AnswerBuilder())

    root_pipeline.connect("retriever", "prompt_builder.documents")
    root_pipeline.connect("prompt_builder", "llm")
    root_pipeline.connect("llm.replies", "answer_builder.replies")

    return root_pipeline







