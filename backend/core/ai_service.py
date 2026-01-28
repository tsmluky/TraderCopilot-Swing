from __future__ import annotations
import os
import requests
from abc import ABC, abstractmethod
from typing import List, Dict


# === ABSTRACTION LAYER ===


class AIProvider(ABC):
    """Interfaz abstracta para proveedores de IA."""

    @abstractmethod
    def chat(
        self, messages: List[Dict[str, str]], system_instruction: str = None
    ) -> str:
        """
        Genera una respuesta de chat.

        Args:
            messages: Lista de mensajes [{"role": "user", "content": "..."}]
            system_instruction: Instrucción opcional del sistema.
        """
        pass

    @abstractmethod
    def generate_analysis(self, prompt: str, system_instruction: str = None) -> str:
        """
        Genera un análisis técnico (one-shot).
        """
        pass


# === DEEPSEEK IMPLEMENTATION (Legacy/Cost-Effective) ===


class DeepSeekProvider(AIProvider):
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.api_url = os.getenv(
            "DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions"
        )
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    def chat(
        self, messages: List[Dict[str, str]], system_instruction: str = None
    ) -> str:
        if not self.api_key:
            return "Error: DEEPSEEK_API_KEY no configurada."

        # Inyectar system message si existe
        full_messages = []
        if system_instruction:
            full_messages.append({"role": "system", "content": system_instruction})

        full_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("DEEPSEEK_MAX_TOKENS", "4000")),
        }

        # [SPEED INTENT] Enable JSON Mode if requested in system instruction
        if system_instruction and "json" in system_instruction.lower():
            payload["response_format"] = {"type": "json_object"}

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            resp = requests.post(
                self.api_url, json=payload, headers=headers, timeout=120
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"DeepSeek Error: {resp.status_code} - {resp.text[:100]}"
        except Exception as e:
            return f"DeepSeek Connection Error: {str(e)}"

    def generate_analysis(self, prompt: str, system_instruction: str = None) -> str:
        # Reutilizamos la lógica de chat para one-shot
        return self.chat([{"role": "user", "content": prompt}], system_instruction)


# === GEMINI IMPLEMENTATION (REST Wrapper) ===

from core.llm_client_gemini import call_llm  # noqa: E402

class GeminiProvider(AIProvider):
    def __init__(self):
        # Validation
        if not os.getenv("GEMINI_API_KEY"):
            print("[AI] ⚠️ GEMINI_API_KEY missing. Functionality will fail if called.")

    def chat(
        self, messages: List[Dict[str, str]], system_instruction: str = None
    ) -> str:
        # Determine Mode (Heuristic or Default)
        # For general chat (Advisor), we use 'advisor' mode
        mode = "advisor"
        
        # Inject system instruction into messages if provided, 
        # BUT call_llm handles it via specific 'system' role or separate arg?
        # wrapper expects messages list. If we pass system_instruction separately, 
        # we should format it as a system message.
        
        msgs_payload = []
        if system_instruction:
            msgs_payload.append({"role": "system", "content": system_instruction})
        
        msgs_payload.extend(messages)
        
        try:
            return call_llm(mode, msgs_payload)
        except Exception as e:
            return f"Gemini Error: {str(e)}"

    def generate_analysis(self, prompt: str, system_instruction: str = None) -> str:
        # For Heavy Analysis (PRO), we use 'pro' mode
        mode = "pro"
        
        msgs_payload = []
        if system_instruction:
            msgs_payload.append({"role": "system", "content": system_instruction})
            
        msgs_payload.append({"role": "user", "content": prompt})
        
        try:
            return call_llm(mode, msgs_payload, temperature=0.4) # Lower temp for analysis
        except Exception as e:
            # Fallback handled by wrapper retries, but if it fails here:
            raise RuntimeError(f"Gemini Analysis Failed: {str(e)}")


# === FACTORY ===


def get_ai_service() -> AIProvider:
    """
    Retorna el proveedor configurado.
    Default: Gemini (Primary).
    """
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    
    if provider == "deepseek":
        return DeepSeekProvider()
    
    # Default to Gemini
    return GeminiProvider()

