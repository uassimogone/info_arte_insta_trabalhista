import google.generativeai as genai
import logging
from src.config import GEMINI_API_KEY, PERSONA_PROMPT

# Configuração básica de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeminiBrain:
    def __init__(self):
        """Inicializa o cliente da API do Gemini e configura o modelo."""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente.")
            
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Temperatura de 0.4: Equilíbrio ideal entre precisão jurídica e criatividade para o feed
        self.generation_config = {
            "temperature": 0.4,
            "top_p": 0.9,
            "top_k": 32,
            "max_output_tokens": 2048,
        }
        
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=self.generation_config,
            system_instruction=PERSONA_PROMPT
        )

    def processar_conteudo(self, texto_bruto: str, camada_origem: int) -> dict:
        """
        Processa o conteúdo de referência aplicando a lógica específica da camada de origem.
        """
        logging.info(f"Processando conteúdo proveniente da Camada {camada_origem}")
        
        instrucao_base = "Crie um roteiro completo de publicação (texto + sugestão de arte) para Instagram/TikTok. "
        
        # Lógica de Roteamento por Camada
        if camada_origem == 1:
            instrucao_especifica = (
                "O texto abaixo reflete uma decisão recente ou movimentação de um Tribunal Superior (TST/STF). "
                "Traduza essa decisão técnica para as consequências práticas no caixa e na gestão da empresa. "
                "Gere um alerta executivo de alto impacto focando em gestão de risco."
            )
        elif camada_origem == 2:
            instrucao_especifica = (
                "O texto abaixo é um artigo de um portal jurídico ou especializado em RH. "
                "Extraia a essência da atualização e transforme em um manual rápido ou checklist estratégico "
                "para o empresário aplicar na blindagem do seu negócio hoje."
            )
        elif camada_origem == 3:
            instrucao_especifica = (
                "ATENÇÃO MÁXIMA: O texto abaixo é de um produtor de conteúdo/influencer. "
                "Use isso APENAS como inspiração de TEMA e ÂNGULO. SOB NENHUMA HIPÓTESE copie o texto original. "
                "Crie um post 100% autoral. Adapte o conteúdo estritamente para a dor do EMPREGADOR e como ele pode se proteger."
            )
        else:
            instrucao_especifica = "Adapte o conteúdo abaixo para um post de alta performance e atração de clientes corporativos."

        prompt_final = (
            f"{instrucao_base}\n\n"
            f"DIRETRIZ DA FONTE:\n{instrucao_especifica}\n\n"
            f"TEXTO DE REFERÊNCIA (INPUT):\n{texto_bruto}\n\n"
            "ESTRUTURA DE SAÍDA EXIGIDA:\n"
            "1. Gancho (Hook): Frase de impacto em até 3 segundos.\n"
            "2. Desenvolvimento: Explicação do risco/solução de forma objetiva e corporativa.\n"
            "3. Call to Action (CTA): Focado em instigar auditoria ou consultoria preventiva.\n"
            "4. Prompt de Imagem: Sugira uma arte baseada nas regras minimalistas do projeto."
        )

        try:
            resposta = self.model.generate_content(prompt_final)
            return {
                "status": "sucesso",
                "conteudo": resposta.text
            }
        except Exception as e:
            logging.error(f"Erro na geração de conteúdo via Gemini: {str(e)}")
            return {
                "status": "erro",
                "mensagem": str(e)
            }

# Instância Singleton para uso em todo o repositório
brain = GeminiBrain()