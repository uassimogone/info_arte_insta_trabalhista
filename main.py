import os
import logging
from src.config import SOURCES, PROFILE_USERNAME
from src.gemini_brain import brain
from src.telegram_bot import bot  # Assumindo que a instância do bot se chama 'bot' no seu telegram_bot.py

# Configuração de logs para exibição no GitHub Actions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HISTORICO_FILE = "historico_urls.txt"

def carregar_historico():
    """Lê o arquivo de histórico para evitar duplicidade de conteúdo."""
    if not os.path.exists(HISTORICO_FILE):
        return set()
    with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def salvar_no_historico(url):
    """Salva a URL ou tema processado no arquivo de histórico."""
    with open(HISTORICO_FILE, "a", encoding="utf-8") as f:
        f.write(f"{url}\n")

def executar_pipeline():
    logging.info(f"Iniciando automação de conteúdo para o perfil {PROFILE_USERNAME}")
    
    historico = carregar_historico()
    conteudo_processado = False

    # Iterar pelas camadas de fontes na ordem de preferência estipulada
    for camada_nome, urls in SOURCES.items():
        if conteudo_processado:
            break
            
        # Determinar o peso numérico da camada para o Gemini aplicar as regras de negócio
        camada_id = 1 if "1" in camada_nome else (2 if "2" in camada_nome else 3)
        
        logging.info(f"Verificando fontes da {camada_nome.upper().replace('_', ' ')}...")

        for url in urls:
            if url in historico:
                logging.info(f"Link já processado anteriormente: {url}. Pulando...")
                continue

            logging.info(f"Nova fonte identificada para processamento: {url}")
            
            # Simulação de captura/Injeção de contexto base
            # Em execuções autônomas avançadas, aqui entraria um scraper. 
            # Como base segura, passamos o contexto do tema/url para o cérebro gerar.
            contexto_bruto = f"Gere uma análise estratégica corporativa baseada nas últimas atualizações de: {url}"
            
            # Aciona o motor da IA com a persona patronal e a regra da camada
            resultado = brain.processar_conteudo(contexto_bruto, camada_origem=camada_id)
            
            if resultado.get("status") == "sucesso":
                texto_final = resultado.get("conteudo")
                
                # Despacha o resultado formatado direto para o bot do Telegram
                logging.info("Enviando roteiro gerado para aprovação no Telegram...")
                try:
                    # Tenta enviar via método de mensagem do seu telegram_bot.py
                    # Se o seu método tiver nome diferente (ex: send_message), ajuste esta linha
                    bot.enviar_mensagem(texto_final) 
                    logging.info("Roteiro enviado com sucesso!")
                    
                    # Salva no histórico para nunca repetir a mesma fonte
                    salvar_no_historico(url)
                    conteudo_processado = True
                    break
                except Exception as e:
                    logging.error(f"Falha ao enviar mensagem para o Telegram: {str(e)}")
            else:
                logging.error(f"Erro no processamento do Gemini: {resultado.get('mensagem')}")

    if not conteudo_processado:
        logging.info("Nenhum conteúdo novo encontrado para processar nesta rodada.")

if __name__ == "__main__":
    try:
        executar_pipeline()
    except Exception as e:
        logging.critical(f"Erro fatal na execução do pipeline principal: {str(e)}")
