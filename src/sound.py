import os
import logging
import tempfile
from gtts import gTTS
from playsound3 import playsound

logging.getLogger(__name__)


def play(text: str, language='en') -> None:
    """
    Sintetiza o texto em voz e o reproduz utilizando a biblioteca gtts e playsound.

    Args:
        text (str): O texto em inglês a ser sintetizado e reproduzido.
    """

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        filename = temp_file.name

    try:
        tts = gTTS(text=text, lang=language)
        tts.save(filename)

        playsound(filename)

    finally:
        try:
            os.remove(filename)
        except PermissionError as e:
            logging.error(f'Erro ao remover arquivo: {e}')
            pass


if __name__ == '__main__':
    play("This is much simpler with the playsound library.")
