import os
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont

class ImageManager:
    """Gerencia o download de fontes e a montagem visual do slide final usando Pillow."""
    
    def __init__(self):
        self.font_bold = "/tmp/Montserrat-Bold.ttf"
        self.font_semibold = "/tmp/Montserrat-SemiBold.ttf"
        self._baixar_fontes_se_necessario()

    def _baixar_fontes_se_necessario(self):
        """Garante que as fontes do projeto estejam disponíveis localmente no ambiente."""
        if not os.path.exists(self.font_bold):
            print("📥 Baixando fonte Montserrat-Bold...")
            url = "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf"
            r = requests.get(url)
            with open(self.font_bold, "wb") as f:
                f.write(r.content)
                
        if not os.path.exists(self.font_semibold):
            print("📥 Baixando fonte Montserrat-SemiBold...")
            url = "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-SemiBold.ttf"
            r = requests.get(url)
            with open(self.font_semibold, "wb") as f:
                f.write(r.content)

    def montar_slide(self, imagem_path: str, titulo: str, arquivo_saida: str):
        """Monta o slide 1080x1080px com imagem no topo, faixa central e título."""
        W, H = 1080, 1080
        TOPO_H = 648
        FAIXA_Y = 648
        FAIXA_H = 86
        TITULO_Y = 734
        TITULO_H = 346

        COR_FAIXA = (0, 0, 0)
        COR_FUNDO = (13, 46, 92)
        COR_TITULO = (255, 255, 255)
        COR_TAG = (255, 255, 255)

        # Inicializa a tela com o azul institucional de fundo
        slide = Image.new("RGB", (W, H), COR_FUNDO)
        draw = ImageDraw.Draw(slide)

        # 1. Processa e cola a imagem do topo
        if imagem_path and os.path.exists(imagem_path):
            img_topo = Image.open(imagem_path).convert("RGB")
            img_topo = img_topo.resize((W, TOPO_H), Image.Resampling.LANCZOS)
            slide.paste(img_topo, (0, 0))
        else:
            # Fallback caso ocorra falha crítica na imagem: cria um gradiente/bloco sólido
            draw.rectangle([(0, 0), (W, TOPO_H)], fill=(20, 60, 120))

        # 2. Desenha a faixa preta centralizada
        draw.rectangle([(0, FAIXA_Y), (W, FAIXA_Y + FAIXA_H)], fill=COR_FAIXA)
        
        # 3. Adiciona a Tag da marca na faixa preta
        fonte_tag = ImageFont.truetype(self.font_semibold, 34)
        tag_text = "@legaltech_br"
        bbox_tag = draw.textbbox((0, 0), tag_text, font=fonte_tag)
        tag_x = (W - (bbox_tag[2] - bbox_tag[0])) // 2
        tag_y = FAIXA_Y + (FAIXA_H - (bbox_tag[3] - bbox_tag[1])) // 2
        draw.text((tag_x, tag_y), tag_text, font=fonte_tag, fill=COR_TAG)

        # 4. Quebra e renderiza o título na zona de segurança inferior
        fonte_titulo = ImageFont.truetype(self.font_bold, 52)
        linhas = textwrap.wrap(titulo.upper(), width=22)
        line_h = draw.textbbox((0, 0), "A", font=fonte_titulo)[3] + 12
        bloco_h = line_h * len(linhas)
        text_y = TITULO_Y + (TITULO_H - bloco_h) // 2

        for linha in linhas:
            bbox_linha = draw.textbbox((0, 0), linha, font=fonte_titulo)
            line_w = bbox_linha[2] - bbox_linha[0]
            x = (W - line_w) // 2
            draw.text((x, text_y), linha, font=fonte_titulo, fill=COR_TITULO)
            text_y += line_h

        # Salva o arquivo final pronto para postagem
        slide.save(arquivo_saida, "PNG", dpi=(300, 300))
        print(f"🖼️ Slide montado e renderizado em: {arquivo_saida}")
        return arquivo_saida