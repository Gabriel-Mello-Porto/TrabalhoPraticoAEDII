class GrafoFluxo:
    def __init__(self, numero_locais):
        self.numero_vertices = numero_locais
        self.nomes_locais = [""] * numero_locais
        
        # inicializa a matriz de adjacencia com zeros
        self.matriz_capacidade = []
        for i in range(numero_locais):
            linha = [0] * numero_locais
            self.matriz_capacidade.append(linha)

    def definir_nome_local(self, indice, nome):
        self.nomes_locais[indice] = nome

    def adicionar_rota_capacidade(self, origem, destino, limite_pedidos):
        self.matriz_capacidade[origem][destino] = limite_pedidos
        self.matriz_capacidade[destino][origem] = 0

    def buscar_caminho_bfs(self, fonte, sumidouro, vetor_caminho):
        # 0 = nao visitado, 1 = visitadoa
        visitados = [0] * self.numero_vertices
        
        fila = []
        
        fila.append(fonte)
        visitados[fonte] = 1
        vetor_caminho[fonte] = -1

        while len(fila) > 0:
            vertice_atual = fila.pop(0)

            for vizinho in range(self.numero_vertices):
                if visitados[vizinho] == 0 and self.matriz_capacidade[vertice_atual][vizinho] > 0:
                    
                    if vizinho == sumidouro:
                        vetor_caminho[vizinho] = vertice_atual
                        return True
                    
                    fila.append(vizinho)
                    visitados[vizinho] = 1
                    vetor_caminho[vizinho] = vertice_atual
                    
        return False

    def calcular_fluxo_maximo(self, id_fonte, id_sumidouro):
        vetor_caminho = [-1] * self.numero_vertices
        
        fluxo_maximo_total = 0
        while self.buscar_caminho_bfs(id_fonte, id_sumidouro, vetor_caminho):
            
            # encontrar o gargalo
            capacidade_gargalo = 9999999
            vertice_atual = id_sumidouro
            
            while vertice_atual != id_fonte:
                origem_anterior = vetor_caminho[vertice_atual]
                capacidade_nesta_via = self.matriz_capacidade[origem_anterior][vertice_atual]
                
                if capacidade_nesta_via < capacidade_gargalo:
                    capacidade_gargalo = capacidade_nesta_via
                    
                vertice_atual = origem_anterior

            vertice_atual = id_sumidouro
            while vertice_atual != id_fonte:
                origem_anterior = vetor_caminho[vertice_atual]
                
                # desconta do caminho principal
                self.matriz_capacidade[origem_anterior][vertice_atual] = self.matriz_capacidade[origem_anterior][vertice_atual] - capacidade_gargalo
                
                # adiciona na aresta reversa
                self.matriz_capacidade[vertice_atual][origem_anterior] = self.matriz_capacidade[vertice_atual][origem_anterior] + capacidade_gargalo
                
                vertice_atual = origem_anterior

            # soma o que conseguiu passar pelo gargalo ao total do restaurante
            fluxo_maximo_total = fluxo_maximo_total + capacidade_gargalo

        return fluxo_maximo_total

# teste
if __name__ == "__main__":
    grafo = GrafoFluxo(6)
    
    grafo.definir_nome_local(0, "Cozinha Central (S)")
    grafo.definir_nome_local(1, "Triagem Norte")
    grafo.definir_nome_local(2, "Triagem Sul")
    grafo.definir_nome_local(3, "Distribuidor Expresso")
    grafo.definir_nome_local(4, "Distribuidor Lento")
    grafo.definir_nome_local(5, "Clientes Finais (T)")

    grafo.adicionar_rota_capacidade(0, 1, 16) 
    grafo.adicionar_rota_capacidade(0, 2, 13) 
    grafo.adicionar_rota_capacidade(1, 2, 10)
    grafo.adicionar_rota_capacidade(1, 3, 12)
    grafo.adicionar_rota_capacidade(2, 1, 4)
    grafo.adicionar_rota_capacidade(2, 4, 14)
    grafo.adicionar_rota_capacidade(3, 2, 9)
    grafo.adicionar_rota_capacidade(3, 5, 20) 
    grafo.adicionar_rota_capacidade(4, 3, 7)
    grafo.adicionar_rota_capacidade(4, 5, 4) 

    fonte = 0 
    sumidouro = 5 

    print("--- ANÁLISE DE CAPACIDADE E GARGALOS (Ford-Fulkerson) ---")
    print("Mapeando vias, capacidades logísticas e atualizando matriz residual...")
    
    total_simultaneo = grafo.calcular_fluxo_maximo(fonte, sumidouro)
    
    print(f"\nRESULTADO LOGÍSTICO:")
    print(f"-> A capacidade MÁXIMA de atendimento simultâneo da rede é: {total_simultaneo} pedidos/hora.")
    if total_simultaneo < (16 + 13): # a cozinha gera até 29
        print("-> ALERTA: Há um gargalo na rede. O restaurante produz mais do que os entregadores finais conseguem despachar!")