import os
from typing import Union

from asyncpg import Connection
from crud import get_session, get_transcripcion
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)
from pydantic import BaseModel

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY") or ""
API_BASE = os.getenv("OPENAI_API_BASE") or ""
API_TYPE = os.getenv("OPENAI_API_TYPE") or ""
API_VERSION = os.getenv("OPENAI_API_VERSION") or ""

DB_NAME = os.getenv("DB_NAME") or ""
DB_USER = "postgres"
DB_PASSWORD = os.getenv("DB_PASSWORD") or ""

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


class Question(BaseModel):
    query: str


@app.get("/summary/palabras/{id}")
async def palabras_clave(id: str, conn: Connection = Depends(get_session)):
    transcripcion, descripcion = await get_transcripcion(id, conn)
    # Load the summary.txt

    model = AzureChatOpenAI(
        openai_api_base=API_BASE,
        openai_api_version=API_VERSION,
        deployment_name="capibarai_chat35_16k",
        openai_api_key=API_KEY,
        openai_api_type="azure",
    )

    system_message_prompt = SystemMessagePromptTemplate.from_template(
        f"Este es un video con los siguientes datos. Descripcion: {descripcion} Contenido: {transcripcion}"
    )

    human_template = "{input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=model, prompt=chat_prompt)
    response = chain.run(
        "Dame un listado de palabras clave del video separadas por espacio y entre comillas"
    )
    return {"answer": response}


@app.post("/summary/{id}")
async def ask_question(
    question: Question, id: str, conn: Connection = Depends(get_session)
):
    transcripcion, descripcion = await get_transcripcion(id, conn)
    # Load the summary.txt

    model = AzureChatOpenAI(
        openai_api_base=API_BASE,
        openai_api_version=API_VERSION,
        deployment_name="capibarai_chat35_16k",
        openai_api_key=API_KEY,
        openai_api_type="azure",
    )

    system_message_prompt = SystemMessagePromptTemplate.from_template(
        f"Este es un video con los siguientes datos. Descripcion: {descripcion} Contenido: {transcripcion}"
    )

    human_template = "{input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=model, prompt=chat_prompt)
    response = chain.run(question.query)
    return {"answer": response}