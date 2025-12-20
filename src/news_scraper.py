"""
News Scraper Module
Monitorea fuentes de noticias usando pygooglenews y RSS feeds
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import feedparser
from pygooglenews import GoogleNews
from newspaper import Article, ArticleException
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsSource:
    """Clase base para fuentes de noticias"""
    
    def __init__(self, name: str):
        self.name = name
        
    def fetch_articles(self, query: Optional[str] = None, days: int = 7) -> List[Dict]:
        """
        Obtiene artículos de la fuente
        
        Args:
            query: Término de búsqueda opcional
            days: Días hacia atrás para buscar
            
        Returns:
            Lista de diccionarios con información de artículos
        """
        raise NotImplementedError


class GoogleNewsSource(NewsSource):
    """Fuente de Google News usando pygooglenews"""
    
    def __init__(self):
        super().__init__("Google News")
        self.gn = GoogleNews(lang='en', country='US')
        
    def fetch_articles(self, query: Optional[str] = None, days: int = 7) -> List[Dict]:
        """Obtiene artículos de Google News"""
        articles = []
        
        try:
            if query:
                logger.info(f"Buscando en Google News: {query}")
                search_result = self.gn.search(query)
            else:
                # Búsqueda por defecto para noticias de negocios/startups
                search_result = self.gn.topic_headlines('BUSINESS')
            
            if search_result and 'entries' in search_result:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                for entry in search_result['entries']:
                    try:
                        # Parsear fecha de publicación
                        pub_date = datetime(*entry.published_parsed[:6])
                        
                        if pub_date < cutoff_date:
                            continue
                        
                        article_data = {
                            'title': entry.title,
                            'url': entry.link,
                            'published': pub_date.isoformat(),
                            'source': entry.source.get('title', 'Unknown') if hasattr(entry, 'source') else 'Google News',
                            'summary': entry.get('summary', ''),
                            'fetched_at': datetime.now().isoformat()
                        }
                        
                        articles.append(article_data)
                        
                    except Exception as e:
                        logger.warning(f"Error procesando entrada de Google News: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error obteniendo artículos de Google News: {e}")
            
        logger.info(f"Google News: {len(articles)} artículos obtenidos")
        return articles


class RSSFeedSource(NewsSource):
    """Fuente RSS genérica"""
    
    def __init__(self, name: str, feed_url: str):
        super().__init__(name)
        self.feed_url = feed_url
        
    def fetch_articles(self, query: Optional[str] = None, days: int = 7) -> List[Dict]:
        """Obtiene artículos del feed RSS"""
        articles = []
        
        try:
            logger.info(f"Obteniendo feed RSS de {self.name}")
            feed = feedparser.parse(self.feed_url)
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for entry in feed.entries:
                try:
                    # Parsear fecha de publicación
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    else:
                        pub_date = datetime.now()
                    
                    if pub_date < cutoff_date:
                        continue
                    
                    # Filtrar por query si se especifica
                    if query:
                        query_lower = query.lower()
                        title_lower = entry.title.lower()
                        summary_lower = entry.get('summary', '').lower()
                        
                        if query_lower not in title_lower and query_lower not in summary_lower:
                            continue
                    
                    article_data = {
                        'title': entry.title,
                        'url': entry.link,
                        'published': pub_date.isoformat(),
                        'source': self.name,
                        'summary': entry.get('summary', entry.get('description', '')),
                        'fetched_at': datetime.now().isoformat()
                    }
                    
                    articles.append(article_data)
                    
                except Exception as e:
                    logger.warning(f"Error procesando entrada RSS de {self.name}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error obteniendo feed RSS de {self.name}: {e}")
            
        logger.info(f"{self.name}: {len(articles)} artículos obtenidos")
        return articles


class ArticleExtractor:
    """Extrae contenido completo de artículos usando Newspaper4k"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        
    def extract_content(self, url: str) -> Dict:
        """
        Extrae contenido completo de un artículo
        
        Args:
            url: URL del artículo
            
        Returns:
            Diccionario con contenido extraído
        """
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            # Intentar extraer NLP features
            try:
                article.nlp()
                keywords = article.keywords
                summary = article.summary
            except:
                keywords = []
                summary = ""
            
            return {
                'text': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                'top_image': article.top_image,
                'keywords': keywords,
                'summary': summary,
                'extraction_success': True
            }
            
        except ArticleException as e:
            logger.warning(f"Error extrayendo artículo de {url}: {e}")
            return {'extraction_success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error inesperado extrayendo artículo de {url}: {e}")
            return {'extraction_success': False, 'error': str(e)}


class NewsMonitor:
    """Monitor principal que coordina todas las fuentes de noticias"""
    
    def __init__(self):
        self.sources = []
        self.extractor = ArticleExtractor()
        
        # Inicializar fuentes por defecto
        self._initialize_default_sources()
        
    def _initialize_default_sources(self):
        """Inicializa las fuentes de noticias por defecto"""
        # Google News
        self.sources.append(GoogleNewsSource())
        
        # TechCrunch RSS
        self.sources.append(RSSFeedSource(
            "TechCrunch",
            "https://techcrunch.com/feed/"
        ))
        
        # VentureBeat RSS
        self.sources.append(RSSFeedSource(
            "VentureBeat",
            "https://venturebeat.com/feed/"
        ))
        
        # Crunchbase News RSS
        self.sources.append(RSSFeedSource(
            "Crunchbase News",
            "https://news.crunchbase.com/feed/"
        ))
        
    def add_source(self, source: NewsSource):
        """Añade una fuente de noticias personalizada"""
        self.sources.append(source)
        
    def fetch_all_news(self, queries: List[str] = None, days: int = 7, extract_content: bool = False) -> List[Dict]:
        """
        Obtiene noticias de todas las fuentes
        
        Args:
            queries: Lista de términos de búsqueda
            days: Días hacia atrás para buscar
            extract_content: Si True, extrae el contenido completo de los artículos
            
        Returns:
            Lista consolidada de artículos
        """
        all_articles = []
        seen_urls = set()
        
        if not queries:
            queries = [
                "startup funding",
                "Series A",
                "venture capital",
                "layoffs tech",
                "company expansion"
            ]
        
        for source in self.sources:
            for query in queries:
                articles = source.fetch_articles(query=query, days=days)
                
                # Deduplicar por URL
                for article in articles:
                    if article['url'] not in seen_urls:
                        seen_urls.add(article['url'])
                        
                        # Extraer contenido completo si se solicita
                        if extract_content:
                            logger.info(f"Extrayendo contenido de: {article['title']}")
                            content = self.extractor.extract_content(article['url'])
                            article['full_content'] = content
                            time.sleep(1)  # Rate limiting
                        
                        all_articles.append(article)
                
                # Rate limiting entre consultas
                time.sleep(2)
        
        logger.info(f"Total de artículos únicos obtenidos: {len(all_articles)}")
        return all_articles
    
    def fetch_realtime_updates(self, topics: List[str] = None) -> List[Dict]:
        """
        Obtiene actualizaciones en tiempo real
        
        Args:
            topics: Tópicos específicos para monitorear
            
        Returns:
            Lista de artículos recientes
        """
        if not topics:
            topics = ["startups", "funding", "acquisitions"]
        
        return self.fetch_all_news(queries=topics, days=1, extract_content=True)


if __name__ == "__main__":
    # Test del monitor
    monitor = NewsMonitor()
    
    # Obtener noticias de las últimas 24 horas
    articles = monitor.fetch_all_news(
        queries=["startup funding", "Series A", "layoffs"],
        days=1,
        extract_content=False
    )
    
    print(f"\n=== Artículos encontrados: {len(articles)} ===")
    for i, article in enumerate(articles[:5], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Fuente: {article['source']}")
        print(f"   URL: {article['url']}")
        print(f"   Publicado: {article['published']}")
