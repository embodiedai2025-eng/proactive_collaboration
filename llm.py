import base64
import concurrent.futures
import os
from io import BytesIO
from typing import Any, List

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_random_exponential

load_dotenv()

# Environment configuration
USE_QWEN_API = os.getenv("USE_Qwen_API", "False")
MODEL = os.getenv("MODEL", "gpt-4o")
ENABLE_THINKING = os.getenv("ENABLE_THINKING", "False")

if USE_QWEN_API.lower() == "true":
    OPENAI_API_KEY = os.getenv("QWEN_KEY")
    BASE_URL = os.getenv("BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
else:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    BASE_URL = os.getenv("BASE_URL", "https://api.openai.com/v1/")

print("Using model:", MODEL)
print("Using base URL:", BASE_URL)
print()

client = OpenAI(api_key=OPENAI_API_KEY, base_url=BASE_URL)


def _str_to_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding


def encode_image(file_path: str, img_res: int = 1080) -> str:
    """
    Encodes an image file to a base64 string with specified resolution.

    Args:
        file_path (str): The path to the image file.
        img_res (int): Desired width resolution for the image, defaults to 1080.

    Returns:
        str: Base64 encoded string of the image.
    """
    image = Image.open(file_path)
    width, height = image.size
    image = image.resize((img_res, int(img_res * height / width)), Image.LANCZOS)

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"


def get_image_chat_prompt(prompt: str, image_path: Any) -> List[dict]:
    """
    Constructs a prompt with text and image(s) for the chat API.

    Args:
        prompt (str): The text prompt for the chat.
        image_path (Any): Path(s) to image(s). Can be a single path or a list of paths.

    Returns:
        list[dict]: A list containing the structured prompt content.
    """
    detail = "auto"
    content = [{"type": "text", "text": prompt}]

    if isinstance(image_path, list):
        for img in image_path:
            img_str = encode_image(img)
            content.append(
                {"type": "image_url", "image_url": {"url": img_str, "detail": detail}}
            )
    else:
        img_str = encode_image(image_path)
        content.append(
            {"type": "image_url", "image_url": {"url": img_str, "detail": detail}}
        )

    return content


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(5))
def chat_completion(messages: list, temperature: float = 0.7) -> dict:
    """
    Sends a completion request to the OpenAI chat API with retry logic.

    Args:
        messages (list): The messages to send to the chat API.
        temperature (float): The temperature for response variation, defaults to 0.7.

    Returns:
        dict: The response content with token usage details, or None if failed.
    """
    try:
        is_qwen_model = "qwen" in MODEL.lower()
        enable_thinking = _str_to_bool(ENABLE_THINKING)

        
        request_kwargs = {
            "model": MODEL,
            "messages": messages,
            "temperature": temperature,
        }
        if is_qwen_model:
            request_kwargs["extra_body"] = {"enable_thinking": enable_thinking}
        response = client.chat.completions.create(**request_kwargs)
        
        return {
            "response": response.choices[0].message.content,
            "tokens_in": response.usage.prompt_tokens,
            "tokens_out": response.usage.completion_tokens,
            "tokens_total": response.usage.prompt_tokens
            + response.usage.completion_tokens,
        }

    except Exception as e:
        print("Error in chat completion:", e)
        raise e



def completion(prompt: str, temperature: float = 0.7):
    """
    Generates a completion for the given prompt using a chat-based AI model.

    Returns:
        response[dict]: keys=["response", "tokens_in", "tokens_out", "tokens_total"]
    """
    # {"role": "system", "content": "The following is a conversation with some AI Agent."}
    messages = [{"role": "user", "content": prompt}]
    response = chat_completion(messages, temperature)
    return response


def threaded_completion(prompts: list[str], temperature: float = 0.7) -> list[dict]:
    """
    Executes multiple completion requests in parallel using threads.

    Args:
        prompts (list[str]): A list of prompts to generate completions for.
        temperature (float): The temperature for response variation, defaults to 0.7.

    Returns:
        list[dict]: A list of responses for each prompt in `prompts`.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(completion, prompt, temperature): i
            for i, prompt in enumerate(prompts)
        }
        results = []
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
        return results


def threaded_chat_completion(
    messages: list[list], temperature: float = 0.7
) -> list[dict]:
    """
    Executes multiple chat completion requests in parallel using threads.

    Args:
        messages (list[list]): A list of message lists, each representing a single conversation.
        temperature (float): The temperature for response variation, defaults to 0.7.

    Returns:
        list[dict]: A list of responses for each message list in `messages`.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(chat_completion, message, temperature): i
            for i, message in enumerate(messages)
        }
        results = []
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
        return results


if __name__ == "__main__":
    test_messages = [{"role": "user", "content": "hello"}]
    response = chat_completion(test_messages)
    print(response)
    # from sklearn.metrics.pairwise import cosine_similarity
    # livingroom = get_embedding("living room")
    # bedroom = get_embedding("bedroom")
    # kitchen = get_embedding("kitchen")
    # bathroom = get_embedding("bathroom")
    pass
