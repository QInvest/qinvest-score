from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import random
from datetime import datetime

app = FastAPI(
    title="QInvest Risk Score API",
    description="API para cálculo de score de risco financeiro baseada em métricas empresariais",
    version="1.0.0"
)

# Modelos Pydantic para validação de entrada
class RiskScoreInput(BaseModel):
    idade_empresa: float
    cpf_score: int
    divida_total: float
    faturamento_anual: float
    saldo_medio_diario: float
    faturamento_medio_mensal: float
    estresse_caixa_dias: int
    valor_maior_cliente: float
    faturamento_total_periodo: float
    cnpj_score_api: int

class InterestRateInput(BaseModel):
    risco_final: float
    prazo_meses: int
    valor_solicitado: float

class FullScoreInput(BaseModel):
    # Dados para cálculo do score de risco
    idade_empresa: float
    cpf_score: int
    divida_total: float
    faturamento_anual: float
    saldo_medio_diario: float
    faturamento_medio_mensal: float
    estresse_caixa_dias: int
    valor_maior_cliente: float
    faturamento_total_periodo: float
    cnpj_score_api: int
    # Dados adicionais para cálculo da taxa de juros
    prazo_meses: int
    valor_solicitado: float

# Modelos de resposta
class RiskScoreOutput(BaseModel):
    score: float
    classificacao: str

class InterestRateOutput(BaseModel):
    taxa_juros_anual: float

class FullScoreOutput(BaseModel):
    score: float
    classificacao: str
    taxa_juros_anual: float

# Modelos para integração Qi Tech
class QiTechCompanyRequest(BaseModel):
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    data_fundacao: str
    endereco: Dict[str, Any]
    telefone: Optional[str] = None
    email: Optional[str] = None

class QiTechPersonRequest(BaseModel):
    cpf: str
    nome: str
    data_nascimento: str
    endereco: Dict[str, Any]
    telefone: Optional[str] = None
    email: Optional[str] = None

class QiTechScoreResponse(BaseModel):
    score: int
    faixa_score: str
    probabilidade_inadimplencia: float
    analise_completa: Dict[str, Any]
    data_consulta: str

def calculate_risk_score(
    idade_empresa: float,
    cpf_score: int,
    divida_total: float,
    faturamento_anual: float,
    saldo_medio_diario: float,
    faturamento_medio_mensal: float,
    estresse_caixa_dias: int,
    valor_maior_cliente: float,
    faturamento_total_periodo: float,
    cnpj_score_api: int
) -> tuple[float, str]:
    """
    Calcula o score de risco e a classificação de uma empresa com base em suas métricas financeiras.
    """
    # --- 1. Normalização das Variáveis ---
    if idade_empresa < 2: risco_idade = 400
    elif idade_empresa < 5: risco_idade = 600
    else: risco_idade = 1000

    if cpf_score < 400: risco_cpf = 100
    elif cpf_score < 700: risco_cpf = 500
    elif cpf_score < 900: risco_cpf = 700
    else: risco_cpf = 1000

    if faturamento_anual > 0:
        indice_endividamento = divida_total / faturamento_anual
        if indice_endividamento > 1.0: risco_endividamento = 100
        elif indice_endividamento > 0.6: risco_endividamento = 300
        elif indice_endividamento > 0.3: risco_endividamento = 700
        else: risco_endividamento = 1000
    else:
        risco_endividamento = 0

    if faturamento_medio_mensal > 0:
        indice_liquidez = saldo_medio_diario / faturamento_medio_mensal
        if indice_liquidez < 0.1: risco_liquidez = 100
        elif indice_liquidez < 0.4: risco_liquidez = 500
        else: risco_liquidez = 1000
    else:
        risco_liquidez = 0

    if estresse_caixa_dias > 10: risco_estresse = 0
    elif estresse_caixa_dias > 5: risco_estresse = 300
    elif estresse_caixa_dias > 0: risco_estresse = 700
    else: risco_estresse = 1000

    if faturamento_total_periodo > 0:
        indice_concentracao = valor_maior_cliente / faturamento_total_periodo
        if indice_concentracao > 0.6: risco_concentracao = 100
        elif indice_concentracao > 0.3: risco_concentracao = 500
        elif indice_concentracao > 0.2: risco_concentracao = 900
        else: risco_concentracao = 1000
    else:
        risco_concentracao = 0

    # --- 2. Aplicação dos Pesos ---
    pesos = {
        "idade": 0.05, "cpf_score": 0.05, "endividamento": 0.15,
        "liquidez": 0.10, "estresse_caixa": 0.10, "concentracao": 0.05,
        "score_biro": 0.5,
    }
    risco_final = (
        risco_endividamento * pesos["endividamento"] + risco_liquidez * pesos["liquidez"] +
        risco_estresse * pesos["estresse_caixa"] + risco_concentracao * pesos["concentracao"] +
        risco_idade * pesos["idade"] + risco_cpf * pesos["cpf_score"] +
        cnpj_score_api * pesos["score_biro"]
    )
    risco_final = max(0, min(1000, risco_final))

    # --- 3. Classificação do Risco ---
    if risco_final > 800: classificacao = 'A'
    elif risco_final > 600: classificacao = 'B'
    elif risco_final > 400: classificacao = 'C'
    elif risco_final > 200: classificacao = 'D'
    else: classificacao = 'automatically_reproved'

    return round(risco_final, 2), classificacao

