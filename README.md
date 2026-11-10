📚 PDF Intelligence
PDF Intelligence is an AI-powered document question-answering app
built with Streamlit,
LangChain, Google
Gemini, and
ChromaDB.

Upload a PDF, let the app extract and index its content, and then ask
questions in natural language. The app retrieves relevant passages from
the document and uses Gemini to generate answers grounded in that
context.
✨ Features
- PDF upload: Upload a PDF directly through the Streamlit
  interface.
- Automatic text extraction: Extract document pages using
  LangChain's PyPDFLoader.
- Text chunking: Split extracted text into overlapping chunks to
  support retrieval.
- Semantic search: Generate embeddings with Google's
  gemini-embedding-001 model and store them in ChromaDB.
- Context-based answers: Retrieve the five most relevant chunks
  and pass them to Gemini 2.5 Flash.
- Document-focused responses: The prompt instructs the model to
  answer using the retrieved PDF context and to say when the PDF does
  not contain the requested information.
- Chat history: Keep the conversation visible during the current
  Streamlit session.
- Document change detection: Hash the uploaded PDF so the app can
  check whether the selected file matches the one that was processed.
- Clear chat: Reset the conversation from the sidebar.
- Temporary-file cleanup: Remove the temporary PDF file after
  processing.
🧰 Tech Stack
  Technology                      Purpose
  Python                          Application language
Streamlit                       Web interface and session state
LangChain                       Retrieval-augmented generation (RAG) pipeline
Google Gemini 2.5 Flash         Answer generation
Google gemini-embedding-001   Text embeddings
ChromaDB                        Vector storage and similarity search
PyPDF                           PDF text extraction
python-dotenv                   Load the Google API key from .env
⚙️ How It Works
The application follows a Retrieval-Augmented Generation (RAG) workflow:
1. Upload: The user selects a PDF file.
2. Extract: PyPDFLoader reads the PDF and extracts its pages.
3. Split: RecursiveCharacterTextSplitter divides the text into
   chunks of 400 characters with 100 characters of overlap.
4. Embed and store: Google embeddings are generated for each chunk
   and saved in a Chroma vector store.
5. Ask: The user submits a question in the chat interface.
6. Retrieve: ChromaDB performs similarity search and returns the
   top five relevant chunks.
7. Generate: The retrieved context and question are passed to
   Gemini 2.5 Flash through a LangChain chain.
8. Display: The generated answer is shown in the chat.
                  PDF Upload
                      |
                      v
               PDF Text Extraction
                      |
                      v
                 Text Chunking
              (400 chars / 100 overlap)
                      |
                      v
             Google Text Embeddings
                      |
                      v
                ChromaDB Store
                      |
                      |
User Question --------+
       |
       v
Similarity Search (Top 5 chunks)
       |
       v
Retrieved Context + Question
       |
       v
     Gemini 2.5 Flash
       |
       v
     AI-generated Answer
🚀 Getting Started
1. Clone the repository
git clone <your-repository-url>
cd <your-repository-folder>
Replace the placeholders with your Git repository URL and folder name.
2. Create a virtual environment
Windows (PowerShell / Command Prompt):
python -m venv venv
venv\Scripts\activate
macOS / Linux:
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
Install the packages used by the application:
pip install streamlit python-dotenv langchain-google-genai langchain-chroma langchain-core langchain-text-splitters langchain-community pypdf
You can also save these packages in a requirements.txt file for easier
installation and reproducible setup.
4. Get a Google Gemini API key
1. Open Google AI Studio.
2. Create or obtain a Google AI API key.
3. Keep the key private. Do not commit it to Git or share it publicly.
5. Configure environment variables
Create a file named .env in the project root:
GOOGLE_API_KEY=your_google_api_key_here
Replace the placeholder with your actual API key.
6. Run the application
If your Streamlit Python file is named app.py, run:
streamlit run app.py
If your file has a different name, replace app.py with that filename.
Streamlit will provide a local URL, usually:
http://localhost:8501
💡 How to Use
1. Start the application.
2. Select a PDF using the Choose a PDF file uploader.
3. Click Upload & Process PDF.
4. Wait while the app extracts the text, creates chunks, generates
   embeddings, and builds the vector store.
5. Once processing succeeds, enter a question in Chat with your
   PDF.
6. Read the answer and continue asking questions about the same
   document.
7. Use Clear Chat History in the sidebar to clear the current
   conversation.
If you select a different PDF, process it before asking questions about
it.
🔐 Environment Variables
  Variable                Required                Description
  GOOGLE_API_KEY        Yes                     API key used by the
Google Gemini chat
model and embedding
model
The application loads this value from the .env file using
python-dotenv.
📁 Suggested Project Structure
The exact repository structure was not included with the application
code. A simple layout could look like this:
pdf-intelligence/
├── app.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
Do not upload .env to source control. Add it to .gitignore:
.env
venv/
__pycache__/
*.py[cod]
⚠️ Notes and Limitations
- The app currently accepts PDF files only.
- Answers depend on the text successfully extracted from the uploaded
  PDF. Scanned PDFs without an extractable text layer may not work as
  expected.
- Retrieval uses similarity search with k=5; only the retrieved
  chunks are provided to the language model.
- The chunk size is 400 characters, with 100 characters of overlap.
- The vector store and chat history are held through the current
  Streamlit session/cache behavior; the code does not configure a
  persistent, user-managed document database.
- The app does not currently display page-level citations or source
  references with its answers.
- Gemini API access, quotas, and usage limits apply. API calls may
  incur costs depending on your Google AI plan.
- Avoid uploading confidential or sensitive documents unless you are
  comfortable processing their content through the configured Google
  AI services.
🛠️ Troubleshooting
  Problem                             What to check
  Google API key not found          Confirm that .env is in the
project root and contains
GOOGLE_API_KEY=.... Restart the
app after changing environment
variables.

  PDF processing fails                Check that the file is a valid PDF
and contains extractable text.

  No readable pages or text           The PDF may be empty, damaged, or
scanned without OCR text.

  Dependency/import error             Activate the intended virtual
environment and install the
dependencies listed above.
Gemini request fails                Check the API key, network
connection, model availability, and
Google AI API quota.
🔮 Possible Future Improvements
- Add page numbers and source citations to generated answers.
- Support multiple PDFs in a single knowledge base.
- Add OCR support for scanned documents.
- Persist vector stores across application restarts.
- Add document deletion and re-indexing controls.
- Add configurable chunk size and retrieval count.
- Add conversation export and downloadable chat history.
🤝 Contributing
Contributions, suggestions, and bug reports are welcome.
1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test the application.
5. Submit a pull request describing your changes.
📄 License
No license is specified in the supplied project code. Add a LICENSE
file and update this section before distributing the project if you want
to define reuse and contribution terms.
