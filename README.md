# TrabalhoPraticoAEDII

Projeto acadêmico da disciplina de Algoritmos e Estruturas de Dados 2

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# INFORMAÇÕES BÁSICAS 
Nome: Gabriel Mello Porto        
Repositório GitHub: https://github.com/Gabriel-Mello-Porto/TrabalhoPraticoAEDII          
Fonte dos dados: Recipes and Interactions no Kaggle (https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions/data)

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# PRÉ-REQUISITOS        
Python 3.8 ou superior instalado.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# COMO RODAR      
Clone o repositório em sua máquina local.        
Executar no terminal o comando: cd [caminho para o projeto]      
Executar no terminal o comando: python main.py (ou python3 main.py para Linux/macOS).  
Na primeira execução, o programa vai construir a Árvore B e salvá-la no disco.
Navegue pelo menu interativo digitando os números correspondentes às opções.
Nas execuções seguintes, o sistema perguntará sobre a criação do banco de dados. Escolha a Opção 1 para manter o mesmo banco ou a Escolha a Opção 2 (Recriar tudo do zero) para que o sistema leia o arquivo .csv, empacote os dados usando struct e crie os arquivos de paginação receitas.bin e indice_arvore_b.bin.      
      

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# PRÉ-PROCESSAMENTO DO DATASET        
Para adequar os dados ao escopo da disciplina e permitir testes eficientes do Algoritmo Guloso, foi desenvolvido um script (preparar_dataset.py) utilizando a biblioteca Pandas. Este script filtrou dados corrompidos, selecionou receitas por prefixos específicos e balanceou a base em faixas de tempo de preparo (rápidas, médias e demoradas). O resultado é o arquivo dataset_cozinha_jacquin_200.csv, contendo 200 registros perfeitamente formatados para consumo do sistema em C/Python puro.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# ESTRUTURAS
1) Árvore Trie foi aplicada no Módulo 1.
Busca de receitas por prefixo e auto-completar.
Em vez de usar expressões regulares ou varrer todas as strings do banco buscando correspondências, a Trie permite encontrar todas as receitas como por exemplo as que começam com "chi" (ex: chicken) em tempo $O(L)$, onde $L$ é o tamanho do prefixo digitado. É a estrutura definitiva para dicionários e auto-complete.

2) Algoritmo Guloso (Greedy) foi aplicada: Módulo 5.
Modo Chef (Recomendação e Otimização de Menu).
Baseado no clássico "Problema da Mochila", o algoritmo faz escolhas localmente ótimas. Ele ordena as receitas usando critérios numéricos (menor tempo de preparo ou menor quantidade de ingredientes) e preenche a capacidade limite do usuário. Garante uma solução rápida e eficiente para restrições operacionais da cozinha.

3) Árvore B com Armazenamento em Disco (Persistência Binária) foi aplicada: Módulo 1.
Busca direta por ID único.
Simula um SGBD real. A Árvore B reside na memória RAM guardando apenas o ID da receita e um "ponteiro de offset" (endereço físico em bytes). O volume denso de texto fica serializado no disco (receitas.bin). Quando um ID é buscado na árvore, o sistema executa um salto (seek) direto para o byte exato no HD, lendo apenas a receita solicitada, operando com consumo de memória extremamente reduzido.

4) Tabelas Hash (Implementação Dupla: Indexação e Segurança)

4.1) Tabelas Hash com Índice Invertido foi aplicada no Módulos 3 e 4.
Busca por Ingredientes e Categorias (Tags).
Para encontrar todas as receitas como por exemplo as que levam "garlic", varrer a lista de ingredientes de cada prato seria ineficiente. Foi criado um Índice Invertido usando uma Tabela Hash, onde a chave calculada (via tabela ASCII) mapeia diretamente para uma lista encadeada de IDs de receitas. Acesso médio de $O(1)$.

4.2) Tabelas Hash com Fingerprint Criptográfico no Modo Investigação.
Utilizado a função hash SHA-256 para gerar assinaturas digitais do conteúdo da receita. Garante a segurança do sistema detectando adulterações na memória RAM (sabotagens). 
O tratamento de colisões por encadeamento no hash do nome nos permitiu discernir logicamente entre Duplicatas Exatas (mesmo hash de conteúdo) e Conflitos de Versão (hashes de conteúdo divergentes).


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# RECUPERAÇÃO P1

Questão escolhida para recuperação: Questão 2 da prova.      
Opção C: Árvores B e Simulação de Memória Secundária (I/O)        

### Explicação Teórica e Arquitetural do Upgrade      
A dificuldade para abstrair e implementar as regras estruturais de balanceamento de uma arvore B, especificamente o algoritmo de split / divisão de nós e para compreender a motivação de hardware que torna essa estrutura tão poderosa em bancos de dados reais.
Para recuperar e consolidar esse conhecimento, foi implementado um SGBD minimalista no arquivo arvore_b.py, transpondo a teoria para a prática de simulação de Memória Secundária.

O upgrade arquitetural consistiu em substituir a construção de uma árvore volátil baseada apenas em ponteiros de memória RAM, pelo desenvolvimento da classe ArvoreB_Disco. Nessa implementação, cada nó da árvore simula uma página de disco, possuindo um tamanho fixo rigorosamente definido em bytes por meio da biblioteca struct.
A persistência em disco e o controle de operações de entrada e saída também foram incorporados ao projeto. A árvore não armazena diretamente strings ou dados densos, mas apenas tuplas no formato (id_receita, ponteiro_offset). Além disso, os ponteiros de filhos (no.filhos) não fazem referência a endereços de memória, e sim a posições de bytes dentro do arquivo binário de índice indice_arvore_b.bin.
Para superar a dificuldade com o algoritmo de Split, implementamos a função _dividir_filho(self, pai, i, filho_cheio), que é obrigada a gravar as alterações físicas (salvando o pai, o filho dividido e o novo irmão recém-alocado) diretamente no HD via chamadas sucessivas de f.seek() e f.write(), provando o completo entendimento das regras de promoção de chaves e particionamento de páginas.

