class NoIndice:
    def __init__(self, chave):
        self.chave = chave
        self.ids_receitas = []

class IndiceInvertidoHash:
    def __init__(self, tamanho=1024):
        self.tamanho = tamanho
        self.tabela = [[] for _ in range(tamanho)]

    def _hash(self, chave):
        soma = sum(ord(char) for char in chave)
        return soma % self.tamanho

    def inserir(self, chave, id_receita):
        chave = chave.lower().strip()
        indice = self._hash(chave)
        
        for no in self.tabela[indice]:
            if no.chave == chave:
                if id_receita not in no.ids_receitas:
                    no.ids_receitas.append(id_receita)
                return
        
        novo_no = NoIndice(chave)
        novo_no.ids_receitas.append(id_receita)
        self.tabela[indice].append(novo_no)

    def buscar(self, chave):
        chave = chave.lower().strip()
        indice = self._hash(chave)
        
        for no in self.tabela[indice]:
            if no.chave == chave:
                return no.ids_receitas
                
        return []