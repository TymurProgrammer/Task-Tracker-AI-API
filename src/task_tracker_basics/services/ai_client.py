from google import genai
from google.genai import types
from google.genai.errors import APIError

class AIServiceError(Exception):
    pass


class GeminiClient:
    def __init__(self, api_key: str, model_name: str):
        self.model_name = model_name
        self._client = genai.Client(api_key=api_key).aio

    async def summarize(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        
        prompt = (
            "Зроби короткий та чіткий підсумок наступного завдання або його опису. "
            "Виділи основну суть у 1-3 реченнях українською мовою:\n\n"
            f"{text}"
        )

        try:
            response = await self._client.models.generate_content(
                model = self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3)
            )
        except APIError as e:
            raise AIServiceError(f"AI-provider raised exception + {e.code}") from e
            
        if response.text:
            return response.text.strip()
        raise AIServiceError("Problems with response")


