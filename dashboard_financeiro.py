# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# 1. CONFIGURAÇÕES DA PÁGINA
st.set_page_config(page_title="Nosso Controle Financeiro 🚗", layout="wide")

# Título Principal e Estilo
st.title("💰 Nosso Painel Financeiro Familiar")
st.markdown("Planejamento conjunto, controle de gastos e nossa meta rumo ao carro novo!")

# 2. INICIALIZAÇÃO DO BANCO DE DADOS TEMPORÁRIO (Session State)
# O Session State mantém as informações salvas enquanto a aba estiver aberta.
if 'transacoes' not in st.session_state:
    # Dados de exemplo para o painel não iniciar vazio
    dados_iniciais = [
        {"Data": "2026-05-01", "Tipo": "Receita", "Responsável": "Mauro", "Categoria": "Salário", "Valor": 6500.0, "Descrição": "Salário Mauro"},
        {"Data": "2026-05-01", "Tipo": "Receita", "Responsável": "Esposa", "Categoria": "Salário", "Valor": 5800.0, "Descrição": "Salário Esposa"},
        {"Data": "2026-05-03", "Tipo": "Despesa", "Responsável": "Ambos", "Categoria": "Moradia", "Valor": 2200.0, "Descrição": "Aluguel + Condomínio"},
        {"Data": "2026-05-05", "Tipo": "Despesa", "Responsável": "Mauro", "Categoria": "Alimentação", "Valor": 650.0, "Descrição": "Supermercado Mensal"},
        {"Data": "2026-05-10", "Tipo": "Despesa", "Responsável": "Esposa", "Categoria": "Transporte", "Valor": 350.0, "Descrição": "Combustível Semanal"},
        {"Data": "2026-05-12", "Tipo": "Despesa", "Responsável": "Ambos", "Categoria": "Lazer", "Valor": 400.0, "Descrição": "Jantar Especial"},
        {"Data": "2026-05-15", "Tipo": "Investimento", "Responsável": "Ambos", "Categoria": "Meta do Carro", "Valor": 2000.0, "Descrição": "Aporte para o Carro Novo"},
        {"Data": "2026-05-18", "Tipo": "Investimento", "Responsável": "Mauro", "Categoria": "Reserva de Emergência", "Valor": 1000.0, "Descrição": "Aporte Tesouro Direto"}
    ]
    st.session_state.transacoes = pd.DataFrame(dados_iniciais)

# Valor inicial guardado em poupança/investimentos para o carro
if 'guardado_carro' not in st.session_state:
    st.session_state.guardado_carro = 32000.0

# Conversão da coluna Data para datetime para evitar erros de ordenação
st.session_state.transacoes["Data"] = pd.to_datetime(st.session_state.transacoes["Data"])

# --- ABAS DO DASHBOARD ---
aba_visao_geral, aba_meta_carro, aba_cadastrar = st.tabs([
    "📊 Visão Geral e Gráficos", 
    "🚗 Meta do Carro Novo", 
    "💸 Lançar Ganhos e Gastos"
])

# =====================================================================
# ABA 1: VISÃO GERAL
# =====================================================================
with aba_visao_geral:
    df_atual = st.session_state.transacoes.copy()
    
    # Cálculos Rápidos para os Cards
    total_receitas = df_atual[df_atual["Tipo"] == "Receita"]["Valor"].sum()
    total_despesas = df_atual[df_atual["Tipo"] == "Despesa"]["Valor"].sum()
    total_investido = df_atual[df_atual["Tipo"] == "Investimento"]["Valor"].sum()
    saldo_final = total_receitas - total_despesas - total_investido
    
    # Exibição das Métricas Principais
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Ganhos", f"R$ {total_receitas:,.2f}", delta_color="normal")
    col2.metric("Total de Gastos", f"R$ {total_despesas:,.2f}", delta_color="inverse")
    col3.metric("Total Investido", f"R$ {total_investido:,.2f}")
    
    if saldo_final >= 0:
        col4.metric("Saldo Sobrando", f"R$ {saldo_final:,.2f}", delta="Superávit")
    else:
        col4.metric("Saldo Sobrando", f"R$ {saldo_final:,.2f}", delta="Atenção, deficit!", delta_color="inverse")

    st.markdown("---")
    
    # Gráficos de Distribuição
    cg1, cg2 = st.columns(2)
    
    with cg1:
        st.subheader("🍕 Onde estamos gastando?")
        df_despesas = df_atual[df_atual["Tipo"] == "Despesa"]
        if not df_despesas.empty:
            fig_pizza = px.pie(
                df_despesas, values="Valor", names="Categoria",
                title="Distribuição das Despesas por Categoria",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            st.plotly_chart(fig_pizza, use_container_width=True)
        else:
            st.info("Nenhuma despesa cadastrada ainda.")
            
    with cg2:
        st.subheader("👥 Divisão de Gastos e Receitas")
        # Gráfico comparando quem gerou receitas e despesas
        fig_barra = px.bar(
            df_atual, x="Responsável", y="Valor", color="Tipo",
            title="Comparativo de Movimentações por Responsável",
            barmode="group",
            color_discrete_map={"Receita": "#2ec4b6", "Despesa": "#e71d36", "Investimento": "#ff9f1c"}
        )
        st.plotly_chart(fig_barra, use_container_width=True)

# =====================================================================
# ABA 2: META DO CARRO NOVO
# =====================================================================
with aba_meta_carro:
    st.subheader("🚗 Acompanhamento do Nosso Carro Novo")
    st.markdown("Configure o valor do carro que vocês querem comprar e acompanhe a evolução das economias.")
    
    # Inputs de configuração da meta
    mc1, mc2 = st.columns(2)
    with mc1:
        valor_carro = st.number_input("Valor Estimado do Carro (R$):", value=85000.0, step=1000.0)
    with mc2:
        # Puxa o total já investido na categoria 'Meta do Carro' do histórico + valor inicial
        investimentos_historico = df_atual[(df_atual["Categoria"] == "Meta do Carro") & (df_atual["Tipo"] == "Investimento")]["Valor"].sum()
        total_acumulado = st.session_state.guardado_carro + investimentos_historico
        st.metric("Total Acumulado para o Carro", f"R$ {total_acumulado:,.2f}")
        
    # Barra de Progresso Visual (Gauge Chart do Plotly)
    percentual_concluido = min((total_acumulado / valor_carro) * 100, 100.0)
    
    fig_progresso = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = total_acumulado,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Progresso da Meta ({percentual_concluido:.1f}%)", 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [None, valor_carro], 'tickformat': "R$ ,.2f"},
            'bar': {'color': "#10b981"},
            'bgcolor': "#e5e7eb",
            'steps': [
                {'range': [0, valor_carro*0.5], 'color': '#fee2e2'},
                {'range': [valor_carro*0.5, valor_carro*0.8], 'color': '#fef3c7'},
                {'range': [valor_carro*0.8, valor_carro], 'color': '#d1fae5'}
            ]
        }
    ))
    st.plotly_chart(fig_progresso, use_container_width=True)
    
    # Calculadora de Projeção
    st.markdown("#### ⏳ Em quanto tempo vamos conquistar?")
    aporte_mensal = st.slider("Quanto conseguimos poupar juntos por mês (R$)?", min_value=500, max_value=8000, value=2000, step=100)
    
    falta_guardar = valor_carro - total_acumulado
    if falta_guardar > 0:
        meses_restantes = int(np.ceil(falta_guardar / aporte_mensal))
        st.success(f"Falta poupar **R$ {falta_guardar:,.2f}**. Mantendo o aporte de **R$ {aporte_mensal:,.2f}/mês**, vocês comprarão o carro em **{meses_restantes} meses**!")
    else:
        st.balloons()
        st.success("🎉 Parabéns! Vocês já atingiram o valor estipulado para a compra do carro novo!")

