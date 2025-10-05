# QInvest Risk Score API

API FastAPI para cálculo de score de risco financeiro baseada em métricas empresariais.

Deploy (Google CLoud Run):
https://qinvest-score-228035976304.us-central1.run.app

Docs
https://qinvest-score-228035976304.us-central1.run.app/docs
https://qinvest-score-228035976304.us-central1.run.app/redoc


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

## Integração com APIs Externas

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

## Modelos de Machine Learning

A aplicação inclui um sistema completo de Machine Learning para previsão de scores de risco baseado em características financeiras históricas.

### Funcionalidades de ML

- **Modelos Múltiplos**: Implementa 5 tipos de algoritmos (Linear, Ridge, Lasso, Random Forest, Gradient Boosting)
- **Treinamento Automático**: Sistema de treinamento e avaliação automática de modelos
- **Previsão de Scores**: Prediz scores com intervalos de confiança
- **Avaliação Completa**: Métricas como R², MAE, RMSE e validação cruzada

### Benefícios do ML

- **Automação**: Processamento automático de grandes volumes de dados
- **Precisão**: Modelos treinados com dados históricos reais
- **Escalabilidade**: Pode ser facilmente expandido com novos algoritmos
- **Insights**: Identifica padrões não óbvios nos dados financeiros
- **Consistência**: Resultados padronizados e reprodutíveis

O sistema de ML complementa os cálculos tradicionais, oferecendo uma abordagem baseada em dados para avaliação de risco empresarial.
