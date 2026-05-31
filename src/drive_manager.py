import os

class DriveManager:
    def __init__(self):
        self.arquivo_nome = "historico_urls.txt"

    def ler_historico_urls(self) -> list:
        """Lê o arquivo de histórico local que o GitHub vai clonar."""
        if os.path.exists(self.arquivo_nome):
            try:
                with open(self.arquivo_nome, "r", encoding="utf-8") as f:
                    return [linha.strip() for list_linha in f if (linha := list_linha.strip())]
            except Exception:
                return []
        return []

    def salvar_no_historico(self, url: str):
        """Salva no arquivo de texto local durante a execução."""
        if not url: return
        try:
            historico = self.ler_historico_urls()
            if url not in historico:
                with open(self.arquivo_nome, "a", encoding="utf-8") as f:
                    f.write(f"{url}\n")
                print(f"✅ URL gravada no histórico de execução.")
        except Exception as e:
            print(f"⚠️ Erro ao atualizar histórico local: {e}")