# =====================================================================
# ABA 3: CADASTRAR TRANSAÇÕES E TABELA DE DADOS
# =====================================================================
with aba_cadastrar:
    st.subheader("📝 Adicionar Nova Movimentação")
    
    # Formulário de Lançamento
    with st.form("form_transacao", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            data_input = st.date_input("Data do Lançamento:", datetime.today())
            tipo_input = st.selectbox("Tipo de Movimentação:", ["Receita", "Despesa", "Investimento"])
        with col_f2:
            resp_input = st.selectbox("Quem realizou?", ["Mauro", "Esposa", "Ambos"])
            valor_input = st.number_input("Valor (R$):", min_value=0.01, step=10.0)
        with col_f3:
            # Categorias dinâmicas com base no tipo selecionado
            if tipo_input == "Receita":
                categorias_disponiveis = ["Salário", "Rendimento", "Outros Ganhos"]
            elif tipo_input == "Despesa":
                categorias_disponiveis = ["Moradia", "Alimentação", "Transporte", "Lazer", "Saúde", "Outros Gastos"]
            else:
                categorias_disponiveis = ["Meta do Carro", "Reserva de Emergência", "Ações/Fundos", "Outros Investimentos"]
            
            cat_input = st.selectbox("Categoria:", categorias_disponiveis)
            desc_input = st.text_input("Descrição curta:", placeholder="Ex: Conta de luz, Compra do mês...")
            
        botao_salvar = st.form_submit_button("💾 Salvar Lançamento")
        
        if botao_salvar:
            # Cria a linha com os novos dados
            nova_linha = {
                "Data": pd.to_datetime(data_input),
                "Tipo": tipo_input,
                "Responsável": resp_input,
                "Categoria": cat_input,
                "Valor": valor_input,
                "Descrição": desc_input
            }
            # Adiciona ao session_state
            st.session_state.transacoes = pd.concat([st.session_state.transacoes, pd.DataFrame([nova_linha])], ignore_index=True)
            st.success("Lançamento adicionado com sucesso! Vá até a aba 'Visão Geral' para ver os gráficos atualizados.")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Nosso Histórico de Lançamentos")
    
    # Exibição da tabela de dados cadastrados
    df_tabela = st.session_state.transacoes.sort_values(by="Data", ascending=False).copy()
    
    # Formatação visual da tabela
    df_tabela["Data"] = df_tabela["Data"].dt.strftime("%d/%m/%Y")
    st.dataframe(df_tabela, use_container_width=True)
    
    # Opção para resetar os dados ou baixar o backup
    col_csv, col_reset = st.columns([4, 1])
    with col_csv:
        # Converter para CSV para download
        csv_data = st.session_state.transacoes.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Backup de Dados (CSV)",
            data=csv_data,
            file_name=f"financeiro_familiar_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    with col_reset:
        if st.button("🚨 Limpar Tudo", help="Apaga todos os registros para começar do zero"):
            st.session_state.transacoes = pd.DataFrame(columns=["Data", "Tipo", "Responsável", "Categoria", "Valor", "Descrição"])
            st.rerun()