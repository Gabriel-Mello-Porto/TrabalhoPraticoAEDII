def gerar_menu_rapido_guloso(lista_receitas, tempo_maximo_menu):

    receitas_ordenadas = sorted(lista_receitas, key=lambda r: r.tempo_preparo)
    
    menu_selecionado = []
    tempo_total_gasto = 0
    
    for receita in receitas_ordenadas:
        if tempo_total_gasto + receita.tempo_preparo <= tempo_maximo_menu:
            menu_selecionado.append(receita)
            tempo_total_gasto += receita.tempo_preparo
        elif tempo_total_gasto >= tempo_maximo_menu:
            break
            
    return menu_selecionado, tempo_total_gasto


def gerar_menu_minimalista_guloso(lista_receitas, max_pratos):

    receitas_ordenadas = sorted(lista_receitas, key=lambda r: len(r.ingredientes.split(',')))
    
    menu_selecionado = []
    for i in range(min(max_pratos, len(receitas_ordenadas))):
        menu_selecionado.append(receitas_ordenadas[i])
        
    return menu_selecionado


def gerar_menu_multiplos_criterios(lista_receitas, tempo_maximo, categoria):

    receitas_filtradas = [r for r in lista_receitas if categoria in r.tags]
    
    return gerar_menu_rapido_guloso(receitas_filtradas, tempo_maximo)