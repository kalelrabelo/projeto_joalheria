import os, requests, logging
log = logging.getLogger(__name__)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")

class LuaFreeAIEngine:
    def __init__(self, model="mistral"):
        self.model = os.environ.get("OLLAMA_MODEL", model)
        try:
            import spacy
            try:
                self.nlp = spacy.load("pt_core_news_sm")
            except Exception:
                log.error("Modelo SpaCy pt não encontrado. Rode: python -m spacy download pt_core_news_sm")
                self.nlp = None
        except Exception:
            self.nlp = None

    def classify_intent(self, text: str) -> str:
        """Classificador simples, sempre retorna \'generic\' se não houver modelo treinado."""
        return "generic"

    def extract_entities(self, text: str) -> dict:
        ents = []
        if self.nlp:
            doc = self.nlp(text)
            ents = [{"text": e.text, "label": e.label_} for e in doc.ents]
        return {"entities": ents}

    def ollama_chat(self, prompt: str) -> str:
        try:
            r = requests.post(f"{OLLAMA_URL}/api/chat", json={
                "model": self.model,
                "messages": [{"role":"user","content": prompt}],
                "stream": False
            }, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data.get("message", {}).get("content", "")
        except Exception as e:
            log.error(f"Ollama falhou: {e}")
            return ""


class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def chat(self, model, messages):
        response = requests.post(f"{self.base_url}/api/chat", json={
            "model": model,
            "messages": messages
        })
        return response.json()


