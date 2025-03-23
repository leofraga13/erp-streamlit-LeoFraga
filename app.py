import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime


def get_connection():
    return sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)


def query_database(query):
    try:
        with get_connection() as conn:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Erro ao executar a consulta: {e}")
        return pd.DataFrame()  


def main():
    st.title("ERP Financeiro com Streamlit")

    menu = ["Clientes", "Contas a Pagar", "Contas a Receber", "Lançamentos", "Relatórios", 
            "Top 5 Clientes", "Receita vs Despesa", "Distribuição das Contas a Pagar"]
    choice = st.sidebar.selectbox("Selecione uma opção", menu)

    if choice == "Clientes":
        st.subheader("Cadastro de Clientes")
        df = query_database("SELECT * FROM clientes")
        st.dataframe(df)

    elif choice == "Contas a Pagar":
        st.subheader("Contas a Pagar")
        df = query_database("SELECT * FROM contas_pagar")
        st.dataframe(df)

    elif choice == "Contas a Receber":
        st.subheader("Contas a Receber")
        df = query_database("SELECT * FROM contas_receber")
        st.dataframe(df)

    elif choice == "Lançamentos":
        st.subheader("Lançamentos Financeiros")
        df = query_database("SELECT * FROM lancamentos")
        st.dataframe(df)

    elif choice == "Relatórios":
        st.subheader("Relatório de Fluxo de Caixa")
        df = query_database("SELECT tipo, SUM(valor) as total FROM lancamentos GROUP BY tipo")
        st.dataframe(df)

    elif choice == "Top 5 Clientes":
        st.subheader("Top 5 Clientes com Maior Receita")

        query = """
        SELECT clientes.nome, SUM(contas_receber.valor) as receita
        FROM contas_receber
        JOIN clientes ON contas_receber.cliente_id = clientes.id
        WHERE strftime('%Y-%m', contas_receber.vencimento) = strftime('%Y-%m', 'now')
        GROUP BY clientes.nome
        ORDER BY receita DESC
        LIMIT 5
        """
        df_top5 = query_database(query)

        if not df_top5.empty:
            st.dataframe(df_top5)

            
            fig, ax = plt.subplots()
            ax.bar(df_top5["nome"], df_top5["receita"], color="green")
            ax.set_xlabel("Clientes")
            ax.set_ylabel("Receita Total (R$)")
            ax.set_title("Top 5 Clientes com Maior Receita")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.warning("Nenhum dado encontrado.")

    elif choice == "Receita vs Despesa":
        st.subheader("Comparação Receita vs Despesa do Mês Atual")

        mes_atual = datetime.now().strftime("%Y-%m")

        query_receita = f"SELECT SUM(valor) as total FROM contas_receber WHERE strftime('%Y-%m', vencimento) = '{mes_atual}'"
        receita_df = query_database(query_receita)
        receita_total = receita_df.iloc[0, 0] if not receita_df.empty and receita_df.iloc[0, 0] is not None else 0

        query_despesa = f"SELECT SUM(valor) as total FROM contas_pagar WHERE strftime('%Y-%m', vencimento) = '{mes_atual}'"
        despesa_df = query_database(query_despesa)
        despesa_total = despesa_df.iloc[0, 0] if not despesa_df.empty and despesa_df.iloc[0, 0] is not None else 0

        st.write(f"**Receita Total do Mês:** R$ {receita_total:,.2f}")
        st.write(f"**Despesa Total do Mês:** R$ {despesa_total:,.2f}")

        
        fig, ax = plt.subplots()
        ax.bar(["Receita", "Despesa"], [receita_total, despesa_total], color=["blue", "red"])
        ax.set_ylabel("Valor (R$)")
        ax.set_title("Receita vs Despesa do Mês Atual")
        st.pyplot(fig)

    elif choice == "Distribuição das Contas a Pagar":
        st.subheader("Distribuição das Contas a Pagar por Fornecedor")

        query = """
        SELECT fornecedor, SUM(valor) as total 
        FROM contas_pagar 
        GROUP BY fornecedor
        ORDER BY total DESC
        """
        df_fornecedores = query_database(query)

        if not df_fornecedores.empty:
            st.dataframe(df_fornecedores)

            
            fig, ax = plt.subplots()
            ax.pie(df_fornecedores["total"], labels=df_fornecedores["fornecedor"], autopct="%1.1f%%", startangle=140)
            ax.set_title("Distribuição das Contas a Pagar por Fornecedor")
            st.pyplot(fig)
        else:
            st.warning("Nenhum dado encontrado.")

if __name__ == "__main__":
    main()
