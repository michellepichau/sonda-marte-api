# API da Sonda em Marte

Essa API REST foi criada para controlar sondas enviadas em missão para explorar um planalto retangular em Marte.

---

## Sobre o Projeto

A API permite lançar sondas em uma malha bidimensional, enviar comandos de movimento e consultar
a posição de todas as sondas ativas. Cada sonda é identificada por um UUID único e mantém seu
estado entre requisições.

---

## Tecnologias utilizadas

| Tecnologia | Versão |
|------------|--------|
| Python     | 3.11+  |
| FastAPI    | 0.110+ |
| Pydantic   | v2     |
| Uvicorn    | 0.29+  |
| Pytest     | 8.0+   |

---

## Instalação e Execução

### Pré-requisitos

- Python 3.11 ou superior
- pip

### Passos

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/sonda-marte-api.git
cd sonda-marte-api
```

**2. Crie e ative o ambiente virtual**
```bash
# Criar
python -m venv .venv


# Ativar — Linux/macOS
source .venv/bin/activate

# Ativar — Windows
.venv\Scripts\activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Execute a API**
```bash
uvicorn sonda_marte_api.main:app --reload
```

A API estará disponível em `http://localhost:8000`.
A documentação interativa (Swagger) em `http://localhost:8000/docs`.

---

## 🗂️ Estrutura do Projeto

 
```
sonda-marte-api/
├── sonda_marte_api/
│   ├── armazenamento/
│   │   └── probe_repository.py   # Persistência em memória
│   ├── rotas/
│   │   └── endpoints_probe.py    # Endpoints FastAPI
│   ├── schemas/
│   │   └── probe_schemas.py      # Modelos Pydantic (entrada/saída)
│   ├── servicos/
│   │   └── probe.py              # Domínio: lógica de movimento e validação
│   └── main.py                   # Inicialização da aplicação
├── tests/
│   ├── conftest.py               # Fixtures compartilhadas
│   ├── test_endpoint_probe.py    # Testes de integração
│   └── test_probe_service.py     # Testes unitários do domínio
├── pyproject.toml
└── README.md
```

## ⚠️ Observações Importantes

- **Armazenamento em memória:** os dados das sondas são perdidos ao reiniciar o servidor.
  Cada vez que a API for reiniciada, novas sondas precisam ser criadas.
- **Sonda sempre inicia em `(0, 0)`**, independente dos limites da malha que serão informados.
- **Uma sonda nunca sairá dos limites da malha,** nesse caso, se causarem isso irá retornar `422`
  e o estado anterior é preservado.

---

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com detalhes de cada teste
pytest -v

# Com cobertura de código
pytest --cov=sonda_marte_api
```

Os testes estão divididos em:

- **`test_probe_servico.py`** — testes unitários da lógica, como: criação, rotação,
  movimento, limites e comandos inválidos.
- **`test_endpoint_probe.py`** — testes de integração dos endpoints, como: lançamento,
  movimentação, persistência entre requisições e listagem.