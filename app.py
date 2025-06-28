import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# --- Funções utilitárias ---
DB_PATH = "infos_pendencias.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def fetch_dataframe(query, params=()):
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def execute_query(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

# --- Configuração da página ---
st.set_page_config(page_title="Infos e Pendências", layout="wide")
st.title("🧠 Infos e Pendências")

# --- Menu lateral ---
menu = st.sidebar.radio("Menu", [
    "📊 Painel do Dia",
    "🗵️ Anotações Diárias",
    "🧑 Conversas & 1:1",
    "✅ Tarefas",
    "🔗 Links Úteis"
])

# --- Tarefas ---
if menu == "✅ Tarefas":
    st.header("✅ Suas Tarefas")

    try:
        execute_query("ALTER TABLE tasks ADD COLUMN deadline TEXT")
    except:
        pass

    with st.expander("➕ Adicionar Nova Tarefa"):
        with st.form("form_tarefa"):
            titulo = st.text_input("Título da tarefa:")
            descricao = st.text_area("Descrição:")
            prioridade = st.selectbox("Prioridade:", ["Alta", "Média", "Baixa"])
            prazo = st.date_input("Prazo da tarefa (opcional):")
            submitted = st.form_submit_button("Adicionar Tarefa")
            if submitted and titulo:
                deadline_str = prazo.strftime("%Y-%m-%d") if prazo else None
                execute_query("""
                    INSERT INTO tasks (title, description, priority, status, created_at, deadline)
                    VALUES (?, ?, ?, 'Pendente', ?, ?)
                """, (titulo, descricao, prioridade, datetime.today().strftime("%Y-%m-%d"), deadline_str))
                st.success("Tarefa adicionada!")
                st.rerun()

    status_filtro = st.selectbox("Filtrar tarefas por status:", ["Todas", "Pendente", "Concluído"])
    query = "SELECT * FROM tasks"
    params = ()
    if status_filtro != "Todas":
        query += " WHERE status = ?"
        params = (status_filtro,)
    query += " ORDER BY deadline IS NULL, deadline ASC, priority"
    tarefas = fetch_dataframe(query, params)

    st.subheader("Lista de Tarefas")
    tarefa_para_editar = None
    for _, row in tarefas.iterrows():
        with st.container():
            exp = st.expander(f"📌 {row['title']}")
            with exp:
                st.write(f"Descrição: {row['description']}")
                st.write(f"Prioridade: {row['priority']}")
                st.write(f"Status: {row['status']}")
                st.write(f"Prazo: {row['deadline'] or 'Sem prazo'}")

                notes = fetch_dataframe("SELECT * FROM notes WHERE related_type = 'Tarefa' AND related_id = ?", (row['id'],))
                for _, note in notes.iterrows():
                    st.markdown(f"\n✍️ Anotação: {note['content']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Concluir", key=f"done_{row['id']}"):
                        execute_query("UPDATE tasks SET status = 'Concluído' WHERE id = ?", (row['id'],))
                        st.rerun()
                with col2:
                    if st.button("✏️ Editar Tarefa", key=f"edit_{row['id']}"):
                        tarefa_para_editar = row['id']

    if tarefa_para_editar:
        tarefa = fetch_dataframe("SELECT * FROM tasks WHERE id = ?", (tarefa_para_editar,)).iloc[0]
        st.markdown("---")
        st.subheader("✏️ Editar Tarefa")
        with st.form("editar_tarefa"):
            novo_titulo = st.text_input("Título:", tarefa['title'])
            nova_desc = st.text_area("Descrição:", tarefa['description'])
            nova_prioridade = st.selectbox("Prioridade:", ["Alta", "Média", "Baixa"], index=["Alta", "Média", "Baixa"].index(tarefa['priority']))
            novo_status = st.selectbox("Status:", ["Pendente", "Concluído"], index=["Pendente", "Concluído"].index(tarefa['status']))
            nova_deadline = st.date_input("Prazo da tarefa:", value=datetime.strptime(tarefa['deadline'], "%Y-%m-%d") if tarefa['deadline'] else datetime.today())
            atualizar = st.form_submit_button("Atualizar Tarefa")
            if atualizar:
                execute_query("UPDATE tasks SET title = ?, description = ?, priority = ?, status = ?, deadline = ? WHERE id = ?",
                              (novo_titulo, nova_desc, nova_prioridade, novo_status, nova_deadline.strftime("%Y-%m-%d"), tarefa['id']))
                st.success("Tarefa atualizada com sucesso!")
                st.rerun()

# --- Anotações Diárias ---
elif menu == "🗵️ Anotações Diárias":
    st.header("🗵️ Anotações Diárias")
    today = datetime.today().strftime("%Y-%m-%d")

    anotacao = st.text_area("Digite sua anotação para hoje:")
    tag = st.text_input("Tag (opcional):")
    assoc_type = st.selectbox("Tipo de associação", ["Nenhum", "Tarefa", "Conversa", "Link"])

    assoc_id = None
    if assoc_type == "Tarefa":
        tarefas = fetch_dataframe("SELECT id, title FROM tasks ORDER BY created_at DESC")
        if not tarefas.empty:
            tarefa_escolhida = st.selectbox("Escolha a tarefa:", tarefas['title'].tolist(), key="select_tarefa")
            assoc_id = int(tarefas[tarefas['title'] == tarefa_escolhida]['id'].values[0])
    elif assoc_type == "Conversa":
        conversas = fetch_dataframe("""
            SELECT conversations.id, people.name || ' - ' || conv_date AS titulo
            FROM conversations
            JOIN people ON people.id = conversations.person_id
            ORDER BY conv_date DESC
        """)
        if not conversas.empty:
            conversa_escolhida = st.selectbox("Escolha a conversa:", conversas['titulo'].tolist(), key="select_conversa")
            assoc_id = int(conversas[conversas['titulo'] == conversa_escolhida]['id'].values[0])

    elif assoc_type == "Link":
        links = fetch_dataframe("SELECT id, title FROM links ORDER BY saved_at DESC")
        if not links.empty:
            link_options = {f"{row['title']} (id {row['id']})": row['id'] for _, row in links.iterrows()}
            link_escolhido = st.selectbox("Escolha o link:", list(link_options.keys()), key="select_link")
            assoc_id = link_options[link_escolhido]


    # Habilita botão se anotação for preenchida e associação estiver válida
    pode_salvar = bool(anotacao) and (assoc_type == "Nenhum" or assoc_type in ["Tarefa", "Conversa", "Link"] and assoc_id is not None)


    if st.button("Salvar Anotação", disabled=not pode_salvar):
        execute_query(
            "INSERT INTO notes (note_date, content, tag, related_type, related_id) VALUES (?, ?, ?, ?, ?)",
            (today, anotacao, tag, assoc_type if assoc_type != "Nenhum" else None, assoc_id)
        )
        st.success("Anotação salva com sucesso!")
        st.rerun()

    st.subheader("Histórico de Anotações")
    notes_df = fetch_dataframe("SELECT * FROM notes ORDER BY note_date DESC")
    st.dataframe(notes_df)


# --- Painel do Dia ---
elif menu == "📊 Painel do Dia":
    st.header("📊 Painel do Dia")
    today = datetime.today().strftime("%Y-%m-%d")

    st.subheader("Tarefas Prioritárias para Hoje")
    tasks_df = fetch_dataframe("SELECT * FROM tasks WHERE status = 'Pendente' ORDER BY CASE priority WHEN 'Alta' THEN 1 WHEN 'Média' THEN 2 ELSE 3 END")
    st.dataframe(tasks_df)

    st.subheader("Últimas Anotações")
    notes_df = fetch_dataframe("SELECT * FROM notes ORDER BY note_date DESC LIMIT 5")
    st.dataframe(notes_df)

    st.subheader("Pessoas sem 1:1 há 14+ dias")
    fourteen_days_ago = (datetime.today() - timedelta(days=14)).strftime("%Y-%m-%d")
    stale_people_df = fetch_dataframe("SELECT name, last_interaction FROM people WHERE last_interaction < ?", (fourteen_days_ago,))
    st.dataframe(stale_people_df)

# --- Conversas & 1:1 ---
elif menu == "🧑 Conversas & 1:1":
    st.header("🧑 Histórico de Conversas e 1:1")
    action = st.radio("Ação", ["Nova Conversa", "Ver Histórico"])

    if action == "Nova Conversa":
        with st.form("form_conversa"):
            nome = st.text_input("Nome da pessoa:")
            data_conversa = st.date_input("Data da conversa:", value=datetime.today())
            conteudo = st.text_area("Resumo da conversa:")
            submitted = st.form_submit_button("Salvar Conversa")
            if submitted and nome and conteudo:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM people WHERE name = ?", (nome,))
                row = cursor.fetchone()
                if row:
                    person_id = row[0]
                else:
                    cursor.execute("INSERT INTO people (name, last_interaction) VALUES (?, ?)", (nome, data_conversa))
                    person_id = cursor.lastrowid
                cursor.execute("INSERT INTO conversations (person_id, conv_date, content) VALUES (?, ?, ?)", (person_id, data_conversa, conteudo))
                cursor.execute("UPDATE people SET last_interaction = ? WHERE id = ?", (data_conversa, person_id))
                conn.commit()
                conn.close()
                st.success("Conversa salva com sucesso!")
                st.rerun()

    else:
        conversas = fetch_dataframe("""
            SELECT conversations.conv_date, conversations.content, people.name
            FROM conversations
            JOIN people ON people.id = conversations.person_id
            ORDER BY conversations.conv_date DESC
        """)
        st.dataframe(conversas)

# --- Links Úteis ---
elif menu == "🔗 Links Úteis":
    st.header("🔗 Links Importantes")
    with st.form("form_links"):
        titulo = st.text_input("Título do link:")
        categoria = st.text_input("Categoria:")
        url = st.text_input("URL:")
        comentario = st.text_area("Comentário:")
        submitted = st.form_submit_button("Salvar Link")
        if submitted and titulo and url:
            execute_query("INSERT INTO links (title, category, url, comment, saved_at) VALUES (?, ?, ?, ?, ?)",
                          (titulo, categoria, url, comentario, datetime.today().strftime("%Y-%m-%d")))
            st.success("Link salvo com sucesso!")
            st.rerun()

    st.subheader("Seus Links")
    links_df = fetch_dataframe("SELECT * FROM links ORDER BY saved_at DESC")
    st.dataframe(links_df)
