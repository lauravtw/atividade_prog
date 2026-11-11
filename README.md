# Festa do IFC Campus Blumenau

Aplicacao web para apoiar estudantes na organizacao de uma festa no IFC Campus Blumenau. Permite cadastrar alimentos e precos de venda, insumos doados e seus fornecedores/doadores, alem das pessoas que trabalharao no evento (alunos, pais e servidores).

## Requisitos

- Python 3.10 ou superior
- [uv](https://docs.astral.sh/uv/)

## Executar localmente

No terminal, a partir da raiz do projeto:

```powershell
uv sync
uv run streamlit run src/app.py
```

O SQLite e usado por padrao para desenvolvimento e testes locais. O arquivo `festa_ifc.db` e criado automaticamente na raiz do projeto.

## Banco de dados MySQL

Em producao, configure a variavel de ambiente `DATABASE_URL` com a URL SQLAlchemy do MySQL. O driver PyMySQL ja esta incluido:

```text
mysql+pymysql://USUARIO:SENHA@HOST:3306/NOME_DO_BANCO?charset=utf8mb4
```

No PowerShell, configure a variavel apenas para a sessao atual com:

```powershell
$env:DATABASE_URL = "mysql+pymysql://USUARIO:SENHA@HOST:3306/NOME_DO_BANCO?charset=utf8mb4"
uv run streamlit run src/app.py
```

Nao salve credenciais no repositorio. Para o Streamlit Community Cloud, cadastre `DATABASE_URL` nos **App settings > Secrets** do aplicativo, por exemplo:

```toml
DATABASE_URL = "mysql+pymysql://USUARIO:SENHA@HOST:3306/NOME_DO_BANCO?charset=utf8mb4"
```

Na configuracao do deploy, use `src/app.py` como arquivo principal do aplicativo.

O banco e as credenciais MySQL devem estar disponiveis ao aplicativo publicado. A aplicacao cria as tabelas necessarias na primeira inicializacao.

## Funcionalidades

- CRUD de alimentos, com descricao, preco de venda e insumos utilizados.
- CRUD de insumos doados, com unidade, quantidade doada e fornecedor/doador.
- CRUD de fornecedores/doadores.
- CRUD de pessoas voluntarias, classificadas como aluno(a), pai/mae ou servidor(a).
- Painel resumido com contagem dos cadastros e cardapio.
