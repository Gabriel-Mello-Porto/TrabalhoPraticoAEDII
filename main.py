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

def criar_banco_arvore_b(caminho_csv, arquivo_bin, arquivo_indice_b):
    print("Iniciando formatação e construção do banco de dados em disco...")
    
    if os.path.exists(arquivo_bin): os.remove(arquivo_bin)
    if os.path.exists(arquivo_indice_b): os.remove(arquivo_indice_b)
        
    arvore = ArvoreB_Disco(arquivo_indice_b, grau_minimo=3)
    receitas_memoria = []
    
    with open(caminho_csv, mode='r', encoding='utf-8') as arq_csv, open(arquivo_bin, mode='wb') as arq_bin:
        leitor = csv.DictReader(arq_csv)
        for linha in leitor:
            tempo = int(linha['minutes'])
            if tempo > 0:
                nova_receita = Receita(linha['id'], linha['name'], linha['ingredients'], tempo, linha['tags'])
                receitas_memoria.append(nova_receita)
                
                # Prepara binário
                dados_dict = {
                    'id': int(linha['id']), 
                    'nome': linha['name'], 
                    'ingredientes': linha['ingredients'], 
                    'tempo': tempo, 
                    'tags': linha['tags']
                }
                dados_bytes = json.dumps(dados_dict).encode('utf-8')
                tamanho_bytes = struct.pack('i', len(dados_bytes))
                
                # Offset (ponteiro) e escrita
                offset = arq_bin.tell()
                arq_bin.write(tamanho_bytes)
                arq_bin.write(dados_bytes)
                
                # Insere o offset direto na Árvore B que salva em disco!
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

def exibir_menu_principal():
    print("=" * 50)
    print("    MENU PRINCIPAL - RESTAURANTE DO JACQUIN")
    print("=" * 50)
    print("1. Modo Consulta Rápida e Livro de Receitas")
    print("2. Modo Chef - Menu Rápido (Algoritmo Guloso)")
    print("3. Modo Investigação - Checar Sabotagens (Tabela Hash)")
    print("4. Sair do Sistema")
    print("=" * 50)
    return input("Escolha uma opção: ")

