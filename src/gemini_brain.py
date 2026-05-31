import json
import requests
import urllib.parse
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from PIL import Image
from src.config import GEMINI_API_KEY, MODELOS_TEXTO, MODELO_IMAGEM, PEXELS_API_KEY
from src.copy_style import ESTILO_COPY_PROPRIO

class GeminiBrain:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("Erro: GEMINI_API_KEY não foi configurada!")
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def buscar_noticias_reais_na_internet(self, historico_urls: list) -> str:
        print("🔍 Iniciando varredura em tempo real na internet (Google Search Grounding)...")
        
        historico_str = "\n".join(historico_urls[-30:]) if historico_urls else "Nenhum histórico recente."
        
        prompt_pesquisa = f"""
        Você é um estrategista em Direito do Trabalho Patronal e Direito Empresarial.
        Sua tarefa é fazer uma varredura profunda na internet hoje e trazer as 5 principais novidades, julgados do TST/STF ou alertas práticos de RH que impactam diretamente os EMPREGADORES.
        
        Siga estritamente estes critérios de curadoria para a busca:
        1. Priorize decisões do TST (Tribunal Superior do Trabalho), STF, portais como Conjur, Migalhas Trabalhista, Machado Meyer e portais de RH (Convenia, RH Noticias).
        2. Busque teses empresariais, regras de compliance, justa causa, LGPD nas relações de emprego e gestão de passivos.
        3. Elimine conteúdos puramente teóricos ou focados em defender o funcionário. O foco é blindar a empresa.
        
        REGRA CRÍTICA DE FILTRO: Não aborde assuntos ou links que já estejam listados no histórico abaixo:
        {historico_str}
        
        Retorne um relatório estruturado contendo o resumo técnico do avanço, a implicação para o empresário e, obrigatoriamente, a URL real de origem da notícia.
        """
        
        try:
            modelo_pesquisa = MODELOS_TEXTO[0]
            response = self.client.models.generate_content(
                model=modelo_pesquisa,
                contents=prompt_pesquisa,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.3
                )
            )
            print("✅ Varredura e filtragem de ineditismo concluídas com sucesso!")
            return response.text
        except Exception as e:
            print(f"❌ Erro na varredura ativa da internet: {e}")
            return ""

    def selecionar_e_redigir_posts(self, conteudo_bruto_web: str, historico_urls: list) -> list:
        system_instruction = f"""
        Sua missão é ler o conteúdo jurídico coletado e criar 3 posts individuais extremamente persuasivos voltados para o empresário, garantindo a prevenção de riscos trabalhistas.
        
        Use obrigatoriamente as diretrizes contidas abaixo:
        {ESTILO_COPY_PROPRIO}
        
        Regras de Negócio Cruciais:
        1. FONTE OBRIGATÓRIA: No final da legenda, escreva "Fonte: [Link da Notícia]".
        2. HASHTAGS OBRIGATÓRIAS.
        
        DIRETRIZES VISUAIS:
        - O prompt_imagem deve ser um conceito visual focado em negócios, escritório clean, minimalista estilo Apple, sem poluição. Sugira objetos como martelo de juiz, gráficos, mesas executivas. NUNCA gere prompts com rostos ou logotipos complexos.

        Responda estritamente em formato JSON válido, contendo exatamente esta estrutura (não adicione saudações fora do JSON):
        [
          {{
            "titulo": "Título de impacto curto (max 22 caracteres por linha) para a arte",
            "legenda_completa": "Legenda profunda seguindo o ESTILO_COPY_PROPRIO, com as quebras e fonte",
            "prompt_imagem": "Prompt de imagem detalhado EM INGLÊS focado em business minimalista",
            "pexels_keyword": "uma_palavra_em_ingles (ex: corporate, office, suit, justice)",
            "url": "A URL real da notícia extraída",
            "contem_ia_nominal": false
          }}
        ]
        """
        
        try:
            modelo_redacao = MODELOS_TEXTO[0]
            response = self.client.models.generate_content(
                model=modelo_redacao,
                contents=f"Conteúdo minerado:\n\n{conteudo_bruto_web}\n\nEscreva os posts respeitando rigorosamente o formato JSON e a persona patronal.",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.4
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"❌ Erro na geração/parsing de copywriting do Gemini: {e}")
            return []

    def _validar_imagem(self, path: str) -> bool:
        try:
            with Image.open(path) as img:
                img.verify()
            return True
        except:
            return False

    def gerar_imagem_ia(self, prompt_visual: str, keyword_pexels: str, url_noticia: str, ia_nominal: bool, output_path: str) -> str:
        print("🌐 GERANDO IMAGEM CORPORATIVA")
        print("👉 [Plano A] Acionando IA Google...")
        img = self._gerar_google_imagen(prompt_visual, output_path)
        if img: return img
        
        print("👉 [Plano B] Acionando IA Pollinations...")
        img = self._gerar_imagem_pollinations(prompt_visual, output_path)
        if img: return img
        
        print("👉 [Plano C] Acionando Pexels...")
        return self._buscar_imagem_pexels(keyword_pexels, output_path)

    def _capturar_imagem_original_noticia(self, url: str, path: str) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200: return ""
            soup = BeautifulSoup(r.text, 'html.parser')
            meta_og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
            if meta_og and meta_og.get("content"):
                img_url = meta_og["content"]
                img_data = requests.get(img_url, timeout=10).content
                with open(path, 'wb') as f:
                    f.write(img_data)
                if self._validar_imagem(path): return path
        except: pass
        return ""

    def _gerar_google_imagen(self, prompt: str, path: str) -> str:
        try:
            result = self.client.models.generate_images(
                model=MODELO_IMAGEM,
                prompt=prompt,
                config=types.GenerateImagesConfig(number_of_images=1, output_mime_type="image/jpeg")
            )
            for generated_image in result.generated_images:
                with open(path, "wb") as f:
                    f.write(generated_image.image.image_bytes)
                if self._validar_imagem(path): return path
        except: pass
        return ""

    def _gerar_imagem_pollinations(self, prompt: str, path: str) -> str:
        try:
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1080&height=1080&nologo=true"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
                if self._validar_imagem(path): return path
        except: pass
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
                if self._validar_imagem(path): return path
        except: pass
        return ""
