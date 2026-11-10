from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnableLambda,RunnablePassthrough,RunnableParallel
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv

load_dotenv()

def content_formatting(text):
    context_data=""
    for content in text:
        context_data += content.page_content + "\n\n"
    return context_data


loader=PyPDFLoader("PDF25-26.pdf")

document=loader.load()
content=""
for page in document:
    content=content+page.page_content+"\n"


splitter=RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100,
        separators=[""]
)
splitted_text=splitter.split_text(content)

embedding_model=GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
vector_store=Chroma.from_texts(
        embedding=embedding_model,
        texts=splitted_text
)

query=input("Enter your query related to the pdf uploaded by you :: ")
retriever=vector_store.as_retriever(search_type="similarity",search_kwargs={'k':5})
parallel_chain=RunnableParallel({
        'context':retriever|RunnableLambda(content_formatting)  ,
        'query':RunnablePassthrough() 
        })
result=parallel_chain.invoke(query)

prompt=PromptTemplate(
        template="""
         Answer the question based only on the context provided below.
    If the answer is not available in the context, say
    "The video does not provide this information."

    Context:
    {context}

    Question:
    {query}

    Answer:
    """,
    input_variables=["context", "query"]
    )

model=ChatGoogleGenerativeAI(model="gemini-2.5-flash")
parser=StrOutputParser()

serial_chain=prompt|model|parser
output=serial_chain.invoke(result)
print(output)
