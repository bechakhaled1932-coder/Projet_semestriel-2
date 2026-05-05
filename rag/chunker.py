from langchain_text_splitters import RecursiveCharacterTextSplitter
def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=150,
        chunk_overlap=20
    )
    return splitter.split_documents(docs)
