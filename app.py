from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from sentence_transformers import SentenceTransformer
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import os
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama3-8b-8192")

documents = [
    Document(
        page_content="Dogs are great companions, known for their loyalty and friendliness.",
        metadata={"source": "mammal-pets-doc"},
    ),
    Document(
        page_content="Cats are independent pets that often enjoy their own space.",
        metadata={"source": "mammal-pets-doc"},
    ),
    Document(
        page_content="Goldfish are popular pets for beginners, requiring relatively simple care.",
        metadata={"source": "fish-pets-doc"},
    ),
    Document(
        page_content="Parrots are intelligent birds capable of mimicking human speech.",
        metadata={"source": "bird-pets-doc"},
    ),
    Document(
        page_content="Rabbits are social animals that need plenty of space to hop around.",
        metadata={"source": "mammal-pets-doc"},
    ),
]

model = SentenceTransformer('all-MiniLM-L6-v2')

class CustomEmbeddings:
    def embed_documents(self, texts):
        return model.encode(texts).tolist() 
    def embed_query(self, text):
        return model.encode([text])[0].tolist()



vectorstore = Chroma.from_documents(
    documents,
    embedding=CustomEmbeddings(),
)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 1},
)
# result=retriever.invoke("cat")
# print(result)




message = """
Respond concisely to the question below. If relevant information is available in the context, provide that information without saying that you are responding from the information from the context just give me answer.
If the context does not provide an answer, give a brief, generic response based on your knowledge. Avoid unnecessary elaboration.

Question: {question}

Context:
{context}
"""


prompt = ChatPromptTemplate.from_messages([("human", message)])

rag_chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm

while True:
    user_input=input("Ask: ")
    if user_input in ['exit','quit','stop']:
        break
    response = rag_chain.invoke(user_input)

    print(response.content)