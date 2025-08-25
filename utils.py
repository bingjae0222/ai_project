import os
import time
import base64
import urllib.request
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
import google.generativeai as genai
from PyPDF2 import PdfReader
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from PIL import Image
import pytesseract   # OCR

# -----------------------------
# 환경 변수
# -----------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# -----------------------------
# OCR 함수 (이미지 → 텍스트)
# -----------------------------
def extract_text_from_image(image_file):
    """업로드한 이미지(JPG, PNG)에서 텍스트 추출"""
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image, lang="eng+kor")  # 한국어+영어 동시 지원
    return text

# -----------------------------
# OpenAI / Gemini 모델
# -----------------------------
def getOpenAI():
    return ChatOpenAI(temperature=0, model_name="gpt-4o")

def getGenAI():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        max_output_tokens=200,
        google_api_key=GOOGLE_API_KEY
    )

def openAiModel():
    return OpenAI(api_key=OPENAI_API_KEY)

def makeMsg(system, user):
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

def openAiModelArg(model, msgs):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=msgs
    )
    return response.choices[0].message.content

def geminiModel():
    genai.configure(api_key=GOOGLE_API_KEY)
    return genai.GenerativeModel("gemini-2.0-flash")

def geminiTxt(txt):
    model = geminiModel()
    response = model.generate_content(txt)
    return response.text

# -----------------------------
# 파일 저장 유틸
# -----------------------------
def save_capturefile(directory, picture, name, st):
    if picture is not None:
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, name), "wb") as file:
            file.write(picture.getvalue())
        st.success(f"저장 완료: {directory}에 {name} 저장되었습니다.")

def save_uploadedfile(directory, file, st):
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(os.path.join(directory, file.name), "wb") as f:
        f.write(file.getbuffer())
    st.success(f"저장 완료: {directory}에 {file.name} 저장되었습니다.")

def progressBar(txt):
    progress_text = txt
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.08)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)
    return my_bar

# -----------------------------
# 오디오 (TTS)
# -----------------------------
def makeAudio(text, name):
    if not os.path.exists("audio"):
        os.makedirs("audio")
    client = openAiModel()
    response = client.audio.speech.create(
        model="tts-1",
        input=text,
        voice="alloy",
        response_format="mp3",
        speed=1.1,
    )
    response.stream_to_file("audio/" + name)

# -----------------------------
# 이미지 생성
# -----------------------------
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def makeImage(prompt, name):
    openModel = openAiModel()
    response = openModel.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    imgName = "img/" + name
    urllib.request.urlretrieve(image_url, imgName)

def makeImages(prompt, name, num):
    openModel = openAiModel()
    response = openModel.images.generate(
        model="dall-e-2",
        prompt=prompt,
        size="1024x1024",
        n=num,
    )
    for n, data in enumerate(response.data):
        imgname = f"img/{name.split('.')[0]}_{n}.png"
        urllib.request.urlretrieve(data.url, imgname)

def cloneImage(imgName, num):
    openModel = openAiModel()
    response = openModel.images.create_variation(
        model="dall-e-2",
        image=open("img/" + imgName, "rb"),
        n=num,
        size="1024x1024"
    )
    for n, data in enumerate(response.data):
        name = f"img/{imgName.split('.')[0]}_clone_{n}.png"
        urllib.request.urlretrieve(data.url, name)

# -----------------------------
# OpenAI Embeddings / 벡터DB
# -----------------------------
def getOpenAIEmbeddings():
    return OpenAIEmbeddings(model="text-embedding-ada-002", api_key=OPENAI_API_KEY)

def process_text(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    embeddings = getOpenAIEmbeddings()
    documents = FAISS.from_texts(chunks, embeddings)
    return documents

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        separators="\\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)

def get_vectorstore(text_chunks):
    embeddings = getOpenAIEmbeddings()
    return FAISS.from_texts(texts=text_chunks, embedding=embeddings)

def split_docs(documents, chunk_size=1000, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)

# -----------------------------
# PDF 처리
# -----------------------------
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# -----------------------------
# 대화 체인
# -----------------------------
def get_conversation_chain(vectorstore):
    memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=getOpenAI(),
        retriever=vectorstore.as_retriever(),
        get_chat_history=lambda h: h,
        memory=memory
    )
    return conversation_chain
