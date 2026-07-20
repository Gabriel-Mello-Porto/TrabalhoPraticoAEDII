class GrafoInfraestrutura:
    def __init__(self, numero_locais):
        self.numero_vertices = numero_locais
        # vetor para armazenar o nome das regioes (tamanho fixo)
        self.nomes_locais = [""] * numero_locais
        
        # inicializa a matriz de adjacencia com zeros (vazia) 
        self.matriz_adjacencia = []
        for i in range(numero_locais):
            linha = [0] * numero_locais
            self.matriz_adjacencia.append(linha)

    def definir_nome_local(self, indice, nome):
        self.nomes_locais[indice] = nome

    def adicionar_rota(self, origem, destino, custo):
        self.matriz_adjacencia[origem][destino] = custo
        self.matriz_adjacencia[destino][origem] = custo

    def calcular_menor_infraestrutura_prim(self):
        visitados = [0] * self.numero_vertices
        
        visitados[0] = 1
        
        arestas_selecionadas = 0
        custo_total = 0
        rotas_escolhidas = []

        while arestas_selecionadas < (self.numero_vertices - 1):
            
            minimo = 9999999 
            vertice_origem = -1
            vertice_destino = -1

            # procura a menor aresta que conecta um vertice visitado a um não visitado
            for i in range(self.numero_vertices):
                if visitados[i] == 1: 
                    for j in range(self.numero_vertices):
                        if visitados[j] == 0 and self.matriz_adjacencia[i][j] != 0:
                            if self.matriz_adjacencia[i][j] < minimo:
                                minimo = self.matriz_adjacencia[i][j]
                                vertice_origem = i
                                vertice_destino = j

            if vertice_origem != -1 and vertice_destino != -1:
                visitados[vertice_destino] = 1 
                rotas_escolhidas.append((vertice_origem, vertice_destino, minimo))
                custo_total = custo_total + minimo
                arestas_selecionadas = arestas_selecionadas + 1
            else:
                break

        return rotas_escolhidas, custo_total

# teste
if __name__ == "__main__":
    grafo_rede = GrafoInfraestrutura(5)
    
    grafo_rede.definir_nome_local(0, "Cozinha Central")
    grafo_rede.definir_nome_local(1, "Retirada Zona Norte")
    grafo_rede.definir_nome_local(2, "Retirada Zona Sul")
    grafo_rede.definir_nome_local(3, "Retirada Centro")
    grafo_rede.definir_nome_local(4, "Retirada Leste")

    grafo_rede.adicionar_rota(0, 1, 10)
    grafo_rede.adicionar_rota(0, 2, 20)
    grafo_rede.adicionar_rota(0, 3, 5)
    grafo_rede.adicionar_rota(1, 3, 15)
    grafo_rede.adicionar_rota(1, 4, 8)
    grafo_rede.adicionar_rota(2, 3, 12)
    grafo_rede.adicionar_rota(3, 4, 25)

    rotas, custo_final = grafo_rede.calcular_menor_infraestrutura_prim()

    print("--- PLANEJAMENTO DE INFRAESTRUTURA (MST) ---")
    for k in range(len(rotas)):
        origem = rotas[k][0]
        destino = rotas[k][1]
        custo = rotas[k][2]
        
        nome_origem = grafo_rede.nomes_locais[origem]
        nome_destino = grafo_rede.nomes_locais[destino]
        
        print(f"Instalar conexão: {nome_origem} <---> {nome_destino} (Custo: {custo})")
        
    print("-" * 44)
    print(f"CUSTO TOTAL DA OBRA: {custo_final}")