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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeminiBrain:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("Erro: GEMINI_API_KEY não configurada!")
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def buscar_noticias_reais_na_internet(self, historico_urls: list) -> str:
        logging.info("🔍 Iniciando varredura em tempo real na internet...")
        historico_str = "\n".join(historico_urls[-30:]) if historico_urls else "Nenhum histórico recente."
        
        prompt_pesquisa = f"""
        Você é um estrategista em Direito do Trabalho Patronal e Direito Empresarial.
        Faça uma varredura profunda na internet hoje e traga as 5 principais novidades, julgados do TST/STF ou alertas práticos de RH que impactam EMPREGADORES.
        Priorize decisões do TST, portais como Conjur e Migalhas. Foco em blindar a empresa.
        Não aborde links listados abaixo:
        {historico_str}
        Retorne um resumo técnico e a URL real da notícia.
        """
        
        for modelo in MODELOS_TEXTO:
            try:
                response = self.client.models.generate_content(
                    model=modelo,
                    contents=prompt_pesquisa,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.3
                    )
                )
                return response.text
            except Exception as e:
                logging.warning(f"⚠️ Modelo {modelo} falhou. Tentando próximo...")
                continue
        return ""

    def selecionar_e_redigir_posts(self, conteudo_bruto_web: str, historico_urls: list) -> list:
        system_instruction = f"""
        Crie 3 posts individuais extremamente persuasivos voltados para o empresário.
        {ESTILO_COPY_PROPRIO}
        
        DIRETRIZES VISUAIS: Prompt de imagem cinematográfico, hiper-realista em inglês. Sem texto na imagem.
        
        Responda estritamente em formato JSON válido:
        [
          {{
            "titulo": "Título contextualizado explicitando a dor/risco (entre 45 e 65 caracteres, 6 a 10 palavras). Ex: 'Justa causa mal aplicada gera multa milionária ao caixa'",
            "legenda_completa": "Legenda completa com quebras de linha",
            "prompt_imagem": "Prompt cinematográfico e hiper-realista EM INGLÊS",
            "pexels_keyword": "palavra simples em ingles",
            "url": "URL da notícia",
            "contem_ia_nominal": false
          }}
        ]
        """
        
        for modelo in MODELOS_TEXTO:
            try:
                response = self.client.models.generate_content(
                    model=modelo,
                    contents=f"Conteúdo minerado:\n\n{conteudo_bruto_web}\n\nEscreva os posts no formato JSON estrito.",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        temperature=0.4
                    )
                )
                
                texto_limpo = response.text.strip()
                if texto_limpo.startswith("```"):
                    texto_limpo = re.sub(r"^```json\s*|^```\s*|```$", "", texto_limpo, flags=re.MULTILINE).strip()

                posts = json.loads(texto_limpo)
                
                for index, post in enumerate(posts):
                    for variante in ["legenda", "texto", "content"]:
                        if variante in post and "legenda_completa" not in post:
                            post["legenda_completa"] = post[variante]
                    if "legenda_completa" not in post or not post["legenda_completa"].strip():
                        post["legenda_completa"] = f"📢 *ALERTA PARA GESTORES*\n\nAtualização importante exige atenção da governança. Fonte: {post.get('url', '')}"
                        
                return posts
            except Exception as e:
                logging.warning(f"⚠️ Erro no modelo {modelo}: {e}. Tentando backup...")
                continue
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
        
        img = self._gerar_google_imagen(prompt_visual, output_path)
        if img: return img
        
        img = self._gerar_imagem_pollinations(prompt_visual, output_path)
        if img: return img
        
        return self._buscar_imagem_pexels(keyword_pexels, output_path)

    def _gerar_google_imagen(self, prompt: str, path: str) -> str:
        try:
            # Correção para o novo SDK: generate_images (plural)
            result = self.client.models.generate_images(
                model=MODELO_IMAGEM,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1, 
                    output_mime_type="image/jpeg",
                    aspect_ratio="1:1"
                )
            )
            for generated_image in result.generated_images:
                with open(path, "wb") as f:
                    f.write(generated_image.image.image_bytes)
                if self._validar_imagem(path): 
                    logging.info("✅ Imagem gerada com sucesso pelo Google Imagen!")
                    return path
        except Exception as e:
            logging.error(f"❌ Google Imagen falhou: {e}")
        return ""

    def _gerar_imagem_pollinations(self, prompt: str, path: str) -> str:
        try:
            prompt_turbinado = f"{prompt}, masterpiece, cinematic"
            encoded_prompt = urllib.parse.quote(prompt_turbinado)
            # Modelo padrão HQ ativado. Removido "?model=flux" para evitar o erro de cobrança 402
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
            r = requests.get(url, timeout=25)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
                if self._validar_imagem(path):
                    logging.info("✅ Imagem gerada pelo Pollinations AI!")
                    return path
        except Exception as e:
            logging.error(f"❌ Pollinations falhou: {e}")
        return ""

    def _buscar_imagem_pexels(self, keyword: str, path: str) -> str:
        try:
            url = f"https://api.pexels.com/v1/search?query={keyword}&per_page=1&orientation=square"
            headers = {"Authorization": PEXELS_API_KEY} if PEXELS_API_KEY else {}
            if not PEXELS_API_KEY: return ""
            r = requests.get(url, headers=headers, timeout=10).json()
            if r.get("photos"):
                img_url = r["photos"][0]["src"]["large"]
                data = requests.get(img_url, timeout=10).content
                with open(path, "wb") as f:
                    f.write(data)
                if self._validar_imagem(path):
                    return path
        except Exception:
            pass
        return ""
