import pandas as pd

def preparar_dataset_trabalho():
    print("Carregando o dataset original...")
    df = pd.read_csv('RAW_recipes.csv')

    # eliminar receitas com dados faltando
    colunas_essenciais = ['id', 'name', 'ingredients', 'minutes', 'tags']
    df = df.dropna(subset=colunas_essenciais)

    # selecionar prefixos para trie
    prefixos = ['chicken', 'chocolate', 'beef', 'pasta', 'cake', 'pizza']
    padrao_regex = '^(' + '|'.join(prefixos) + ')' 
    
    df_prefixos = df[df['name'].str.contains(padrao_regex, case=False, na=False)]

    # separar por categorias de tempo para o guloso ter o que otimizar
    rapidas = df_prefixos[df_prefixos['minutes'] <= 15].head(50)
    medias = df_prefixos[(df_prefixos['minutes'] > 15) & (df_prefixos['minutes'] <= 30)].head(50)
    demoradas = df_prefixos[(df_prefixos['minutes'] > 30) & (df_prefixos['minutes'] <= 60)].head(50)
    muito_demoradas = df_prefixos[df_prefixos['minutes'] > 60].head(50)

    df_final = pd.concat([rapidas, medias, demoradas, muito_demoradas])

    if len(df_final) < 200:
        faltam = 200 - len(df_final)
        df_extra = df_prefixos.drop(df_final.index).sample(n=faltam, random_state=42)
        df_final = pd.concat([df_final, df_extra])

    df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)

    # Salva o arquivo 
    nome_arquivo_saida = 'dataset_cozinha_jacquin_200.csv'
    df_final.to_csv(nome_arquivo_saida, index=False)
    
    print(f"Sucesso! Arquivo '{nome_arquivo_saida}' criado com {len(df_final)} receitas.")

# executa
preparar_dataset_trabalho()