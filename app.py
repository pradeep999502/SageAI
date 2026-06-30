from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from flask import render_template
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace, HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import InMemoryVectorStore 
import win32com.client
load_dotenv()


app = Flask(__name__)
textmodel = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')
vectorstore = InMemoryVectorStore(embedding=embedding)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("start.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data["prompt"]

    print(f"User: {prompt}")

    prompt_format = f"""
    You are an AI assistant.

    Give the response to "{prompt}" in the following format:
    1. Less than 100 words.
    2. Concise and informative.
    3. Mention the source.
    """
    res = textmodel.invoke(prompt_format)

    return jsonify({
        "reply": res.content
    })
@app.route("/chattemplate")
def chattemplate():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/rag")
def rag():
    return render_template("Rag.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["document"]

    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    print(f"file uploaded: {filename}")
    return jsonify({
        "status": "success",
        "filename": filename
    })

@app.route("/docresponse", methods=["POST"])
def docresponse():
    userdata = request.get_json()
    user_prompt = userdata["ragprompt"]
    files = [
        os.path.join(UPLOAD_FOLDER, f)
        for f in os.listdir(UPLOAD_FOLDER)
        if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))
    ]

    # if not files:
    #     return jsonify({"filename": None})

    latest_file = max(files, key=os.path.getmtime)
    print(f"last file uploaded: {latest_file}")
    extension = os.path.splitext(latest_file)[1].lower()

    if extension == ".pdf":
        loader = PyPDFLoader(latest_file)

    elif extension == ".docx":
        loader = Docx2txtLoader(latest_file)
    elif extension == ".doc":

        # Start Microsoft Word
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False

        # Open the .doc file
        doc = word.Documents.Open(os.path.abspath(latest_file))

        # Create PDF path
        pdf_path = os.path.splitext(latest_file)[0] + ".pdf"

        # Save as PDF
        doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)

        # Close Word
        doc.Close()
        word.Quit()

        # Load the converted PDF
        loader = PyPDFLoader(pdf_path)

    else:
        raise ValueError("Unsupported file type")

    document = loader.load()
    id_list = []
    for i in range(len(document)):
        a = f"id{i+1}"
        id_list.append(a)
    vectorstore.add_documents(documents=document, ids=id_list)

    userprompt= user_prompt
    context = vectorstore.similarity_search(userprompt, k=1)
    prompt = f'''You are an ai asisstant.
    you are provided the context and prompt from user and you are required 
     to answer the user prompt only from given context using following:
     Prompt: {userprompt}
     context: {context}

     1. answer should be concise
     2. answer should be in 150-200 words
     3. use bullet points and headings
     
     if prompt does not match any context then you can match keywords between prompt and 
     document, then you can give answer from your side. but if keyword does not appear in your context or 
     document then you can simply tell user that it is out of context.
       '''
    query_res = textmodel.invoke(prompt)

    return jsonify({
        "reply": query_res.content
    })
    


if __name__ == "__main__":
    app.run(debug=True, port=4000)
    