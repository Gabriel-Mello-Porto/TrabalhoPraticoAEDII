import csv
import json
import struct

def criar_arquivo_binario(csv_origem, bin_destino):
    print(f"Iniciando conversão de {csv_origem} para {bin_destino}...\n")
    
    try:
        with open(csv_origem, mode='r', encoding='utf-8') as arq_csv, \
             open(bin_destino, mode='wb') as arq_bin:
            
            leitor_csv = csv.DictReader(arq_csv)
            receitas_processadas = 0
            
            print("--- Primeiros 5 Ponteiros (Offsets) Gerados ---")
            
            for linha in leitor_csv:
                tempo = int(linha['minutes'])
                
                if tempo > 0:
                    dados_receita = {
                        'id': int(linha['id']),
                        'nome': linha['name'],
                        'ingredientes': linha['ingredients'],
                        'tempo': tempo,
                        'tags': linha['tags']
                    }
                    
                    # converte o dicionario para uma string JSON e depois codifica para Bytes
                    dados_bytes = json.dumps(dados_receita).encode('utf-8')
                    
                    # empacota o tamanho dessa receita em um inteiro de 4 bytes
                    tamanho_bytes = struct.pack('i', len(dados_bytes))
                    
                    ponteiro_offset = arq_bin.tell()
                    
                    # escreve no disco: primeiro os 4 bytes do tamanho, depois os dados em si
                    arq_bin.write(tamanho_bytes)
                    arq_bin.write(dados_bytes)
                    
                    if receitas_processadas < 5:
                        print(f"ID da Receita: {dados_receita['id']:<8} | Ponteiro no Disco: Byte {ponteiro_offset}")
                        
                    receitas_processadas += 1
                    
            print("-------------------------------------------------\n")
            print(f"Sucesso! {receitas_processadas} receitas foram gravadas no disco em formato binário.")
            print("Um novo arquivo chamado 'receitas.bin' apareceu na sua pasta.")

    except FileNotFoundError:
        print(f"Erro Crítico: O arquivo '{csv_origem}' não foi encontrado.")

if __name__ == "__main__":
    arquivo_csv = 'dataset_cozinha_jacquin_200.csv'
    arquivo_binario = 'receitas.bin'
    criar_arquivo_binario(arquivo_csv, arquivo_binario)