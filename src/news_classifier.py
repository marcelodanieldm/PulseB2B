"""
News Classifier Module
Clasifica noticias por palabras clave y realiza análisis de sentimiento
usando un modelo BERT liviano
"""

import logging
import re
from typing import List, Dict, Tuple
from datetime import datetime
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KeywordClassifier:
    """Clasifica noticias basándose en palabras clave específicas"""
    
    def __init__(self):
        # Definir categorías y sus palabras clave
        self.categories = {
            'Funding': {
                'keywords': [
                    'funding', 'series a', 'series b', 'series c', 'series d',
                    'seed round', 'venture capital', 'investment', 'raised',
                    'investors', 'valuation', 'financing', 'capital raise',
                    'round', 'vc', 'pre-seed', 'angel investor', 'fundraising'
                ],
                'weight': 1.0
            },
            'Series A': {
                'keywords': [
                    'series a', 'series-a', 'series a round', 'series a funding',
                    'a round', 'first institutional round'
                ],
                'weight': 1.5
            },
            'Layoffs': {
                'keywords': [
                    'layoffs', 'layoff', 'job cuts', 'workforce reduction',
                    'downsizing', 'restructuring', 'employees laid off',
                    'staff reduction', 'termination', 'firing', 'redundancies',
                    'headcount reduction', 'cutting jobs'
                ],
                'weight': 1.2
            },
            'Expansion': {
                'keywords': [
                    'expansion', 'expanding', 'growth', 'hiring', 'new office',
                    'new market', 'scaling', 'international expansion',
                    'opening', 'launching', 'entering market', 'geographic expansion',
                    'market entry', 'new location', 'team growth'
                ],
                'weight': 1.0
            },
            'Acquisition': {
                'keywords': [
                    'acquisition', 'acquired', 'acquires', 'merger', 'takeover',
                    'bought', 'purchasing', 'deal', 'm&a', 'mergers and acquisitions'
                ],
                'weight': 1.3
            },
            'IPO': {
                'keywords': [
                    'ipo', 'initial public offering', 'going public', 'public listing',
                    'stock market debut', 'public offering'
                ],
                'weight': 1.4
            },
            'Bankruptcy': {
                'keywords': [
                    'bankruptcy', 'bankrupt', 'insolvent', 'chapter 11',
                    'administration', 'liquidation', 'ceased operations',
                    'shutting down', 'closing down'
                ],
                'weight': 1.5
            }
        }
        
    def classify(self, text: str, title: str = "") -> Dict[str, float]:
        """
        Clasifica un texto según categorías de palabras clave
        
        Args:
            text: Texto del artículo
            title: Título del artículo (peso adicional)
            
        Returns:
            Diccionario con categorías y scores
        """
        # Combinar título y texto con peso adicional para el título
        combined_text = f"{title} {title} {title} {text}".lower()
        
        scores = {}
        
        for category, data in self.categories.items():
            score = 0.0
            matches = []
            
            for keyword in data['keywords']:
                # Buscar coincidencias de palabras completas
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                occurrences = len(re.findall(pattern, combined_text))
                
                if occurrences > 0:
                    matches.append((keyword, occurrences))
                    # Score acumulativo con rendimientos decrecientes
                    score += data['weight'] * (1 + np.log1p(occurrences))
            
            scores[category] = {
                'score': round(score, 2),
                'matches': matches,
                'detected': score > 0
            }
        
        return scores
    
    def get_primary_category(self, scores: Dict) -> Tuple[str, float]:
        """
        Obtiene la categoría principal basándose en los scores
        
        Returns:
            Tupla (categoría, score)
        """
        if not scores:
            return ("Uncategorized", 0.0)
        
        primary = max(scores.items(), key=lambda x: x[1]['score'])
        
        if primary[1]['score'] == 0:
            return ("Uncategorized", 0.0)
        
        return (primary[0], primary[1]['score'])


