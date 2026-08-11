import os
import time
import shutil
import logging
import subprocess
import httpx
from typing import Optional
from backend.app.config.settings import settings

logger = logging.getLogger(__name__)

class OllamaLLMService:
    _instance: Optional["OllamaLLMService"] = None

    def __init__(
        self,
        base_url: str = settings.OLLAMA_BASE_URL,
        model_name: str = settings.OLLAMA_MODEL_NAME
    ):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self._service_ready: bool = False
        self._model_ready: bool = False

    def _try_start_ollama_daemon(self) -> bool:
        """Attempts to auto-start the local Ollama server process if it is not running."""
        ollama_bin = shutil.which("ollama")
        if not ollama_bin:
            win_path = os.path.expanduser("~") + r"\AppData\Local\Programs\Ollama\ollama.exe"
            if os.path.exists(win_path):
                ollama_bin = win_path

        if ollama_bin:
            try:
                logger.info("Attempting to auto-start local Ollama server daemon...")
                creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                subprocess.Popen(
                    [ollama_bin, "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=creationflags
                )
                # Give daemon up to 5 seconds to respond
                urls_to_check = [self.base_url, "http://127.0.0.1:11434", "http://localhost:11434"]
                for _ in range(10):
                    time.sleep(0.5)
                    for url in urls_to_check:
                        try:
                            resp = httpx.get(f"{url}/api/tags", timeout=2.0)
                            if resp.status_code == 200:
                                self.base_url = url
                                self._service_ready = True
                                logger.info(f"Ollama server started successfully on {self.base_url}.")
                                return True
                        except Exception:
                            continue
            except Exception as e:
                logger.warning(f"Auto-start Ollama server attempt failed: {e}")
        return False

    def is_service_available(self, force_check: bool = False) -> bool:
        """Checks if local Ollama daemon is reachable on base_url, 127.0.0.1, or localhost fallbacks."""
        if self._service_ready and not force_check:
            return True

        urls_to_try = [self.base_url]
        if "localhost" in self.base_url:
            urls_to_try.append(self.base_url.replace("localhost", "127.0.0.1"))
        elif "127.0.0.1" in self.base_url:
            urls_to_try.append(self.base_url.replace("127.0.0.1", "localhost"))
        
        for url in urls_to_try:
            try:
                resp = httpx.get(f"{url}/api/tags", timeout=3.0)
                if resp.status_code == 200:
                    self.base_url = url  # Lock on working URL
                    self._service_ready = True
                    return True
            except Exception:
                continue

        # If not reachable, attempt auto-starting daemon
        if self._try_start_ollama_daemon():
            return True

        self._service_ready = False
        return False

    def is_model_available(self, force_check: bool = False) -> bool:
        """Checks if configured model is available in Ollama."""
        if self._model_ready and not force_check:
            return True

        if not self.is_service_available(force_check=force_check):
            return False
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=3.0)
            if resp.status_code == 200:
                models_data = resp.json().get("models", [])
                target = self.model_name.lower()
                for m in models_data:
                    m_name = m.get("name", "").lower()
                    m_model = m.get("model", "").lower()
                    if (target == m_name or target == m_model or 
                        m_name.startswith(f"{target}:") or target.startswith(m_name.split(":")[0])):
                        self._model_ready = True
                        return True
        except Exception as e:
            logger.error(f"Error checking Ollama model availability: {e}")
            
        self._model_ready = False
        return False

    def generate(self, prompt: str) -> str:
        """Generates response via local Ollama LLM using retrieved RAG context."""
        if not self.is_service_available():
            logger.warning(f"Ollama service at {self.base_url} is unreachable.")
            return (
                f"⚠️ **Ollama Service Unavailable**: Could not connect to local Ollama server at `{self.base_url}`. "
                f"Please ensure Ollama is installed and running (`ollama serve`), then pull the model using:\n"
                f"`ollama pull {self.model_name}`"
            )

        if not self.is_model_available():
            logger.warning(f"Ollama model {self.model_name} is not available on {self.base_url}.")
            return (
                f"⚠️ **Ollama Model Missing**: Service is running at `{self.base_url}`, but configured model `{self.model_name}` is not pulled.\n"
                f"Please run the following command to download the model:\n"
                f"`ollama pull {self.model_name}`"
            )

        try:
            # Direct HTTP API endpoint call with speed-optimized parameters
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 250,   # Compact generation limit for sub-15s CPU response times
                    "num_ctx": 1024,       # Minimal context window overhead on CPU
                    "top_p": 0.9
                }

            }
            resp = httpx.post(f"{self.base_url}/api/generate", json=payload, timeout=90.0)
            if resp.status_code == 200:
                answer = resp.json().get("response", "").strip()
                if answer:
                    return answer

            # Fallback via LangChain ChatOllama if HTTP post did not return answer
            try:
                try:
                    from langchain_ollama import ChatOllama
                except ImportError:
                    from langchain_community.chat_models import ChatOllama

                llm = ChatOllama(
                    base_url=self.base_url,
                    model=self.model_name,
                    temperature=0.1
                )
                response = llm.invoke(prompt)
                return response.content
            except Exception as inner_e:
                logger.error(f"LangChain ChatOllama fallback error: {inner_e}")
                return f"Error from Ollama API ({resp.status_code}): {resp.text}"

        except Exception as e:
            # Reset readiness flags on failure so connection will re-validate on next call
            self._service_ready = False
            self._model_ready = False
            logger.error(f"Ollama generation error: {e}")
            return f"An error occurred while communicating with local Ollama LLM: {str(e)}"


def get_ollama_service() -> OllamaLLMService:
    if OllamaLLMService._instance is None:
        OllamaLLMService._instance = OllamaLLMService()
    return OllamaLLMService._instance

