import requests
import logging
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class TelegramBot:
    def __init__(self):
        """Inicializa as credenciais do bot com as variáveis de ambiente."""
        self.token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        
        if not self.token or not self.chat_id:
            logging.error("ERRO CRÍTICO: Credenciais do Telegram ausentes no ambiente.")

    def enviar_mensagem(self, texto: str) -> bool:
        """
        Envia a mensagem gerada para o chat configurado.
        Utiliza o método sendMessage da API oficial do Telegram.
        """
        if not self.token or not self.chat_id:
            raise ValueError("Token ou Chat ID do Telegram não configurados.")

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        
        payload = {
            "chat_id": self.chat_id,
            "text": texto,
            "parse_mode": "HTML" # Permite negritos e formatações básicas caso a IA gere
        }

        try:
            logging.info("Disparando requisição HTTP POST para a API do Telegram...")
            response = requests.post(url, json=payload, timeout=10)
            
            # Levanta exceção se o HTTP Status Code for erro (4xx ou 5xx)
            response.raise_for_status() 
            
            return True
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Falha na comunicação com o Telegram: {str(e)}")
            if response is not None:
                logging.error(f"Retorno da API: {response.text}")
            raise e

# Exporta uma instância Singleton (o objeto 'bot' que o main.py está procurando)
bot = TelegramBot()