def calcular_taxa_juros_anual(
    risco_final: float,
    prazo_meses: int,
    valor_solicitado: float
) -> float:
    """
    Calcula a taxa de juros anual com base no risco, prazo e valor.
    """
    TAXA_BASE = 0.12
    premio_risco = (-(risco_final - 1000) / 1000) * 0.25

    if prazo_meses <= 6: premio_prazo = 0.00
    elif prazo_meses <= 12: premio_prazo = 0.02
    elif prazo_meses <= 18: premio_prazo = 0.04
    else: premio_prazo = 0.06

    if valor_solicitado < 50000: premio_valor = 0.00
    elif valor_solicitado < 150000: premio_valor = 0.01
    elif valor_solicitado < 300000: premio_valor = 0.025
    else: premio_valor = 0.05

    taxa_final_anual = TAXA_BASE + (premio_risco + premio_prazo + premio_valor)
    return taxa_final_anual

def consultar_score_qi_tech_empresa(cnpj: str) -> QiTechScoreResponse:
    """
    Função mockada que simula consulta de score empresarial na API da Qi Tech.

    Na implementação real, esta função faria:
    1. Autenticação na API da Qi Tech
    2. Chamada para endpoint de análise de empresa
    3. Tratamento da resposta
    4. Mapeamento dos dados para nosso formato

    Exemplo de integração real:
    ```python
    import requests
    import json

    def consultar_score_qi_tech_empresa_real(cnpj: str) -> QiTechScoreResponse:
        # Configurações da API Qi Tech
        QI_TECH_BASE_URL = "https://api.qitech.com.br"
        QI_TECH_TOKEN = os.getenv("QI_TECH_API_TOKEN")

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
            json=payload
        )

        if response.status_code == 200:
            data = response.json()

            # Mapeia resposta da Qi Tech para nosso formato
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

    Documentação da API Qi Tech:
    - Endpoint: POST /v1/empresas/analise
    - Headers: Authorization: Bearer {token}, Content-Type: application/json
    - Payload: {"cnpj": "string", "tipo_analise": "simples|completa"}
    - Resposta: {"score": int, "faixa": str, "probabilidade_inadimplencia": float, ...}
    """
    # Simulação de resposta da Qi Tech com dados mockados
    # Na prática, isso seria uma chamada real para a API

    # Base de dados mockada para demonstração
    empresas_mock = {
        "12345678000123": {
            "score": 750,
            "faixa": "B",
            "prob_inadimplencia": 0.15,
            "setor": "Comércio",
            "porte": "Médio",
            "tempo_atuacao": 8
        },
        "98765432000198": {
            "score": 450,
            "faixa": "D",
            "prob_inadimplencia": 0.35,
            "setor": "Serviços",
            "porte": "Pequeno",
            "tempo_atuacao": 3
        }
    }

    # Busca dados mockados ou gera valores aleatórios
    if cnpj in empresas_mock:
        empresa_data = empresas_mock[cnpj]
    else:
        # Gera dados aleatórios para demonstração
        empresa_data = {
            "score": random.randint(300, 900),
            "faixa": random.choice(["A", "B", "C", "D"]),
            "prob_inadimplencia": round(random.uniform(0.05, 0.40), 3),
            "setor": random.choice(["Comércio", "Serviços", "Indústria"]),
            "porte": random.choice(["Micro", "Pequeno", "Médio", "Grande"]),
            "tempo_atuacao": random.randint(1, 20)
        }

    return QiTechScoreResponse(
        score=empresa_data["score"],
        faixa_score=empresa_data["faixa"],
        probabilidade_inadimplencia=empresa_data["prob_inadimplencia"],
        analise_completa={
            "cnpj": cnpj,
            "dados_empresa": empresa_data,
            "fonte": "Qi Tech API (mockado)",
            "timestamp": datetime.now().isoformat()
        },
        data_consulta=datetime.now().isoformat()
    )

