import struct
import os

class NoArvoreB:
    def __init__(self, folha=False, endereco=-1):
        self.folha = folha
        self.chaves = []  # lista de tuplas: (id_receita, offset_receita_no_csv_binario)
        self.filhos = []  # lista de inteiros: offsets dos nós filhos no arquivo de indice
        self.endereco = endereco # onde este nó esta salvo no disco

class ArvoreB_Disco:
    def __init__(self, nome_arquivo_indice, grau_minimo=3):
        self.arquivo = nome_arquivo_indice
        self.t = grau_minimo
        
        self.formato_no = '<? i 10i 6i'
        self.tamanho_no = struct.calcsize(self.formato_no)
        
        self.raiz_offset = -1
        self._inicializar_arquivo()

    def _inicializar_arquivo(self):
        if not os.path.exists(self.arquivo):
            with open(self.arquivo, 'wb') as f:
                f.write(struct.pack('<i', -1))
        else:
            with open(self.arquivo, 'rb') as f:
                f.seek(0)
                bytes_raiz = f.read(4)
                if bytes_raiz:
                    self.raiz_offset = struct.unpack('<i', bytes_raiz)[0]

    def _salvar_raiz_offset(self, offset):
        self.raiz_offset = offset
        with open(self.arquivo, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack('<i', offset))

    def _alocar_novo_no(self, folha=False):
        with open(self.arquivo, 'a+b') as f:
            f.seek(0, os.SEEK_END)
            endereco = f.tell()
            if endereco < 4:
                endereco = 4
        
        novo_no = NoArvoreB(folha, endereco)
        self._escrever_no(novo_no)
        return novo_no

    def _escrever_no(self, no):
        chaves_flat = []
        for i in range((2 * self.t) - 1):
            if i < len(no.chaves):
                chaves_flat.extend([no.chaves[i][0], no.chaves[i][1]])
            else:
                chaves_flat.extend([-1, -1]) # Preenche espaço vazio com -1

        filhos_flat = []
        for i in range(2 * self.t):
            if i < len(no.filhos):
                filhos_flat.append(no.filhos[i])
            else:
                filhos_flat.append(-1)

        dados_empacotados = struct.pack(self.formato_no, no.folha, len(no.chaves), *chaves_flat, *filhos_flat)
        
        with open(self.arquivo, 'r+b') as f:
            f.seek(no.endereco)
            f.write(dados_empacotados)

    def _ler_no(self, endereco):
        with open(self.arquivo, 'rb') as f:
            f.seek(endereco)
            dados = f.read(self.tamanho_no)
            
        desempacotado = struct.unpack(self.formato_no, dados)
        no = NoArvoreB(folha=desempacotado[0], endereco=endereco)
        num_chaves = desempacotado[1]
        
        idx_tupla = 2
        for _ in range(num_chaves):
            id_rec = desempacotado[idx_tupla]
            offset_rec = desempacotado[idx_tupla + 1]
            no.chaves.append((id_rec, offset_rec))
            idx_tupla += 2
            
        idx_filhos = 2 + ((2 * self.t) - 1) * 2
        for _ in range(num_chaves + 1):
            if not no.folha:
                no.filhos.append(desempacotado[idx_filhos])
            idx_filhos += 1
            
        return no

    def buscar(self, k, endereco_no=None):
        if self.raiz_offset == -1:
            return None
            
        if endereco_no is None:
            endereco_no = self.raiz_offset
            
        no = self._ler_no(endereco_no)
        i = 0
        while i < len(no.chaves) and k > no.chaves[i][0]:
            i += 1

        if i < len(no.chaves) and no.chaves[i][0] == k:
            return no.chaves[i][1] # retorna o ponteiro do arquivo receitas.bin

        if no.folha:
            return None

        # desce para o filho buscando no disco
        return self.buscar(k, no.filhos[i])

    def inserir(self, id_receita, offset_disco):
        if self.raiz_offset == -1:
            nova_raiz = self._alocar_novo_no(folha=True)
            nova_raiz.chaves.append((id_receita, offset_disco))
            self._escrever_no(nova_raiz)
            self._salvar_raiz_offset(nova_raiz.endereco)
            return

        raiz = self._ler_no(self.raiz_offset)
        if len(raiz.chaves) == (2 * self.t) - 1:
            nova_raiz = self._alocar_novo_no(folha=False)
            nova_raiz.filhos.append(raiz.endereco)
            self._salvar_raiz_offset(nova_raiz.endereco)
            self._dividir_filho(nova_raiz, 0, raiz)
            self._inserir_nao_cheio(nova_raiz, (id_receita, offset_disco))
        else:
            self._inserir_nao_cheio(raiz, (id_receita, offset_disco))

    def _inserir_nao_cheio(self, no, tupla_dado):
        i = len(no.chaves) - 1
        
        if no.folha:
            no.chaves.append((None, None))
            while i >= 0 and tupla_dado[0] < no.chaves[i][0]:
                no.chaves[i + 1] = no.chaves[i]
                i -= 1
            no.chaves[i + 1] = tupla_dado
            self._escrever_no(no) # salva a modificação no disco
        else:
            while i >= 0 and tupla_dado[0] < no.chaves[i][0]:
                i -= 1
            i += 1
            
            filho = self._ler_no(no.filhos[i])
            if len(filho.chaves) == (2 * self.t) - 1:
                self._dividir_filho(no, i, filho)
                if tupla_dado[0] > no.chaves[i][0]:
                    i += 1
                    filho = self._ler_no(no.filhos[i])
                    
            self._inserir_nao_cheio(filho, tupla_dado)

    def _dividir_filho(self, pai, i, filho_cheio):
        t = self.t
        novo_filho = self._alocar_novo_no(folha=filho_cheio.folha)

        pai.chaves.insert(i, filho_cheio.chaves[t - 1])
        pai.filhos.insert(i + 1, novo_filho.endereco)

        novo_filho.chaves = filho_cheio.chaves[t: (2 * t) - 1]
        filho_cheio.chaves = filho_cheio.chaves[0: t - 1]

        if not filho_cheio.folha:
            novo_filho.filhos = filho_cheio.filhos[t: 2 * t]
            filho_cheio.filhos = filho_cheio.filhos[0: t]

        # salva os 3 nós alterados no disco
        self._escrever_no(filho_cheio)
        self._escrever_no(novo_filho)
        self._escrever_no(pai)