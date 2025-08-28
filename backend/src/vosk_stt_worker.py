
import vosk
import sounddevice as sd
import json
import queue
import os
import logging

from src.lua_core.lua_free_ai_engine import LuaFreeAIEngine

log = logging.getLogger(__name__)

class VoskSTTWorker:
    def __init__(self, model_path, samplerate=16000):
        if not os.path.exists(model_path):
            raise Exception(f"Modelo Vosk não encontrado em: {model_path}")
        
        self.model = vosk.Model(model_path)
        self.samplerate = samplerate
        self.q = queue.Queue()
        self.lua_free_ai = LuaFreeAIEngine() # Instancia a engine de IA
        self.device = None

    def callback(self, indata, frames, time, status):
        """Callback para o stream de áudio."""
        if status:
            log.warning(status)
        self.q.put(bytes(indata))

    def start_listening(self):
        """Inicia a escuta e transcrição de áudio."""
        log.info("Iniciando escuta de áudio...")
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, 
                               device=self.device, dtype=\'int16\', 
                               channels=1, callback=self.callback) as stream:
            
            log.info(f"Dispositivo de áudio: {stream.device}")
            log.info(f"Sample rate: {stream.samplerate}")

            rec = vosk.KaldiRecognizer(self.model, self.samplerate)
            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if text:
                        log.info(f"Texto Transcrito: {text}")
                        # Envia o texto transcrito para a LuaFreeAIEngine
                        response = self.lua_free_ai.ollama_chat(text)
                        log.info(f"Resposta da IA: {response}")
                else:
                    partial_result = json.loads(rec.PartialResult())
                    # log.debug(f"Partial: {partial_result.get(\"partial\", \"\")}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    MODEL_PATH = "/home/ubuntu/projeto_joalheria/backend/resources/vosk/pt/vosk-model-small-pt-0.3"
    try:
        worker = VoskSTTWorker(MODEL_PATH)
        worker.start_listening()
    except Exception as e:
        log.error(f"Erro ao iniciar o worker STT: {e}")