def consultar_score_qi_tech_pessoa(cpf: str) -> QiTechScoreResponse:
    """
    Função mockada que simula consulta de score pessoal na API da Qi Tech.

    Na implementação real, esta função faria:
    1. Autenticação na API da Qi Tech
    2. Chamada para endpoint de análise de pessoa física
    3. Tratamento da resposta
    4. Mapeamento dos dados para nosso formato

    Exemplo de integração real:
    ```python
    def consultar_score_qi_tech_pessoa_real(cpf: str) -> QiTechScoreResponse:
        QI_TECH_BASE_URL = "https://api.qitech.com.br"
        QI_TECH_TOKEN = os.getenv("QI_TECH_API_TOKEN")

        headers = {
            "Authorization": f"Bearer {QI_TECH_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "cpf": cpf,
            "tipo_analise": "completa"
        }

        response = requests.post(
            f"{QI_TECH_BASE_URL}/v1/pessoas/analise",
            headers=headers,
            json=payload
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

    Documentação da API Qi Tech:
    - Endpoint: POST /v1/pessoas/analise
    - Headers: Authorization: Bearer {token}, Content-Type: application/json
    - Payload: {"cpf": "string", "tipo_analise": "simples|completa"}
    - Resposta: {"score": int, "faixa": str, "probabilidade_inadimplencia": float, ...}
    """
    # Simulação de resposta da Qi Tech com dados mockados
    # Na prática, isso seria uma chamada real para a API

    # Base de dados mockada para demonstração
    pessoas_mock = {
        "12345678901": {
            "score": 820,
            "faixa": "A",
            "prob_inadimplencia": 0.08,
            "idade": 35,
            "renda_mensal": 8500,
            "estado_civil": "Casado"
        },
        "98765432109": {
            "score": 380,
            "faixa": "D",
            "prob_inadimplencia": 0.42,
            "idade": 25,
            "renda_mensal": 2200,
            "estado_civil": "Solteiro"
        }
    }

    # Busca dados mockados ou gera valores aleatórios
    if cpf in pessoas_mock:
        pessoa_data = pessoas_mock[cpf]
    else:
        # Gera dados aleatórios para demonstração
        pessoa_data = {
            "score": random.randint(200, 950),
            "faixa": random.choice(["A", "B", "C", "D"]),
            "prob_inadimplencia": round(random.uniform(0.02, 0.50), 3),
            "idade": random.randint(18, 70),
            "renda_mensal": random.randint(1500, 15000),
            "estado_civil": random.choice(["Solteiro", "Casado", "Divorciado", "Viúvo"])
        }

    return QiTechScoreResponse(
        score=pessoa_data["score"],
        faixa_score=pessoa_data["faixa"],
        probabilidade_inadimplencia=pessoa_data["prob_inadimplencia"],
        analise_completa={
            "cpf": cpf,
            "dados_pessoa": pessoa_data,
            "fonte": "Qi Tech API (mockado)",
            "timestamp": datetime.now().isoformat()
        },
        data_consulta=datetime.now().isoformat()
    )

