import json
import re
import httpx
from app.core.config import settings
from app.llm.mock import MockLLM
from app.schemas.dto import ExtractionPayload

SYSTEM_PROMPT = """You are NEXORA AI, a strict conversational business-data extraction engine.
Return JSON only. Never add markdown. Use this exact shape:
{
  "customer": {"name":{"value":null,"confidence":0,"source_span":""},"phone":{"value":null,"confidence":0,"source_span":""},"email":{"value":null,"confidence":0,"source_span":""},"address":{"value":null,"confidence":0,"source_span":""},"city":{"value":null,"confidence":0,"source_span":""},"pincode":{"value":null,"confidence":0,"source_span":""},"gstin":{"value":null,"confidence":0,"source_span":""}},
  "intent":"inquiry|order|payment|follow-up|complaint|cancellation|other",
  "products":[{"name":"","sku_match":null,"quantity":1,"unit":"unit","price":null,"confidence":0,"source_span":""}],
  "delivery_date":null,"delivery_mode":null,
  "payment":{"status":"unknown","amount":null,"method":null,"reference":null,"confidence":0,"source_span":""},
  "follow_up":{"date_time":null,"reason":null,"confidence":0,"source_span":""},
  "sentiment":"positive|neutral|negative","language":"","summary":"","confidence":0
}
Resolve relative dates using today's date supplied in the user message. Keep confidence between 0 and 1. Do not invent missing fields."""


def _clean_json(text: str):
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*|\s*```$', '', text, flags=re.I | re.S).strip()
    start, end = text.find('{'), text.rfind('}')
    return text[start:end + 1] if start >= 0 and end > start else text


def _coerce(payload: dict) -> ExtractionPayload:
    return ExtractionPayload.model_validate(payload)


class OpenAIProvider(MockLLM):
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model

    def extract(self, text: str) -> ExtractionPayload:
        if not self.api_key:
            return super().extract(text)
        prompt = f"Today's date is {__import__('datetime').date.today().isoformat()}. Extract the following customer conversation:\n\n{text}"
        last = None
        for _ in range(3):
            try:
                r = httpx.post('https://api.openai.com/v1/chat/completions', headers={'Authorization': f'Bearer {self.api_key}'}, json={'model': self.model, 'temperature': 0, 'response_format': {'type': 'json_object'}, 'messages': [{'role': 'system', 'content': SYSTEM_PROMPT}, {'role': 'user', 'content': prompt}]}, timeout=30)
                r.raise_for_status()
                content = r.json()['choices'][0]['message']['content']
                return _coerce(json.loads(_clean_json(content)))
            except Exception as exc:
                last = exc
        return super().extract(text)


class AnthropicProvider(MockLLM):
    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.model = settings.anthropic_model

    def extract(self, text: str) -> ExtractionPayload:
        if not self.api_key:
            return super().extract(text)
        prompt = f"Today's date is {__import__('datetime').date.today().isoformat()}. Extract the following customer conversation and return strict JSON only:\n\n{text}"
        for _ in range(3):
            try:
                r = httpx.post('https://api.anthropic.com/v1/messages', headers={'x-api-key': self.api_key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'}, json={'model': self.model, 'max_tokens': 1800, 'temperature': 0, 'system': SYSTEM_PROMPT, 'messages': [{'role': 'user', 'content': prompt}]}, timeout=30)
                r.raise_for_status()
                content = ''.join(x.get('text', '') for x in r.json().get('content', []) if x.get('type') == 'text')
                return _coerce(json.loads(_clean_json(content)))
            except Exception:
                continue
        return super().extract(text)


def get_llm():
    return {'mock': MockLLM, 'openai': OpenAIProvider, 'anthropic': AnthropicProvider}.get(settings.llm_provider, MockLLM)()
