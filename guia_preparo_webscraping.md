# Guia de preparação para Web Scraping em Python

Este guia reúne os principais passos para preparar um ambiente seguro e eficiente para web scraping com Python.

## 1. O que é Web Scraping?

Web Scraping é a técnica de automatizar a coleta de dados de páginas web para transformá-los em informações úteis para análise, relatórios, automações e projetos pessoais.

É muito usado para:
- extrair preços e produtos;
- coletar notícias e dados públicos;
- monitorar concorrência;
- obter informações de portais e sites;
- criar pequenos projetos de automação.

> Atenção: sempre respeite os termos de uso do site, o arquivo robots.txt e as regras de acesso.

---

## 2. Bibliotecas essenciais

### 2.1 requests
Usada para fazer requisições HTTP. Com ela você acessa uma página e recebe o conteúdo em HTML, JSON etc.

Exemplo:
```python
import requests

url = "https://example.com"
response = requests.get(url, timeout=10)

print(response.status_code)
print(response.text[:500])
```

### 2.2 BeautifulSoup
Usada para analisar o HTML e extrair dados como textos, links, preços, títulos e elementos específicos.

Exemplo:
```python
from bs4 import BeautifulSoup
import requests

url = "https://example.com"
html = requests.get(url, timeout=10).text
soup = BeautifulSoup(html, "html.parser")

print(soup.title)
print(soup.find("a"))
```

### 2.3 lxml
É um parser rápido para HTML e XML. Funciona muito bem para páginas maiores ou extrações mais pesadas.

### 2.4 pandas
Não faz scraping em si, mas ajuda a organizar os dados em tabelas e exportar CSV, Excel e JSON.

Exemplo:
```python
import pandas as pd

dados = [
    {"titulo": "Python", "preco": 99},
    {"titulo": "JavaScript", "preco": 89}
]

df = pd.DataFrame(dados)
print(df)
```

### 2.5 selenium
Usada quando a página depende de JavaScript para carregar o conteúdo. Você consegue abrir o navegador, clicar, preencher campos e extrair dados dinâmicos.

### 2.6 scrapy
Framework mais avançado para scraping em projetos maiores e com múltiplas páginas.

---

## 3. Ambiente virtual

Antes de começar, é recomendável criar um ambiente virtual para isolar as dependências do projeto.

### 3.1 Criar o ambiente virtual
No Windows:
```bash
python -m venv .venv
```

No Linux/macOS:
```bash
python3 -m venv .venv
```

### 3.2 Ativar o ambiente virtual
No Windows:
```bash
.venv\Scripts\activate
```

No Linux/macOS:
```bash
source .venv/bin/activate
```

### 3.3 Atualizar o pip
```bash
python -m pip install --upgrade pip
```

### 3.4 Instalar bibliotecas
```bash
pip install requests beautifulsoup4 lxml pandas
```

Se você for trabalhar com páginas dinâmicas, também pode instalar:
```bash
pip install selenium
```

Ou Playwright:
```bash
pip install playwright
playwright install
```

### 3.5 Gerar requirements.txt
```bash
pip freeze > requirements.txt
```

Para instalar tudo em outro ambiente:
```bash
pip install -r requirements.txt
```

---

## 4. Como inspecionar uma página antes de escrever o código

Antes de extrair dados, é importante entender a estrutura da página.

### Passos:
1. Abra a página no navegador.
2. Pressione F12 para abrir o DevTools.
3. Vá em "Elements" para ver o HTML.
4. Vá em "Network" para descobrir endpoints, JSON e requisições recebidas pela página.
5. Procure tags e classes importantes, como:
   - div
   - a
   - h1, h2, p
   - class=
   - id=
   - href
   - data-*

### Dica
Muita vez, o conteúdo não está no HTML principal, mas em um arquivo JSON vindo da API. Nesses casos, a melhor forma é inspecionar a aba "Network".

---

## 5. O que fazer antes de começar a codar

### Checklist importante
- [ ] Definir exatamente o que você quer extrair
- [ ] Verificar se o site permite scraping
- [ ] Olhar o robots.txt e os termos de uso
- [ ] Ver se os dados vêm do HTML ou de uma API
- [ ] Testar uma requisição simples com requests
- [ ] Verificar o código de status da resposta
- [ ] Entender a estrutura da página
- [ ] Definir como salvar os dados

---

## 6. Exemplo básico de requisição

```python
import requests

url = "https://example.com"
response = requests.get(url, timeout=10)

print(response.status_code)
print(response.headers.get("Content-Type"))
print(response.text[:400])
```

Se o status for 200, a página foi acessada corretamente.

---

## 7. Exemplo básico com BeautifulSoup

```python
import requests
from bs4 import BeautifulSoup

url = "https://example.com"
response = requests.get(url, timeout=10)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

for link in soup.find_all("a")[:10]:
    print(link.get("href"))
```

Esse código busca links da página e mostra os primeiros 10.

---

## 8. Quando a página é dinâmica

Alguns sites carregam conteúdo via JavaScript. Nessas páginas, o HTML bruto pode não mostrar o que você quer.

Você pode tentar:
- usar Selenium;
- usar Playwright;
- procurar uma API que a página utiliza;
- verificar a aba Network para encontrar os dados em JSON.

Esse é um ponto muito importante que aparece nos vídeos que você revisou.

---

## 9. Boas práticas de web scraping

- respeite o site e o robots.txt;
- não faça milhares de requisições em sequência;
- use timeouts para evitar travamentos;
- adicione delay entre as requisições;
- trate erros corretamente;
- simule um navegador quando necessário;
- prefira APIs públicas, quando existir;
- salve os dados em arquivos CSV/JSON para não perder o trabalho;
- teste pequenas partes antes de automatizar tudo.

Exemplo com erro e timeout:
```python
import requests

try:
    response = requests.get("https://example.com", timeout=10)
    response.raise_for_status()
    print(response.text[:200])
except requests.exceptions.RequestException as e:
    print("Erro ao acessar a página:", e)
```

Exemplo de pausa:
```python
import time

time.sleep(2)
```

---

## 10. Headers e User-Agent

Alguns sites bloqueiam acessos automáticos. Em alguns casos, uma solução simples é enviar um User-Agent como se o código estivesse sendo executado por um navegador.

Exemplo:
```python
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get("https://example.com", headers=headers, timeout=10)
print(response.status_code)
```

---

## 11. Estrutura recomendada de projeto

```text
meu_projeto_scraping/
├── .venv/
├── requirements.txt
├── main.py
├── scraper.py
├── dados/
│   └── resultado.csv
└── README.md
```

---

## 12. Checklist final antes de codar

- [ ] Ambiente virtual criado
- [ ] Bibliotecas instaladas
- [ ] Página inspecionada no navegador
- [ ] Dados identificados
- [ ] Código de status validado
- [ ] Tratamento de erro implementado
- [ ] Estrutura do site entendida
- [ ] Arquivo de saída definido

---

## 13. Conclusão

Para começar em Web Scraping com Python, os primeiros passos são simples:

1. criar um ambiente virtual;
2. instalar requests e BeautifulSoup;
3. testar a página com uma requisição;
4. inspecionar o HTML;
5. extrair os dados com cuidado;
6. verificar se a página usa JavaScript ou API.

Esse preparo é importante porque muitos projetos quebram por causa de páginas dinâmicas ou por extrair elementos errados.

Se você seguir essa ordem, já estará pronto para começar a escrever seus primeiros scrapers com mais segurança.
