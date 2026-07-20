import ast

class GrafoPreparo:
    def __init__(self):
        self.adjacencias = {}
        self.passos_originais = {}

    def adicionar_passo(self, id_passo, texto):
        if id_passo not in self.adjacencias:
            self.adjacencias[id_passo] = []
            self.passos_originais[id_passo] = texto

    def adicionar_dependencia(self, passo_anterior, passo_posterior):
        if passo_anterior in self.adjacencias and passo_posterior in self.adjacencias:
            self.adjacencias[passo_anterior].append(passo_posterior)

    def ordenacao_topologica(self):
        visitados = {}
        pilha_recursao = {}
        ordem = []
        
        for vertice in self.adjacencias:
            visitados[vertice] = False
            pilha_recursao[vertice] = False
            
        for vertice in self.adjacencias:
            if visitados[vertice] == False:
                # DFS
                tem_ciclo = self._busca_em_profundidade(vertice, visitados, pilha_recursao, ordem)
                if tem_ciclo == True:
                    return None, "[ALERTA DE INVESTIGAÇAO] Dependência circular (Deadlock) detectada na receita!"
                    
        return ordem, "Fluxo de preparo validado com sucesso."
        
    def _busca_em_profundidade(self, vertice, visitados, pilha_recursao, ordem):
        visitados[vertice] = True
        pilha_recursao[vertice] = True
        
        for vizinho in self.adjacencias[vertice]:
            if visitados[vizinho] == False:
                tem_ciclo = self._busca_em_profundidade(vizinho, visitados, pilha_recursao, ordem)
                if tem_ciclo == True:
                    return True
            elif pilha_recursao[vizinho] == True:
                return True # ciclo encontrado
                
        pilha_recursao[vertice] = False
        ordem.insert(0, vertice)
        return False

def converter_steps_para_grafo(string_passos):
    
    # le a string do CSV e converte para o Grafo
    if string_passos == "" or string_passos == "[]":
        return None
        
    try:
        lista_passos = ast.literal_eval(string_passos)
    except:
        return None
        
    grafo = GrafoPreparo()
    tamanho = len(lista_passos)
    
    # cria todos os vertices
    for i in range(tamanho):
        grafo.adicionar_passo(i, lista_passos[i])
        
    # cria as arestas
    for i in range(1, tamanho):
        grafo.adicionar_dependencia(i - 1, i)
        
    return grafo



# MOTOR MODULO 5: OFICINA DE PRODUÇAO (DEPENDENCIAS ENTRE RECEITAS)
class GrafoMenuDoDia:
    def __init__(self):
        self.adjacencias = {}
        self.nomes_receitas = {}

    def adicionar_preparo(self, id_receita, nome_receita):
        if id_receita not in self.adjacencias:
            self.adjacencias[id_receita] = []
            self.nomes_receitas[id_receita] = nome_receita

    def adicionar_dependencia(self, id_pre_requisito, id_final):
        if id_pre_requisito in self.adjacencias and id_final in self.adjacencias:
            if id_final not in self.adjacencias[id_pre_requisito]:
                self.adjacencias[id_pre_requisito].append(id_final)

    def listar_pre_requisitos(self, id_alvo):
        pre_requisitos = []
        for id_receita, dependentes in self.adjacencias.items():
            if id_alvo in dependentes:
                pre_requisitos.append(id_receita)
        return pre_requisitos

    def ordenacao_topologica(self):
        visitados = {}
        pilha_recursao = {}
        ordem = []
        
        for vertice in self.adjacencias:
            visitados[vertice] = False
            pilha_recursao[vertice] = False
            
        for vertice in self.adjacencias:
            if visitados[vertice] == False:
                tem_ciclo = self._busca_em_profundidade(vertice, visitados, pilha_recursao, ordem)
                if tem_ciclo == True:
                    return None, "[ERRO GRAVE] Inconsistência detectada! Existe um ciclo de dependência entre as preparações (Ex: A depende de B, que depende de A)."
                    
        return ordem, "Sequência viável de preparo gerada com sucesso."
        
    def _busca_em_profundidade(self, vertice, visitados, pilha_recursao, ordem):
        visitados[vertice] = True
        pilha_recursao[vertice] = True
        
        for vizinho in self.adjacencias[vertice]:
            if visitados[vizinho] == False:
                tem_ciclo = self._busca_em_profundidade(vizinho, visitados, pilha_recursao, ordem)
                if tem_ciclo == True:
                    return True
            elif pilha_recursao[vizinho] == True:
                return True 
                
        pilha_recursao[vertice] = False
        ordem.insert(0, vertice)
        return False

    def identificar_receitas_isoladas(self):
        isolados = []
        todos_nos = set(self.adjacencias.keys())
        
        nos_com_entrada = set()
        for origem in self.adjacencias:
            for destino in self.adjacencias[origem]:
                nos_com_entrada.add(destino)
                
        for no in todos_nos:
            if len(self.adjacencias[no]) == 0 and no not in nos_com_entrada:
                isolados.append(no)
                
        return isolados