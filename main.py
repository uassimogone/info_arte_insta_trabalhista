import datetime
from src.config import TOTAL_POSTS
from src.drive_manager import DriveManager
from src.gemini_brain import GeminiBrain
from src.image_manager import ImageManager
from src.telegram_bot import TelegramBot

def executar_pipeline_diario():
    print(f"⏰ [{datetime.datetime.now().strftime('%H:%M:%S')}] Iniciando Pipeline Dinâmico e Real...")
    
    drive = DriveManager()
    brain = GeminiBrain()
    img_render = ImageManager()
    telegram = TelegramBot()

    # 1. Carrega o histórico persistente (Sem redefinir ou limpar a lista)
    historico = drive.ler_historico_urls()

    # 2. Executa a varredura ativa na internet de 2026 via Google Grounding
    conteudo_bruto = brain.buscar_noticias_reais_na_internet(historico)

    if not conteudo_bruto:
        print("☕ Falha ou ausência de atualizações inéditas na internet. Encerrando.")
        return

    # 3. Processa e redige os posts estruturados com o seu tom de voz (copy_style)
    print("🧠 Redigindo posts com a inteligência artificial...")
    posts_selecionados = brain.selecionar_e_redigir_posts(conteudo_bruto, historico)

    if not posts_selecionados:
        print("☕ Nenhuma postagem relevante qualificada para hoje. Encerrando.")
        return

    posts_enviados_com_sucesso = 0
    for index, post in enumerate(posts_selecionados[:TOTAL_POSTS], start=1):
        print(f"🎬 Processando Post {index}/{len(posts_selecionados)}...")

        titulo = post.get("titulo", "Novidade Tech")
        legenda = post.get("legenda_completa", "")
        prompt_vis = post.get("prompt_imagem", "Modern abstract corporate technology background")
        keyword_pex = post.get("pexels_keyword", "technology")
        url_noticia = post.get("url", "")
        ia_nominal = post.get("contem_ia_nominal", False)

        tmp_img_ia = f"/tmp/topo_gerado_{index}.jpg"
        img_final_png = f"/tmp/post_pronto_{index}.png"

        # Executa a estratégia de cascata visual inteligente
        img_resolvida = brain.gerar_imagem_ia(prompt_vis, keyword_pex, url_noticia, ia_nominal, tmp_img_ia)

        if not img_resolvida:
            print(f"⏭️ ALERTA: Nenhuma imagem obtida na cascata. Abortando Post {index}.")
            continue

        # Monta o slide final com a tarja do título e envia para o Telegram
        img_render.montar_slide(img_resolvida, titulo, img_final_png)
        telegram.enviar_post(img_final_png, index, legenda, titulo)
        posts_enviados_com_sucesso += 1

        # Alimenta a persistência para garantir o ineditismo nas próximas execuções
        if url_noticia:
            drive.salvar_no_historico(url_noticia)

    if posts_enviados_com_sucesso > 0:
        telegram.enviar_mensagem(f"✅ *Produção e curadoria concluídas!* {posts_enviados_com_sucesso} posts reais gerados e postados.")

if __name__ == "__main__":
    executar_pipeline_diario()
