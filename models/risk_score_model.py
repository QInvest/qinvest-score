"""
Modelo de Machine Learning para previsão de scores de risco.

Este módulo implementa modelos de ML para prever scores de risco baseados
em características financeiras das empresas.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.pipeline import Pipeline
import joblib
import os
from typing import Dict, Tuple, Any, Optional
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskScorePredictor:
    """
    Modelo de ML para previsão de scores de risco empresarial.

    Características usadas para previsão:
    - idade_empresa: Tempo de existência da empresa
    - divida_total: Total de dívidas
    - faturamento_anual: Faturamento anual
    - saldo_medio_diario: Saldo médio diário
    - estresse_caixa_dias: Dias de estresse no caixa
    - valor_maior_cliente: Valor do maior cliente
    - concentracao_clientes: Concentração de clientes
    """

    def __init__(self, model_type: str = "linear"):
        """
        Inicializa o preditor de scores.

        Args:
            model_type: Tipo de modelo ('linear', 'ridge', 'lasso', 'random_forest', 'gradient_boosting')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.pipeline = None
        self.is_trained = False
        self.feature_columns = [
            'idade_empresa', 'divida_total', 'faturamento_anual',
            'saldo_medio_diario', 'estresse_caixa_dias',
            'valor_maior_cliente', 'concentracao_clientes'
        ]
        self.model_dir = os.path.join(os.path.dirname(__file__), 'trained_models')
        os.makedirs(self.model_dir, exist_ok=True)

    def _create_model(self):
        """Cria o modelo baseado no tipo especificado."""
        models = {
            'linear': LinearRegression(),
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=0.1),
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
        }

        return models.get(self.model_type, LinearRegression())

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara as características para o modelo.

        Args:
            df: DataFrame com dados brutos

        Returns:
            DataFrame com características preparadas
        """
        # Criar características derivadas
        df_processed = df.copy()

        # Calcular concentração de clientes (se disponível)
        if 'faturamento_total_periodo' in df.columns and 'valor_maior_cliente' in df.columns:
            df_processed['concentracao_clientes'] = df['valor_maior_cliente'] / df['faturamento_total_periodo']
        else:
            # Usar valor padrão se não disponível
            df_processed['concentracao_clientes'] = 0.3  # 30% concentração média

        # Selecionar apenas as colunas de características
        available_features = [col for col in self.feature_columns if col in df_processed.columns]

        if not available_features:
            raise ValueError("Nenhuma característica disponível para treinamento")

        logger.info(f"Características usadas: {available_features}")
        return df_processed[available_features]

    def train(self, df: pd.DataFrame, target_column: str = 'score') -> Dict[str, Any]:
        """
        Treina o modelo com dados históricos.

        Args:
            df: DataFrame com dados históricos
            target_column: Nome da coluna alvo (score)

        Returns:
            Dicionário com métricas de treinamento
        """
        logger.info(f"Iniciando treinamento do modelo {self.model_type}")

        if target_column not in df.columns:
            raise ValueError(f"Coluna alvo '{target_column}' não encontrada")

        # Preparar dados
        X = self.prepare_features(df)
        y = df[target_column]

        # Dividir dados em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Criar pipeline
        self.pipeline = Pipeline([
            ('scaler', self.scaler),
            ('model', self._create_model())
        ])

        # Treinar modelo
        self.pipeline.fit(X_train, y_train)

        # Avaliar modelo
        y_pred = self.pipeline.predict(X_test)

        # Calcular métricas
        metrics = {
            'model_type': self.model_type,
            'training_date': datetime.now().isoformat(),
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'features_used': list(X.columns),
            'metrics': {
                'mse': mean_squared_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'mae': mean_absolute_error(y_test, y_pred),
                'r2_score': r2_score(y_test, y_pred)
            }
        }

        # Validação cruzada
        cv_scores = cross_val_score(self.pipeline, X, y, cv=5, scoring='r2')
        metrics['cross_validation'] = {
            'mean_r2': cv_scores.mean(),
            'std_r2': cv_scores.std(),
            'scores': cv_scores.tolist()
        }

        self.is_trained = True
        logger.info(f"Modelo treinado com sucesso. R²: {metrics['metrics']['r2_score']:.3f}")

        return metrics

    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Faz previsão de score para novos dados.

        Args:
            features: Dicionário com características da empresa

        Returns:
            Dicionário com previsão e confiança
        """
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado ainda")

        # Converter para DataFrame
        df_features = pd.DataFrame([features])

        # Preparar características
        X = self.prepare_features(df_features)

        # Fazer previsão
        prediction = self.pipeline.predict(X)[0]

        # Calcular intervalo de confiança (aproximado)
        # Usando desvio padrão residual como estimativa de incerteza
        if hasattr(self.pipeline.named_steps['model'], 'predict'):
            # Para modelos lineares, podemos estimar a variância
            residual_std = np.sqrt(mean_squared_error(
                self.pipeline.predict(self.pipeline.named_steps['scaler'].transform(
                    self.prepare_features(pd.DataFrame([features]))
                )), [prediction]
            ))

            confidence_interval = 1.96 * residual_std  # 95% confidence
        else:
            confidence_interval = 50  # Valor padrão para modelos complexos

        # Classificar o score previsto
        if prediction > 800:
            classificacao = 'A'
        elif prediction > 600:
            classificacao = 'B'
        elif prediction > 400:
            classificacao = 'C'
        elif prediction > 200:
            classificacao = 'D'
        else:
            classificacao = 'automatically_reproved'

        result = {
            'predicted_score': round(prediction, 2),
            'classificacao': classificacao,
            'confidence_interval': round(confidence_interval, 2),
            'confidence_level': '95%',
            'model_type': self.model_type,
            'input_features': features
        }

        logger.info(f"Previsão realizada: {result['predicted_score']} ({result['classificacao']})")
        return result

    def save_model(self, filename: Optional[str] = None) -> str:
        """
        Salva o modelo treinado em arquivo.

        Args:
            filename: Nome do arquivo (opcional)

        Returns:
            Caminho completo do arquivo salvo
        """
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado ainda")

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"risk_score_model_{self.model_type}_{timestamp}.pkl"

        filepath = os.path.join(self.model_dir, filename)

        # Salvar modelo e metadados
        model_data = {
            'model': self.pipeline,
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'feature_columns': self.feature_columns,
            'training_date': datetime.now().isoformat()
        }

        joblib.dump(model_data, filepath)
        logger.info(f"Modelo salvo em: {filepath}")

        return filepath

    def load_model(self, filepath: str) -> bool:
        """
        Carrega modelo treinado de arquivo.

        Args:
            filepath: Caminho do arquivo

        Returns:
            True se carregou com sucesso
        """
        try:
            model_data = joblib.load(filepath)

            self.pipeline = model_data['model']
            self.model_type = model_data['model_type']
            self.is_trained = model_data['is_trained']
            self.feature_columns = model_data['feature_columns']

            logger.info(f"Modelo carregado de: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo atual."""
        return {
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'feature_columns': self.feature_columns,
            'pipeline_steps': list(self.pipeline.named_steps.keys()) if self.pipeline else []
        }

def create_sample_training_data() -> pd.DataFrame:
    """
    Cria dados de treinamento sintéticos para demonstração.

    Returns:
        DataFrame com dados de treinamento
    """
    np.random.seed(42)
    n_samples = 1000

    data = {
        'idade_empresa': np.random.exponential(5, n_samples) + 1,  # 1-20 anos
        'divida_total': np.random.exponential(50000, n_samples),     # 0-500k
        'faturamento_anual': np.random.exponential(300000, n_samples) + 50000,  # 50k-1M
        'saldo_medio_diario': np.random.exponential(15000, n_samples),  # 0-100k
        'estresse_caixa_dias': np.random.poisson(3, n_samples),     # 0-15 dias
        'valor_maior_cliente': np.random.exponential(80000, n_samples),  # 0-400k
        'faturamento_total_periodo': np.random.exponential(250000, n_samples) + 100000  # 100k-1M
    }

    df = pd.DataFrame(data)

    # Calcular scores baseados nas características (lógica simplificada)
    # Empresas mais antigas, com menos dívidas e mais faturamento têm scores mais altos
    scores = (
        (df['idade_empresa'] / 20) * 200 +  # Idade contribui até 200 pontos
        (1 - (df['divida_total'] / df['faturamento_anual']).clip(0, 2)) * 200 +  # Endividamento
        (df['faturamento_anual'] / 1000000).clip(0, 1) * 300 +  # Faturamento
        (df['saldo_medio_diario'] / 100000).clip(0, 1) * 150 +  # Liquidez
        (1 - (df['estresse_caixa_dias'] / 15).clip(0, 1)) * 100 +  # Estresse caixa
        (1 - (df['valor_maior_cliente'] / df['faturamento_total_periodo']).clip(0, 1)) * 50  # Concentração
    )

    # Adicionar ruído e garantir range 0-1000
    scores = scores + np.random.normal(0, 50, n_samples)
    scores = np.clip(scores, 0, 1000)

    df['score'] = scores

    return df

def train_and_evaluate_models(data_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Treina e avalia múltiplos modelos de ML.

    Args:
        data_path: Caminho para arquivo CSV com dados (opcional)

    Returns:
        Dicionário com resultados de todos os modelos
    """
    logger.info("Iniciando treinamento e avaliação de modelos")

    # Carregar ou criar dados
    if data_path and os.path.exists(data_path):
        df = pd.read_csv(data_path)
        logger.info(f"Dados carregados de: {data_path}")
    else:
        df = create_sample_training_data()
        logger.info("Dados sintéticos criados para demonstração")

    results = {}

    # Testar diferentes tipos de modelo
    model_types = ['linear', 'ridge', 'lasso', 'random_forest', 'gradient_boosting']

    for model_type in model_types:
        logger.info(f"Treinando modelo: {model_type}")

        try:
            predictor = RiskScorePredictor(model_type=model_type)
            metrics = predictor.train(df)

            results[model_type] = metrics

            # Salvar modelo treinado
            model_path = predictor.save_model()
            results[model_type]['model_path'] = model_path

        except Exception as e:
            logger.error(f"Erro no treinamento do modelo {model_type}: {e}")
            results[model_type] = {'error': str(e)}

    # Identificar melhor modelo
    best_model = None
    best_score = -np.inf

    for model_type, metrics in results.items():
        if 'metrics' in metrics and 'r2_score' in metrics['metrics']:
            score = metrics['metrics']['r2_score']
            if score > best_score:
                best_score = score
                best_model = model_type

    logger.info(f"Melhor modelo: {best_model} (R²: {best_score:.3f})")

    return {
        'results': results,
        'best_model': best_model,
        'best_score': best_score,
        'total_models_tested': len(model_types)
    }
