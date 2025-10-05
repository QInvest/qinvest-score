import pytest
import httpx
import asyncio
from src.main import app
from fastapi.testclient import TestClient
import json

# Dados de teste baseados no exemplo do README
TEST_RISK_DATA = {
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
}

TEST_INTEREST_DATA = {
    "risco_final": 650.5,
    "prazo_meses": 12,
    "valor_solicitado": 100000
}

TEST_FULL_DATA = {
    **TEST_RISK_DATA,
    **TEST_INTEREST_DATA
}

class TestRootEndpoint:
    """Testes para o endpoint raiz"""

    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Testa se o endpoint raiz retorna informações corretas"""
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "QInvest Risk Score API" in data["message"]
        assert "version" in data
        assert "docs" in data

class TestHealthCheck:
    """Testes para o health check"""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Testa se o health check está funcionando"""
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

class TestRiskScoreEndpoint:
    """Testes para o cálculo de score de risco"""

    @pytest.mark.asyncio
    async def test_calculate_risk_score_valid_data(self):
        """Testa cálculo de score com dados válidos"""
        client = TestClient(app)
        response = client.post("/calculate-risk-score", json=TEST_RISK_DATA)

        assert response.status_code == 200
        data = response.json()

        # Verifica estrutura da resposta
        assert "score" in data
        assert "classificacao" in data

        # Verifica tipos
        assert isinstance(data["score"], float)
        assert isinstance(data["classificacao"], str)

        # Verifica se o score está dentro do range esperado (0-1000)
        assert 0 <= data["score"] <= 1000

        # Verifica se a classificação é válida
        assert data["classificacao"] in ['A', 'B', 'C', 'D', 'automatically_reproved']

    @pytest.mark.asyncio
    async def test_calculate_risk_score_missing_fields(self):
        """Testa cálculo de score com campos faltando"""
        incomplete_data = TEST_RISK_DATA.copy()
        del incomplete_data["idade_empresa"]

        client = TestClient(app)
        response = client.post("/calculate-risk-score", json=incomplete_data)

        assert response.status_code == 422  # Unprocessable Entity

    @pytest.mark.asyncio
    async def test_calculate_risk_score_invalid_types(self):
        """Testa cálculo de score com tipos de dados inválidos"""
        invalid_data = TEST_RISK_DATA.copy()
        invalid_data["idade_empresa"] = "invalid_string"

        client = TestClient(app)
        response = client.post("/calculate-risk-score", json=invalid_data)

        assert response.status_code == 422  # Unprocessable Entity

    @pytest.mark.asyncio
    async def test_calculate_risk_score_edge_cases(self):
        """Testa casos extremos para score de risco"""
        # Teste com empresa nova (idade baixa)
        edge_data = TEST_RISK_DATA.copy()
        edge_data["idade_empresa"] = 0.5
        edge_data["cpf_score"] = 300  # Score baixo
        edge_data["divida_total"] = 600000  # Dívida alta
        edge_data["faturamento_anual"] = 100000  # Faturamento baixo

        client = TestClient(app)
        response = client.post("/calculate-risk-score", json=edge_data)

        assert response.status_code == 200
        data = response.json()
        assert data["score"] > 0  # Deve ter algum score
        assert data["classificacao"] in ['A', 'B', 'C', 'D', 'automatically_reproved']

