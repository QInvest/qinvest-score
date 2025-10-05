# QInvest Risk Score API

API FastAPI para cálculo de score de risco financeiro baseada em métricas empresariais.

## Funcionalidades

### Cálculos Internos
- **Cálculo de Score de Risco**: Avalia empresas baseado em métricas financeiras
- **Cálculo de Taxa de Juros**: Determina taxa de juros baseada no score de risco
- **Cálculo Completo**: Combina ambos os cálculos em uma única chamada

### Integração com APIs Externas (Qi Tech)
- **Consulta de Score Empresarial**: Integração mockada com API da Qi Tech para empresas
- **Consulta de Score Pessoal**: Integração mockada com API da Qi Tech para pessoas físicas
- **Demonstração Comparativa**: Compara scores internos com dados externos

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Como executar

### Desenvolvimento
```bash
python main.py
```

Ou usando uvicorn diretamente:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Produção
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Endpoints

### Raiz
- **GET /**: Informações básicas da API

### Health Check
- **GET /health**: Verifica se a API está funcionando

### Cálculo de Score de Risco
- **POST /calculate-risk-score**: Calcula o score de risco
- **Body**: Dados financeiros da empresa

### Cálculo de Taxa de Juros
- **POST /calculate-interest-rate**: Calcula a taxa de juros anual
- **Body**: Score de risco, prazo e valor solicitado

### Cálculo Completo
- **POST /calculate-full-score**: Calcula score e taxa de juros
- **Body**: Todos os dados necessários

## Documentação da API

Acesse `http://localhost:8000/docs` para ver a documentação interativa Swagger/OpenAPI.

## Testes

### Executar todos os testes
```bash
pytest test_api.py -v
```

### Executar testes específicos
```bash
# Apenas testes de score de risco
pytest test_api.py::TestRiskScoreEndpoint -v

# Apenas testes de taxa de juros
pytest test_api.py::TestInterestRateEndpoint -v

# Apenas testes de integração
pytest test_api.py::TestFullScoreEndpoint -v
```

### Executar com cobertura
```bash
pip install pytest-cov
pytest --cov=main test_api.py
```

### Usando o script auxiliar
```bash
# Executar todos os testes
python run_tests.py

# Executar testes específicos (interativo)
python run_tests.py --specific

# Ver ajuda
python run_tests.py --help
```

## Exemplo de Uso

### Cálculo de Score de Risco
```bash
curl -X POST "http://localhost:8000/calculate-risk-score" \
     -H "Content-Type: application/json" \
     -d '{
       "idade_empresa": 3.5,
       "cpf_score": 750,
       "divida_total": 100000,
       "faturamento_anual": 500000,
       "saldo_medio_diario": 15000,
       "faturamento_medio_mensal": 41667,
       "estresse_caixa_dias": 2,
       "valor_maior_cliente": 80000,
       "faturamento_total_periodo": 300000,
       "cnpj_score_api": 800
     }'
```

### Cálculo de Taxa de Juros
```bash
curl -X POST "http://localhost:8000/calculate-interest-rate" \
     -H "Content-Type: application/json" \
     -d '{
       "risco_final": 650.5,
       "prazo_meses": 12,
       "valor_solicitado": 100000
     }'
```

### Integração com Qi Tech (Exemplos Mockados)

#### Consulta de Score Empresarial
```bash
curl "http://localhost:8000/qi-tech/empresa/score?cnpj=12345678000123"
```

#### Consulta de Score Pessoal
```bash
curl "http://localhost:8000/qi-tech/pessoa/score?cpf=12345678901"
```

#### Demonstração Comparativa
```bash
curl "http://localhost:8000/qi-tech/demo"
```

## Parâmetros do Score de Risco

- `idade_empresa`: Tempo de existência da empresa em anos
- `cpf_score`: Score de crédito do CPF (0-1000)
- `divida_total`: Total de dívidas da empresa
- `faturamento_anual`: Faturamento anual da empresa
- `saldo_medio_diario`: Saldo médio diário em caixa
- `faturamento_medio_mensal`: Faturamento médio mensal
- `estresse_caixa_dias`: Dias de estresse no caixa
- `valor_maior_cliente`: Valor do maior cliente
- `faturamento_total_periodo`: Faturamento total do período
- `cnpj_score_api`: Score do CNPJ via API (0-1000)

## Classificações de Risco

- **A**: Score > 800 (Baixo risco)
- **B**: Score > 600 (Risco moderado)
- **C**: Score > 400 (Risco médio)
- **D**: Score > 200 (Alto risco)
- **automatically_reproved**: Score ≤ 200 (Reprovado automaticamente)

## 🔗 Integração com APIs Externas

### Qi Tech API Integration

A API inclui endpoints mockados que demonstram como integrar com a API da Qi Tech para obter scores de empresas e pessoas físicas.

#### Endpoints Disponíveis

- `GET /qi-tech/empresa/score?cnpj={cnpj}` - Consulta score empresarial
- `GET /qi-tech/pessoa/score?cpf={cpf}` - Consulta score pessoal
- `GET /qi-tech/demo` - Demonstração comparativa de scores

#### Implementação Real

Para implementar a integração real com a API da Qi Tech:

1. **Obter credenciais**: Registre-se na Qi Tech e obtenha um token de API
2. **Configurar ambiente**: Adicione as variáveis de ambiente:
   ```bash
   export QI_TECH_BASE_URL="https://api.qitech.com.br"
   export QI_TECH_API_TOKEN="seu_token_aqui"
   ```

3. **Substituir funções mockadas**: No arquivo `src/main.py`, substitua as funções `consultar_score_qi_tech_empresa` e `consultar_score_qi_tech_pessoa` pela implementação real usando `requests`

4. **Instalar dependências**: Adicione `requests` ao `requirements.txt`:
   ```bash
   pip install requests
   ```

#### Exemplo de Implementação Real

```python
import requests
import os

QI_TECH_BASE_URL = os.getenv("QI_TECH_BASE_URL", "https://api.qitech.com.br")
QI_TECH_TOKEN = os.getenv("QI_TECH_API_TOKEN")

def consultar_score_qi_tech_empresa_real(cnpj: str) -> QiTechScoreResponse:
    headers = {
        "Authorization": f"Bearer {QI_TECH_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "cnpj": cnpj,
        "tipo_analise": "completa"
    }

    response = requests.post(
        f"{QI_TECH_BASE_URL}/v1/empresas/analise",
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        return QiTechScoreResponse(
            score=data["score"],
            faixa_score=data["faixa"],
            probabilidade_inadimplencia=data["probabilidade_inadimplencia"],
            analise_completa=data,
            data_consulta=datetime.now().isoformat()
        )
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Erro na API Qi Tech: {response.text}"
        )
```

#### Benefícios da Integração

- **Dados externos**: Complementa análise interna com dados de mercado
- **Validação cruzada**: Compara scores internos com fontes externas
- **Melhor precisão**: Combinação de múltiplas fontes de dados
- **Conformidade**: Uso de dados de bureaus de crédito reconhecidos


## Dataset

About
This dataset is designed for bankruptcy prediction concerning American public companies. It includes detailed accounting data for companies listed on the New York Stock Exchange (NYSE) and NASDAQ from 1999 to 2018. The dataset identifies companies as bankrupt if their management filed for Chapter 11 (reorganisation) or Chapter 7 (cessation of operations) of the Bankruptcy Code. A label of '1' signifies bankruptcy in the fiscal year prior to filing, while '0' indicates normal operation. This dataset is notable for being complete, with no missing values, synthetic entries, or imputed additions.
Columns
company_name: The name of the company. This column can be optionally removed.
status_label: The target column indicating the company's status, either 'alive' or 'failed' (bankrupt).
year: The fiscal year to which the accounting data corresponds, ranging from 1999 to 2018.
X1 (Current assets): All assets expected to be sold or used in standard business operations within the next year.
X2 (Cost of goods sold): The total amount paid directly related to the sale of products.
X3 (Depreciation and amortisation): The loss of value of tangible (depreciation) and intangible (amortisation) fixed assets over time.
X4 (EBITDA): Earnings before interest, taxes, depreciation, and amortisation, serving as a measure of overall financial performance.
X5 (Inventory): The accounting of items and raw materials used in production or sold by the company.
X6 (Net Income): The overall profitability of a company after all expenses and costs have been deducted from total revenue.
X7 (Total Receivables): The balance of money owed to a firm for goods or services delivered or used but not yet paid for by customers.
X8 (Market value): The price of an asset in a marketplace, specifically referring to market capitalisation for publicly traded companies.
X9 (Net sales): The sum of a company's gross sales minus returns, allowances, and discounts.
X10 (Total assets): All assets, or items of value, owned by a business.
X11 (Total Long-term debt): A company's loans and other liabilities not due within one year of the balance sheet date.
X12 (EBIT): Earnings before interest and taxes.
X13 (Gross Profit): The profit a business makes after subtracting all costs related to manufacturing and selling its products or services.
X14 (Total Current Liabilities): The sum of accounts payable, accrued liabilities, and taxes such as bonds payable at year-end, salaries, and commissions remaining.
X15 (Retained Earnings): The amount of profit a company has left after paying all its direct costs, indirect costs, income taxes, and dividends to shareholders.
X16 (Total Revenue): The income a business has made from all sales before subtracting expenses, potentially including interest and dividends from investments.
X17 (Total Liabilities): The combined debts and obligations that the company owes to outside parties.
X18 (Total Operating Expenses): The expenses a business incurs through its normal business operations.