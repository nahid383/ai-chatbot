"""
Thin wrapper around the Gemini API. Keeping this isolated means that
switching to OpenAI or a local Llama model later (per your tech stack
plan) only requires changing THIS file - nothing else in the app
needs to know which provider is behind it.
"""

from google import genai
from google.genai import types

from app.config import settings

_client = genai.Client(api_key=settings.GEMINI_API_KEY)

SYSTEM_INSTRUCTIONS = """You are the SWE23 AI Assistant, a helpful assistant \
for SUST Software Engineering 2023 batch students.

Rules you must always follow:
1. Answer the student's question using ONLY the information in the CONTEXT \
section below. Do not use outside knowledge, even if you know the answer.
2. If the CONTEXT does not contain enough information to answer confidently, \
respond with EXACTLY this phrase and nothing else: \
"I don't have that information yet - I've flagged this for the CR to review."
3. Never guess or make up dates, room numbers, or deadlines.
4. Keep answers concise and directly useful to a student.
5. After your answer, on a new line, list sources you used in the format: \
Sources: <filename1>, <filename2>. If you used no sources, omit this line.
"""


def generate_chat_reply(
    context_block: str,
    history_block: str,
    user_question: str,
) -> str:
    """
    Builds the structured RAG prompt (Lesson 5: system instructions ->
    context -> history -> question) and calls Gemini with low temperature,
    since this is a factual retrieval task, not creative writing.
    """
    prompt = f"""{SYSTEM_INSTRUCTIONS}

CONTEXT:
{context_block if context_block else "(no relevant documents found)"}

CONVERSATION HISTORY:
{history_block if history_block else "(no prior messages)"}

STUDENT QUESTION:
{user_question}
"""

    response = _client.models.generate_content(
        model=settings.GEMINI_CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.2),
    )
    return response.text


def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """
    Converts text into an embedding vector (Lesson 2).

    task_type differs for documents vs queries: Gemini's embedding model
    optimizes the vector slightly differently depending on whether the
    text being embedded is something to be SEARCHED (a document chunk)
    or something DOING the searching (a user's question). Using the
    right task_type measurably improves retrieval quality.
    """
    result = _client.models.embed_content(
        model=f"models/{settings.GEMINI_EMBEDDING_MODEL}",
        contents=text,
        config=types.EmbedContentConfig(task_type=task_type),
    )
    return result.embeddings[0].values
