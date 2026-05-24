class NoTrie:
    def __init__(self):
        self.filhos = {}
        self.fim_de_palavra = False
        self.ids_receitas = [] 

class ArvoreTrie:
    def __init__(self):
        self.raiz = NoTrie()

    def inserir(self, palavra, id_receita):
        no_atual = self.raiz
        for letra in palavra.lower():
            if letra not in no_atual.filhos:
                no_atual.filhos[letra] = NoTrie()
            no_atual = no_atual.filhos[letra]
        
        no_atual.fim_de_palavra = True
        no_atual.ids_receitas.append(id_receita)

    def buscar_por_prefixo(self, prefixo):
        no_atual = self.raiz
        for letra in prefixo.lower():
            if letra not in no_atual.filhos:
                return []
            no_atual = no_atual.filhos[letra]
        
        resultados_ids = []
        self._coletar_receitas(no_atual, resultados_ids)
        return resultados_ids

    def _coletar_receitas(self, no, resultados_ids):
        if no.fim_de_palavra:
            resultados_ids.extend(no.ids_receitas)
        
        for letra, no_filho in no.filhos.items():
            self._coletar_receitas(no_filho, resultados_ids)