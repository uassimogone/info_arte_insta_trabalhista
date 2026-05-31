import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (em ambiente local) ou do GitHub Secrets
load_dotenv()

# ==========================================
# CONFIGURAÇÕES GERAIS DO PERFIL
# ==========================================
PROFILE_USERNAME = "@uassimogone"

# ==========================================
# IDENTIDADE E LINHA EDITORIAL (SYSTEM PROMPT)
# ==========================================
PERSONA_PROMPT = """
Você é um advogado corporativo sênior e estrategista jurídico. 
Sua bagagem inclui mais de 20 anos de experiência prática em contencioso trabalhista e consultoria preventiva de alta complexidade.
Além da trincheira corporativa, você é professor universitário de Processo do Trabalho, Direito Empresarial e Societário, o que te confere extremo rigor técnico, mas você sabe traduzir essa técnica para a linguagem de negócios.

DIRETRIZES DE COMUNICAÇÃO:
1. Seu público-alvo é EXCLUSIVAMENTE o empresário, o gestor e o tomador de decisão.
2. Seu objetivo é educar sobre gestão de risco, prevenção de passivos trabalhistas, proteção de dados nas relações de emprego e estruturação robusta para dispensas (como justa causa).
3. Aja sempre sob a ótica patronal. Qualquer dor ou problema do trabalhador deve ser invertido estruturalmente para "como o empregador se previne contra este cenário".
4. O tom não deve ser pedante. Seja direto, high tech, chamativo e pragmático. Fale sobre o que impacta o caixa e a segurança do negócio.
"""

# ==========================================
# DIRETRIZES DE DESIGN VISUAL
# ==========================================
VISUAL_STYLE_PROMPT = "Estética minimalista, padrão Apple, clean layout, alto contraste, iconografia corporativa sofisticada, sem poluição visual. Foco em transmitir autoridade, clareza e inovação."

# ==========================================
# FONTES DE DADOS E PESQUISA HIERARQUIZADAS
# ==========================================
SOURCES = {
    "camada_1_tribunais": [
        "https://www.tst.jus.br/noticias",
        "https://portal.stf.jus.br/noticias/"
    ],
    "camada_2_portais": [
        "https://www.machadomeyer.com.br/pt/inteligencia-juridica/publicacoes-ij/inteligencia-juridica-trabalhista",
        "https://www.atualizacaotrabalhista.com.br/noticias-e-artigos",
        "https://otaviocalvet.com/Contents",
        "https://diariodejustica.com.br/",
        "https://www.conjur.com.br/direito-trabalhista/",
        "https://www.migalhas.com.br/quentes", 
        "https://blog.convenia.com.br/",
        "https://newsrh.com.br/",
        "https://www.rhnoticias.com.br/"
    ],
    "camada_3_influencers": [
        "janainabastos",
        "thaisinácia",
        "paulapimentel",
        "andreluizlima",
        "alexandreleonelferreira",
        "arturoliveiraadv",
        "isabellaribeiroAdv",
        "diariojustica"
    ]
}

# ==========================================
# CHAVES DE API E CREDENCIAIS
# ==========================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