def main():
    print("Iniciando o Sistema: Desafio na Cozinha do Jacquin...\n")

    arquivo_csv = 'dataset_cozinha_jacquin_200.csv'
    arquivo_binario = 'receitas.bin'
    arquivo_indice_b = 'indice_arvore_b.bin'

    print("Verificando banco de dados no disco...")
    if os.path.exists(arquivo_binario) and os.path.exists(arquivo_indice_b):
        escolha = input("Arquivos de banco detectados. Deseja [1] Usar banco existente ou [2] Recriar tudo do zero? ")
        if escolha == '1':
            print("Carregando apenas estruturas auxiliares na RAM. A Árvore B ficará em disco!")
            receitas = carregar_receitas_do_csv(arquivo_csv)
            arvore_b = ArvoreB_Disco(arquivo_indice_b) # Reconecta ao arquivo sem reconstruir
        else:
            receitas, arvore_b = criar_banco_arvore_b(arquivo_csv, arquivo_binario, arquivo_indice_b)
    else:
        receitas, arvore_b = criar_banco_arvore_b(arquivo_csv, arquivo_binario, arquivo_indice_b)

    # População das estruturas auxiliares (Trie, Hash, etc) que exigem RAM
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

    while True:
        opcao = exibir_menu_principal()

        if opcao == '1':
            while True:
                print("\n>> CONSULTA RÁPIDA E LIVRO DE RECEITAS <<")
                print("1. Listar todas as receitas")
                print("2. Buscar receitas por Nome/Prefixo     (Árvore Trie)")
                print("3. Buscar receitas por ID único         (Árvore B + Disco Binário)")
                print("4. Buscar receitas por Categoria        (Hash de Tags)")
                print("5. Buscar receitas por Ingredientes     (Índice Invertido via Hash)")
                print("0. Voltar ao menu anterior")
                sub_opcao_consulta = input("Escolha uma opção: ")

                if sub_opcao_consulta == '0':
                    print("\nVoltando ao menu principal...")
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
                            print("-" * 50 + "\n")
                    except ValueError:
                        print("Entrada inválida.\n")

                elif sub_opcao_consulta == '4':
                    categoria = input("Digite a categoria desejada (ex: vegan, main-ingredient, time-to-make, main-dish, 30-minutes-or-less): ")
                    ids_encontrados = indice_categorias.buscar(categoria)
                    if not ids_encontrados: 
                        print(f"Nenhuma receita encontrada na categoria '{categoria}'.\n")
                    else:
                        for id_rec in ids_encontrados: print(f"[{id_rec}] {mapa_receitas[id_rec].nome.title()}")

                elif sub_opcao_consulta == '5':
                    print("\n--- MÓDULO DE INGREDIENTES (Índice Invertido) ---")
                    pesquisa_ing = input("Qual ingrediente o Chef deseja utilizar? \n(0 para voltar)\n(ex: salt, pepper, garlic, onion, potato, carrot)\n:").strip()
                    if pesquisa_ing == '0':
                        print("\nVoltando ao menu anterior...")
                        continue
                        
                    ids_encontrados = indice_ingredientes.buscar(pesquisa_ing)
                    if not ids_encontrados:
                        print(f"Não há receitas registradas contendo '{pesquisa_ing}'.\n")
                    else:
                        print(f"\nForam encontradas {len(ids_encontrados)} receita(s) com '{pesquisa_ing}':\n")
                        for id_rec in ids_encontrados: 
                            print(f"[{id_rec}] {mapa_receitas[id_rec].nome.title()}")
                        print("-" * 50 + "\n")

                else:
                    print("Opção inválida na Consulta Rápida.\n")
            
        elif opcao == '2':
            while True:
                print("\n--- MODO CHEF (Recomendação e Otimização) ---")
                print("1. Menu Rápido               (Restrição: Tempo Máximo)")
                print("2. Menu Minimalista          (Métrica: Menos Ingredientes)")
                print("3. Menu Personalizado        (Múltiplos Critérios: Tempo + Categoria)")
                print("0. Voltar ao Menu Anterior")
                sub_opcao_chef = input("Escolha uma opção: ")
                
                if sub_opcao_chef == '0':
                    print("\nVoltando ao menu principal...")
                    break
                    
                elif sub_opcao_chef == '1':
                    try:
                        tempo_max = int(input("Qual o tempo máximo total para o menu em minutos?: "))
                        menu, tempo_gasto = gerar_menu_rapido_guloso(receitas, tempo_max)
                        if not menu: 
                            print("Tempo limite muito baixo.\n")
                        else:
                            print(f"\nMenu gerado com {len(menu)} pratos (Tempo total utilizado: {tempo_gasto} min):")
                            for prato in menu: print(f" - {prato.nome} ({prato.tempo_preparo} min)")
                            print()
                    except ValueError: 
                        print("Entrada inválida.\n")
                        
                elif sub_opcao_chef == '2':
                    try:
                        max_pratos = int(input("Quantas opções de receitas você quer que o sistema liste neste menu?: "))
                        menu = gerar_menu_minimalista_guloso(receitas, max_pratos)
                        if not menu: 
                            print("Nenhuma receita disponível.\n")
                        else:
                            print(f"\nMenu Minimalista gerado com {len(menu)} pratos:")
                            for prato in menu: 
                                qtd_ingredientes = len(prato.ingredientes.split(','))
                                print(f" - {prato.nome} ({qtd_ingredientes} ingredientes)")
                            print()
                    except ValueError: 
                        print("Entrada inválida.\n")
                        
                elif sub_opcao_chef == '3':
                    try:
                        categoria = input("Digite a categoria desejada (ex: vegan, main-ingredient, main-dish): ").strip()
                        tempo_max = int(input("Qual o tempo máximo total em minutos?: "))
                        menu, tempo_gasto = gerar_menu_multiplos_criterios(receitas, tempo_max, categoria)
                        if not menu: 
                            print("Nenhuma receita encontrada para esses critérios.\n")
                        else:
                            print(f"\nMenu Personalizado gerado com {len(menu)} pratos (Tempo total: {tempo_gasto} min):")
                            for prato in menu: print(f" - {prato.nome} ({prato.tempo_preparo} min)")
                            print()
                    except ValueError: 
                        print("Entrada inválida.\n")
                else:
                    print("Opção inválida no Modo Chef.\n")
                
        elif opcao == '3':
            while True:
                print("\n--- MODO INVESTIGAÇÃO (Tabela Hash) ---")
                print("1. Verificar integridade de receita específica por ID")
                print("2. Gerar Relatório Completo de Investigação (Varredura total)")
                print("3. Simular uma sabotagem (Injetar erro para teste)")
                print("0. Voltar ao Menu Anterior")
                sub_opcao = input("Escolha uma opção: ")
                
                if sub_opcao == '0':
                    print("\nVoltando ao menu principal...")
                    break
                elif sub_opcao == '1':
                    try:
                        id_alvo = int(input("Digite o ID único da receita: "))
                        if id_alvo in mapa_receitas:
                            _, msg = tabela_hash.verificar_integridade_unica(mapa_receitas[id_alvo])
                            print(f"\n[Resultado]: {msg}\n")
                        else:
                            print("Identificador não cadastrado no sistema.\n")
                    except ValueError:
                        print("ID inválido.\n")
                elif sub_opcao == '2':
                    print("\n[INFO] Iniciando varredura na Tabela Hash...")
                    tabela_hash.gerar_relatorio_investigacao(receitas)
                elif sub_opcao == '3':
                    if mapa_receitas:
                        print("\nEscolhendo memória RAM...")
                        id_teste = list(mapa_receitas.keys())[0]
                        rec = mapa_receitas[id_teste]
                        tempo_orig = rec.tempo_preparo
                        print(f" -> Receita escolhida: [{rec.id}] {rec.nome.title()}")
                        print(f" -> Tempo oficial no registro: {tempo_orig} minutos")
                        
                        print("\nInjetando erro (Sabotagem)...")
                        rec.tempo_preparo = 999
                        print(f" -> Novo tempo adulterado para: {rec.tempo_preparo} minutos")
                        
                        print("\nAcionando a segurança da Tabela Hash (Recalculando SHA-256)...")
                        _, msg = tabela_hash.verificar_integridade_unica(rec)
                        print(f" -> [ALARME DISPARADO]: {msg}")
                        
                        print("\nLimpando o erro...")
                        rec.tempo_preparo = tempo_orig
                        print(f" -> Tempo revertido com segurança para: {rec.tempo_preparo} minutos")
                        print("[INFO] Simulação de ataque concluída.\n")
                    else:
                        print("Nenhuma receita carregada na memória para testar.\n")
                else:
                    print("Opção inválida.\n")
                        
        elif opcao == '4':
            print("Encerrando o sistema.")
            break
        else:
            print("Opção inválida no menu principal.\n")

if __name__ == "__main__":
    main()