class SentimentAnalyzer:
    """Analiza sentimiento usando un modelo BERT liviano optimizado"""
    
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        """
        Inicializa el analizador de sentimiento
        
        Args:
            model_name: Nombre del modelo BERT a usar (por defecto DistilBERT)
        """
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        logger.info(f"Cargando modelo de sentimiento: {model_name}")
        logger.info(f"Usando dispositivo: {self.device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("Modelo de sentimiento cargado exitosamente")
        except Exception as e:
            logger.error(f"Error cargando modelo de sentimiento: {e}")
            raise
    
    def analyze(self, text: str, max_length: int = 512) -> Dict:
        """
        Analiza el sentimiento de un texto
        
        Args:
            text: Texto a analizar
            max_length: Longitud máxima de tokens
            
        Returns:
            Diccionario con análisis de sentimiento
        """
        if not text or len(text.strip()) == 0:
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'scores': {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
            }
        
        try:
            # Truncar texto si es muy largo
            if len(text) > 5000:
                text = text[:5000]
            
            # Tokenizar
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
                padding=True
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Inferencia
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Obtener scores
            scores = predictions[0].cpu().numpy()
            
            # Mapear a sentimientos
            # DistilBERT-SST-2: 0=negativo, 1=positivo
            negative_score = float(scores[0])
            positive_score = float(scores[1])
            
            # Determinar sentimiento
            if positive_score > 0.6:
                sentiment = 'positive'
                confidence = positive_score
            elif negative_score > 0.6:
                sentiment = 'negative'
                confidence = negative_score
            else:
                sentiment = 'neutral'
                confidence = 1.0 - abs(positive_score - negative_score)
            
            return {
                'sentiment': sentiment,
                'confidence': round(confidence, 4),
                'scores': {
                    'positive': round(positive_score, 4),
                    'negative': round(negative_score, 4),
                    'neutral': round(1.0 - (positive_score + negative_score) / 2, 4)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analizando sentimiento: {e}")
            return {
                'sentiment': 'error',
                'confidence': 0.0,
                'scores': {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0},
                'error': str(e)
            }
    
    def analyze_stability(self, text: str, company_context: str = "") -> Dict:
        """
        Analiza la estabilidad financiera de una empresa basándose en el texto
        
        Args:
            text: Texto del artículo
            company_context: Contexto adicional sobre la empresa
            
        Returns:
            Diccionario con análisis de estabilidad
        """
        # Palabras clave de estabilidad
        stability_positive = [
            'profitable', 'growth', 'strong revenue', 'expansion', 'hiring',
            'successful', 'milestone', 'achievement', 'record', 'increased',
            'partnership', 'contract', 'deal', 'customer growth'
        ]
        
        stability_negative = [
            'layoffs', 'debt', 'losses', 'declining', 'struggle', 'challenge',
            'concern', 'worry', 'risk', 'downturn', 'restructuring', 'pivot',
            'cash burn', 'runway', 'unprofitable'
        ]
        
        # Análisis de sentimiento general
        sentiment_result = self.analyze(text)
        
        # Contar indicadores de estabilidad
        text_lower = text.lower()
        positive_indicators = sum(1 for word in stability_positive if word in text_lower)
        negative_indicators = sum(1 for word in stability_negative if word in text_lower)
        
        # Calcular score de estabilidad (0-100)
        stability_score = 50  # Neutral base
        
        # Ajustar por sentimiento
        if sentiment_result['sentiment'] == 'positive':
            stability_score += 20 * sentiment_result['confidence']
        elif sentiment_result['sentiment'] == 'negative':
            stability_score -= 20 * sentiment_result['confidence']
        
        # Ajustar por indicadores
        stability_score += (positive_indicators * 5)
        stability_score -= (negative_indicators * 7)
        
        # Normalizar entre 0-100
        stability_score = max(0, min(100, stability_score))
        
        # Clasificar estabilidad
        if stability_score >= 70:
            stability_label = 'stable'
        elif stability_score >= 40:
            stability_label = 'moderate'
        else:
            stability_label = 'unstable'
        
        return {
            'stability_score': round(stability_score, 2),
            'stability_label': stability_label,
            'sentiment': sentiment_result,
            'positive_indicators': positive_indicators,
            'negative_indicators': negative_indicators
        }


class NewsClassifier:
    """Clasificador completo de noticias que integra keywords y sentimiento"""
    
    def __init__(self, load_sentiment_model: bool = True):
        """
        Inicializa el clasificador
        
        Args:
            load_sentiment_model: Si True, carga el modelo BERT para análisis de sentimiento
        """
        self.keyword_classifier = KeywordClassifier()
        self.sentiment_analyzer = None
        
        if load_sentiment_model:
            try:
                self.sentiment_analyzer = SentimentAnalyzer()
            except Exception as e:
                logger.warning(f"No se pudo cargar el modelo de sentimiento: {e}")
                logger.warning("Continuando sin análisis de sentimiento")
    
    def classify_article(self, article: Dict, extract_companies: bool = True) -> Dict:
        """
        Clasifica un artículo completo
        
        Args:
            article: Diccionario con información del artículo
            extract_companies: Si True, intenta extraer nombres de empresas
            
        Returns:
            Diccionario con clasificación completa
        """
        # Obtener texto
        text = ""
        if 'full_content' in article and article['full_content'].get('extraction_success'):
            text = article['full_content'].get('text', '')
        
        if not text:
            text = article.get('summary', '')
        
        title = article.get('title', '')
        
        # Clasificación por keywords
        keyword_scores = self.keyword_classifier.classify(text, title)
        primary_category, primary_score = self.keyword_classifier.get_primary_category(keyword_scores)
        
        # Análisis de sentimiento
        sentiment = None
        stability = None
        
        if self.sentiment_analyzer and text:
            sentiment = self.sentiment_analyzer.analyze(text)
            stability = self.sentiment_analyzer.analyze_stability(text)
        
        # Extraer empresas mencionadas (simple)
        companies = []
        if extract_companies:
            companies = self._extract_companies(title, text)
        
        result = {
            'article_id': article.get('url', ''),
            'title': title,
            'url': article.get('url', ''),
            'published': article.get('published', ''),
            'source': article.get('source', ''),
            'primary_category': primary_category,
            'primary_score': primary_score,
            'all_categories': keyword_scores,
            'sentiment': sentiment,
            'stability_analysis': stability,
            'companies_mentioned': companies,
            'classified_at': datetime.now().isoformat()
        }
        
        return result
    
    def _extract_companies(self, title: str, text: str, max_companies: int = 5) -> List[str]:
        """
        Extrae nombres de empresas del texto (método simple basado en capitalización)
        
        Args:
            title: Título del artículo
            text: Texto del artículo
            max_companies: Número máximo de empresas a extraer
            
        Returns:
            Lista de nombres de empresas
        """
        # Esta es una implementación simple. Para mejor precisión, usar NER (Named Entity Recognition)
        companies = set()
        
        # Buscar en título y primeras líneas del texto
        search_text = f"{title}. {text[:1000]}"
        
        # Patrón para palabras capitalizadas (posibles empresas)
        # Excluir palabras comunes
        common_words = {'The', 'A', 'An', 'In', 'On', 'At', 'To', 'For', 'Of', 'With', 'By', 'From'}
        
        # Buscar secuencias de palabras capitalizadas
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.findall(pattern, search_text)
        
        for match in matches:
            if match not in common_words and len(match) > 2:
                companies.add(match)
                
                if len(companies) >= max_companies:
                    break
        
        return list(companies)[:max_companies]
    
    def classify_batch(self, articles: List[Dict]) -> List[Dict]:
        """
        Clasifica un lote de artículos
        
        Args:
            articles: Lista de artículos
            
        Returns:
            Lista de artículos clasificados
        """
        classified = []
        
        for i, article in enumerate(articles, 1):
            logger.info(f"Clasificando artículo {i}/{len(articles)}: {article.get('title', 'Sin título')}")
            
            try:
                result = self.classify_article(article)
                classified.append(result)
            except Exception as e:
                logger.error(f"Error clasificando artículo: {e}")
                continue
        
        logger.info(f"Clasificación completada: {len(classified)} artículos")
        return classified


if __name__ == "__main__":
    # Test del clasificador
    classifier = NewsClassifier(load_sentiment_model=False)
    
    # Artículo de prueba
    test_article = {
        'title': 'TechStartup raises $50M Series A led by Sequoia Capital',
        'summary': 'TechStartup, a AI company, announced today that it has raised $50 million in Series A funding led by Sequoia Capital. The company plans to use the funds for expansion and hiring.',
        'url': 'https://example.com/article',
        'source': 'TechCrunch',
        'published': '2025-12-20T10:00:00'
    }
    
    result = classifier.classify_article(test_article)
    
    print("\n=== Resultado de Clasificación ===")
    print(f"Título: {result['title']}")
    print(f"Categoría Principal: {result['primary_category']} (Score: {result['primary_score']})")
    print(f"Empresas Mencionadas: {result['companies_mentioned']}")
    print(f"\nTodas las Categorías:")
    for cat, data in result['all_categories'].items():
        if data['detected']:
            print(f"  - {cat}: {data['score']} (matches: {len(data['matches'])})")
