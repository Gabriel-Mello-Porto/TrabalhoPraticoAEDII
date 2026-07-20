import sys
import struct
import json
import os
import csv
from receita import Receita, carregar_receitas_do_csv
from trie import ArvoreTrie
from guloso import gerar_menu_rapido_guloso, gerar_menu_minimalista_guloso, gerar_menu_multiplos_criterios
from hash_table import TabelaHash
from indice_invertido import IndiceInvertidoHash
from arvore_b import ArvoreB_Disco

# IMPORTAÇoES DO T2
from grafo_cozinha import converter_steps_para_grafo, GrafoMenuDoDia
from grafo_logistica import construir_cidade_jacquin
from grafo_mst import GrafoInfraestrutura
from grafo_fluxo import GrafoFluxo
from otimizacao_vip import gerar_menu_vip_mochila, gerar_menu_vip_orcamento, calcular_custo_e_avaliacao

# cores
BLUE = '\033[94m'    # para conteudos do T1
GREEN = '\033[92m'   # para conteudos do T2
PURPLE = '\033[95m'  # para as estruturas/algoritmos
BOLD = '\033[1m'     # negrito para cabeçalhos
RESET = '\033[0m'    # reseta a formatação

def print_opcao(numero_texto, cor_texto, algoritmo=""):
    texto_formatado = f"{cor_texto}{numero_texto:<55}{RESET}"
    if algoritmo:
        texto_formatado += f" {PURPLE}{algoritmo}{RESET}"
    print(f"  {texto_formatado}")


# funçoes de banco de dados em disco
def criar_banco_arvore_b(caminho_csv, arquivo_bin, arquivo_indice_b):
    print("iniciando formatação e construção do banco de dados em disco...")
    
    if os.path.exists(arquivo_bin): os.remove(arquivo_bin)
    if os.path.exists(arquivo_indice_b): os.remove(arquivo_indice_b)
        
    arvore = ArvoreB_Disco(arquivo_indice_b, grau_minimo=3)
    receitas_memoria = []
    
    with open(caminho_csv, mode='r', encoding='utf-8') as arq_csv, open(arquivo_bin, mode='wb') as arq_bin:
        leitor = csv.DictReader(arq_csv)
        for linha in leitor:
            tempo = int(linha['minutes'])
            if tempo > 0:
                passos_str = linha.get('steps', "[]")
                nova_receita = Receita(linha['id'], linha['name'], linha['ingredients'], tempo, linha['tags'], passos_str)
                receitas_memoria.append(nova_receita)
                
                dados_dict = {
                    'id': int(linha['id']), 
                    'nome': linha['name'], 
                    'ingredientes': linha['ingredients'], 
                    'tempo': tempo, 
                    'tags': linha['tags'],
                    'passos': passos_str
                }
                dados_bytes = json.dumps(dados_dict).encode('utf-8')
                tamanho_bytes = struct.pack('i', len(dados_bytes))
                
                offset = arq_bin.tell()
                arq_bin.write(tamanho_bytes)
                arq_bin.write(dados_bytes)
                
                arvore.inserir(dados_dict['id'], offset)
                
    print("Banco de dados construído e Árvore B salva em disco com sucesso!\n")
    return receitas_memoria, arvore

def buscar_receita_no_disco(caminho_bin, offset):
    with open(caminho_bin, mode='rb') as arq:
        arq.seek(offset)
        bytes_tamanho = arq.read(4)
        tamanho = struct.unpack('i', bytes_tamanho)[0]
        bytes_dados = arq.read(tamanho)
        return json.loads(bytes_dados.decode('utf-8'))

