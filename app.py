import streamlit as st
import os
from datetime import datetime
from io import BytesIO
from fpdf import FPDF, XPos, YPos

# ============ FUNÇÕES AUXILIARES ============

def formatar_moeda(valor):
    """Formata valor como moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def limpar_texto(texto):
    """Remove caracteres especiais que fpdf nao suporta"""
    mapa = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e',
        'í': 'i', 'ì': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u', 'ù': 'u',
        'ç': 'c',
        'Á': 'A', 'À': 'A', 'Â': 'A', 'Ã': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E',
        'Í': 'I', 'Ì': 'I',
        'Ó': 'O', 'Ò': 'O', 'Ô': 'O', 'Õ': 'O',
        'Ú': 'U', 'Ù': 'U',
        'Ç': 'C'
    }
    for char, replacement in mapa.items():
        texto = texto.replace(char, replacement)
    return texto

def gerar_orcamento_pdf(cliente, endereco_obra, budget_number, metros_lineares, 
                        preco_por_metro=38.00, valor_mobilizacao=0, 
                        nome_responsavel="Alesxandro Rodrigues Da Silva", valor_fixo=None,
                        com_nf=False, com_art=False, telefone_cliente="", 
                        Qnt_estacas="", profundidade="",
                        valor_fixo_até_metros=None, metros_limite=None, preco_metros_excedentes=None):
    """
    Gera orçamento em PDF e retorna em BytesIO
    """
    
    # Limpar textos
    cliente = limpar_texto(cliente)
    endereco_obra = limpar_texto(endereco_obra)
    nome_responsavel = limpar_texto(nome_responsavel)
    
    # Calculos
    if valor_fixo is not None:
        valor_perfuracao = valor_fixo
        total_geral = valor_perfuracao + valor_mobilizacao
    elif valor_fixo_até_metros is not None and metros_limite is not None and preco_metros_excedentes is not None:
        if metros_lineares <= metros_limite:
            valor_perfuracao = valor_fixo_até_metros
        else:
            metros_excedentes = metros_lineares - metros_limite
            valor_excedentes = metros_excedentes * preco_metros_excedentes
            valor_perfuracao = valor_fixo_até_metros + valor_excedentes
        total_geral = valor_perfuracao + valor_mobilizacao
    else:
        valor_perfuracao = metros_lineares * preco_por_metro
        total_geral = valor_perfuracao + valor_mobilizacao
    
    # Calcular taxas condicionais
    taxa_nf = total_geral * 0.22 if com_nf else 0
    taxa_art = 1500 if com_art else 0
    total_taxas = taxa_nf + taxa_art
    total_com_taxas = total_geral + total_taxas
    
    entrada_40 = total_com_taxas * 0.4
    conclusao_60 = total_com_taxas * 0.6
    
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    # Criar PDF em memória
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font("Helvetica", "", 10)
    
    # ====== CABEÇALHO ======
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 8, "ESTACA LITORAL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "CNPJ: 45.248.080/0001-37", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 5, "Avenida Sambaiatuba, 2107 - Jockey Clube, Sao Vicente - SP, CEP 11365-140", 
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 5, "(13) 99678-8265 | rodriguesalesxandro@gmail.com", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 5, "www.estacalitoral.com.br | IG: @estaca_straus", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    # Linha divisória
    pdf.set_draw_color(44, 62, 80)
    pdf.line(20, pdf.get_y() + 2, 190, pdf.get_y() + 2)
    pdf.ln(8)
    
    # ====== TITULO ======
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(242, 242, 242)
    pdf.cell(0, 8, "ORCAMENTO DE PRESTACAO DE SERVICOS", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
    pdf.ln(6)
    
    # ====== INFORMAÇÕES BÁSICAS ======
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(40, 6, "Orcamento N.:", border=0)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, budget_number, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(40, 6, "Data:", border=0)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, data_atual, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(40, 6, "Cliente:", border=0)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, cliente, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    
    if telefone_cliente:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(40, 6, "Telefone:", border=0)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, telefone_cliente, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(40, 6, "Endereco da Obra:", border=0)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, endereco_obra, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(6)
    
    # ====== SECAO 1: ESCOPO ======
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 6, "1. ESCOPO DOS SERVICOS", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Helvetica", "", 9.5)
    escopo = f"Perfuracao para {Qnt_estacas} estacas do tipo Strauss, com diametro de 30 cm"
    if profundidade:
        escopo += f" e profundidade {profundidade} mts conforme especificado."
    else:
        escopo += " conforme especificado."
    pdf.multi_cell(0, 4, escopo)
    pdf.ln(5)
    
    # ====== TABELA DE VALORES ======
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(44, 62, 80)
    pdf.set_text_color(255, 255, 255)
    
    pdf.cell(80, 7, "Descricao do Item", border=1, fill=True)
    pdf.cell(25, 7, "Qtd.", border=1, align="C", fill=True)
    pdf.cell(30, 7, "Preco Unit.", border=1, align="R", fill=True)
    pdf.cell(35, 7, "Valor Total", border=1, align="R", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    
    if valor_fixo_até_metros is not None and metros_limite is not None and preco_metros_excedentes is not None:
        if metros_lineares <= metros_limite:
            pdf.cell(80, 6, f"Perfuracao Estaca Strauss (Valor ate {metros_limite}m)", border=1)
            pdf.cell(25, 6, f"{metros_lineares} m", border=1, align="C")
            pdf.cell(30, 6, "---", border=1, align="R")
            pdf.cell(35, 6, formatar_moeda(valor_perfuracao), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            metros_excedentes = metros_lineares - metros_limite
            pdf.cell(80, 6, f"Perfuracao - Valor (ate {metros_limite}m)", border=1)
            pdf.cell(25, 6, f"{metros_limite} m", border=1, align="C")
            pdf.cell(30, 6, "---", border=1, align="R")
            pdf.cell(35, 6, formatar_moeda(valor_fixo_até_metros), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            pdf.cell(80, 6, f"Perfuracao - Metros excedentes ({metros_excedentes}m)", border=1)
            pdf.cell(25, 6, f"{metros_excedentes} m", border=1, align="C")
            pdf.cell(30, 6, f"{formatar_moeda(preco_metros_excedentes)}/m", border=1, align="R")
            pdf.cell(35, 6, formatar_moeda(metros_excedentes * preco_metros_excedentes), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.cell(80, 6, "Perfuracao Estaca Strauss", border=1)
        if valor_fixo is None and metros_lineares > 0:
            pdf.cell(25, 6, f"{metros_lineares} m", border=1, align="C")
            pdf.cell(30, 6, f"{formatar_moeda(preco_por_metro)}/m", border=1, align="R")
        else:
            pdf.cell(25, 6, "1", border=1, align="C")
            pdf.cell(30, 6, "---", border=1, align="R")
        
        pdf.cell(35, 6, formatar_moeda(valor_perfuracao), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.cell(80, 6, "Mobilizacao/Desmobilizacao", border=1)
    pdf.cell(25, 6, "1", border=1, align="C")
    pdf.cell(30, 6, "---", border=1, align="R")
    pdf.cell(35, 6, formatar_moeda(valor_mobilizacao), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    if com_nf:
        pdf.cell(80, 6, "Nota Fiscal (22%)", border=1)
        pdf.cell(25, 6, "", border=1, align="C")
        pdf.cell(30, 6, "---", border=1, align="R")
        pdf.cell(35, 6, formatar_moeda(taxa_nf), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    if com_art:
        pdf.cell(80, 6, "ART - Anotacao de Responsabilidade Tecnica ", border=1)
        pdf.cell(25, 6, "", border=1, align="C")
        pdf.cell(30, 6, "---", border=1, align="R")
        pdf.cell(35, 6, formatar_moeda(taxa_art), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Total
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(249, 249, 249)
    pdf.cell(80, 7, "", border=1, fill=True)
    pdf.cell(25, 7, "", border=1, fill=True)
    pdf.cell(30, 7, "TOTAL GERAL:", border=1, align="R", fill=True)
    pdf.cell(35, 7, formatar_moeda(total_com_taxas), border=1, align="R", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    if valor_fixo_até_metros is not None and metros_limite is not None and preco_metros_excedentes is not None:
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.set_text_color(102, 102, 102)
        pdf.multi_cell(0, 3, f"Apos {metros_limite} metros lineares, sera cobrado o valor excedente de {formatar_moeda(preco_metros_excedentes)} por metro perfurado.")
        pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    # ====== SECAO 2: CONDICOES DE PAGAMENTO ===
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 6, "2. CONDICOES DE PAGAMENTO", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_fill_color(232, 244, 248)
    pdf.ln(2)
    tex_pagamento = f"Meios: Dinheiro ou PIX. (13) 996788265 |  Forma: 40% de entrada ({formatar_moeda(entrada_40)}) e 60% na conclusao ({formatar_moeda(conclusao_60)})."
    pdf.multi_cell(0, 5, tex_pagamento, fill=True)
    
    pdf.ln(3)
    notas = []
    if com_nf:
        notas.append(f"Nota Fiscal (22%): +{formatar_moeda(taxa_nf)}")
    if com_art:
        notas.append(f"ART (fixo): +{formatar_moeda(taxa_art)}")
    
    if notas:
        nota_adicionais = "Adicionais inclusos: " + " | ".join(notas)
        pdf.set_fill_color(230, 248, 255)
        pdf.multi_cell(0, 4, nota_adicionais, fill=True)
        pdf.ln(3)
    else:
        pdf.set_fill_color(230, 248, 255)
        pdf.multi_cell(0, 4, "Nota: Este orcamento nao inclui Nota Fiscal nem ART (Anotacao de Responsabilidade Tecnica).", fill=True)
        pdf.ln(3)
    
    # ====== SECAO 3: PRAZOS ======
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 6, "3. PRAZOS E GARANTIA", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "- Inicio: A combinar com o cliente.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    pdf.cell(0, 5, "- Garantia: 05 (cinco) anos pelos servicos prestados.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 4, "Nota: Nota Fiscal acresce 22% ao valor total\nART acresse R$ 1500,00 ao valor total.")
    pdf.ln(8)
    
    # ====== ASSINATURAS ======
    pdf.set_font("Helvetica", "", 9)
    y_sig = pdf.get_y() + 5
    
    pdf.set_xy(25, y_sig)
    pdf.line(25, y_sig + 15, 75, y_sig + 15)
    pdf.set_xy(25, y_sig + 16)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(50, 4, "ESTACA LITORAL", align="C")
    pdf.ln(4)
    pdf.set_x(25)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(50, 3, nome_responsavel, align="C")
    
    pdf.set_xy(115, y_sig)
    pdf.line(115, y_sig + 15, 165, y_sig + 15)
    pdf.set_xy(115, y_sig + 16)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(50, 4, "CONTRATANTE", align="C")
    pdf.ln(4)
    pdf.set_x(115)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(50, 3, cliente, align="C")
    
    # ====== NOVA PAGINA 2: RESPONSABILIDADES E MATERIAIS ======
    pdf.add_page()
    
    # Titulo da pagina
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(242, 242, 242)
    pdf.cell(0, 8, "RESPONSABILIDADES E FORNECIMENTO DE MATERIAIS", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
    pdf.ln(6)
    
    # ====== RESPONSABILIDADES DO CLIENTE ======
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 6, "RESPONSABILIDADES DO CLIENTE", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)
    pdf.multi_cell(0, 5, 
        "Todos os materiais necessarios para a execucao dos servicos - como areia, pedra, cimento, ferro, agua e energia eletrica - serao de responsabilidade do cliente.\n\nTerreno limpo e piquetado nos pontos das estacas.")
    
    pdf.ln(2)
    pdf.multi_cell(0, 5,
        "Tambem sera necessario disponibilizar um espaco adequado (barracaao) para armazenamento dos materiais, bem como para que a equipe possa realizar a troca de roupas.")
    
    pdf.ln(4)
    
    # ====== MATERIAIS INICIAIS ======
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 6, "MATERIAIS INICIAIS PARA EXECUCAO", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.ln(2)
    
    # Areia
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "Areia:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "01 viagem de areia media lavada (aproximadamente 6 m3)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    
    # Brita
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "Brita:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "01 viagem de pedra n. 1 (aproximadamente 6 m3)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    
    # Ferragem
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "Ferragem:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "Cada estaca devera conter:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.cell(5, 4, "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(5, 4, "")
    pdf.cell(0, 4, "01 coluna com 4 ferros de 3 metros de comprimento", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(5, 4, "")
    pdf.cell(0, 4, "Estribos redondos com diametro maximo de 20 cm", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(5, 4, "")
    pdf.cell(0, 4, "Espacamento entre estribos: 20 cm", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    
    # Cimento
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "Cimento:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "50 (cinquenta) sacos para inicio dos servicos", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    
    # ====== ESPECIFICACAO DE CONSUMO ======
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 6, "ESPECIFICACAO DE CONSUMO DE MATERIAIS", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.ln(2)
    pdf.multi_cell(0, 5,
        "Para execucao de estrutura circular com 30 cm de diametro, considerando intervalo de 2 metros lineares, o consumo estimado eh:")
    
    pdf.ln(3)
    
    # Tabela de consumo
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(44, 62, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(100, 6, "Material", border=1, fill=True)
    pdf.cell(0, 6, "Consumo por 2 m lineares", border=1, align="C", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    
    pdf.cell(100, 6, "Areia media lavada", border=1)
    pdf.cell(0, 6, "4 latas", border=1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.cell(100, 6, "Brita n. 1", border=1)
    pdf.cell(0, 6, "6 latas", border=1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.cell(100, 6, "Cimento", border=1)
    pdf.cell(0, 6, "2 latas", border=1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Retornar PDF em BytesIO
    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes

# ============ CONFIGURAÇÃO STREAMLIT ============

st.set_page_config(
    page_title="Gerador de Orçamentos", 
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS para melhor responsividade
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .stColumns > div {
            min-width: 100% !important;
        }
    }
    .metric-card {
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Gerador de Orçamentos")
st.markdown("**Estaca Litoral**")
st.markdown("---")

# Criar abas
tab1, tab2 = st.tabs(["📊 Orçamento", "ℹ️ Sobre"])

with tab1:
    # Seção 1: Dados do Cliente e Obra
    with st.expander("👤 Dados do Cliente e Obra", expanded=True):
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.subheader("Cliente", divider=True)
            cliente = st.text_input("Nome do cliente", value="", placeholder="Ex: João Silva", key="cliente")
            telefone = st.text_input("Telefone", value="", placeholder="(13) 99999-9999", key="tel")
            endereco = st.text_input("Endereço da obra", value="", placeholder="Rua Exemplo, 123 - São Vicente", key="end")
        
        with col_right:
            st.subheader("Obra", divider=True)
            qnt_estacas = st.text_input("Quantidade de estacas", value="", placeholder="Ex: 10", key="est")
            profundidade = st.text_input("Profundidade", value="", placeholder="Ex: 8m", key="prof")
            numero_orcamento = st.text_input("Nº Orçamento", value=datetime.now().strftime("%d%m%Y"), key="nro")
    
    # Seção 2: Opções de Cálculo
    with st.expander("🧮 Opções de Cálculo", expanded=True):
        opcao = st.radio(
            "Escolha o modelo de cálculo:",
            ["Cálculo Automático (metros × preço)", "Valor Fixo", "Valor Fixo até X metros + excedentes"],
            index=2,
            horizontal=False
        )
        
        if opcao == "Cálculo Automático (metros × preço)":
            col1, col2 = st.columns(2)
            with col1:
                metros = st.number_input("Metros lineares", min_value=0.0, value=30.0, step=0.5, key="auto_m")
            with col2:
                preco_metro = st.number_input("Preço/metro (R$)", min_value=0.0, value=38.0, step=1.0, key="auto_p")
            
            valor_fixo = None
            valor_fixo_até_metros = None
            metros_limite = None
            preco_metros_exc = None
            
        elif opcao == "Valor Fixo":
            valor_fixo = st.number_input("Valor fixo do orçamento (R$)", min_value=0.0, value=1000.0, step=100.0, key="fixo_v")
            metros = 0
            preco_metro = 38.0
            valor_fixo_até_metros = None
            metros_limite = None
            preco_metros_exc = None
            
        else:  # Valor Fixo até X metros
            col1, col2, col3 = st.columns(3)
            with col1:
                valor_fixo_até_metros = st.number_input("Valor fixo (R$)", min_value=0.0, value=10000.0, step=500.0, key="fixo_x")
            with col2:
                metros_limite = st.number_input("Limite de metros", min_value=0.0, value=250.0, step=10.0, key="lim_m")
            with col3:
                preco_metros_exc = st.number_input("Preço/m excedente", min_value=0.0, value=38.0, step=1.0, key="exc_p")
            
            metros = st.number_input("Metros do projeto", min_value=0.0, value=300.0, step=0.5, key="tot_m")
            
            valor_fixo = None
            preco_metro = 38.0
    
    # Seção 3: Taxas e Responsável
    with st.expander("⚙️ Configurações Adicionais", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            valor_mobilizacao = st.number_input("Mobilização (R$)", min_value=0.0, value=0.0, step=100.0, key="mob")
        with col2:
            com_nf = st.checkbox("Nota Fiscal (+ 22%)", key="nf")
        with col3:
            com_art = st.checkbox("ART (+ R$ 1.500)", key="art")
        
        st.divider()
        nome_responsavel = st.text_input("Nome do responsável", value="Alesxandro Rodrigues Da Silva", key="resp")
    
    # Seção 4: Botão Gerar PDF
    st.divider()
    col_btn_1, col_btn_2 = st.columns([2, 1])
    
    with col_btn_1:
        if st.button("📄 Gerar PDF", use_container_width=True, type="primary", key="btn_pdf"):
            if not cliente:
                st.error("⚠️ Preencha o nome do cliente!")
            elif not endereco:
                st.error("⚠️ Preencha o endereço da obra!")
            else:
                try:
                    # Gerar PDF
                    pdf_bytes = gerar_orcamento_pdf(
                        cliente=cliente,
                        endereco_obra=endereco,
                        budget_number=numero_orcamento,
                        metros_lineares=metros,
                        preco_por_metro=preco_metro,
                        valor_mobilizacao=valor_mobilizacao,
                        nome_responsavel=nome_responsavel,
                        valor_fixo=valor_fixo,
                        com_nf=com_nf,
                        com_art=com_art,
                        telefone_cliente=telefone,
                        Qnt_estacas=qnt_estacas,
                        profundidade=profundidade,
                        valor_fixo_até_metros=valor_fixo_até_metros,
                        metros_limite=metros_limite,
                        preco_metros_excedentes=preco_metros_exc
                    )
                    
                    # Exibir botão de download
                    st.success("✅ Orçamento gerado com sucesso!")
                    
                    nome_arquivo = f"{limpar_texto(cliente)}.pdf"
                    
                    st.download_button(
                        label="⬇️ Baixar PDF",
                        data=pdf_bytes,
                        file_name=nome_arquivo,
                        mime="application/pdf",
                        use_container_width=True,
                        key="dl_pdf"
                    )
                    
                    # Exibir resumo
                    st.divider()
                    st.subheader("📊 Resumo do Orçamento")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("👤 Cliente", cliente[:20] + "..." if len(cliente) > 20 else cliente)
                    with col2:
                        st.metric("📌 Número", numero_orcamento)
                    with col3:
                        st.metric("📅 Data", datetime.now().strftime("%d/%m/%Y"))
                    
                except Exception as e:
                    st.error(f"❌ Erro ao gerar PDF: {str(e)}")

with tab2:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 📋 Sobre o App
        
        ### ✨ Funcionalidades:
        - ✅ Geração automática de orçamentos em PDF
        - ✅ Três modelos de cálculo diferentes
        - ✅ Opções de Nota Fiscal e ART
        - ✅ Download direto do PDF
        - ✅ Interface responsiva (móvel + desktop)
        
        ### 🚀 Como Usar:
        1. Preencha os dados do cliente e da obra
        2. Escolha um modelo de cálculo
        3. Configure as opções adicionais (se necessário)
        4. Clique em "Gerar PDF"
        5. Baixe o arquivo
        
        ### 📋 Modelos de Cálculo:
        
        **Automático:** metros lineares × preço por metro + mobilização
        
        **Fixo:** um valor fixo total
        
        **Fixo + Excedentes:** valor fixo até X metros, depois preço por metro
        """)
    
    with col1:
        st.markdown("""
        ---
        
        ### 🏢 Dados da Empresa
        
        **ESTACA LITORAL**
        
        - **CNPJ:** 45.248.080/0001-37
        - **Endereço:** Avenida Sambaiatuba, 2107  
          Jockey Clube, São Vicente - SP  
          CEP: 11365-140
        - **Telefone:** (13) 99678-8265
        - **Email:** rodriguesalesxandro@gmail.com
        - **Site:** www.estacalitoral.com.br
        - **Instagram:** @estaca_straus
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Dicas
        
        - Os PDFs incluem 2 páginas completas
        - Data é preenchida automaticamente
        - Todos os dados são processados localmente
        - Sem necessidade de enviar para servidor externo
        
        ### 🔧 Versão
        v1.0 - Streamlit + Python
        """)