@app.get("/")
async def root():
    """Endpoint raiz com informações básicas da API"""
    return {
        "message": "QInvest Risk Score API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.post("/calculate-risk-score", response_model=RiskScoreOutput)
async def calculate_risk_score_endpoint(data: RiskScoreInput):
    """
    Calcula o score de risco com base nas métricas financeiras da empresa.

    Parâmetros necessários:
    - idade_empresa: Tempo de existência da empresa em anos
    - cpf_score: Score de crédito do CPF (0-1000)
    - divida_total: Total de dívidas da empresa
    - faturamento_anual: Faturamento anual da empresa
    - saldo_medio_diario: Saldo médio diário em caixa
    - faturamento_medio_mensal: Faturamento médio mensal
    - estresse_caixa_dias: Dias de estresse no caixa
    - valor_maior_cliente: Valor do maior cliente
    - faturamento_total_periodo: Faturamento total do período
    - cnpj_score_api: Score do CNPJ via API (0-1000)
    """
    try:
        score, classificacao = calculate_risk_score(
            data.idade_empresa,
            data.cpf_score,
            data.divida_total,
            data.faturamento_anual,
            data.saldo_medio_diario,
            data.faturamento_medio_mensal,
            data.estresse_caixa_dias,
            data.valor_maior_cliente,
            data.faturamento_total_periodo,
            data.cnpj_score_api
        )

        return RiskScoreOutput(score=score, classificacao=classificacao)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro no cálculo: {str(e)}")

@app.post("/calculate-interest-rate", response_model=InterestRateOutput)
async def calculate_interest_rate_endpoint(data: InterestRateInput):
    """
    Calcula a taxa de juros anual com base no score de risco, prazo e valor solicitado.

    Parâmetros necessários:
    - risco_final: Score de risco calculado (0-1000)
    - prazo_meses: Prazo do financiamento em meses
    - valor_solicitado: Valor solicitado para financiamento
    """
    try:
        taxa_juros = calcular_taxa_juros_anual(
            data.risco_final,
            data.prazo_meses,
            data.valor_solicitado
        )

        return InterestRateOutput(taxa_juros_anual=round(taxa_juros, 4))

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro no cálculo da taxa: {str(e)}")

@app.post("/calculate-full-score", response_model=FullScoreOutput)
async def calculate_full_score_endpoint(data: FullScoreInput):
    """
    Calcula o score de risco completo e a taxa de juros recomendada.

    Esta rota combina ambos os cálculos em uma única chamada.
    """
    try:
        # Primeiro calcula o score de risco
        score, classificacao = calculate_risk_score(
            data.idade_empresa,
            data.cpf_score,
            data.divida_total,
            data.faturamento_anual,
            data.saldo_medio_diario,
            data.faturamento_medio_mensal,
            data.estresse_caixa_dias,
            data.valor_maior_cliente,
            data.faturamento_total_periodo,
            data.cnpj_score_api
        )

        # Depois calcula a taxa de juros baseada no score
        taxa_juros = calcular_taxa_juros_anual(
            score,
            data.prazo_meses,
            data.valor_solicitado
        )

        return FullScoreOutput(
            score=score,
            classificacao=classificacao,
            taxa_juros_anual=round(taxa_juros, 4)
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro no cálculo completo: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return {"status": "healthy"}

@app.post("/qi-tech/empresa/score", response_model=QiTechScoreResponse)
async def consultar_score_empresa_qi_tech(cnpj: str):
    """
    Consulta score empresarial usando API da Qi Tech (mockado).

    Este endpoint demonstra como seria a integração real com a API da Qi Tech
    para consultar scores de empresas.

    Parâmetros de query:
    - cnpj: CNPJ da empresa (apenas números)

    Exemplo de uso:
    GET /qi-tech/empresa/score?cnpj=12345678000123

    Na implementação real, seria necessário:
    1. Token de autenticação da Qi Tech
    2. Chamada para endpoint oficial
    3. Tratamento de erros e rate limiting
    """
    if not cnpj or len(cnpj) != 14:
        raise HTTPException(status_code=400, detail="CNPJ deve ter 14 dígitos")

    try:
        return consultar_score_qi_tech_empresa(cnpj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Qi Tech: {str(e)}")

@app.post("/qi-tech/pessoa/score", response_model=QiTechScoreResponse)
async def consultar_score_pessoa_qi_tech(cpf: str):
    """
    Consulta score pessoal usando API da Qi Tech (mockado).

    Este endpoint demonstra como seria a integração real com a API da Qi Tech
    para consultar scores de pessoas físicas.

    Parâmetros de query:
    - cpf: CPF da pessoa (apenas números)

    Exemplo de uso:
    GET /qi-tech/pessoa/score?cpf=12345678901

    Na implementação real, seria necessário:
    1. Token de autenticação da Qi Tech
    2. Chamada para endpoint oficial
    3. Tratamento de erros e rate limiting
    """
    if not cpf or len(cpf) != 11:
        raise HTTPException(status_code=400, detail="CPF deve ter 11 dígitos")

    try:
        return consultar_score_qi_tech_pessoa(cpf)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Qi Tech: {str(e)}")

@app.get("/qi-tech/demo")
async def demo_qi_tech_integration():
    """
    Endpoint de demonstração que mostra como seria usar múltiplas fontes de score.

    Este endpoint combina:
    1. Nosso cálculo interno de risco
    2. Consulta mockada à API da Qi Tech
    3. Análise comparativa dos resultados

    Exemplo de resposta:
    {
        "analise_interna": {
            "score": 650.5,
            "classificacao": "B",
            "fonte": "QInvest Risk Score"
        },
        "qi_tech_empresa": {
            "score": 750,
            "faixa": "B",
            "fonte": "Qi Tech API"
        },
        "comparacao": {
            "diferenca_score": 99.5,
            "recomendacao": "Usar média ponderada"
        }
    }
    """
    # Dados de exemplo
    cnpj_exemplo = "12345678000123"

    # Calcula score interno
    dados_internos = {
        "idade_empresa": 5.0,
        "cpf_score": 750,
        "divida_total": 150000,
        "faturamento_anual": 800000,
        "saldo_medio_diario": 25000,
        "faturamento_medio_mensal": 66667,
        "estresse_caixa_dias": 3,
        "valor_maior_cliente": 120000,
        "faturamento_total_periodo": 600000,
        "cnpj_score_api": 700
    }

    score_interno, classificacao_interna = calculate_risk_score(**dados_internos)

    # Consulta Qi Tech (mockada)
    qi_tech_result = consultar_score_qi_tech_empresa(cnpj_exemplo)

    # Análise comparativa
    diferenca = abs(score_interno - qi_tech_result.score)

    if diferenca < 50:
        recomendacao = "Scores similares - usar média ponderada"
    elif score_interno > qi_tech_result.score:
        recomendacao = "Score interno mais conservador - revisar parâmetros"
    else:
        recomendacao = "Qi Tech mais otimista - validar dados externos"

    return {
        "analise_interna": {
            "score": round(score_interno, 2),
            "classificacao": classificacao_interna,
            "fonte": "QInvest Risk Score"
        },
        "qi_tech_empresa": {
            "score": qi_tech_result.score,
            "faixa": qi_tech_result.faixa_score,
            "probabilidade_inadimplencia": qi_tech_result.probabilidade_inadimplencia,
            "fonte": "Qi Tech API"
        },
        "comparacao": {
            "diferenca_score": round(diferenca, 2),
            "recomendacao": recomendacao
        },
        "dados_completos_qi_tech": qi_tech_result.analise_completa
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
