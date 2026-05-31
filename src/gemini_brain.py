import json
import requests
import urllib.parse
import logging
import re
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from PIL import Image
from src.config import GEMINI_API_KEY, MODELOS_TEXTO, MODELO_IMAGEM, PEXELS_API_KEY
from src.copy_style import ESTILO_COPY_PROPRIO

# Configuração de logs para exibição limpa no GitHub Actions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeminiBrain:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("Erro: GEMINI_API_KEY não foi configurada!")
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def buscar_noticias_reais_na_internet(self, historico_urls: list) -> str:
        logging.info("🔍 Iniciando varredura em tempo real na internet (Google Search Grounding)...")
        
        historico_str = "\n".join(historico_urls[-30:]) if historico_urls else "Nenhum histórico recente."
        
        prompt_pesquisa = f"""
        Você é um estrategista em Direito do Trabalho Patronal e Direito Empresarial.
        Sua tarefa é fazer uma varredura profunda na internet hoje e trazer as 5 principais novidades, julgados do TST/STF ou alertas práticos de RH que impactam diretamente os EMPREGADORES.
        
        Siga estritamente estes critérios de curadoria para a busca:
        1. Priorize decisões do TST, STF, portais como Conjur, Migalhas Trabalhista, Machado Meyer e portais de RH.
        2. Busque teses empresariais, regras de compliance, justa causa, LGPD nas relações de emprego e gestão de passivos.
        3. Elimine conteúdos puramente teóricos ou focados em defender o funcionário. O foco é blindar a empresa.
        
        REGRA CRÍTICA DE FILTRO: Não aborde assuntos ou links que já estejam listados no histórico abaixo:
        {historico_str}
        
        Retorne um relatório estruturado contendo o resumo técnico do avanço, a implicação para o empresário e a URL real da notícia.
        """
        
        for modelo in MODELOS_TEXTO:
            try:
                logging.info(f"🔄 Solicitando varredura ao modelo: {modelo}...")
                response = self.client.models.generate_content(
                    model=modelo,
                    contents=prompt_pesquisa,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.3
                    )
                )
                logging.info(f"✅ Varredura concluída com sucesso pelo modelo {modelo}!")
                return response.text
            except Exception as e:
                logging.warning(f"⚠️ Modelo {modelo} falhou ou está sobrecarregado. Tentando próximo... Erro: {e}")
                continue
                
        logging.error("❌ Todos os modelos de busca falharam. Instabilidade no Google.")
        return ""

    def selecionar_e_redigir_posts(self, conteudo_bruto_web: str, historico_urls: list) -> list:
        system_instruction = f"""
        Sua missão é ler o conteúdo jurídico e criar 3 posts individuais extremamente persuasivos voltados para o empresário.
        
        Use obrigatoriamente as diretrizes contidas abaixo:
        {ESTILO_COPY_PROPRIO}
        
        Regras Cruciais de Legenda:
        1. FONTE OBRIGATÓRIA: No final da legenda, escreva "Fonte: [Link da Notícia]".
        2. HASHTAGS OBRIGATÓRIAS.
        
        DIRETRIZES VISUAIS REFINADAS (NEXO E COERÊNCIA COM A NOTÍCIA):
        - O "prompt_imagem" deve criar uma metáfora visual DIRETAMENTE RELACIONADA com o tema específico da notícia redigida.
        - Se a notícia for sobre Justa Causa ou Julgamento, foque em elementos de lei (gavel, law scales).
        - Se for sobre Segurança do Trabalho ou EPI, inclua elementos industriais elegantes (safety helmet on glass desk, industrial blueprint).
        - Se for sobre Dinheiro, Horas Extras ou Caixa, inclua elementos financeiros (fountain pen on financial charts, calculator, luxury watch).
        - Use OBRIGATORIAMENTE os termos fotográficos: "Cinematic lighting, 8k resolution, photorealistic, hyper-detailed, dramatic shadows, modern luxury corporate aesthetic, professional photography".
        - O cenário deve ser sempre sofisticado (fundo de escritório de luxo escuro desfocado, mesa de vidro preta). NUNCA coloque texto escrito dentro da imagem, símbolos bizarros ou rostos humanos nítidos.

        Responda estritamente em formato JSON válido:
        [
          {{
            "titulo": "Título curto de impacto (max 25 caracteres)",
            "legenda_completa": "Legenda profunda e completa seguindo o ESTILO_COPY_PROPRIO, com as quebras de linha, fonte e tags",
            "prompt_imagem": "Prompt cinematográfico, hiper-realista e temático EM INGLÊS conectando o objeto ao assunto da notícia",
            "pexels_keyword": "uma unica palavra em ingles para busca reserva (ex: gavel, office, document)",
            "url": "A URL real da notícia",
            "contem_ia_nominal": false
          }}
        ]
        """
        
        for modelo in MODELOS_TEXTO:
            try:
                logging.info(f"🧠 Redigindo posts com a inteligência artificial (Modelo: {modelo})...")
                response = self.client.models.generate_content(
                    model=modelo,
                    contents=f"Conteúdo minerado:\n\n{conteudo_bruto_web}\n\nEscreva os posts no formato JSON estrito.",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        temperature=0.4
                    )
                )
                
                # Limpeza de possíveis marcações Markdown do JSON para evitar falhas de parsing
                texto_limpo = response.text.strip()
                if texto_limpo.startswith("```"):
                    texto_limpo = re.sub(r"^```json\s*|^```\s*|```$", "", texto_limpo, flags=re.MULTILINE).strip()

                # Parsing do JSON gerado
                posts = json.loads(texto_limpo)
                
                # BLINDAGEM MÁXIMA ANTI-OSCILAÇÃO DE CHAVES (POST 1, 2 e 3):
                for index, post in enumerate(posts):
                    # Procura variações alternativas que a IA possa ter gerado para o texto
                    for variante in ["legenda", "texto", "content", "copy", "legenda_completa_"]:
                        if variante in post and "legenda_completa" not in post:
                            post["legenda_completa"] = post[variante]
                    
                    # Fallback de segurança se o campo continuar ausente ou vazio
                    if "legenda_completa" not in post or not post["legenda_completa"].strip():
                        tit = post.get("titulo", "Alerta Estratégico")
                        lnk = post.get("url", "Tribunais Superiores")
                        logging.warning(f"⚠️ Atenção: Detectada falha de preenchimento na legenda do Post {index+1}. Injetando Fallback.")
                        post["legenda_completa"] = (
                            f"📢 *ALERTA EXTRAORDINÁRIO PARA GESTORES*\n\n"
                            f"Novas atualizações e precedentes nos tribunais demandam auditoria preventiva imediata "
                            f"sobre os procedimentos internos da sua empresa.\n\n"
                            f"Mantenha a governança corporativa alinhada para mitigar passivos trabalhistas ocultos e proteger o caixa do seu negócio.\n\n"
                            f"Fonte: {lnk}\n\n"
                            f"#AdvocaciaPatronal #DireitoDoTrabalho #ComplianceTrabalhista #GestaoDeRisco"
                        )
                        
                return posts
            except Exception as e:
                logging.warning(f"⚠️ Modelo {modelo} falhou na geração ou parsing do JSON. Erro: {e}. Tentando backup...")
                continue
                
        logging.error("❌ Todos os modelos de redação falharam.")
        return []

    def _validar_imagem(self, path: str) -> bool:
        try:
            with Image.open(path) as img:
                img.verify()
            return True
        except:
            return False

    def gerar_imagem_ia(self, prompt_visual: str, keyword_pexels: str, url_noticia: str, ia_nominal: bool, output_path: str) -> str:
        logging.info(f"🌐 PROCESSANDO IMAGEM PARA O PROMPT: {prompt_visual}")
        
        logging.info("👉 [Plano A] Acionando Google Imagen 3...")
        img = self._gerar_google_imagen(prompt_visual, output_path)
        if img: return img
        
        logging.info("👉 [Plano B] Acionando Modelo FLUX.1 (Cinematográfico)...")
        img = self._gerar_imagem_pollinations(prompt_visual, output_path)
        if img: return img
        
        logging.info("👉 [Plano C] Acionando Pexels (Fallback final)...")
        return self._buscar_imagem_pexels(keyword_pexels, output_path)

    def _gerar_google_imagen(self, prompt: str, path: str) -> str:
        try:
            result = self.client.models.generate_image(
                model=MODELO_IMAGEM,
                prompt=prompt,
                config=dict(
                    numberOfImages=1,
                    outputMimeType="image/jpeg",
                    aspectRatio="1:1"
                )
            )
            for generated_image in result.generated_images:
                with open(path, "wb") as f:
                    f.write(generated_image.image.image_bytes)
                if self._validar_imagem(path): 
                    logging.info("✅ Imagem gerada com sucesso pelo Google Imagen!")
                    return path
        except Exception as e:
            logging.error(f"❌ Google Imagen negou ou falhou: {e}")
        return ""

    def _gerar_imagem_pollinations(self, prompt: str, path: str) -> str:
        try:
            prompt_turbinado = f"{prompt}, masterpiece, best quality, cinematic photography"
            encoded_prompt = urllib.parse.quote(prompt_turbinado)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=
