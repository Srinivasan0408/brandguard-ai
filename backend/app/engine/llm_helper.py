import os
import json
from typing import List, Dict, Any, Optional
import httpx
from ..config import settings

class LLMHelper:
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY

    def is_available(self) -> bool:
        return bool(self.openai_key or self.gemini_key)

    async def analyze_tone_and_refine(self, content: str, brand: Dict[str, Any], existing_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Invokes LLM if configured; otherwise returns empty list (graceful fallback).
        """
        if not self.is_available():
            return []

        # If Gemini key is set:
        if self.gemini_key:
            return await self._call_gemini(content, brand, existing_findings)
        # If OpenAI key is set:
        elif self.openai_key:
            return await self._call_openai(content, brand, existing_findings)

        return []

    async def _call_gemini(self, content: str, brand: Dict[str, Any], existing_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
            prompt = (
                f"You are BrandGuard AI, a brand governance reviewer for {brand.get('name', 'NovaTech')}.\n"
                f"Preferred tone: {brand.get('preferred_tone')}\n"
                f"Content to review:\n{content}\n\n"
                f"Analyze this content for tone alignment and subtle brand risk. Respond with a JSON array of findings:\n"
                f"[{{\"category\": \"tone\", \"severity\": \"low\"|\"medium\"|\"high\", \"title\": \"...\", \"excerpt\": \"...\", \"explanation\": \"...\", \"recommended_correction\": \"...\"}}]\n"
                f"Only return valid JSON without code blocks if possible."
            )
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json={
                    "contents": [{"parts": [{"text": prompt}]}]
                })
                if res.status_code == 200:
                    data = res.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if text.startswith("```json"):
                        text = text[7:-3].strip()
                    elif text.startswith("```"):
                        text = text[3:-3].strip()
                    parsed = json.loads(text)
                    for item in parsed:
                        item["detection_method"] = "llm_assisted"
                        item["confidence"] = "medium"
                        item["applicable_guideline"] = "AI Tone & Brand Voice Evaluation"
                        item["status"] = "open"
                    return parsed
        except Exception:
            return []
        return []

    async def _call_openai(self, content: str, brand: Dict[str, Any], existing_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
            prompt = (
                f"You are BrandGuard AI, an enterprise governance reviewer for {brand.get('name', 'NovaTech')}.\n"
                f"Target tone: {brand.get('preferred_tone')}\n"
                f"Review content:\n{content}\n\n"
                f"Output a JSON array of tone or style findings: [{{'category': 'tone', 'severity': 'medium', 'title': '...', 'excerpt': '...', 'explanation': '...', 'recommended_correction': '...'}}]"
            )
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=headers, json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                })
                if res.status_code == 200:
                    data = res.json()
                    parsed = json.loads(data["choices"][0]["message"]["content"])
                    findings = parsed.get("findings", []) if isinstance(parsed, dict) else parsed
                    for item in findings:
                        item["detection_method"] = "llm_assisted"
                        item["confidence"] = "medium"
                        item["applicable_guideline"] = "AI Brand Voice & Context Evaluation"
                        item["status"] = "open"
                    return findings
        except Exception:
            return []
        return []

llm_helper = LLMHelper()
