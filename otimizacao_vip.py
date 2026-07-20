def calcular_lucro_esperado(receita):
    # conta a quantidade de itens removendo colchetes e aspas da string original
    ingredientes_brutos = receita.ingredientes.strip("[]").replace("'", "").replace('"', '').split(", ")
    tags_brutas = receita.tags.strip("[]").replace("'", "").replace('"', '').split(", ")
    
    qtd_ingredientes = 0
    for i in ingredientes_brutos:
        if i != "":
            qtd_ingredientes = qtd_ingredientes + 1
            
    qtd_tags = 0
    for t in tags_brutas:
        if t != "":
            qtd_tags = qtd_tags + 1
    
    # cada ingrediente agrega R$ 8 de valor, e cada tecnica/tag agrega R$ 3
    lucro_estimado = (qtd_ingredientes * 8) + (qtd_tags * 3)
    
    # bonus se for uma receita rapida
    if receita.tempo_preparo <= 30:
        lucro_estimado = lucro_estimado + 15
        
    return lucro_estimado


def gerar_menu_vip_mochila(receitas, tempo_max_minutos):
    itens = []
    for rec in receitas:
        if rec.tempo_preparo > 0:
            itens.append(rec)
            
    n = len(itens)
    
    if n == 0 or tempo_max_minutos <= 0:
        return [], 0, 0

    dp = []
    for i in range(n + 1):
        linha = []
        for w in range(tempo_max_minutos + 1):
            linha.append(0)
        dp.append(linha)
    
    for i in range(1, n + 1):
        item_atual = itens[i - 1]
        peso_i = item_atual.tempo_preparo
        valor_i = calcular_lucro_esperado(item_atual)
        
        for w in range(tempo_max_minutos + 1):
            if peso_i <= w:
                opcao_ignorar = dp[i - 1][w]
                opcao_incluir = dp[i - 1][w - peso_i] + valor_i
                
                if opcao_incluir > opcao_ignorar:
                    dp[i][w] = opcao_incluir
                else:
                    dp[i][w] = opcao_ignorar
            else:
                dp[i][w] = dp[i - 1][w]
                
    menu_selecionado = []
    tempo_restante = tempo_max_minutos
    
    for i in range(n, 0, -1):
        if dp[i][tempo_restante] != dp[i - 1][tempo_restante]:
            receita_escolhida = itens[i - 1]
            menu_selecionado.append(receita_escolhida)
            
            tempo_restante = tempo_restante - receita_escolhida.tempo_preparo
            
    # calcula os totais finais
    lucro_total = dp[n][tempo_max_minutos]
    tempo_gasto = tempo_max_minutos - tempo_restante
    
    menu_selecionado.reverse()
    
    return menu_selecionado, lucro_total, tempo_gasto


def calcular_custo_e_avaliacao(receita):
    ingredientes_brutos = receita.ingredientes.strip("[]").replace("'", "").replace('"', '').split(", ")
    
    qtd_ingredientes = 0
    for i in ingredientes_brutos:
        if i != "":
            qtd_ingredientes = qtd_ingredientes + 1
    
    # custo simulado: R$ 15 de base + R$ 4 por ingrediente
    custo_producao = 15 + (qtd_ingredientes * 4)
    
    pontuacao = 50 + (qtd_ingredientes * 3)
    if 15 <= receita.tempo_preparo <= 45:
        pontuacao = pontuacao + 20 # pratos com tempo ideal ganham bonus
    
    if pontuacao > 100:
        avaliacao_final = 100
    else:
        avaliacao_final = pontuacao
    
    return custo_producao, avaliacao_final


def gerar_menu_vip_orcamento(receitas, orcamento_max):
    itens = []
    for rec in receitas:
        if rec.tempo_preparo > 0:
            itens.append(rec)
            
    n = len(itens)
    
    if n == 0 or orcamento_max <= 0:
        return [], 0, 0

    dp = []
    for i in range(n + 1):
        linha = []
        for w in range(orcamento_max + 1):
            linha.append(0)
        dp.append(linha)
    
    for i in range(1, n + 1):
        item_atual = itens[i - 1]
        custo_i, avaliacao_i = calcular_custo_e_avaliacao(item_atual)
        
        for w in range(orcamento_max + 1):
            if custo_i <= w:
                opcao_ignorar = dp[i - 1][w]
                opcao_incluir = dp[i - 1][w - custo_i] + avaliacao_i
                
                if opcao_incluir > opcao_ignorar:
                    dp[i][w] = opcao_incluir
                else:
                    dp[i][w] = opcao_ignorar
            else:
                dp[i][w] = dp[i - 1][w]
                
    menu_selecionado = []
    orcamento_restante = orcamento_max
    
    for i in range(n, 0, -1):
        if dp[i][orcamento_restante] != dp[i - 1][orcamento_restante]:
            receita_escolhida = itens[i - 1]
            menu_selecionado.append(receita_escolhida)
            
            custo_item, avaliacao_item = calcular_custo_e_avaliacao(receita_escolhida)
            orcamento_restante = orcamento_restante - custo_item
            
    pontuacao_total = dp[n][orcamento_max]
    custo_total_gasto = orcamento_max - orcamento_restante
    menu_selecionado.reverse()
    
    return menu_selecionado, pontuacao_total, custo_total_gasto


# teste
if __name__ == "__main__":
    class ReceitaMock:
        def __init__(self, nome, tempo_preparo, ingredientes, tags):
            self.nome = nome
            self.tempo_preparo = tempo_preparo
            self.ingredientes = ingredientes
            self.tags = tags

    pratos_teste = [
        ReceitaMock("Ovo Frito", 10, "['ovo', 'oleo', 'sal']", "['rapido', 'basico']"),
        ReceitaMock("Risoto de Funghi", 40, "['arroz', 'funghi', 'manteiga', 'queijo', 'caldo']", "['italiano', 'vegetariano', 'gourmet']"),
        ReceitaMock("Boeuf Bourguignon", 120, "['carne', 'vinho', 'cebola', 'cenoura', 'bacon', 'alho']", "['frances', 'lento', 'classico']"),
        ReceitaMock("Salada Caprese", 15, "['tomate', 'mussarela', 'manjericao', 'azeite']", "['frio', 'italiano', 'saudavel']")
    ]

    tempo_limite = 60

    print("--- OTIMIZAÇÃO DE CARDÁPIO VIP (MOCHILA 0/1) ---")
    print(f"Tempo limite do evento: {tempo_limite} minutos\n")
    
    menu_final, lucro, tempo_usado = gerar_menu_vip_mochila(pratos_teste, tempo_limite)
    
    print(f"Pratos selecionados pelo Algoritmo para maximizar o lucro:")
    for prato in menu_final:
        valor_calculado = calcular_lucro_esperado(prato)
        print(f" -> {prato.nome} (Leva {prato.tempo_preparo} min | Agrega R$ {valor_calculado} de valor)")
        
    print("-" * 46)
    print(f"LUCRO MÁXIMO PROJETADO: R$ {lucro}")
    print(f"TEMPO TOTAL COMPROMETIDO: {tempo_usado} minutos")