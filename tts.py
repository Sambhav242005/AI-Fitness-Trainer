import pyttsx3
import threading

class TextToSpeech:
    def __init__(self):
        self.engine = None
        # Initialize in a way that doesn't conflict with threads if possible
        # pyttsx3 init might need to happen on the main thread or be carefully managed
        try:
            self.engine = pyttsx3.init()
        except Exception as e:
            print(f"TTS Init Error: {e}")

    def speak(self, text):
        """Speaks the text in a separate thread to avoid blocking."""
        if not text:
            return
        
        # Create a new thread for speech
        t = threading.Thread(target=self._speak_thread, args=(text,))
        t.start()

    def _speak_thread(self, text):
        try:
            # Re-initializing inside the thread is safer for some engines
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")

# Global instance
tts = TextToSpeech()

def speak(text):
    tts.speak(text)
