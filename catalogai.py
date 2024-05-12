import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError  # Import corrected

# --- Configuração (oculte a chave API) ---
with open("api_key.txt") as f:
    api_key = f.read().strip()
genai.configure(api_key=api_key)

# --- Configuração do modelo ---
generation_config = {"candidate_count": 1, "temperature": 0.7}

# É altamente recomendável manter os filtros de segurança ativados!
safety_settings = {
    'HATE': 'BLOCK_NONE',
    'HARASSMENT': 'BLOCK_NONE',
    'SEXUAL' : 'BLOCK_NONE',
    'DANGEROUS' : 'BLOCK_NONE'
}

# Inicializando o modelo
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro-latest',
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# --- Instruções do sistema ---
# Instrução para resposta personalizada
resposta_personalizada_instruction = """
Você é um especialista em filmes, animes e séries, com um estilo de comunicação divertido e informal. Sua tarefa é criar uma resposta personalizada para um usuário que acabou de inserir uma lista de títulos.

Siga estas regras:
* Referencie os títulos: Mencione pelo menos um ou dois títulos da lista do usuário.
* Adapte ao gênero: Faça comentários relacionados ao gênero identificado na lista.
* Seja informal e divertido: Use linguagem coloquial e expressões que engajem o usuário.
* Inclua uma frase de transição: Inclua uma frase que conecte a resposta personalizada com as recomendações, como "Saca só essas recomendações que separei para você:" ou "Prepare-se para maratonar, porque aqui vão minhas dicas:".

Exemplos:
* Títulos: Deadpool, Vingadores, Homem de Ferro
* Resposta: E aí, fã da Marvel? Deadpool é hilário, né? E os Vingadores, então? Que time! 💪 Se liga nessas outras dicas que tenho pra você:
* Títulos: O Senhor dos Anéis, Game of Thrones, The Witcher
* Resposta: Aventura épica é com você, né? O Senhor dos Anéis é um clássico, Game of Thrones tem reviravoltas incríveis... Mas calma que tem mais! Dá uma olhada nessas outras sugestões:
* Títulos: Parasita, Coringa, O Poderoso Chefão
* Resposta: Gosta de filmes que te fazem pensar, hein? Parasita é sensacional, Coringa é perturbador... E aí, bora ver mais uns filmes nesse estilo? 😉
"""
# Instrução para identificar o gênero
identificar_genero_instruction = """
Você é um especialista em filmes, animes e séries. Sua tarefa é identificar o(s) gênero(s) predominante(s) em uma lista de títulos. Considere subgêneros e nuances para uma análise mais precisa.

Responda apenas com o(s) nome(s) do(s) gênero(s), separados por barra (/) se houver mais de um.

Exemplos:
* Títulos: The Walking Dead, Guerra Mundial Z, Zumbilândia
    Gênero: Terror/Zumbi
* Títulos: Your Name, A Viagem de Chihiro, O Castelo Animado
    Gênero: Fantasia/Anime
* Títulos: O Senhor dos Anéis, Game of Thrones, The Witcher
    Gênero: Fantasia Medieval
* Títulos: Parasita, Coringa, O Poderoso Chefão
    Gênero: Drama/Thriller/Comédia Negra 
* Títulos: Deadpool, Se Beber, Não Case!, Missão Madrinha de Casamento
    Gênero: Ação/Comédia
* Títulos: John Wick, Mad Max: Estrada da Fúria, Busca Implacável
    Gênero: Ação
* Títulos: Blade Runner, 2001: Uma Odisseia no Espaço, Duna
    Gênero: Ficção Científica
* Títulos: La Casa de Papel, Round 6, Lupin
    Gênero: Suspense/Thriller
* Títulos: Stranger Things, Dark, The Umbrella Academy
    Gênero: Ficção Científica/Mistério
* Títulos: Grey's Anatomy, House, The Good Doctor
    Gênero: Drama Médico
"""