class TestInterestRateEndpoint:
    """Testes para o cálculo de taxa de juros"""

    @pytest.mark.asyncio
    async def test_calculate_interest_rate_valid_data(self):
        """Testa cálculo de taxa de juros com dados válidos"""
        client = TestClient(app)
        response = client.post("/calculate-interest-rate", json=TEST_INTEREST_DATA)

        assert response.status_code == 200
        data = response.json()

        # Verifica estrutura da resposta
        assert "taxa_juros_anual" in data
        assert isinstance(data["taxa_juros_anual"], float)

        # Verifica se a taxa está dentro de um range razoável
        assert 0 <= data["taxa_juros_anual"] <= 1  # Taxa anual em decimal

    @pytest.mark.asyncio
    async def test_calculate_interest_rate_missing_fields(self):
        """Testa cálculo de taxa com campos faltando"""
        incomplete_data = TEST_INTEREST_DATA.copy()
        del incomplete_data["risco_final"]

        client = TestClient(app)
        response = client.post("/calculate-interest-rate", json=incomplete_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_interest_rate_different_scenarios(self):
        """Testa diferentes cenários de taxa de juros"""
        scenarios = [
            {"risco_final": 900, "prazo_meses": 6, "valor_solicitado": 25000},   # Alto risco, curto prazo, valor baixo
            {"risco_final": 300, "prazo_meses": 24, "valor_solicitado": 400000}, # Baixo risco, longo prazo, valor alto
            {"risco_final": 650, "prazo_meses": 12, "valor_solicitado": 100000}, # Cenário médio
        ]

        for scenario in scenarios:
            client = TestClient(app)
            response = client.post("/calculate-interest-rate", json=scenario)
            assert response.status_code == 200
            data = response.json()
            assert "taxa_juros_anual" in data
            assert isinstance(data["taxa_juros_anual"], float)
            assert 0 <= data["taxa_juros_anual"] <= 1

class TestFullScoreEndpoint:
    """Testes para o cálculo completo (score + taxa)"""

    @pytest.mark.asyncio
    async def test_calculate_full_score_valid_data(self):
        """Testa cálculo completo com dados válidos"""
        client = TestClient(app)
        response = client.post("/calculate-full-score", json=TEST_FULL_DATA)

        assert response.status_code == 200
        data = response.json()

        # Verifica estrutura da resposta
        assert "score" in data
        assert "classificacao" in data
        assert "taxa_juros_anual" in data

        # Verifica tipos
        assert isinstance(data["score"], float)
        assert isinstance(data["classificacao"], str)
        assert isinstance(data["taxa_juros_anual"], float)

        # Verifica se o score está dentro do range esperado
        assert 0 <= data["score"] <= 1000
        assert data["classificacao"] in ['A', 'B', 'C', 'D', 'automatically_reproved']
        assert 0 <= data["taxa_juros_anual"] <= 1

    @pytest.mark.asyncio
    async def test_calculate_full_score_missing_fields(self):
        """Testa cálculo completo com campos faltando"""
        incomplete_data = TEST_FULL_DATA.copy()
        del incomplete_data["idade_empresa"]

        client = TestClient(app)
        response = client.post("/calculate-full-score", json=incomplete_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_full_score_integration(self):
        """Testa se os dois cálculos são consistentes quando chamados separadamente"""
        client = TestClient(app)
        # Primeiro faz o cálculo completo
        full_response = client.post("/calculate-full-score", json=TEST_FULL_DATA)
        full_data = full_response.json()

        # Depois calcula separadamente
        risk_response = client.post("/calculate-risk-score", json=TEST_RISK_DATA)
        risk_data = risk_response.json()

        interest_response = client.post("/calculate-interest-rate", json=TEST_INTEREST_DATA)
        interest_data = interest_response.json()

        # Verifica consistência
        assert abs(full_data["score"] - risk_data["score"]) < 0.01  # Mesma precisão
        assert full_data["classificacao"] == risk_data["classificacao"]
        # Tolerância maior para taxa de juros devido ao arredondamento do score
        assert abs(full_data["taxa_juros_anual"] - interest_data["taxa_juros_anual"]) < 0.05

class TestErrorHandling:
    """Testes para tratamento de erros"""

    @pytest.mark.asyncio
    async def test_invalid_json(self):
        """Testa requisição com JSON inválido"""
        client = TestClient(app)
        response = client.post("/calculate-risk-score", content="invalid json")

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_values_handling(self):
        """Testa se valores negativos são tratados adequadamente"""
        negative_data = TEST_RISK_DATA.copy()
        negative_data["divida_total"] = -1000  # Valor negativo

        client = TestClient(app)
        response = client.post("/calculate-risk-score", json=negative_data)

        # Pode aceitar valores negativos dependendo da lógica de negócio
        # O importante é que não quebre
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_zero_values_handling(self):
        """Testa tratamento de valores zero"""
        zero_data = TEST_RISK_DATA.copy()
        zero_data["faturamento_anual"] = 0
        zero_data["saldo_medio_diario"] = 0

        client = TestClient(app)
        response = client.post("/calculate-risk-score", json=zero_data)

        # Deve conseguir calcular mesmo com zeros (não deve dividir por zero)
        assert response.status_code == 200
        data = response.json()
        assert "score" in data

class TestPerformance:
    """Testes básicos de performance"""

    @pytest.mark.asyncio
    async def test_response_time(self):
        """Testa se a resposta é rápida o suficiente"""
        import time

        client = TestClient(app)
        start_time = time.time()
        response = client.post("/calculate-risk-score", json=TEST_RISK_DATA)
        end_time = time.time()

        assert response.status_code == 200
        # Deve responder em menos de 1 segundo
        assert (end_time - start_time) < 1.0

class TestQiTechIntegration:
    """Testes para integração com API Qi Tech"""

    @pytest.mark.asyncio
    async def test_qi_tech_empresa_score_valid_cnpj(self):
        """Testa consulta de score empresarial com CNPJ válido"""
        client = TestClient(app)
        response = client.post("/qi-tech/empresa/score?cnpj=12345678000123")

        assert response.status_code == 200
        data = response.json()

        # Verifica estrutura da resposta
        assert "score" in data
        assert "faixa_score" in data
        assert "probabilidade_inadimplencia" in data
        assert "analise_completa" in data
        assert "data_consulta" in data

        # Verifica tipos
        assert isinstance(data["score"], int)
        assert isinstance(data["faixa_score"], str)
        assert isinstance(data["probabilidade_inadimplencia"], float)

        # Verifica se o score está dentro do range esperado
        assert 0 <= data["score"] <= 1000
        assert data["faixa_score"] in ["A", "B", "C", "D"]

    @pytest.mark.asyncio
    async def test_qi_tech_empresa_score_invalid_cnpj(self):
        """Testa consulta de score empresarial com CNPJ inválido"""
        client = TestClient(app)
        response = client.post("/qi-tech/empresa/score?cnpj=123")

        assert response.status_code == 400
        data = response.json()
        assert "CNPJ deve ter 14 dígitos" in data["detail"]

    @pytest.mark.asyncio
    async def test_qi_tech_pessoa_score_valid_cpf(self):
        """Testa consulta de score pessoal com CPF válido"""
        client = TestClient(app)
        response = client.post("/qi-tech/pessoa/score?cpf=12345678901")

        assert response.status_code == 200
        data = response.json()

        # Verifica estrutura da resposta
        assert "score" in data
        assert "faixa_score" in data
        assert "probabilidade_inadimplencia" in data
        assert "analise_completa" in data
        assert "data_consulta" in data

        # Verifica tipos
        assert isinstance(data["score"], int)
        assert isinstance(data["faixa_score"], str)
        assert isinstance(data["probabilidade_inadimplencia"], float)

        # Verifica se o score está dentro do range esperado
        assert 0 <= data["score"] <= 1000
        assert data["faixa_score"] in ["A", "B", "C", "D"]

    @pytest.mark.asyncio
    async def test_qi_tech_pessoa_score_invalid_cpf(self):
        """Testa consulta de score pessoal com CPF inválido"""
        client = TestClient(app)
        response = client.post("/qi-tech/pessoa/score?cpf=123")

        assert response.status_code == 400
        data = response.json()
        assert "CPF deve ter 11 dígitos" in data["detail"]

    @pytest.mark.asyncio
    async def test_qi_tech_demo_integration(self):
        """Testa demonstração comparativa de scores"""
        client = TestClient(app)
        response = client.get("/qi-tech/demo")

        assert response.status_code == 200
        data = response.json()

        # Verifica estrutura da resposta
        assert "analise_interna" in data
        assert "qi_tech_empresa" in data
        assert "comparacao" in data
        assert "dados_completos_qi_tech" in data

        # Verifica análise interna
        analise_interna = data["analise_interna"]
        assert "score" in analise_interna
        assert "classificacao" in analise_interna
        assert "fonte" in analise_interna
        assert analise_interna["fonte"] == "QInvest Risk Score"

        # Verifica dados Qi Tech
        qi_tech = data["qi_tech_empresa"]
        assert "score" in qi_tech
        assert "faixa" in qi_tech
        assert "fonte" in qi_tech
        assert qi_tech["fonte"] == "Qi Tech API"

        # Verifica comparação
        comparacao = data["comparacao"]
        assert "diferenca_score" in comparacao
        assert "recomendacao" in comparacao

        # Verifica dados completos
        dados_qi_tech = data["dados_completos_qi_tech"]
        assert "fonte" in dados_qi_tech
        assert dados_qi_tech["fonte"] == "Qi Tech API (mockado)"

if __name__ == "__main__":
    # Executa os testes diretamente
    asyncio.run(pytest.main([__file__, "-v"]))
