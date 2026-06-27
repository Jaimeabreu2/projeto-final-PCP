# Bar dos Filósofos

Neste trabalho, simulamos o Problema do Bar dos Filósofos usando Python. Cada
filósofo é uma thread e cada garrafa é um recurso compartilhado protegido por
um `threading.Lock`.

Implementamos duas formas de evitar deadlock:

- **Ordenação de Recursos:** as garrafas são sempre adquiridas pela ordem dos
  seus identificadores;
- **Garçom:** um controle central limita a quantidade de filósofos tentando
  pegar garrafas e coordena a retirada dos recursos.

O programa mede os tempos dos filósofos, compara as soluções e pode gerar
CSV, gráficos e um relatório simples em TXT.

## Requisitos

- Python 3.10 ou mais recente;
- `matplotlib`, usado somente para gerar gráficos.

As outras bibliotecas usadas (`threading`, `random`, `time`, `argparse` e
`csv`) já fazem parte do Python.

Para instalar a dependência:

```text
python -m pip install -r requirements.txt
```

No Windows, se o comando `python` não funcionar, tente usar `py`.

## Como executar

Os comandos devem ser executados na pasta em que está o arquivo `main.py`.

Ordenação de Recursos:

```text
python main.py matrizes/caso1.txt ordenacao
```

Garçom:

```text
python main.py matrizes/caso1.txt garcom
```

Comparação das duas soluções:

```text
python main.py matrizes/caso1.txt comparar
```

Para usar os outros casos, basta trocar `caso1.txt` por `caso2.txt` ou
`caso3.txt`.

### Comandos dos três casos

```text
python main.py matrizes/caso1.txt ordenacao
python main.py matrizes/caso1.txt garcom
python main.py matrizes/caso1.txt comparar

python main.py matrizes/caso2.txt ordenacao
python main.py matrizes/caso2.txt garcom
python main.py matrizes/caso2.txt comparar

python main.py matrizes/caso3.txt ordenacao
python main.py matrizes/caso3.txt garcom
python main.py matrizes/caso3.txt comparar
```

## Opções disponíveis

### Seed

A seed ajuda a repetir sorteios parecidos:

```text
python main.py matrizes/caso1.txt comparar --seed 42
```

Mesmo com a seed, os tempos podem mudar um pouco porque a ordem de execução
das threads depende do sistema operacional.

### CSV

```text
python main.py matrizes/caso1.txt comparar --seed 42 --csv
```

Os arquivos são salvos em `resultados/`. No modo `comparar`, o programa gera
um CSV para cada solução e outro com a comparação.

### Verbose

```text
python main.py matrizes/caso1.txt ordenacao --seed 42 --verbose
```

O modo verbose mostra mudanças de estado, garrafas sorteadas, tentativas de
aquisição e liberação. Um lock de impressão impede que duas threads escrevam
na mesma linha. Para a apresentação, recomendamos usar esse modo com o Caso 1,
pois nos casos maiores a saída fica bem extensa.

### Gráficos

```text
python main.py matrizes/caso1.txt comparar --seed 42 --csv --graficos
```

São gerados dois gráficos:

- comparação do tempo total;
- comparação da espera média geral.

O `--csv` não é obrigatório para os gráficos, mas é útil para guardar também
os valores usados.

### Relatório em TXT

```text
python main.py matrizes/caso1.txt comparar --seed 42 --csv --graficos --relatorio
```

O relatório registra a configuração da execução, as métricas, os arquivos
gerados e uma conclusão curta.

### Executar todos os casos

```text
python main.py todos --seed 42
```

Esse comando executa Ordenação e Garçom nos três casos. Também é possível
combinar todas as opções:

```text
python main.py todos --seed 42 --csv --graficos --relatorio
```

Essa execução demora mais porque realiza seis simulações.

## Casos de teste

- `caso1.txt`: 5 filósofos, 5 garrafas e 6 ciclos por filósofo;
- `caso2.txt`: 6 filósofos, 8 garrafas e 6 ciclos por filósofo;
- `caso3.txt`: 12 filósofos, 21 garrafas e 3 ciclos por filósofo.

Cada arquivo contém uma matriz de adjacência. Exemplo:

```text
0, 1, 0
1, 0, 1
0, 1, 0
```

Antes de iniciar as threads, o programa verifica se a matriz:

- não está vazia;
- é quadrada;
- possui somente `0` e `1`;
- possui diagonal principal igual a zero;
- é simétrica;
- não possui filósofos isolados.

## Funcionamento da simulação

Cada filósofo repete a sequência:

```text
tranquilo -> com sede -> bebendo -> tranquilo
```

- **Tranquilo:** espera um tempo aleatório;
- **Com sede:** sorteia as garrafas e aguarda até conseguir todas;
- **Bebendo:** mantém as garrafas por um segundo e depois as libera.

O tempo com sede corresponde à espera pelos recursos.

### Ordenação de Recursos

Todas as garrafas possuem um identificador. Antes de adquirir os locks, o
filósofo ordena as garrafas pelo ID. Como todos seguem a mesma ordem, não se
forma uma espera circular.

### Garçom

O Garçom usa um `Semaphore` com `N - 1` permissões. Um lock adicional coordena
a retirada do conjunto de garrafas. Ao terminar de beber, o filósofo libera
as garrafas e devolve a permissão.

## Métricas

Para cada filósofo, mostramos:

- tempo tranquilo;
- tempo com sede;
- tempo bebendo;
- quantidade de vezes que bebeu;
- espera média.

Para cada solução, mostramos:

- tempo total;
- espera média geral;
- maior e menor espera média;
- diferença entre as esperas;
- deadlock;
- possível starvation.

O alerta de starvation é uma análise simples. Ele aparece quando a maior
espera individual é de pelo menos `0,10s` e supera duas vezes a espera média
geral. Esse alerta mostra um possível desequilíbrio, não uma prova de erro.

## Estrutura

```text
Projeto final PCP/
├── main.py
├── grafo.py
├── garrafa.py
├── filosofo.py
├── solucoes.py
├── relatorio.py
├── relatorio_automatico.py
├── graficos.py
├── log_simulacao.py
├── requirements.txt
├── matrizes/
├── resultados/
└── tests/
```

- `main.py`: recebe os argumentos e coordena as execuções;
- `grafo.py`: lê e valida a matriz, criando filósofos e garrafas;
- `garrafa.py`: representa uma garrafa e seu lock;
- `filosofo.py`: contém a thread e os estados do filósofo;
- `solucoes.py`: contém Ordenação e Garçom;
- `relatorio.py`: mostra resultados e salva CSV;
- `relatorio_automatico.py`: gera o arquivo TXT;
- `graficos.py`: gera os gráficos;
- `log_simulacao.py`: controla a impressão do verbose.

## Testes

```text
python -m unittest discover -s tests -v
```

Nos testes, as pausas são removidas para que a suíte termine rápido. A lógica
das threads, locks e semáforos continua sendo executada.

## Rodar em outro computador

1. Copie ou compacte a pasta inteira do projeto.
2. Extraia a pasta no outro computador.
3. Abra o terminal dentro da pasta.
4. Instale as dependências:

```text
python -m pip install -r requirements.txt
```

5. Execute um teste simples:

```text
python main.py matrizes/caso1.txt comparar --seed 42
```