# Instrução para recomendar títulos
recomendar_instruction = """
Você é um assistente especializado em recomendar animes, filmes e séries.

Siga estas regras:
* Histórico: Evite recomendar títulos que já foram recomendados anteriormente e estão presentes no histórico.
* Recomendações únicas: Nunca sugira o mesmo título que o usuário forneceu como entrada.
* Diversidade: Recomende um filme, um anime e uma série, um de cada, a menos que o usuário especifique o contrário.
* Personalização: Leve em consideração o gênero identificado na lista de títulos fornecida pelo usuário.
* Formato da resposta: Separe as recomendações com "===" e use o seguinte formato para cada recomendação:
    * Tipo: [Filme, Anime ou Série]
    * Título: [Título]
    * Sinopse: [Breve sinopse]
    * Chances de Você Gostar: [Alta, Média ou Baixa]

Exemplo:

Informação: The Walking Dead, Guerra Mundial Z, Zumbilândia, John Wick, Mad Max
Resposta:
===
Tipo: Filme
Título: Army of the Dead
Sinopse: Um grupo de mercenários planeja um assalto a um cassino em Las Vegas durante um surto de zumbis.
Chances de Você Gostar: Alta
===
Tipo: Anime
Título: Highschool of the Dead
Sinopse: Um grupo de estudantes precisa lutar para sobreviver a um apocalipse zumbi.
Chances de Você Gostar: Média
===
Tipo: Série
Título: Kingdom
Sinopse: Um príncipe coreano precisa enfrentar uma misteriosa praga zumbi que está devastando o reino.
Chances de Você Gostar: Alta

Informação: O Senhor dos Anéis: A Sociedade do Anel, Game of Thrones, The Witcher
Resposta: 
===
Tipo: Filme
Título: Willow: Na Terra da Magia
Sinopse: Um fazendeiro anão embarca em uma jornada para proteger um bebê com um destino mágico.
Chances de Você Gostar: Alta
===
Tipo: Anime
Título: Berserk
Sinopse: Um guerreiro solitário chamado Guts luta contra demônios e busca vingança em um mundo sombrio.
Chances de Você Gostar: Média
===
Tipo: Série
Título: A Roda do Tempo
Sinopse: Uma jovem descobre que é a reencarnação de uma poderosa feiticeira e precisa salvar o mundo de uma força maligna.
Chances de Você Gostar: Alta

Informação: Parasita, Coringa, O Poderoso Chefão
Resposta: 
===
Tipo: Filme
Título: Seven: Os Sete Crimes Capitais
Sinopse: Dois detetives investigam uma série de assassinatos inspirados nos sete pecados capitais.
Chances de Você Gostar: Alta
===
Tipo: Anime
Título: Psycho-Pass
Sinopse: Em um futuro distópico, a polícia utiliza um sistema que prevê crimes antes que eles aconteçam.
Chances de Você Gostar: Alta
===
Tipo: Série
Título: Mindhunter
Sinopse: Dois agentes do FBI entrevistam serial killers para entender suas mentes e desenvolver novas técnicas de investigação.
Chances de Você Gostar: Alta

Informação: Deadpool, Se Beber, Não Case!, Missão Madrinha de Casamento
Resposta:
===
Tipo: Filme
Título: Anjos da Lei
Sinopse: Dois policiais jovens e imaturos se disfarçam de estudantes do ensino médio para investigar uma rede de drogas.
Chances de Você Gostar: Alta
===
Tipo: Anime
Título: Gintama
Sinopse: Um samurai excêntrico e seu aprendiz vivem aventuras hilárias em um Japão feudal futurista.
Chances de Você Gostar: Alta
===
Tipo: Série
Título: Brooklyn Nine-Nine
Sinopse: Uma delegacia de polícia no Brooklyn é palco de situações engraçadas e investigações criminais.
Chances de Você Gostar: Alta
"""
# Inicializa o histórico na session state
if 'historico' not in st.session_state:
    st.session_state.historico = []

