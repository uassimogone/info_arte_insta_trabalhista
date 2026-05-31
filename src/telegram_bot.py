import requests
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class TelegramBot:
    """Gerencia toda a comunicação e entrega dos materiais produzidos via Telegram API."""
    
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def enviar_mensagem(self, texto: str):
        """Envia uma mensagem de texto simples para o canal/chat."""
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": texto, "parse_mode": "Markdown"}
        try:
            r = requests.post(url, json=payload, timeout=15)
            return r.json()
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem de texto no Telegram: {e}")

    def enviar_post(self, imagem_path: str, num_post: int, legenda: str, titulo_hook: str):
        """Envia a imagem gerada seguida imediatamente pela legenda correspondente."""
        url_photo = f"{self.base_url}/sendPhoto"
        
        # 1. Envia o card visual do post
        print(f"📤 Enviando imagem do Post {num_post}/3 para o Telegram...")
        try:
            with open(imagem_path, "rb") as img:
                files = {"photo": img}
                data = {"chat_id": self.chat_id}
                requests.post(url_photo, data=data, files=files, timeout=30)
        except Exception as e:
            print(f"❌ Falha ao enviar imagem do Post {num_post}: {e}")

        # 2. Envia a legenda formatada estruturada
        print(f"✍️ Enviando legenda do Post {num_post}/3...")
        texto_completo = f"📢 *LEGENDA — POST {num_post} DE 3*\n*{titulo_hook}*\n\n---\n{legenda}\n---"
        self.enviar_mensagem(texto_completo)