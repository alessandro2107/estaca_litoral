from fpdf import FPDF, XPos, YPos
from datetime import datetime
import os

def formatar_moeda(valor):
    """Formata valor como moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def limpar_texto(texto):
    """Remove caracteres especiais que fpdf nao suporta"""
    # Substituir caracteres acentuados por versoes sem acento
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

def gerar_orcamento(cliente, endereco_obra, budget_number, metros_lineares, 
                    preco_por_metro=38.00, valor_mobilizacao=0, 
                    nome_responsavel="Alesxandro Rodrigues Da Silva", valor_fixo=None,
                    com_nf=False, com_art=False, telefone_cliente="", 
                    valor_fixo_até_metros=None, metros_limite=None, preco_metros_excedentes=None):
    """
    Gera orcamento em PDF com dados dinamicos
    
    Parametros:
    - cliente: Nome do cliente
    - endereco_obra: Endereco da obra
    - budget_number: Numero do orcamento (ex: "25-2026")
    - metros_lineares: Quantidade de metros lineares
    - preco_por_metro: Preco por metro (padrao: 38.00)
    - valor_mobilizacao: Valor de mobilizacao (padrao: 500.00)
    - nome_responsavel: Nome de quem assina (padrao: "Alesxandro Rodrigues Da Silva")
    - valor_fixo: Valor fixo do orcamento (se fornecido, substitui calculos automaticos)
    - com_nf: Se True, acrescenta 5% ao valor total para Nota Fiscal
    - com_art: Se True, acrescenta 5% ao valor total para ART
    - telefone_cliente: Telefone de contato do cliente
    - valor_fixo_até_metros: Valor fixo cobrado até o limite de metros (opcao 3)
    - metros_limite: Limite de metros para aplicar o valor fixo (opcao 3)
    - preco_metros_excedentes: Preco por metro dos metros acima do limite (opcao 3)
    """
    
    # Limpar textos
    cliente = limpar_texto(cliente)
    endereco_obra = limpar_texto(endereco_obra)
    nome_responsavel = limpar_texto(nome_responsavel)
    
    # Calculos
    if valor_fixo is not None:
        # Opcao 2: Se valor fixo foi fornecido, usa esse valor
        valor_perfuracao = valor_fixo
        total_geral = valor_perfuracao + valor_mobilizacao
    elif valor_fixo_até_metros is not None and metros_limite is not None and preco_metros_excedentes is not None:
        # Opcao 3: Valor fixo ate X metros, depois preco por metro
        if metros_lineares <= metros_limite:
            # Se nao ultrapassou o limite, so cobra o valor fixo
            valor_perfuracao = valor_fixo_até_metros
        else:
            # Se ultrapassou, soma o valor fixo + valor_por_metro dos excedentes
            metros_excedentes = metros_lineares - metros_limite
            valor_excedentes = metros_excedentes * preco_metros_excedentes
            valor_perfuracao = valor_fixo_até_metros + valor_excedentes
        
        total_geral = valor_perfuracao + valor_mobilizacao
    else:
        # Opcao 1: Calculo automatico
        valor_perfuracao = metros_lineares * preco_por_metro
        total_geral = valor_perfuracao + valor_mobilizacao
    
    # Calcular taxas condicionais
    taxa_nf = total_geral * 0.22 if com_nf else 0  # Nota Fiscal: 22% do valor total
    taxa_art = 1500 if com_art else 0  # ART: valor fixo de R$ 1500
    total_taxas = taxa_nf + taxa_art
    total_com_taxas = total_geral + total_taxas
    
    entrada_40 = total_com_taxas * 0.4
    conclusao_60 = total_com_taxas * 0.6
    
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    # Criar PDF
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # Configurar fonte
    pdf.set_font("Helvetica", "", 10)
    
    # ====== CABECALHO ======
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 8, "ESTACA LITORAL", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "CNPJ: 45.248.080/0001-37", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 5, "Avenida Sambaiatuba, 2107 - Jockey Clube, Sao Vicente - SP, CEP 11365-140", 
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 5, "(13) 99678-8265 | rodriguesalesxandro@gmail.com", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 5, "www.estacalitoral.com.br | IG: @estaca_straus", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    # Linha divisoria
    pdf.set_draw_color(44, 62, 80)
    pdf.line(20, pdf.get_y() + 2, 190, pdf.get_y() + 2)
    pdf.ln(8)
    
    # ====== TITULO ======
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(242, 242, 242)
    pdf.cell(0, 8, "ORCAMENTO DE PRESTACAO DE SERVICOS", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
    pdf.ln(6)
    
    # ====== INFORMACOES BASICAS ======
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
    pdf.multi_cell(0, 4, 
        f"Perfuracao  para {Qnt_estacas} estacas do tipo Strauss, com diametro de 30 cm e profundidade {profundidade} mts conforme especificado.")
    pdf.ln(5)
    
    # ====== TABELA DE VALORES ======
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(44, 62, 80)
    pdf.set_text_color(255, 255, 255)
    
    # Cabecalho da tabela
    pdf.cell(80, 7, "Descricao do Item", border=1, fill=True)
    pdf.cell(25, 7, "Qtd.", border=1, align="C", fill=True)
    pdf.cell(30, 7, "Preco Unit.", border=1, align="R", fill=True)
    pdf.cell(35, 7, "Valor Total", border=1, align="R", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Linhas da tabela
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    
    # Adaptando a exibicao conforme o tipo de calculo
    if valor_fixo_até_metros is not None and metros_limite is not None and preco_metros_excedentes is not None:
        # Opcao 3: Valor fixo até X metros, depois preço por metro
        if metros_lineares <= metros_limite:
            # Nao ultrapassou o limite
            pdf.cell(80, 6, f"Perfuracao Estaca Strauss (Valor ate {metros_limite}m)", border=1)
            pdf.cell(25, 6, f"{metros_lineares} m", border=1, align="C")
            pdf.cell(30, 6, "---", border=1, align="R")
            pdf.cell(35, 6, formatar_moeda(valor_perfuracao), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            # Ultrapassou o limite - mostrar detalhes
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
        # Opcao 1 e 2: Calculo automatico ou valor fixo
        pdf.cell(80, 6, "Perfuracao Estaca Strauss", border=1)
        if valor_fixo is None and metros_lineares > 0:
            # Opcao 1: mostrar metros e preco unitário
            pdf.cell(25, 6, f"{metros_lineares} m", border=1, align="C")
            pdf.cell(30, 6, f"{formatar_moeda(preco_por_metro)}/m", border=1, align="R")
        else:
            # Opcao 2: valor fixo, nao mostrar breakdown
            pdf.cell(25, 6, "1", border=1, align="C")
            pdf.cell(30, 6, "---", border=1, align="R")
        
        pdf.cell(35, 6, formatar_moeda(valor_perfuracao), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.cell(80, 6, "Mobilizacao/Desmobilizacao", border=1)
    pdf.cell(25, 6, "1", border=1, align="C")
    pdf.cell(30, 6, "---", border=1, align="R")
    pdf.cell(35, 6, formatar_moeda(valor_mobilizacao), border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Taxas adicionais
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
    
    # ====== SECAO 4: RESPONSABILIDADES ======
    #pdf.set_font("Helvetica", "B", 11)
    #pdf.set_text_color(44, 62, 80)
    #pdf.cell(0, 6, "4. RESPONSABILIDADES DO CLIENTE", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    #pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 4, 
     "Nota: Nota Fiscal acresce 22% ao valor total.")
    pdf.ln(8)
    
    # ====== ASSINATURAS ======
    pdf.set_font("Helvetica", "", 9)
    y_sig = pdf.get_y() + 5
    
    # Linha de assinatura esquerda
    pdf.set_xy(25, y_sig)
    pdf.line(25, y_sig + 15, 75, y_sig + 15)
    pdf.set_xy(25, y_sig + 16)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(50, 4, "ESTACA LITORAL", align="C")
    pdf.ln(4)
    pdf.set_x(25)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(50, 3, nome_responsavel, align="C")
    
    # Linha de assinatura direita
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
    pdf.cell(0, 5, "01 viagem de areia media lavada (aproximadamente 6 m³)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    
    # Brita
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "Brita:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "01 viagem de pedra n. 1 (aproximadamente 6 m³)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
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
    
    # Salvar PDF na Área de Trabalho
    desktop_path = os.path.expanduser("~\\Desktop")
    # Se o Desktop padrão não existir, usar a Área de Trabalho do OneDrive
    if not os.path.exists(desktop_path):
        desktop_path = os.path.expanduser("~\\OneDrive\\Área de Trabalho")
    # Criar o diretório se não existir
    os.makedirs(desktop_path, exist_ok=True)
    output_path = os.path.join(desktop_path, f'{limpar_texto(cliente)}_orcamento.pdf')
    pdf.output(output_path)
    print(f"Sucesso! Orcamento gerado com sucesso!")
    print(f"  Arquivo: {os.path.basename(output_path)}")
    print(f"  Caminho: {output_path}")
    print(f"\nDetalhes:")
    print(f"  Cliente: {cliente}")
    print(f"  Numero orcamento: {budget_number}")
    
    if valor_fixo_até_metros is not None and metros_limite is not None:
        print(f"  Opcao: Valor fixo ate {metros_limite}m + metros excedentes")
        print(f"  Valor fixo: {formatar_moeda(valor_fixo_até_metros)}")
        print(f"  Metros lineares: {metros_lineares}m")
        if metros_lineares > metros_limite:
            metros_excedentes = metros_lineares - metros_limite
            print(f"  Metros excedentes: {metros_excedentes}m x {formatar_moeda(preco_metros_excedentes)}/m")
    elif valor_fixo is not None:
        print(f"  Opcao: Valor fixo")
    else:
        print(f"  Opcao: Calculo automatico")
        print(f"  Metros lineares: {metros_lineares}m")
        print(f"  Preco por metro: {formatar_moeda(preco_por_metro)}/m")
    
    print(f"  Total geral: {formatar_moeda(total_geral)}")
    if valor_mobilizacao:
        print(f"  (Com mobilizacao: {formatar_moeda(valor_mobilizacao)})")

# ====== EXECUCAO INTERATIVA ======
if __name__ == "__main__":
    print("\n" + "="*60)
    print("GERADOR DE ORCAMENTOS - ESTACA LITORAL")
    print("="*60 + "\n")
    
    # Solicitar dados do cliente
    cliente = input("Nome do cliente: ").strip()
    if not cliente:
        cliente = "Cliente Padrao"
    
    endereco_obra = input("Endereco da obra: ").strip()
    if not endereco_obra:
        endereco_obra = "Endereco a confirmar"
    
    telefone_cliente = input("Telefone do cliente: ").strip()

    Qnt_estacas = input("Quantidade de estacas a serem perfuradas: ").strip()

    profundidade = input("Profundidade das estacas (ex: 6m, 8m, 10m): ").strip()
    
    # Gerar numero do orcamento automaticamente com data no formato ddmmyyyy
    budget_number = datetime.now().strftime("%d%m%Y")
    
    # Menu de opcoes de calculo
    print("\nOpcoes de calculo disponíveis:")
    print("  1 - Calculo automatico (metros x preco + mobilizacao)")
    print("  2 - Valor fixo (valor total unico)")
    print("  3 - Valor fixo ate X metros, depois preco por metro excedente")
    
    opcao = input("Escolha a opcao (1, 2 ou 3, padrao: 3): ").strip() or "3"
    
    valor_fixo = None
    valor_fixo_até_metros = None
    metros_limite = None
    preco_metros_excedentes = None
    metros_lineares = None
    preco_por_metro = None
    valor_mobilizacao = None
    
    if opcao == "3":
        # Opcao 3: Valor fixo até X metros, depois preço por metro
        while True:
            try:
                valor_fixo_até_metros = float(input("Valor fixo (cobrado até o limite de metros): "))
                if valor_fixo_até_metros <= 0:
                    print("  [Valor deve ser maior que 0]")
                    continue
                break
            except ValueError:
                print("  [Valor invalido, tente novamente]")
        
        while True:
            try:
                metros_limite = float(input("Metros limite para valor fixo (ex: 250 ou 300): "))
                if metros_limite <= 0:
                    print("  [Metros deve ser maior que 0]")
                    continue
                break
            except ValueError:
                print("  [Metros invalido, tente novamente]")
        
        while True:
            try:
                entrada = input("Preco por metro dos metros excedentes (padrao: 38.00): ").strip()
                preco_metros_excedentes = float(entrada or "38.00")
                if preco_metros_excedentes <= 0:
                    print("  [Valor deve ser maior que 0]")
                    continue
                break
            except ValueError:
                print("  [Valor invalido, tente novamente]")
        
        while True:
            try:
                entrada = input("Valor de mobilizacao : ").strip()
                valor_mobilizacao = float(entrada or "0.00")
                if valor_mobilizacao < 0:
                    print("  [Valor nao pode ser negativo]")
                    continue
                break
            except ValueError:
                print("  [Valor invalido, tente novamente]")
        
        while True:
            try:
                metros_lineares = float(input("Metros lineares do projeto: "))
                if metros_lineares <= 0:
                    print("  [Metros deve ser maior que 0]")
                    continue
                break
            except ValueError:
                print("  [Metros invalido, tente novamente]")
    
    elif opcao == "2":
        # Opcao 2: Valor fixo
        try:
            valor_fixo = float(input("Valor fixo do orcamento: "))
        except ValueError:
            print("  [Valor invalido, usaremos calculo automatico]")
            opcao = "1"
        
        # Permitir adicionar taxa de transporte na opção 2
        try:
            valor_mobilizacao = float(input("Taxa de transporte de equipamento (padrao: 0.00): ").strip() or "0.00")
        except ValueError:
            valor_mobilizacao = 0.00
    
    if opcao == "1":
        # Opcao 1: Calculo automatico
        try:
            metros_lineares = float(input("Metros lineares: "))
        except ValueError:
            metros_lineares = 30
            print(f"  [Usando valor padrao: {metros_lineares}]")
        
        try:
            preco_por_metro = float(input("Preco por metro (padrao: 38.00): ").strip() or "38.00")
        except ValueError:
            preco_por_metro = 38.00
        
        try:
            valor_mobilizacao = float(input("Valor de mobilizacao (padrao: 0.00): ").strip() or "0.00")
        except ValueError:
            valor_mobilizacao = 0.00
    
    nome_responsavel = input("Nome do responsavel (padrao: Alesxandro Rodrigues Da Silva): ").strip()
    if not nome_responsavel:
        nome_responsavel = "Alesxandro Rodrigues Da Silva"
    
    # Perguntar sobre Nota Fiscal e ART
    com_nf = input("Incluir Nota Fiscal? (s/n, padrao: n): ").strip().lower() == 's'
    com_art = input("Incluir ART (Anotacao de Responsabilidade Tecnica)? (s/n, padrao: n): ").strip().lower() == 's'
    
    # Garantir que todas as variáveis têm valores padrão
    if metros_lineares is None:
        metros_lineares = 0
    if preco_por_metro is None:
        preco_por_metro = 38.00
    if valor_mobilizacao is None:
        valor_mobilizacao = 0.00
    
    print("\nGerando orcamento...\n")
    gerar_orcamento(
        cliente=cliente,
        endereco_obra=endereco_obra,
        budget_number=budget_number,
        metros_lineares=metros_lineares,
        preco_por_metro=preco_por_metro,
        valor_mobilizacao=valor_mobilizacao,
        nome_responsavel=nome_responsavel,
        valor_fixo=valor_fixo,
        com_nf=com_nf,
        com_art=com_art,
        telefone_cliente=telefone_cliente,
        valor_fixo_até_metros=valor_fixo_até_metros,
        metros_limite=metros_limite,
        preco_metros_excedentes=preco_metros_excedentes
    )