# --- Função para obter recomendações ---
def obter_recomendacoes(titulos, historico):
    try:
        chat = model.start_chat(history=[]) 
        prompt_genero = f"Títulos: {', '.join(titulos)}\nGênero: "
        response_genero = chat.send_message(identificar_genero_instruction + prompt_genero)
        genero = response_genero.text.strip()

        # Geração da resposta personalizada
        prompt_personalizado = f"Títulos: {', '.join(titulos)}\nHistórico: {', '.join(historico)}\nResposta: "
        response_personalizada = chat.send_message(resposta_personalizada_instruction + prompt_personalizado)
        resposta_personalizada = response_personalizada.text.strip()

        # Instrução de recomendação modificada para incluir o histórico
        prompt_recomendacoes = f"""
        Informação: {', '.join(titulos)}
        Histórico: {', '.join(historico)}
        Resposta: 
        """
        response_recomendacoes = chat.send_message(recomendar_instruction + prompt_recomendacoes)
        return genero, resposta_personalizada, response_recomendacoes.text.strip()

        prompt_recomendacoes = f"Informação: {', '.join(titulos)}.\nResposta:\n"
        response_recomendacoes = chat.send_message(recomendar_instruction + prompt_recomendacoes)
        return genero, resposta_personalizada, response_recomendacoes.text.strip()
    except GoogleAPIError as e:
        if e.code == 429: 
            st.error(f"Erro na API do Gemini: {e}. Aguarde alguns instantes e tente novamente.")
        else:
            st.error(f"Erro na API do Gemini: {e}")
        return None, None, None  # Retorna None para todos os valores em caso de erro

# --- Interface do Streamlit ---
st.title("✨ CatalogAI: Seu Guia Personalizado para Filmes, Animes e Séries ✨")
st.write("Conte-nos seus gostos e o CatalogAI usará inteligência artificial para te recomendar filmes, animes e séries que você vai amar! 🤖🍿")
st.write("**Experimente:** Digite 'Stranger Things, Naruto, Your Name' e veja o que o CatalogAI recomenda!")

if "titulos_input" not in st.session_state:
    st.session_state.titulos_input = ""

titulos_input = st.text_area(
    "Insira os títulos que você gosta, separados por vírgula:",
    value=st.session_state.titulos_input,
)
titulos = [t.strip() for t in titulos_input.split(",")]

if "recomendacoes" not in st.session_state:
    st.session_state.recomendacoes = None

if "genero" not in st.session_state:  # Inicializa o genero na session state
    st.session_state.genero = None

# Botão condicional
if st.button("Obter Recomendações"):
    if all(titulos):
        with st.spinner("Pensando em recomendações incríveis..."):
            resultado_recomendacoes = obter_recomendacoes(titulos, st.session_state.historico)

        if resultado_recomendacoes is not None:
            st.session_state.genero, st.session_state.resposta_personalizada, recomendacoes_str = resultado_recomendacoes

            if st.session_state.genero and recomendacoes_str and st.session_state.resposta_personalizada:
                st.session_state.recomendacoes = recomendacoes_str

                # Adiciona os novos títulos recomendados ao histórico
                novas_recomendacoes = [linha.split(":")[1].strip() for linha in recomendacoes_str.split("\n") if linha.startswith("Título:")]
                st.session_state.historico.extend(novas_recomendacoes)

            else:
                st.warning("Por favor, insira pelo menos um título.")
        else:
            st.error("Ocorreu um erro ao obter as recomendações. Tente novamente mais tarde.")

# Exibe as recomendações (se houver)
if st.session_state.recomendacoes:
    st.write(st.session_state.resposta_personalizada)  # Exibe a resposta personalizada
    recomendacoes = st.session_state.recomendacoes.split("===")
    for recomendacao in recomendacoes:
        if recomendacao.strip():  # Check for empty recommendations
            linhas = recomendacao.strip().split("\n")
            tipo = linhas[0].split(":")[1].strip() if len(linhas) > 0 else "Tipo não especificado"

            # Use try-except to para possiveis erros
            try:
                titulo = linhas[1].split(":")[1].strip()
            except IndexError:
                titulo = "Título não especificado"

            try:
                sinopse = linhas[2].split(":")[1].strip()
            except IndexError:
                sinopse = "Sinopse não disponível"

            try:
                chances = linhas[3].split(":")[1].strip()
            except IndexError:
                chances = "Chances de gostar não especificadas"

            st.markdown(f"## **{tipo}: {titulo}**")
            st.write(f"_{sinopse}_")
            st.write(f"**Chances de Você Gostar:** {chances}")

# Botão "Refazer Teste"
if st.session_state.recomendacoes and st.button("Refazer Teste"):
    st.session_state.recomendacoes = None
    st.experimental_rerun()  # Recarrega a página para gerar novas recomendações com o histórico