# menu principal
def main():
    os.system("")
    print(f"\n{BOLD}Iniciando o Sistema: Desafio na Cozinha do Jacquin...{RESET}\n")

    arquivo_csv = 'dataset_cozinha_jacquin_200.csv'
    arquivo_binario = 'receitas.bin'
    arquivo_indice_b = 'indice_arvore_b.bin'

    print("Verificando banco de dados no disco...")
    if os.path.exists(arquivo_binario) and os.path.exists(arquivo_indice_b):
        escolha = input("Arquivos de banco detectados. Deseja [1] Usar banco existente ou [2] Recriar tudo do zero? ")
        if escolha == '1':
            print("Carregando apenas estruturas auxiliares na RAM. A Árvore B ficará em disco!")
            receitas = carregar_receitas_do_csv(arquivo_csv)
            arvore_b = ArvoreB_Disco(arquivo_indice_b) 
        else:
            receitas, arvore_b = criar_banco_arvore_b(arquivo_csv, arquivo_binario, arquivo_indice_b)
    else:
        receitas, arvore_b = criar_banco_arvore_b(arquivo_csv, arquivo_binario, arquivo_indice_b)

    trie = ArvoreTrie()
    tabela_hash = TabelaHash()
    indice_ingredientes = IndiceInvertidoHash()
    indice_categorias = IndiceInvertidoHash()
    mapa_receitas = {} 
    
    for receita in receitas:
        trie.inserir(receita.nome, receita.id)
        tabela_hash.registrar_receita(receita)
        
        ingredientes_limpos = receita.ingredientes.strip("[]").replace("'", "").replace('"', '').split(", ")
        for ing in ingredientes_limpos:
            indice_ingredientes.inserir(ing, receita.id)
            
        tags_limpas = receita.tags.strip("[]").replace("'", "").replace('"', '').split(", ")
        for tag in tags_limpas:
            indice_categorias.inserir(tag, receita.id)
            
        mapa_receitas[receita.id] = receita 

    # Inicializa motores persistentes dos Grafos
    menu_do_dia = GrafoMenuDoDia()
    cidade = construir_cidade_jacquin()

    while True:
        print(f"\n{BOLD}=================================================================={RESET}")
        print(f"{BOLD}            SISTEMA DE GESTÃO - RESTAURANTE DO JACQUIN            {RESET}")
        print(f"{BOLD}=================================================================={RESET}")
        print(f"  1. Modo Consulta Rápida      {BLUE}[Livro de Receitas]{RESET}")
        print(f"  2. Modo Chef                 {GREEN}[Planejamento & Menus]{RESET}")
        print(f"  3. Modo Logística            {GREEN}[Operação & Delivery]{RESET}")
        print(f"  4. Modo Investigação         {GREEN}[Auditoria & Inconsistências]{RESET}")
        print(f"  {BOLD}0. Sair do Sistema{RESET}")
        print(f"{BOLD}=================================================================={RESET}")
        
        opcao = input("\nEscolha um módulo para acessar: ")

        # 1. modo consulta rápida
        if opcao == '1':
            while True:
                print(f"\n{BOLD}--- 1. MODO CONSULTA RÁPIDA E LIVRO DE RECEITAS ---{RESET}")
                print_opcao("1. Listar todas as receitas", BLUE)
                print_opcao("2. Buscar receitas por Nome/Prefixo", BLUE, "(Árvore Trie)")
                print_opcao("3. Buscar receitas por ID único", BLUE, "(Árvore B + Disco Binário)")
                print_opcao("4. Buscar receitas por Categoria", BLUE, "(Hash de Tags)")
                print_opcao("5. Buscar receitas por Ingredientes", BLUE, "(Índice Invertido via Hash)")
                print(f"  {BOLD}0. Voltar ao menu anterior{RESET}")
                
                sub_opcao_consulta = input("\nEscolha uma opção: ")

                if sub_opcao_consulta == '0':
                    break
                elif sub_opcao_consulta == '1':
                    print(f"\n--- LIVRO DE RECEITAS ---")
                    for rec in receitas: print(f"[{rec.id}] {rec.nome.title()} ({rec.tempo_preparo} min)")
                elif sub_opcao_consulta == '2':
                    pesquisa = input("Digite o prefixo da receita: ")
                    ids_encontrados = trie.buscar_por_prefixo(pesquisa)
                    if not ids_encontrados: 
                        print("Nenhum resultado para o prefixo inserido.\n")
                    else:
                        for id_rec in ids_encontrados: print(mapa_receitas[id_rec])
                elif sub_opcao_consulta == '3':
                    try:
                        id_busca = int(input("Digite o ID único da receita para busca em DISCO: "))
                        offset = arvore_b.buscar(id_busca)
                        
                        if offset is None:
                            print("Identificador não localizado na Árvore B.\n")
                        else:
                            print(f"\n[Árvore B] Chave encontrada! Offset físico: Byte {offset}")
                            dados_disco = buscar_receita_no_disco(arquivo_binario, offset)
                            
                            print("--- DADOS EXTRAÍDOS DIRETAMENTE DO DISCO ---")
                            print(f"ID Selecionado : {dados_disco['id']}")
                            print(f"Nome do Prato  : {dados_disco['nome'].upper()}")
                            print(f"Tempo Preparo  : {dados_disco['tempo']} minutos")
                            print(f"Ingredientes   : {dados_disco['ingredientes']}")
                            print("-" * 50 + "\n")
                    except ValueError:
                        print("Entrada inválida.\n")
                elif sub_opcao_consulta == '4':
                    categoria = input("Digite a categoria desejada: ")
                    ids_encontrados = indice_categorias.buscar(categoria)
                    if not ids_encontrados: 
                        print(f"Nenhuma receita encontrada na categoria '{categoria}'.\n")
                    else:
                        for id_rec in ids_encontrados: print(f"[{id_rec}] {mapa_receitas[id_rec].nome.title()}")
                elif sub_opcao_consulta == '5':
                    pesquisa_ing = input("Qual ingrediente o Chef deseja utilizar? (0 para voltar): ").strip()
                    if pesquisa_ing == '0':
                        continue
                    ids_encontrados = indice_ingredientes.buscar(pesquisa_ing)
                    if not ids_encontrados:
                        print(f"Não há receitas registradas contendo '{pesquisa_ing}'.\n")
                    else:
                        print(f"\nEncontradas {len(ids_encontrados)} receita(s):\n")
                        for id_rec in ids_encontrados: 
                            print(f"[{id_rec}] {mapa_receitas[id_rec].nome.title()}")
                        print("-" * 50 + "\n")
                else:
                    print("Opção inválida na Consulta Rápida.\n")
            
        # 2. modo chef
        elif opcao == '2':
            while True:
                print(f"\n{BOLD}--- 2. MODO CHEF: PLANEJAMENTO ESTRATÉGICO ---{RESET}")
                print_opcao("1. Menu Rápido por Tempo", BLUE, "(Guloso)")
                print_opcao("2. Menu Minimalista de Ingredientes", BLUE, "(Guloso)")
                print_opcao("3. Menu Personalizado (Tempo + Cat)", BLUE, "(Guloso)")
                print_opcao("4. Menu VIP: Maximizar Lucro por Tempo", GREEN, "(Programaçao Dinamica)")
                print_opcao("5. Menu VIP: Maximizar Avaliação por Orçamento", GREEN, "(Programaçao Dinamica)")
                print_opcao("6. Menu VIP: Restrição de Despensa", GREEN, "(Filtro + Programaçao Dinamica)")
                print(f"  {BOLD}0. Voltar ao menu anterior{RESET}")
                
                sub_opcao_chef = input("\nEscolha uma opção: ")
                
                if sub_opcao_chef == '0':
                    break
                # logicas gulosas
                elif sub_opcao_chef == '1':
                    try:
                        tempo_max = int(input("Qual o tempo máximo total para o menu em minutos?: "))
                        menu, tempo_gasto = gerar_menu_rapido_guloso(receitas, tempo_max)
                        if not menu: print("Tempo limite muito baixo.\n")
                        else:
                            print(f"\nMenu gerado com {len(menu)} pratos (Tempo total: {tempo_gasto} min):")
                            for prato in menu: print(f" - {prato.nome} ({prato.tempo_preparo} min)")
                    except ValueError: print("Entrada inválida.\n")
                elif sub_opcao_chef == '2':
                    try:
                        max_pratos = int(input("Quantas opções de receitas neste menu?: "))
                        menu = gerar_menu_minimalista_guloso(receitas, max_pratos)
                        if not menu: print("Nenhuma receita disponível.\n")
                        else:
                            print(f"\nMenu Minimalista gerado com {len(menu)} pratos:")
                            for prato in menu: 
                                qtd_ingredientes = len(prato.ingredientes.split(','))
                                print(f" - {prato.nome} ({qtd_ingredientes} ingredientes)")
                    except ValueError: print("Entrada inválida.\n")
                elif sub_opcao_chef == '3':
                    try:
                        categoria = input("Digite a categoria desejada: ").strip()
                        tempo_max = int(input("Qual o tempo máximo total em minutos?: "))
                        menu, tempo_gasto = gerar_menu_multiplos_criterios(receitas, tempo_max, categoria)
                        if not menu: print("Nenhuma receita encontrada para esses critérios.\n")
                        else:
                            print(f"\nMenu Personalizado gerado (Tempo total: {tempo_gasto} min):")
                            for prato in menu: print(f" - {prato.nome} ({prato.tempo_preparo} min)")
                    except ValueError: print("Entrada inválida.\n")
                # logicas programação dinamica (mochila)
                elif sub_opcao_chef == '4':
                    try:
                        tempo_max = int(input("Qual o tempo máximo disponível em minutos? (ex: 180): "))
                        menu_vip, lucro, tempo_gasto = gerar_menu_vip_mochila(receitas, tempo_max)
                        if not menu_vip: print("restrição muito severa. nenhum prato selecionado.\n")
                        else:
                            print(f"\n>> MENU VIP GERADO COM SUCESSO <<")
                            print(f"-> Restrição: {tempo_max} min | Gasto: {tempo_gasto} min")
                            print(f"-> Lucro Máximo Alcançado: R$ {lucro},00\n")
                            for i, prato in enumerate(menu_vip, 1): print(f" {i}º -> [{prato.id}] {prato.nome.upper()} ({prato.tempo_preparo} min)")
                    except ValueError: print("Entrada inválida.\n")
                elif sub_opcao_chef == '5':
                    try:
                        orcamento_max = int(input("Qual o ORÇAMENTO MÁXIMO disponível em Reais? (ex: 500): "))
                        menu_vip, pontuacao, custo_gasto = gerar_menu_vip_orcamento(receitas, orcamento_max)
                        if not menu_vip: print("Orçamento muito baixo. Nenhum prato selecionado.\n")
                        else:
                            print(f"\n>> MENU VIP GERADO COM SUCESSO <<")
                            print(f"-> Restrição de Verba: R$ {orcamento_max},00 | Gasto: R$ {custo_gasto},00")
                            print(f"-> Pontuação Alcançada: {pontuacao} pontos VIP\n")
                            for i, prato in enumerate(menu_vip, 1):
                                custo_p, nota_p = calcular_custo_e_avaliacao(prato)
                                print(f" {i}º -> [{prato.id}] {prato.nome.upper()} (Custo: R${custo_p} | Nota: {nota_p}/100)")
                    except ValueError: print("Entrada inválida.\n")
                elif sub_opcao_chef == '6':
                    try:
                        print("\n[Dica] Digite os ingredientes em inglês separados por vírgula.")
                        entrada_ing = input("Quais ingredientes você tem na despensa?: ").strip()
                        if not entrada_ing: continue
                        
                        entrada_limpa = entrada_ing.replace("'", "").replace('"', '').replace('[', '').replace(']', '')
                        ingredientes_disp = set([i.strip().lower() for i in entrada_limpa.split(',') if i.strip()])
                        
                        receitas_viaveis = [rec for rec in receitas if set([i.strip().lower() for i in rec.ingredientes.strip("[]").replace("'", "").replace('"', '').split(", ") if i.strip()]).issubset(ingredientes_disp)]
                                
                        if not receitas_viaveis:
                            print("\n[!] AVISO: Nenhuma receita do banco pode ser feita APENAS com esses ingredientes.\n")
                        else:
                            print(f"\n[OK] Encontradas {len(receitas_viaveis)} receita(s) viáveis.")
                            tempo_max = int(input("Qual o TEMPO MÁXIMO para o preparo do menu? (ex: 120): "))
                            menu_vip, lucro, tempo_gasto = gerar_menu_vip_mochila(receitas_viaveis, tempo_max)
                            if not menu_vip: print("Tempo insuficiente.\n")
                            else:
                                print(f"\n>> MENU VIP 'DESPENSA RESTRITA' GERADO <<\n-> Lucro: R$ {lucro},00 | Tempo: {tempo_gasto} min\n")
                                for i, prato in enumerate(menu_vip, 1): print(f" {i}º -> [{prato.id}] {prato.nome.upper()} ({prato.tempo_preparo} min)")
                    except ValueError: print("Entrada inválida.\n")
                else: print("Opção inválida no Modo Chef.\n")

        # 3. modo logistica
        elif opcao == '3':
            while True:
                print(f"\n{BOLD}--- 3. MODO LOGÍSTICA E PRODUÇÃO ---{RESET}")
                print_opcao("1. Produção: Cadastrar prato no Menu do Dia", GREEN, "(DAG / Kahn)")
                print_opcao("2. Produção: Cadastrar dependência de preparo", GREEN, "(DAG / Kahn)")
                print_opcao("3. Produção: Consultar sequência correta", GREEN, "(DAG / Kahn)")
                print_opcao("4. Produção: Listar pré-requisitos de receita", GREEN, "(DAG / Kahn)")
                print_opcao("5. Produção: Organizar roteiro interno de receita", GREEN, "(DAG / Kahn)")
                print_opcao("6. Delivery: Calcular Rota de Entrega Padrão", GREEN, "(A*)")
                print_opcao("7. Delivery: Simular Bloqueio e Recalcular", GREEN, "(A*)")
                print_opcao("8. Infraestrutura: Planejar Pontos de Retirada", GREEN, "(AGM / Prim)")
                print_opcao("9. Infraestrutura: Capacidade Máxima do Sistema", GREEN, "(Fluxo Máximo / Ford-Fulkerson)")
                print(f"  {BOLD}0. Voltar ao menu anterior{RESET}")
                
                sub_opcao_log = input("\nEscolha uma opção: ")

                if sub_opcao_log == '0':
                    break
                # bloco DAG
                elif sub_opcao_log == '1':
                    try:
                        id_rec = int(input("Digite o ID da receita para adicionar ao menu: "))
                        if id_rec in mapa_receitas:
                            menu_do_dia.adicionar_preparo(id_rec, mapa_receitas[id_rec].nome)
                            print(f"[OK] Receita '{mapa_receitas[id_rec].nome.upper()}' adicionada ao Menu do Dia!")
                        else: print("Identificador não cadastrado no sistema.\n")
                    except ValueError: print("Entrada inválida.\n")
                elif sub_opcao_log == '2':
                    try:
                        print("\nAviso: As receitas já devem estar cadastradas no Menu do Dia (Opção 1).")
                        id_pre = int(input("ID da receita PRÉ-REQUISITO (feita primeiro): "))
                        id_fin = int(input("ID da receita FINAL (depende da outra): "))
                        if id_pre in menu_do_dia.adjacencias and id_fin in menu_do_dia.adjacencias:
                            menu_do_dia.adicionar_dependencia(id_pre, id_fin)
                            print("[OK] Dependência cadastrada com sucesso!")
                        else: print("[ERRO] Uma ou ambas as receitas não estão no Menu do Dia.\n")
                    except ValueError: print("Entrada inválida.\n")
                elif sub_opcao_log == '3':
                    if not menu_do_dia.adjacencias:
                        print("Menu do Dia vazio.\n")
                        continue
                    ordem, msg = menu_do_dia.ordenacao_topologica()
                    if ordem == None: print(f"\nNão é possível gerar sequência: {msg}\n")
                    else:
                        print("\n>> SEQUÊNCIA CORRETA DE PRODUÇÃO <<")
                        for i, id_rec in enumerate(ordem): print(f" {i + 1}º -> [{id_rec}] {menu_do_dia.nomes_receitas[id_rec].upper()}")
                elif sub_opcao_log == '4':
                    try:
                        id_alvo = int(input("Digite o ID da receita no Menu para checar pré-requisitos: "))
                        if id_alvo in menu_do_dia.adjacencias:
                            pre_reqs = menu_do_dia.listar_pre_requisitos(id_alvo)
                            if not pre_reqs: print("Pode ser feita a qualquer momento.\n")
                            else:
                                print(f"\nPara produzir '{menu_do_dia.nomes_receitas[id_alvo].upper()}', conclua ANTES:")
                                for pr in pre_reqs: print(f" -> [{pr}] {menu_do_dia.nomes_receitas[pr].upper()}")
                        else: print("Receita não cadastrada no Menu do Dia.\n")
                    except ValueError: print("Entrada inválida.\n")
                elif sub_opcao_log == '5':
                    try:
                        id_alvo = int(input("Digite o ID da receita para organizar a produção interna: "))
                        if id_alvo in mapa_receitas:
                            receita_escolhida = mapa_receitas[id_alvo]
                            grafo = converter_steps_para_grafo(receita_escolhida.passos)
                            if getattr(receita_escolhida, 'passos', "[]") == "[]" or not grafo:
                                print("Falha: Receita sem passos ou erro de conversão.\n")
                            else:
                                ordem_execucao, msg = grafo.ordenacao_topologica()
                                if ordem_execucao == None: print(f"\n[ALERTA DETECTADO] {msg}\n")
                                else:
                                    print("\n>> ROTEIRO DE EXECUÇÃO SEGURO <<")
                                    for i, idx in enumerate(ordem_execucao): print(f" {i + 1}º -> {grafo.passos_originais[idx]}")
                        else: print("Identificador não cadastrado no sistema.\n")
                    except ValueError: print("Entrada inválida.\n")
                # bloco A*
                elif sub_opcao_log in ['6', '7']:
                    max_x = max([int(id_no.split('_')[0]) for id_no in cidade.vertices.keys()])
                    max_y = max([int(id_no.split('_')[1]) for id_no in cidade.vertices.keys()])

                    # desenha o grid
                    print(f"\n{BOLD}--- MAPA DA CIDADE ---{RESET}")
                    for y in range(max_y + 1):
                        linha_visual = ""
                        for x in range(max_x + 1):
                            id_no = f"{x}_{y}"
                            if id_no in cidade.vertices:
                                nome_local = cidade.vertices[id_no]['nome']
                                if "Restaurante" in nome_local:
                                    linha_visual += f"{BLUE}[ R ]{RESET} "
                                elif "VIP" in nome_local:
                                    linha_visual += f"{GREEN}[ V ]{RESET} "
                                else:
                                    linha_visual += "[ + ] " # cruzamento comum
                            else:
                                linha_visual += "      " # espaço vazio se nao houver rua
                        print(linha_visual)
                    
                    print("\nLegenda: [ R ] Restaurante | [ V ] Cliente VIP | [ + ] Cruzamento")
                    print("-" * 55)
                    
                    origem = input("ID de saída (ex: 3_2): ")
                    destino = input("ID de entrega (ex: 6_4): ")
                                    
                    backup_arestas = None
                    no_bloqueado = ""
                    if sub_opcao_log == '7':
                        no_bloqueado = input("ID da rua bloqueada: ")
                        if no_bloqueado in cidade.adjacencias:
                            backup_arestas = cidade.adjacencias[no_bloqueado]
                            cidade.adjacencias[no_bloqueado] = {} 
                            print(f"[!] Rua {no_bloqueado} interditada!")
                    
                    rota, tempo_est = cidade.calcular_rota_a_estrela(origem, destino)
                    if rota:
                        print(f"\n-> ROTA ENCONTRADA! Tempo: {tempo_est} min.")
                        for i, id_no in enumerate(rota):
                            nome_local = cidade.vertices[id_no]['nome']
                            if i == 0: print(f"   [SAÍDA]   {nome_local} (ID: {id_no})")
                            elif i == len(rota)-1: print(f"   [CHEGADA] {nome_local} (ID: {id_no})")
                            else: print(f"     |-> Passar por: {nome_local} (ID: {id_no})")
                    else: print(f"\nErro: Destino inacessível!\n")
                    
                    if sub_opcao_log == '7' and backup_arestas:
                        cidade.adjacencias[no_bloqueado] = backup_arestas
                # bloco AGM & fluxo
                elif sub_opcao_log == '8':
                    qtd_vertices = len(cidade.vertices)
                    grafo_rede = GrafoInfraestrutura(qtd_vertices)
                    
                    mapa_str_para_int = {}
                    mapa_int_para_str = {}
                    
                    for indice, (id_str, dados) in enumerate(cidade.vertices.items()):
                        mapa_str_para_int[id_str] = indice
                        mapa_int_para_str[indice] = id_str
                        grafo_rede.definir_nome_local(indice, f"{dados['nome']} ({id_str})")

                    for id_origem, conexoes in cidade.adjacencias.items():
                        origem_int = mapa_str_para_int[id_origem]
                        for rua in conexoes:
                            destino_int = mapa_str_para_int[rua['destino']]
                            custo = rua['peso']
                            grafo_rede.adicionar_rota(origem_int, destino_int, custo)

                    print("\nCalculando a Árvore Geradora Mínima para toda a cidade (35 vértices)...")
                    rotas, custo_final = grafo_rede.calcular_menor_infraestrutura_prim()
                    
                    print("\n--- PLANEJAMENTO AGM (Prim) ---")
                    print(f"Foram calculadas {len(rotas)} conexões essenciais para interligar toda a cidade.")
                    print("Exibindo as 5 primeiras conexões sugeridas:")
                    for i in range(min(5, len(rotas))):
                        o, d, c = rotas[i]
                        print(f"Instalar conexão: {grafo_rede.nomes_locais[o]} <---> {grafo_rede.nomes_locais[d]} (Custo: {c})")
                    print("...")
                    print(f"\nCUSTO TOTAL DA OBRA PARA A CIDADE: {custo_final}\n")
                elif sub_opcao_log == '9':
                    qtd_vertices = len(cidade.vertices)
                    grafo_fluxo = GrafoFluxo(qtd_vertices)
                    
                    mapa_str_para_int = {}
                    for indice, (id_str, dados) in enumerate(cidade.vertices.items()):
                        mapa_str_para_int[id_str] = indice
                        grafo_fluxo.definir_nome_local(indice, dados['nome'])
                    
                    for id_origem, conexoes in cidade.adjacencias.items():
                        origem_int = mapa_str_para_int[id_origem]
                        for rua in conexoes:
                            destino_int = mapa_str_para_int[rua['destino']]
                            capacidade = rua['capacidade']
                            grafo_fluxo.adicionar_rota_capacidade(origem_int, destino_int, capacidade)

                    id_fonte_str = "3_2"
                    id_sumidouro_str = "0_0"
                    
                    fonte_int = mapa_str_para_int[id_fonte_str]
                    sumidouro_int = mapa_str_para_int[id_sumidouro_str]

                    print(f"\nCalculando fluxo do {cidade.vertices[id_fonte_str]['nome']} até o {cidade.vertices[id_sumidouro_str]['nome']}...")
                    total_simultaneo = grafo_fluxo.calcular_fluxo_maximo(fonte_int, sumidouro_int)
                    
                    print("\n--- CAPACIDADE MÁXIMA DA ROTA PRINCIPAL ---")
                    print(f"-> Escoamento Máximo até este cliente: {total_simultaneo} pedidos simultâneos.\n")
                else: print("Opção inválida.\n")

        # 4. modo investigacao e auditoria
        elif opcao == '4':
            while True:
                print(f"\n{BOLD}--- 4. MODO INVESTIGAÇÃO E AUDITORIA ---{RESET}")
                print_opcao("1. Hash: Verificar integridade de receita específica", BLUE, "(Tabela Hash)")
                print_opcao("2. Hash: Gerar Relatório Completo de Investigação", BLUE, "(Tabela Hash)")
                print_opcao("3. Hash: Simular Sabotagem (Injetar erro)", BLUE, "(Tabela Hash)")
                print_opcao("4. Grafos: Checar erros de dependência na Cozinha", GREEN, "(Ciclos DAG)")
                print_opcao("5. Grafos: Gerar Relatório de Gargalos Operacionais", GREEN, "(Fluxo Corte Mínimo)")
                print_opcao("6. Grafos: Checar Tarefas Desconexas no Menu", GREEN, "(DAG)")
                print_opcao("7. Grafos: Encontrar Bairros Inacessíveis", GREEN, "(Componentes Conexas via BFS)")
                print(f"  {BOLD}0. Voltar ao menu anterior{RESET}")
                
                sub_opcao_inv = input("\nEscolha uma opção: ")
                
                if sub_opcao_inv == '0':
                    break
                elif sub_opcao_inv == '1':
                    try:
                        id_alvo = int(input("Digite o ID único da receita: "))
                        if id_alvo in mapa_receitas:
                            _, msg = tabela_hash.verificar_integridade_unica(mapa_receitas[id_alvo])
                            print(f"\n[Resultado]: {msg}\n")
                        else: print("Identificador não cadastrado.\n")
                    except ValueError: print("ID inválido.\n")
                elif sub_opcao_inv == '2':
                    tabela_hash.gerar_relatorio_investigacao(receitas)
                elif sub_opcao_inv == '3':
                    if mapa_receitas:
                        id_teste = list(mapa_receitas.keys())[0]
                        rec = mapa_receitas[id_teste]
                        tempo_orig = rec.tempo_preparo
                        print(f"\nSabotando: [{rec.id}] {rec.nome.title()} (Oficial: {tempo_orig} min)")
                        rec.tempo_preparo = 999
                        _, msg = tabela_hash.verificar_integridade_unica(rec)
                        print(f" -> [ALARME DISPARADO]: {msg}")
                        rec.tempo_preparo = tempo_orig
                        print("[INFO] Simulação concluída, tempo revertido.\n")
                elif sub_opcao_inv == '4':
                    if not menu_do_dia.adjacencias:
                        print("O Menu do Dia está vazio. Nada para analisar.\n")
                        continue
                    ordem, msg = menu_do_dia.ordenacao_topologica()
                    if ordem == None: print(f"\n[ALERTA DETECTADO] SIM, HÁ CICLO: {msg}\n")
                    else: print("\n[OK] NÃO: O fluxo de dependências está validado e não possui ciclos.\n")
                elif sub_opcao_inv == '5':
                    qtd_vertices = len(cidade.vertices)
                    grafo_fluxo = GrafoFluxo(qtd_vertices)
                    
                    mapa_str_para_int = {}
                    for indice, (id_str, dados) in enumerate(cidade.vertices.items()):
                        mapa_str_para_int[id_str] = indice
                        grafo_fluxo.definir_nome_local(indice, dados['nome'])
                    
                    for id_origem, conexoes in cidade.adjacencias.items():
                        origem_int = mapa_str_para_int[id_origem]
                        for rua in conexoes:
                            destino_int = mapa_str_para_int[rua['destino']]
                            capacidade = rua['capacidade']
                            grafo_fluxo.adicionar_rota_capacidade(origem_int, destino_int, capacidade)

                    id_fonte_str = "3_2"
                    id_sumidouro_str = "0_0"
                    fonte_int = mapa_str_para_int[id_fonte_str]
                    sumidouro_int = mapa_str_para_int[id_sumidouro_str]

                    total_simultaneo = grafo_fluxo.calcular_fluxo_maximo(fonte_int, sumidouro_int)
                    
                    print("\n--- RELATÓRIO DE GARGALOS ---")
                    producao_total = 16 + 13
                    if total_simultaneo < producao_total:
                        print(f"[ALERTA] Represamento logístico. Produção: {producao_total} | Capacidade Rede: {total_simultaneo}.")
                    else:
                        print("[OK] A estrutura atual suporta 100% da demanda gerada.")
                    print("-" * 40 + "\n")
                elif sub_opcao_inv == '6':
                    if not menu_do_dia.adjacencias:
                        print("O Menu do Dia está vazio. Cadastre receitas no Módulo de Logística primeiro.\n")
                        continue
                        
                    print("\nAuditoria: Varrendo o Grafo de Dependências (DAG)...")
                    receitas_isoladas = menu_do_dia.identificar_receitas_isoladas()
                    
                    if not receitas_isoladas:
                        print("[OK] Todas as receitas estão conectadas no fluxo de produção.\n")
                    else:
                        print(f"[ALERTA] Foram encontradas {len(receitas_isoladas)} receita(s) isolada(s) (sem pré-requisitos e sem dependentes):")
                        for id_isolado in receitas_isoladas:
                            nome_prato = menu_do_dia.nomes_receitas[id_isolado]
                            print(f" -> [{id_isolado}] {nome_prato.upper()}")
                        print("-" * 50 + "\n")

                elif sub_opcao_inv == '7':
                    print("\nAuditoria: Mapeando Regiões da Cidade (Componentes Conexas via BFS)...")
                    
                    # inicio do hack de teste
                    simular = input("Deseja simular um bloqueio total na cidade (cortando ruas de 2_0 até 2_4)? (s/n): ").strip().lower()
                    
                    if simular == 's':
                        # corta as conexoes entre a coluna 2 e a coluna 3 do mapa de cima a baixo
                        for y in range(5):
                            n1 = f"2_{y}"
                            n2 = f"3_{y}"
                            # rompe a ida (2 -> 3)
                            cidade.adjacencias[n1] = [rua for rua in cidade.adjacencias[n1] if rua['destino'] != n2]
                            # rompe a volta (3 -> 2)
                            cidade.adjacencias[n2] = [rua for rua in cidade.adjacencias[n2] if rua['destino'] != n1]
                    # fim do hack de teste

                    # chama o algoritmo no grafo da cidade
                    regioes = cidade.identificar_regioes_isoladas()
                    
                    if len(regioes) == 1:
                        print(f"\n[OK] A infraestrutura é sólida. Todos os {len(regioes[0])} pontos da cidade estão conectados entre si!\n")
                    elif len(regioes) == 0:
                        print("\n[ALERTA] A cidade não possui nenhum cruzamento ou rua cadastrada.\n")
                    else:
                        print(f"\n[ALERTA GRAVE] Ruptura logística! A cidade está dividida em {len(regioes)} regiões isoladas que não se comunicam:\n")
                        
                        for i, regiao in enumerate(regioes, 1):
                            print(f"--- Região {i} (Contém {len(regiao)} ponto(s) isolados) ---")
                            amostra = regiao[:5]
                            nomes_locais = [cidade.vertices[no]['nome'] for no in amostra]
                            
                            print(f"Exemplos: {', '.join(nomes_locais)}")
                            if len(regiao) > 5:
                                print(f"... e mais {len(regiao) - 5} cruzamento(s).")
                            print()
                        print("\nCidade consertada!")    
                    
                    # restaura a cidade consertando o grafo completamente apos a simulacao
                    if simular == 's':
                        cidade = construir_cidade_jacquin()

                else: print("Opção inválida.\n")

        elif opcao == '0':
            print("\nEncerrando o sistema.")
            sys.exit(0)
        else:
            print(f"\n{BOLD}[!] Opção inválida. Tente novamente.{RESET}")

if __name__ == "__main__":
    main()