### Passo a Passo para Testar a Funcionalidade da P1        
- Execute python main.py pela primeira vez e escolha a opção [2] Recriar tudo do zero. Isso forçará o sistema a ler o CSV e a construir os arquivos receitas.bin e indice_arvore_b.bin fisicamente no seu computador.        
- [Teste de I/O Isolado]: Feche o programa (matando a RAM).        
- Execute python main.py novamente.        
- Quando o sistema perguntar "Arquivos de banco detectados", escolha a Opção 1 (Usar banco existente). Ao escolher esta opção, o sistema não reconstrói a árvore B. Ele apenas "liga" a variável arvore_b ao arquivo binário que já está salvo no HD.        
- No Menu Principal, entre na Opção 1 (Consulta Rápida).      
- Escolha a Opção 3 (Buscar receita por ID único - Árvore B + Disco Binário).
- Digite um ID de receita válido (ex: 52443 ou qualquer ID listado se você rodar a listagem completa antes).      

O que acontece durante esse processo: O sistema navegará pelo arquivo indice_arvore_b.bin pulando blocos de bytes matematicamente. Ao achar a chave, ele resgatará o offset físico, saltará para esse exato byte no arquivo receitas.bin e extrairá a string JSON apenas daquela receita, provando a leitura I/O sob demanda sem carregar o banco de dados na RAM.


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# ESTRUTURAS E ALGORITMOS AVANÇADOS (PARTE 2 DO TRABALHO)

## 5) Módulo 5: Oficina de Produção (Grafos e Dependências)
Utiliza Grafos Direcionados Acíclicos (DAG).
Para mapear as dependências entre receitas (ex: um preparo intermediário como caldo precisa ser feito antes da finalização do prato), as receitas viram vértices e as dependências viram arestas direcionadas. Foi implementada a Busca em Profundidade (DFS) para rastrear todo o caminho e detectar inconsistências ou ciclos (deadlocks operacionais onde A depende de B e B depende de A). Quando não há ciclos, o sistema usa o algoritmo de Ordenação Topológica para gerar uma sequência linear e viável de produção para a equipe.

## 6) Módulo 6: Menu Degustação VIP (Programação Dinâmica)
Utiliza a lógica do Problema da Mochila (Knapsack 0/1).
O objetivo é gerar um menu especial que maximize um critério de interesse (como lucro esperado ou avaliação) sob uma restrição severa de tempo total ou orçamento máximo. Diferente de uma abordagem Gulosa (que faz escolhas locais e pode falhar em achar o ótimo global), a Programação Dinâmica avalia e preenche uma matriz com subproblemas sobrepostos. O algoritmo decide matematicamente se incluir ou ignorar cada prato maximiza o valor final sem estourar o limite da "mochila".

## 7) Módulo 7: O Pesadelo Logístico (Redes, Infraestrutura e Gargalos)
7.1) Árvore Geradora Mínima (Algoritmo de Prim):
O sistema precisa interligar novos pontos operacionais do restaurante criando a menor rede de conexões possível. O algoritmo de Prim avalia o grafo com todos os pontos da cidade e seleciona sequencialmente apenas as rotas de menor custo que conectam os vértices. Isso interliga todo o sistema sem formar ciclos redundantes, minimizando financeiramente o custo total da obra

7.2) Fluxo Máximo (Algoritmo de Ford-Fulkerson / Edmonds-Karp):
O objetivo é calcular a capacidade máxima de atendimento simultâneo da rede. Utilizando a Busca em Largura (BFS) para encontrar caminhos aumentantes na rede residual, o algoritmo identifica as vias que representam gargalos logísticos entre a cozinha central (fonte) e os clientes finais (sumidouro), indicando onde a operação de entrega fica represada.

## 8) Módulo 8: Laboratório de Inovação do Chef (A e Rotas Dinâmicas)*
O Módulo 8 foca na exploração de abordagens avançadas para a tomada de decisão logística dentro do restaurante, abordando especificamente o desafio de Navegação em Tempo Real: Encontrar rotas considerando mudanças dinâmicas no ambiente. O problema relevante identificado foi o alto impacto de atrasos nas entregas causados por imprevistos logísticos, como ruas bloqueadas, congestionamentos e áreas temporariamente indisponíveis, que o sistema anterior não conseguia contornar. Para resolver isso, foi modelado o mapa urbano como um Grafo Ponderado, onde cruzamentos e clientes são vértices e as ruas são arestas cujo peso representa o tempo de viagem. A solução funcional foi implementada na Opção 7 do Modo Logística, onde o sistema permite simular bloqueios dinâmicos, desconectando arestas instantaneamente e disparando um novo cálculo de rota de desvio. A decisão de utilizar o algoritmo A* com uma fila de prioridade foi estratégica, pois a inclusão de uma função heurística baseada na distância em linha reta direciona a busca apenas para as direções do destino, descartando rotas ineficientes e permitindo respostas em milissegundos. Como limitação, a heurística atual utiliza coordenadas estáticas e bloqueios de via total, o que abre espaço para melhorias futuras como a integração de APIs de tráfego real ou bloqueios direcionais de trânsito.

