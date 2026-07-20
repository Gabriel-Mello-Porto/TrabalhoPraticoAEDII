import csv

class Receita:
    def __init__(self, id_receita, nome, ingredientes, tempo_preparo, tags, passos="[]"):
        self.id = int(id_receita)
        self.nome = nome
        self.ingredientes = ingredientes  
        self.tempo_preparo = int(tempo_preparo)
        self.tags = tags
        self.passos = passos # novo atributo

    def __str__(self):
        return (
            f"[{self.id}] {self.nome.upper()}\n"
            f" ├─ Categoria (Tags): {self.tags[:80]}...\n"
            f" ├─ Ingredientes: {self.ingredientes[:80]}...\n"
            f" └─ Tempo (Critério Numérico): {self.tempo_preparo} min\n"
        )

def carregar_receitas_do_csv(caminho_arquivo):
    lista_receitas = []
    try:
        with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo:
            leitor_csv = csv.DictReader(arquivo)
            
            for linha in leitor_csv:
                tempo = int(linha['minutes'])
                
                if tempo > 0:
                    passos_csv = linha.get('steps', "[]") 
                    
                    nova_receita = Receita(
                        id_receita=linha['id'],
                        nome=linha['name'],
                        ingredientes=linha['ingredients'],
                        tempo_preparo=tempo,
                        tags=linha['tags'],
                        passos=passos_csv
                    )
                    lista_receitas.append(nova_receita)
                
        return lista_receitas
    except FileNotFoundError:
        print(f"Erro Crítico: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return []