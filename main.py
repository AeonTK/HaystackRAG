from dotenv import load_dotenv
from haystack.document_stores import InMemoryDocumentStore

from core.pipeline import generate_root_pipeline
from core.search import generate_search_pipeline

load_dotenv()


def main():

    document_store = InMemoryDocumentStore()

    search_pipeline = generate_search_pipeline()

    question = input("Enter your question: ")

    documents = search_pipeline.run(
    {
        "search": {"query": question},
    })

    document_store.write_documents(documents["search"]["documents"])

    root_pipeline = generate_root_pipeline(document_store)

    results = root_pipeline.run(
    {
        "retriever": {"query": question},
        "prompt_builder": {"question": question},
        "answer_builder": {"query": question},
    })

    for answer in results["answer_builder"]["answers"]:
        print(answer.data)

    return


if __name__ == "__main__":
    main()

