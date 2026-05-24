import hashlib

class TabelaHash:
    def __init__(self, tamanho=1024):
        self.tamanho = tamanho
        self.tabela_conteudo = [[] for _ in range(tamanho)]
        self.tabela_nomes = [[] for _ in range(tamanho)]

    def _gerar_hash_conteudo(self, receita):
        conteudo = f"{receita.nome}|{receita.ingredientes}|{receita.tempo_preparo}"
        return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()

    def _gerar_hash_nome(self, nome):
        return hashlib.sha256(nome.lower().encode('utf-8')).hexdigest()

    def _indice(self, chave_hash):
        # int(..., 16) converte a string hexadecimal do SHA-256 para um número inteiro na base 10
        return int(chave_hash, 16) % self.tamanho

    def registrar_receita(self, receita):
        hash_cont = self._gerar_hash_conteudo(receita)
        idx_cont = self._indice(hash_cont)
        self.tabela_conteudo[idx_cont].append((receita.id, hash_cont))

        hash_nome = self._gerar_hash_nome(receita.nome)
        idx_nome = self._indice(hash_nome)
        self.tabela_nomes[idx_nome].append((receita.id, hash_cont))

    def verificar_integridade_unica(self, receita_atual):
        hash_atual = self._gerar_hash_conteudo(receita_atual)
        idx = self._indice(hash_atual)
        
        for tupla in self.tabela_conteudo[idx]:
            id_rec = tupla[0]
            hash_salvo = tupla[1]
            if id_rec == receita_atual.id:
                if hash_salvo == hash_atual:
                    return True, "Integridade confirmada."
                return False, "SABOTAGEM: O conteúdo não bate com o registro original."
        return False, "Receita não encontrada no registro oficial."

    def gerar_relatorio_investigacao(self, lista_receitas):

        print("\n" + "="*50)
        print(" RELATÓRIO DE INVESTIGAÇÃO DE SABOTAGENS")
        print("="*50)
        
        duplicatas_exatas = []
        conflitos_versao = []
        receitas_corrompidas = []

        # validar a integridade
        for receita in lista_receitas:
            valida, _ = self.verificar_integridade_unica(receita)
            if not valida:
                receitas_corrompidas.append(receita.id)

        # identificar duplicatas 
        for lista_nomes in self.tabela_nomes:
            if len(lista_nomes) > 1:
                primeiro_hash = lista_nomes[0][1]
                
                # Versão básica: Laço 'for' com variável booleana no lugar do 'all()'
                todos_hashes_iguais = True
                for tupla in lista_nomes:
                    hash_atual = tupla[1]
                    if hash_atual != primeiro_hash:
                        todos_hashes_iguais = False
                        break
                
                # Versão básica: Laço 'for' e append() no lugar da List Comprehension
                ids_envolvidos = []
                for tupla in lista_nomes:
                    id_receita = tupla[0]
                    ids_envolvidos.append(id_receita)
                
                if todos_hashes_iguais:
                    duplicatas_exatas.append(ids_envolvidos)
                else:
                    conflitos_versao.append(ids_envolvidos)

        # resultados
        print(f"-> Receitas Corrompidas/Alteradas: {len(receitas_corrompidas)}")
        print(f"-> Duplicatas Exatas (Mesmo conteúdo, IDs diferentes): {len(duplicatas_exatas)}")
        print(f"-> Conflitos de Versão (Mesmo nome, conteúdos divergentes): {len(conflitos_versao)}\n")
        
        if conflitos_versao:
            print("Detalhes dos Conflitos de Versão (IDs suspeitos):")
            for conflito in conflitos_versao:
                print(f" - Receita com múltiplas versões registradas nos IDs: {conflito}")
        
        print("="*50 + "\n")