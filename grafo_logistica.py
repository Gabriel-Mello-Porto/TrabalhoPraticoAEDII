import math
import random
import heapq

class GrafoLogistica:
    def __init__(self):
        self.vertices = {} 
        self.adjacencias = {} 
        
    def adicionar_vertice(self, id_vertice, nome, x, y, tipo="cruzamento"):
        self.vertices[id_vertice] = {
            'nome': nome, 
            'x': x, 
            'y': y, 
            'tipo': tipo
        }
        if id_vertice not in self.adjacencias:
            self.adjacencias[id_vertice] = []
            
    def adicionar_aresta(self, origem, destino, peso, capacidade, bidirecional=True):
        self.adjacencias[origem].append({
            'destino': destino, 
            'peso': peso, 
            'capacidade': capacidade
        })
        if bidirecional:
            self.adjacencias[destino].append({
                'destino': origem, 
                'peso': peso, 
                'capacidade': capacidade
            })
            
    def imprimir_resumo_cidade(self):
        qtd_vertices = len(self.vertices)
        
        qtd_arestas_direcionadas = 0
        for conexoes in self.adjacencias.values():
            tamanho_da_lista = len(conexoes)
            qtd_arestas_direcionadas += tamanho_da_lista
            
        qtd_ruas = qtd_arestas_direcionadas // 2
        
        print(f"--- MAPA DA CIDADE GERADO ---")
        print(f"Total de Locais (Vértices) : {qtd_vertices}")
        print(f"Total de Ruas (Arestas)    : {qtd_ruas} ruas bidirecionais ({qtd_arestas_direcionadas} direcionais)")
        print("-" * 30)

    def heuristica_estimativa_tempo(self, id_atual, id_objetivo):
        x1 = self.vertices[id_atual]['x']
        y1 = self.vertices[id_atual]['y']
        x2 = self.vertices[id_objetivo]['x']
        y2 = self.vertices[id_objetivo]['y']
        
        distancia_reta = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        estimativa_minutos = (distancia_reta / 100.0) * 2.0
        return estimativa_minutos

    def calcular_rota_a_estrela(self, id_inicio, id_destino):
        if id_inicio not in self.vertices or id_destino not in self.vertices:
            return None, "Origem ou Destino inválidos."

        fila_prioridade = []
        heapq.heappush(fila_prioridade, (0, id_inicio))

        caminho_anterior = {}

        g_score = {vertice: float('inf') for vertice in self.vertices}
        g_score[id_inicio] = 0

        f_score = {vertice: float('inf') for vertice in self.vertices}
        f_score[id_inicio] = self.heuristica_estimativa_tempo(id_inicio, id_destino)

        while len(fila_prioridade) > 0:
            f_atual, id_atual = heapq.heappop(fila_prioridade)

            if id_atual == id_destino:
                rota_final = []
                tempo_total = g_score[id_destino]
                passo = id_atual
                
                while passo in caminho_anterior:
                    rota_final.append(passo)
                    passo = caminho_anterior[passo]
                rota_final.append(id_inicio)
                
                rota_final.reverse() 
                return rota_final, tempo_total

            for rua in self.adjacencias[id_atual]:
                id_vizinho = rua['destino']
                peso_rua = rua['peso']

                custo_tentativo = g_score[id_atual] + peso_rua

                if custo_tentativo < g_score[id_vizinho]:
                    caminho_anterior[id_vizinho] = id_atual
                    g_score[id_vizinho] = custo_tentativo
                    
                    estimativa = self.heuristica_estimativa_tempo(id_vizinho, id_destino)
                    f_score[id_vizinho] = custo_tentativo + estimativa
                    
                    heapq.heappush(fila_prioridade, (f_score[id_vizinho], id_vizinho))

        return None, "Não foi possível encontrar uma rota válida."
    
    def identificar_regioes_isoladas(self):
        visitados = set()
        componentes = []

        for vertice in self.vertices:
            if vertice not in visitados:
                componente_atual = []
                fila = [vertice]
                visitados.add(vertice)
                
                while fila:
                    atual = fila.pop(0)
                    componente_atual.append(atual)
                    
                    ruas_conectadas = self.adjacencias.get(atual, [])
                    for rua in ruas_conectadas:
                        id_vizinho = rua['destino']
                        
                        if id_vizinho not in visitados:
                            visitados.add(id_vizinho)
                            fila.append(id_vizinho)
                            
                componentes.append(componente_atual)
                
        return componentes


def construir_cidade_jacquin():
    grafo = GrafoLogistica()
    colunas = 7
    linhas = 5
    distancia_quarteirao = 100
    
    for x in range(colunas):
        for y in range(linhas):
            id_vertice = f"{x}_{y}"
            coord_x = x * distancia_quarteirao
            coord_y = y * distancia_quarteirao
            
            if x == 3 and y == 2:
                nome = "Restaurante Central"
                tipo = "restaurante"
            elif (x == 0 and y == 0) or (x == 6 and y == 4) or (x == 0 and y == 4):
                nome = f"Cliente VIP ({x},{y})"
                tipo = "cliente"
            else:
                nome = f"Cruzamento {x}-{y}"
                tipo = "cruzamento"
                
            grafo.adicionar_vertice(id_vertice, nome, coord_x, coord_y, tipo)
            
    random.seed(42) 
    
    for x in range(colunas):
        for y in range(linhas):
            id_atual = f"{x}_{y}"
            
            if x < colunas - 1:
                id_direita = f"{x+1}_{y}"
                peso = random.randint(2, 8)
                capacidade = random.randint(1, 5)
                grafo.adicionar_aresta(id_atual, id_direita, peso, capacidade)
                
            if y < linhas - 1:
                id_cima = f"{x}_{y+1}"
                peso = random.randint(2, 8)
                capacidade = random.randint(1, 5)
                grafo.adicionar_aresta(id_atual, id_cima, peso, capacidade)
                
    return grafo

# teste 
if __name__ == "__main__":
    cidade = construir_cidade_jacquin()
    cidade.imprimir_resumo_cidade()
    
    print("\n--- TESTE DO MÓDULO 8: LOGÍSTICA DE ENTREGAS (A*) ---")
    
    origem_teste = "3_2" 
    destino_teste = "0_0"
    
    nome_origem = cidade.vertices[origem_teste]['nome']
    nome_destino = cidade.vertices[destino_teste]['nome']
    
    print(f"Solicitando rota de: [{nome_origem}] PARA [{nome_destino}]")
    
    rota, tempo = cidade.calcular_rota_a_estrela(origem_teste, destino_teste)
    
    if rota:
        print(f"-> ROTA ENCONTRADA COM SUCESSO! Tempo estimado de viagem: {tempo} minutos.")
        print("-> Passos do GPS (Nós percorridos):")
        
        for i in range(len(rota)):
            id_no = rota[i]
            nome_local = cidade.vertices[id_no]['nome']
            if i == 0:
                print(f"   [SAÍDA]  {nome_local} (ID: {id_no})")
            elif i == len(rota) - 1:
                print(f"   [CHEGADA]{nome_local} (ID: {id_no})")
            else:
                print(f"     |-> Passar por: {nome_local} (ID: {id_no})")
    else:
        print("Erro:", tempo) # 'tempo' carrega a mensagem de erro se a rota for None