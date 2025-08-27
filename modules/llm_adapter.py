
from dotenv import load_dotenv
from openai import OpenAI
from modules.settings import load_settings
import asyncio
from openai import DefaultAioHttpClient
from openai import AsyncOpenAI


def chat_llm(messages):
    load_dotenv()
    settings = load_settings()
    llm_service = settings.get("llm_service", None)
    if llm_service == "openai":
        return chat_openai(messages)
    else:
        raise ValueError(f"Unknown LLM service: {llm_service}")

def batch_chat_llm(messages_list):
    load_dotenv()
    settings = load_settings()
    llm_service = settings.get("llm_service", None)
    if llm_service == "openai":
        return batch_chat_openai(messages_list)
    else:
        raise ValueError(f"Unknown LLM service: {llm_service}")


async def chat_openai_async(messages):
    settings = load_settings().get("openai", {})
    client_args = settings.get("client", {})
    completions_arg = settings.get("completions", {})
    async with AsyncOpenAI(
        **client_args
    ) as client:
        completion = await client.chat.completions.create(
            messages=messages,
            **completions_arg
        )

        content = completion.choices[0].message.content
        return content


def chat_openai(messages):
    return asyncio.run(chat_openai_async(messages))

async def gather(routines):
    return await asyncio.gather(*routines)

def batch_chat_openai(messages_list):
    routines = []
    for messages in messages_list:
        routines.append(chat_openai_async(messages))
    return asyncio.run(gather(routines))
