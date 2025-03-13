import pyttsx3
import threading

class SpeechService:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)  # Скорость речи по умолчанию
        self.lock = threading.Lock()
        
    def get_voices(self):
        voices = self.engine.getProperty('voices')
        return [voice.name for voice in voices]
        
    def speech(self, text, voice_name=None, rate=None):
        # Выполняем в отдельном потоке, чтобы не блокировать UI
        thread = threading.Thread(target=self._speech_thread, args=(text, voice_name, rate))
        thread.daemon = True
        thread.start()
    
    def _speech_thread(self, text, voice_name, rate):
        with self.lock:  # Предотвращаем одновременное использование движка
            if voice_name:
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if voice.name == voice_name:
                        self.engine.setProperty('voice', voice.id)
                        break
                        
            if rate is not None:
                self.engine.setProperty('rate', rate)
                
            self.engine.say(text)
            self.engine.runAndWait()