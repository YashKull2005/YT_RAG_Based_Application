
import os
import tempfile
import hashlib

import streamlit as st
from dotenv import load_dotenv

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
    RunnableParallel
)
from langchain_community.document_loaders import PyPDFLoader


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="PDF Intelligence | AI Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# 2. CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #eef2ff 0%,
        #f5f3ff 50%,
        #ecfeff 100%
    );
}

.block-container {
    padding-top: 2rem;
    max-width: 1100px;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(
        90deg,
        #4f46e5,
        #9333ea,
        #0891b2
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 16px;
    margin-bottom: 30px;
}

.upload-card {
    background: white;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #e0e7ff;
    box-shadow: 0 5px 20px rgba(79,70,229,0.08);
}

.stButton > button {
    background: linear-gradient(
        90deg,
        #4f46e5,
        #9333ea
    );
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 10px 20px;
    width: 100%;
}

.stButton > button:hover {
    background: linear-gradient(
        90deg,
        #4338ca,
        #7e22ce
    );
    color: white;
    border: none;
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #1e1b4b,
        #312e81
    );
}

[data-testid="stSidebar"] * {
    color: white;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 3. PAGE HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">📚 PDF Intelligence</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Upload your PDF and chat with your documents using AI'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# 4. SESSION STATE
# --------------------------------------------------

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "pdf_hash" not in st.session_state:
    st.session_state.pdf_hash = None

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# 5. FORMAT RETRIEVED DOCUMENTS
# --------------------------------------------------

def content_formatting(documents):

    context_data = ""

    for document in documents:
        context_data += document.page_content + "\n\n"

    return context_data


# --------------------------------------------------
# 6. CREATE VECTOR STORE
# --------------------------------------------------

@st.cache_resource(show_spinner=False)
def create_vector_store(pdf_bytes):

    temp_path = None

    try:

        # Save uploaded PDF temporarily

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(pdf_bytes)
            temp_path = temp_file.name

        # Load PDF

        loader = PyPDFLoader(temp_path)
        documents = loader.load()

        if not documents:
            raise ValueError("No readable pages found in PDF.")

        # Split documents

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=100
        )

        splitted_documents = splitter.split_documents(documents)

        if not splitted_documents:
            raise ValueError("No text could be extracted from PDF.")

        # Create embeddings

        embedding_model = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001"
        )

        # Store vectors in ChromaDB

        vector_store = Chroma.from_documents(
            documents=splitted_documents,
            embedding=embedding_model
        )

        return vector_store, len(splitted_documents)

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# --------------------------------------------------
# 7. CREATE RAG CHAIN
# --------------------------------------------------

def create_rag_chain(vector_store):

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    # Parallel chain

    parallel_chain = RunnableParallel({

        "context": (
            retriever |
            RunnableLambda(content_formatting)
        ),

        "query": RunnablePassthrough()

    })

    # Prompt template

    prompt = PromptTemplate(

        template="""
        Answer the question based only on the context
        provided below.

        If the answer is not available in the context,
        say:
        "The PDF does not provide this information."

        Context:
        {context}

        Question:
        {query}

        Answer:
        """,

        input_variables=["context", "query"]
    )

    # Gemini model

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    # Output parser

    parser = StrOutputParser()

    # Complete sequential chain

    serial_chain = prompt | model | parser

    # Complete RAG chain

    rag_chain = parallel_chain | serial_chain

    return rag_chain


# --------------------------------------------------
# 8. SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("## 📚 PDF Assistant")

    st.markdown("---")

    st.markdown("### How to use")

    st.write("1. Upload your PDF.")
    st.write("2. Click Process PDF.")
    st.write("3. Wait for processing.")
    st.write("4. Ask questions.")
    st.write("5. Get AI-generated answers.")

    st.markdown("---")

    st.markdown("### ⚙️ Technology")

    st.write("🔹 LangChain")
    st.write("🔹 Google Gemini")
    st.write("🔹 ChromaDB")
    st.write("🔹 Streamlit")

    st.markdown("---")

    if st.button("🗑️ Clear Chat History"):

        st.session_state.messages = []
        st.rerun()

    if st.session_state.vector_store is not None:

        st.success("PDF is ready!")

    else:

        st.info("Upload a PDF to get started.")


# --------------------------------------------------
# 9. PDF UPLOAD SECTION
# --------------------------------------------------

st.markdown("## 📂 Upload your document")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    help="Upload the PDF you want to ask questions about."
)

if uploaded_file is not None:

    pdf_bytes = uploaded_file.getvalue()

    current_hash = hashlib.md5(pdf_bytes).hexdigest()

    st.markdown(
        f"""
        <div class="upload-card">
            <h4>📄 {uploaded_file.name}</h4>
            <p style="color:gray;">
                File size: {len(pdf_bytes) / 1024:.2f} KB
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("🚀 Upload & Process PDF"):

        if not os.getenv("GOOGLE_API_KEY"):

            st.error(
                "Google API key not found. "
                "Please configure your .env file."
            )

        else:

            try:

                with st.spinner(
                    "Reading PDF, creating chunks and generating embeddings..."
                ):

                    vector_store, total_chunks = create_vector_store(
                        pdf_bytes
                    )

                    st.session_state.vector_store = vector_store
                    st.session_state.pdf_hash = current_hash
                    st.session_state.pdf_name = uploaded_file.name
                    st.session_state.messages = []

                st.success(
                    f"PDF processed successfully! "
                    f"{total_chunks} chunks created."
                )

                st.balloons()

            except Exception as e:

                st.error(f"Error processing PDF: {str(e)}")


# --------------------------------------------------
# 10. CHAT SECTION
# --------------------------------------------------

st.markdown("---")

st.markdown("## 💬 Chat with your PDF")

if st.session_state.vector_store is None:

    st.info(
        "👆 Please upload and process a PDF before asking questions."
    )

elif uploaded_file is None or current_hash != st.session_state.pdf_hash:

    st.warning(
        "You have selected a different PDF. "
        "Click Upload & Process PDF before asking questions."
    )

else:

    st.caption(f"Currently chatting with: {st.session_state.pdf_name}")

    # Display previous messages

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # User input

    user_query = st.chat_input(
        "Ask anything about your PDF..."
    )

    if user_query:

        # Display user question

        st.session_state.messages.append({

            "role": "user",
            "content": user_query

        })

        with st.chat_message("user"):

            st.markdown(user_query)

        # Generate AI answer

        with st.chat_message("assistant"):

            try:

                with st.spinner("Searching your PDF and generating answer..."):

                    rag_chain = create_rag_chain(
                        st.session_state.vector_store
                    )

                    response = rag_chain.invoke(user_query)

                st.markdown(response)

                st.session_state.messages.append({

                    "role": "assistant",
                    "content": response

                })

            except Exception as e:

                st.error(f"Something went wrong: {str(e)}")
