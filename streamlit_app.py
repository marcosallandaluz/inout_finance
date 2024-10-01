import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# Função para criar a tabela no banco de dados SQLite
def create_table():
    conn = sqlite3.connect('finances.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  type TEXT,
                  month TEXT,
                  amount REAL,
                  description TEXT)''')
    conn.commit()
    conn.close()

# Função para adicionar uma transação
def add_transaction(transaction_type, month, amount, description):
    conn = sqlite3.connect('finances.db')
    c = conn.cursor()
    c.execute("INSERT INTO transactions (type, month, amount, description) VALUES (?, ?, ?, ?)",
              (transaction_type, month, amount, description))
    conn.commit()
    conn.close()

# Função para obter todas as transações
def get_transactions():
    conn = sqlite3.connect('finances.db')
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return df

# Função para calcular o resumo financeiro
def get_summary(df):
    # Garantir que a coluna 'type' esteja sem espaços e com a capitalização correta
    df['type'] = df['type'].str.strip().str.lower()  # Remove espaços e converte para minúsculas
    
    # Converter a coluna 'amount' para numérico para garantir que está sendo somado corretamente
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    # Somar corretamente as entradas e saídas, independentemente do campo 'month'
    total_entrada = df[df['type'] == 'entrada']['amount'].sum()
    total_saida = df[df['type'] == 'saida']['amount'].sum()
    
    saldo = total_entrada - total_saida
    
    # Print para debug, você pode remover depois
    print(f"Total de Entradas: {total_entrada}, Total de Saídas: {total_saida}, Saldo: {saldo}")
    
    return total_entrada, total_saida, saldo

# Função para criar o gráfico
def create_chart(total_entrada, total_saida, saldo):
    fig, ax = plt.subplots()
    labels = ['Entradas', 'Saídas', 'Saldo']
    values = [total_entrada, total_saida, saldo]
    colors = ['#4CAF50', '#F44336', '#2196F3']
    ax.bar(labels, values, color=colors)
    ax.set_ylabel('Valor (R$)')
    ax.set_title('Resumo Financeiro')
    for i, v in enumerate(values):
        ax.text(i, v, f'R$ {v:.2f}', ha='center', va='bottom')
    return fig

# Criar a tabela no banco de dados
create_table()

# Título principal
st.title("Controle Pix")

# Sidebar para entrada de dados
st.sidebar.header("Adicionar Transação")

transaction_type = st.sidebar.selectbox("Tipo", ["Entrada", "Saída"])
month = st.sidebar.selectbox("Mês", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro", ""])
amount = st.sidebar.number_input("Valor", min_value=0.00, step=0.00)
description = st.sidebar.text_input("Descrição")

if st.sidebar.button("Adicionar Transação"):
    add_transaction(transaction_type, month, amount, description)
    st.sidebar.success("Transação adicionada com sucesso!")
    st.rerun()  # Atualizar a página após adicionar a transação

# Obter todas as transações
transactions_df = get_transactions()

# Calcular o resumo
total_entrada, total_saida, saldo = get_summary(transactions_df)

# Exibir o resumo
st.header("Resumo Financeiro")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Entradas", f"R$ {total_entrada:.2f}")
col2.metric("Total de Saídas", f"R$ {total_saida:.2f}")
col3.metric("Saldo", f"R$ {saldo:.2f}")

# Criar e exibir o gráfico
st.header("Gráfico")
chart = create_chart(total_entrada, total_saida, saldo)
st.pyplot(chart)

# Exibir a lista de transações
st.header("Lista de Transações")
if not transactions_df.empty:
    # Adicionar uma coluna de cor baseada no tipo de transação, garantindo que a coluna existe
    transactions_df['color'] = transactions_df['type'].map({'entrada': '#4CAF50', 'saida': '#F44336'})
    
    # Aplicar estilo com base na coluna 'color'
    styled_df = transactions_df.style.apply(
        lambda x: ['background-color: ' + str(x['color'])] * len(x), axis=1
    )
    
    # Exibir a tabela estilizada
    st.dataframe(styled_df, height=400)
    
    # Adicionar funcionalidade para excluir transações
    transaction_to_delete = st.selectbox("Selecione uma transação para excluir", 
                                         transactions_df['id'].tolist(),
                                         format_func=lambda x: f"ID: {x} - {transactions_df[transactions_df['id'] == x]['description'].values[0]}")
    if st.button("Excluir Transação Selecionada"):
        delete_transaction(transaction_to_delete)
        st.success("Transação excluída com sucesso!")
        st.rerun()  # Atualizar a página após excluir a transação
else:
    st.info("Nenhuma transação encontrada.")

# Adicionar algumas informações úteis
st.sidebar.markdown("---")
st.sidebar.subheader("Sobre o aplicativo")
st.sidebar.info("Este é um aplicativo de controle financeiro que permite adicionar entradas e saídas de dinheiro, visualizar um resumo financeiro e gerenciar suas transações.")
st.sidebar.warning("Os dados são armazenados localmente em um banco de dados SQLite.")