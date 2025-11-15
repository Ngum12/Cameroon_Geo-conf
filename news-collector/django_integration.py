"""
PROJECT SENTINEL - DJANGO INTEGRATION MODULE
Cameroon Defense Force OSINT Intelligence System

Integration layer for connecting news scraping to Django backend processing.
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import time
from dataclasses import asdict

from news_scraper import ScrapedArticle, NewsScrapingEngine
from sources_config import get_active_sources, get_high_priority_sources

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectSentinelAPIClient:
    """
    Comprehensive client for interfacing with all Project Sentinel services.
    """
    
    def __init__(self, django_base_url: str = "http://127.0.0.1:8000"):
        self.base_url = django_base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Project-Sentinel-Intelligence-Pipeline/2.0'
        })
        
        # Service endpoints
        self.endpoints = {
            # Django Backend
            'health': f"{self.base_url}/health/",
            'process_article': f"{self.base_url}/api/v1/process-article-real/",
            'get_events': f"{self.base_url}/api/v1/events/",
            'statistics': f"{self.base_url}/api/v1/statistics/",
            
            # NLP Services
            'translation': "http://127.0.0.1:8001/translate",
            'ner_analysis': "http://127.0.0.1:8002/analyze-entities",
            'actor_networks': "http://127.0.0.1:8002/analyze-actor-networks",
            
            # ML Services
            'ml_prediction': "http://127.0.0.1:8001/predict",
            'rl_intervention': "http://127.0.0.1:8003/recommend-intervention",
            
            # Health checks
            'translation_health': "http://127.0.0.1:8001/health",
            'ner_health': "http://127.0.0.1:8002/health",
            'ml_health': "http://127.0.0.1:8001/health",
            'rl_health': "http://127.0.0.1:8003/health"
        }
        
        # Service status tracking
        self.service_status = {
            'django': False,
            'translation': False,
            'ner': False,
            'ml_prediction': False,
            'rl_system': False
        }
    
    def check_all_services_health(self) -> Dict[str, bool]:
        """Comprehensive health check for all Project Sentinel services."""
        logger.info("🏥 CHECKING ALL SERVICES HEALTH...")
        
        # Django Backend
        try:
            response = self.session.get(self.endpoints['health'], timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.service_status['django'] = True
                logger.info(f"✅ Django Backend: {data.get('status', 'healthy')} ({data.get('articles_count', 0)} articles)")
            else:
                self.service_status['django'] = False
                logger.warning(f"⚠️ Django Backend: HTTP {response.status_code}")
        except Exception as e:
            self.service_status['django'] = False
            logger.error(f"❌ Django Backend: {e}")

        # Translation Service
        try:
            response = self.session.get(self.endpoints['translation_health'], timeout=5)
            self.service_status['translation'] = response.status_code == 200
            logger.info(f"✅ Translation Service: {'Operational' if self.service_status['translation'] else 'Down'}")
        except Exception:
            self.service_status['translation'] = False
            logger.warning("⚠️ Translation Service: Not available")

        # NER Service  
        try:
            response = self.session.get(self.endpoints['ner_health'], timeout=5)
            self.service_status['ner'] = response.status_code == 200
            logger.info(f"✅ NER Service: {'Operational' if self.service_status['ner'] else 'Down'}")
        except Exception:
            self.service_status['ner'] = False
            logger.warning("⚠️ NER Service: Not available")

        # ML Prediction Service
        try:
            response = self.session.get(self.endpoints['ml_health'], timeout=5)
            self.service_status['ml_prediction'] = response.status_code == 200
            logger.info(f"✅ ML Prediction: {'Operational' if self.service_status['ml_prediction'] else 'Down'}")
        except Exception:
            self.service_status['ml_prediction'] = False
            logger.warning("⚠️ ML Prediction Service: Not available")

        # RL System
        try:
            response = self.session.get(self.endpoints['rl_health'], timeout=5)
            self.service_status['rl_system'] = response.status_code == 200
            logger.info(f"✅ RL System: {'Operational' if self.service_status['rl_system'] else 'Down'}")
        except Exception:
            self.service_status['rl_system'] = False
            logger.warning("⚠️ RL System: Not available")

        operational_services = sum(self.service_status.values())
        total_services = len(self.service_status)
        
        logger.info(f"🏥 HEALTH CHECK SUMMARY: {operational_services}/{total_services} services operational")
        
        return self.service_status.copy()
    
    def check_backend_health(self) -> bool:
        """Quick Django backend health check."""
        return self.service_status.get('django', False)
    
    def process_article_enhanced(self, article: ScrapedArticle) -> Optional[Dict[str, Any]]:
        """
        Process article through complete intelligence pipeline: Translation → NER → ML Assessment → Storage
        """
        logger.info(f"🔄 ENHANCED PROCESSING: {article.title[:40]}...")
        processing_result = {
            'original_article': article,
            'translation': None,
            'entities': None,
            'actor_networks': None,
            'threat_assessment': None,
            'django_result': None,
            'processing_stages': []
        }
        
        try:
            text_for_analysis = article.content
            
            # STAGE 1: Translation (if French)
            if article.language == 'fr' and self.service_status.get('translation', False):
                logger.info("🌐 Stage 1: Translating French article...")
                try:
                    translation_data = {
                        'text': article.content[:2000],  # Limit for API
                        'source_lang': 'fr',
                        'target_lang': 'en'
                    }
                    
                    response = self.session.post(
                        self.endpoints['translation'],
                        data=json.dumps(translation_data),
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        translation_result = response.json()
                        processing_result['translation'] = translation_result
                        text_for_analysis = translation_result.get('translated_text', article.content)
                        processing_result['processing_stages'].append('translation_success')
                        logger.info(f"✅ Translation completed: {translation_result.get('confidence', 0):.2f} confidence")
                    else:
                        processing_result['processing_stages'].append('translation_failed')
                        logger.warning("⚠️ Translation failed, using original text")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Translation error: {e}")
                    processing_result['processing_stages'].append('translation_error')
            else:
                processing_result['processing_stages'].append('no_translation_needed')
            
            # STAGE 2: Named Entity Recognition & Actor Networks  
            if self.service_status.get('ner', False):
                logger.info("🏷️ Stage 2: NER Analysis & Actor Networks...")
                try:
                    # Basic NER
                    ner_data = {'text': text_for_analysis[:1500]}
                    ner_response = self.session.post(
                        self.endpoints['ner_analysis'],
                        data=json.dumps(ner_data),
                        timeout=10
                    )
                    
                    if ner_response.status_code == 200:
                        ner_result = ner_response.json()
                        processing_result['entities'] = ner_result
                        processing_result['processing_stages'].append('ner_success')
                        logger.info(f"✅ NER completed: {ner_result.get('entity_count', 0)} entities found")
                        
                        # Actor Network Analysis (if entities found)
                        if ner_result.get('entity_count', 0) > 2:
                            try:
                                network_data = {'texts': [text_for_analysis[:1000]]}
                                network_response = self.session.post(
                                    self.endpoints['actor_networks'],
                                    data=json.dumps(network_data),
                                    timeout=15
                                )
                                
                                if network_response.status_code == 200:
                                    network_result = network_response.json()
                                    processing_result['actor_networks'] = network_result
                                    processing_result['processing_stages'].append('network_analysis_success')
                                    logger.info(f"✅ Network analysis: {len(network_result.get('actors', []))} actors, {len(network_result.get('relationships', []))} relationships")
                                
                            except Exception as e:
                                logger.warning(f"⚠️ Network analysis error: {e}")
                                processing_result['processing_stages'].append('network_analysis_error')
                    else:
                        processing_result['processing_stages'].append('ner_failed')
                        
                except Exception as e:
                    logger.warning(f"⚠️ NER error: {e}")
                    processing_result['processing_stages'].append('ner_error')
            else:
                processing_result['processing_stages'].append('ner_unavailable')
            
            # STAGE 3: ML Threat Assessment
            if self.service_status.get('ml_prediction', False):
                logger.info("🧠 Stage 3: ML Threat Assessment...")
                try:
                    # Determine primary region from article
                    primary_region = "Centre"  # Default
                    for region in article.region_mentions:
                        if any(keyword in region.lower() for keyword in ['north', 'nord', 'southwest', 'northwest']):
                            primary_region = region
                            break
                    
                    ml_data = {
                        'region': primary_region,
                        'article_count': 1,
                        'priority_distribution': {'high': 0.7, 'medium': 0.3, 'low': 0.0},
                        'text_sample': text_for_analysis[:500],
                        'time_horizon': 7
                    }
                    
                    ml_response = self.session.post(
                        self.endpoints['ml_prediction'],
                        data=json.dumps(ml_data),
                        timeout=10
                    )
                    
                    if ml_response.status_code == 200:
                        ml_result = ml_response.json()
                        processing_result['threat_assessment'] = ml_result
                        processing_result['processing_stages'].append('ml_assessment_success')
                        logger.info(f"✅ ML Assessment: {ml_result.get('risk_score', 0):.3f} threat score for {primary_region}")
                    else:
                        processing_result['processing_stages'].append('ml_assessment_failed')
                        
                except Exception as e:
                    logger.warning(f"⚠️ ML Assessment error: {e}")
                    processing_result['processing_stages'].append('ml_assessment_error')
            else:
                processing_result['processing_stages'].append('ml_assessment_unavailable')
            
            # STAGE 4: Store in Django with enhanced data
            logger.info("💾 Stage 4: Storing enhanced article data...")
            enhanced_article_data = {
                'url': article.url,
                'title': article.title,
                'raw_text': article.content,
                'source': article.source,
                'language': article.language,
                'relevance_score': article.relevance_score,
                'geopolitical_keywords': article.geopolitical_keywords,
                'region_mentions': article.region_mentions,
                
                # Enhanced data from pipeline (with safety checks)
                'translated_text': processing_result.get('translation', {}).get('translated_text') if processing_result.get('translation') else text_for_analysis,
                'entities_detected': processing_result.get('entities', {}).get('entity_count', 0) if processing_result.get('entities') else 0,
                'threat_score': processing_result.get('threat_assessment', {}).get('risk_score', 0.0) if processing_result.get('threat_assessment') else 0.0,
                'processing_stages': processing_result['processing_stages'],
                'actor_count': len(processing_result.get('actor_networks', {}).get('actors', [])) if processing_result.get('actor_networks') else 0,
                'network_relationships': len(processing_result.get('actor_networks', {}).get('relationships', [])) if processing_result.get('actor_networks') else 0
            }
            
            # Add publication date if available
            if article.publish_date:
                enhanced_article_data['publish_date'] = article.publish_date.isoformat()
            
            # Send to Django
            django_response = self.session.post(
                self.endpoints['process_article'], 
                data=json.dumps(enhanced_article_data),
                timeout=300  # 5 minutes for complex intelligence processing
            )
            
            if django_response.status_code == 201:
                django_result = django_response.json()
                processing_result['django_result'] = django_result
                processing_result['processing_stages'].append('django_storage_success')
                
                # Calculate overall success metrics
                stages_completed = len([s for s in processing_result['processing_stages'] if 'success' in s])
                total_attempted = len([s for s in processing_result['processing_stages'] if not s.endswith('unavailable')])
                success_rate = (stages_completed / max(total_attempted, 1)) * 100
                
                logger.info(f"✅ ENHANCED PROCESSING COMPLETE:")
                logger.info(f"   📊 Article ID: {django_result.get('article', {}).get('id', 'N/A')}")
                logger.info(f"   🎯 Pipeline Success: {success_rate:.1f}% ({stages_completed}/{total_attempted} stages)")
                logger.info(f"   🏷️ Entities: {enhanced_article_data['entities_detected']}")
                logger.info(f"   🧠 Threat Score: {enhanced_article_data['threat_score']:.3f}")
                logger.info(f"   🕸️ Actor Networks: {enhanced_article_data['actor_count']} actors")
                
                return processing_result
            else:
                logger.error(f"❌ Django storage failed ({django_response.status_code}): {django_response.text}")
                processing_result['processing_stages'].append('django_storage_failed')
                return None
                
        except Exception as e:
            logger.error(f"❌ Enhanced processing failed for '{article.title[:30]}...': {e}")
            processing_result['processing_stages'].append('fatal_error')
            return None
    
    def process_article(self, article: ScrapedArticle) -> Optional[Dict[str, Any]]:
        """
        Legacy method - routes to enhanced processing if services available.
        """
        # Use enhanced processing if NLP services are available
        if self.service_status.get('ner', False) or self.service_status.get('translation', False):
            return self.process_article_enhanced(article)
        
        # Fallback to basic processing
        return self.process_article_basic(article)
    
    def process_article_basic(self, article: ScrapedArticle) -> Optional[Dict[str, Any]]:
        """Basic article processing without NLP pipeline."""
        try:
            article_data = {
                'url': article.url,
                'title': article.title,
                'raw_text': article.content,
                'source': article.source,
                'language': article.language,
                'relevance_score': article.relevance_score,
                'geopolitical_keywords': article.geopolitical_keywords,
                'region_mentions': article.region_mentions
            }
            
            if article.publish_date:
                article_data['publish_date'] = article.publish_date.isoformat()
            
            response = self.session.post(
                self.endpoints['process_article'], 
                data=json.dumps(article_data),
                timeout=300  # 5 minutes for processing
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"✅ Basic processing: {article.title[:50]}... (ID: {result.get('article_id', 'N/A')})")
                return result
            else:
                logger.error(f"❌ Basic processing failed ({response.status_code}): {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Basic processing error '{article.title[:30]}...': {e}")
            return None
    
    def get_processed_articles_count(self) -> int:
        """Get count of articles in Django database."""
        try:
            response = self.session.get(self.endpoints['get_events'], timeout=10)
            if response.status_code == 200:
                articles = response.json()
                return len(articles) if isinstance(articles, list) else 0
            return 0
        except Exception:
            return 0

class AdvancedIntelligenceProcessor:
    """
    Advanced intelligence processing system with complete NLP pipeline.
    """
    
    def __init__(self, django_url: str = "http://127.0.0.1:8000"):
        self.scraper = NewsScrapingEngine()
        self.api_client = ProjectSentinelAPIClient(django_url)
        self.processing_stats = {
            'articles_scraped': 0,
            'articles_processed': 0,
            'articles_rejected': 0,
            'sources_processed': 0,
            'processing_time': 0.0,
            'start_time': None,
            'end_time': None
        }
    
    def run_advanced_intelligence_cycle(self, max_sources: int = 5) -> Dict[str, Any]:
        """
        Run advanced intelligence collection cycle with full NLP pipeline.
        """
        logger.info("🚀 STARTING ADVANCED INTELLIGENCE COLLECTION CYCLE")
        logger.info("=" * 70)
        
        start_time = time.time()
        self.processing_stats['start_time'] = datetime.now()
        
        # 1. Comprehensive health check of all services
        logger.info("🏥 Checking all Project Sentinel services...")
        service_status = self.api_client.check_all_services_health()
        
        if not service_status.get('django', False):
            logger.error("❌ Django backend not available. Aborting cycle.")
            return self.processing_stats
        
        # Log service availability for intelligence processing
        available_services = [service for service, status in service_status.items() if status]
        logger.info(f"✅ Available services: {', '.join(available_services)}")
        
        initial_count = self.api_client.get_processed_articles_count()
        logger.info(f"📊 Initial articles in database: {initial_count}")
        
        # 2. Get high-priority sources for this cycle
        sources = get_high_priority_sources()[:max_sources]
        logger.info(f"🎯 Processing {len(sources)} high-priority sources")
        
        # Log source details for debugging
        for i, source in enumerate(sources, 1):
            logger.info(f"   {i}. {source.name} ({source.source_type.value}) - Credibility: {source.credibility_score}")
        
        # 3. Scrape articles from all sources
        scraped_articles = []
        for i, source in enumerate(sources, 1):
            try:
                logger.info(f"📡 {i}/{len(sources)}: Scraping {source.name}...")
                articles = self.scraper.scrape_source(source)
                
                if articles:
                    scraped_articles.extend(articles)
                    logger.info(f"✅ {source.name}: {len(articles)} relevant articles found")
                else:
                    logger.warning(f"⚠️ {source.name}: No relevant articles found")
                
                self.processing_stats['sources_processed'] += 1
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Failed to scrape {source.name}: {e}")
                continue
        
        self.processing_stats['articles_scraped'] = len(scraped_articles)
        logger.info(f"📊 SCRAPING COMPLETE: {len(scraped_articles)} total articles")
        
        if not scraped_articles:
            logger.warning("⚠️ No articles scraped. Ending cycle.")
            return self.processing_stats
        
        # 4. Sort articles by relevance score
        scraped_articles.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # 5. Process articles through ADVANCED INTELLIGENCE PIPELINE
        logger.info("🔄 STARTING ADVANCED INTELLIGENCE PIPELINE...")
        logger.info("   🌐 Translation → 🏷️ NER → 🕸️ Networks → 🧠 ML Threat → 💾 Storage")
        processed_successfully = []
        
        # Process top articles with full pipeline
        top_articles = scraped_articles[:15]  # Focus on highest quality articles
        
        for i, article in enumerate(top_articles, 1):
            try:
                logger.info(f"🔄 [{i}/{len(top_articles)}] PIPELINE: '{article.title[:50]}...'")
                logger.info(f"   📊 Source: {article.source} | Language: {article.language} | Relevance: {article.relevance_score:.1f}")
                
                # Process through enhanced pipeline
                result = self.api_client.process_article_enhanced(article)
                
                if result:
                    processed_successfully.append(result)
                    self.processing_stats['articles_processed'] += 1
                    
                    # Log enhanced processing results
                    if isinstance(result, dict) and 'processing_stages' in result:
                        successful_stages = [s for s in result['processing_stages'] if 'success' in s]
                        logger.info(f"✅ PIPELINE SUCCESS: {len(successful_stages)} stages completed")
                        
                        # Log specific intelligence gathered
                        if result.get('entities'):
                            entity_count = result['entities'].get('entity_count', 0)
                            logger.info(f"   🏷️ Entities: {entity_count}")
                        
                        if result.get('actor_networks'):
                            actor_count = len(result['actor_networks'].get('actors', []))
                            relationship_count = len(result['actor_networks'].get('relationships', []))
                            logger.info(f"   🕸️ Networks: {actor_count} actors, {relationship_count} relationships")
                        
                        if result.get('threat_assessment'):
                            threat_score = result['threat_assessment'].get('risk_score', 0)
                            logger.info(f"   🧠 Threat Score: {threat_score:.3f}")
                    else:
                        logger.info(f"✅ Basic processing successful")
                        
                else:
                    self.processing_stats['articles_rejected'] += 1
                    logger.warning(f"⚠️ Pipeline failed for: {article.title[:40]}...")
                
                time.sleep(1)  # Rate limiting for enhanced processing
                
            except Exception as e:
                logger.error(f"❌ Processing error: {e}")
                self.processing_stats['articles_rejected'] += 1
                continue
        
        # 6. Final statistics
        end_time = time.time()
        self.processing_stats['processing_time'] = end_time - start_time
        self.processing_stats['end_time'] = datetime.now()
        
        final_count = self.api_client.get_processed_articles_count()
        new_articles = final_count - initial_count
        
        # Enhanced statistics
        pipeline_enhanced_count = len([r for r in processed_successfully if isinstance(r, dict) and 'processing_stages' in r])
        basic_processed_count = self.processing_stats['articles_processed'] - pipeline_enhanced_count
        
        logger.info("🏆 ADVANCED INTELLIGENCE CYCLE COMPLETE!")
        logger.info("=" * 70)
        logger.info(f"📊 FINAL STATISTICS:")
        logger.info(f"   • Sources processed: {self.processing_stats['sources_processed']}")
        logger.info(f"   • Articles scraped: {self.processing_stats['articles_scraped']}")
        logger.info(f"   • Articles processed: {self.processing_stats['articles_processed']}")
        logger.info(f"     - Enhanced pipeline: {pipeline_enhanced_count}")
        logger.info(f"     - Basic processing: {basic_processed_count}")
        logger.info(f"   • Articles rejected: {self.processing_stats['articles_rejected']}")
        logger.info(f"   • New articles in DB: {new_articles}")
        logger.info(f"   • Total processing time: {self.processing_stats['processing_time']:.2f} seconds")
        logger.info(f"   • Average per article: {self.processing_stats['processing_time']/max(self.processing_stats['articles_processed'], 1):.2f} seconds")
        logger.info(f"   • Available services: {len(available_services)}/5")
        
        # Intelligence quality metrics
        if pipeline_enhanced_count > 0:
            logger.info(f"🧠 INTELLIGENCE QUALITY METRICS:")
            logger.info(f"   • Enhanced processing rate: {(pipeline_enhanced_count/self.processing_stats['articles_processed'])*100:.1f}%")
            logger.info(f"   • NLP pipeline operational: {'✅' if service_status.get('ner', False) else '❌'}")
            logger.info(f"   • Translation available: {'✅' if service_status.get('translation', False) else '❌'}")  
            logger.info(f"   • ML threat assessment: {'✅' if service_status.get('ml_prediction', False) else '❌'}")
            logger.info(f"   • Actor network analysis: {'✅' if service_status.get('ner', False) else '❌'}")
        
        return self.processing_stats
    
    def run_continuous_intelligence_monitoring(self, cycle_interval_minutes: int = 60):
        """
        Run continuous intelligence monitoring with advanced processing cycles.
        """
        logger.info(f"🔄 STARTING CONTINUOUS INTELLIGENCE MONITORING")
        logger.info(f"⏰ Cycle interval: {cycle_interval_minutes} minutes")
        logger.info(f"🛡️ CAMEROON DEFENSE FORCE - PROJECT SENTINEL OPERATIONAL")
        
        cycle_count = 0
        total_articles_processed = 0
        total_intelligence_gathered = 0
        
        try:
            while True:
                cycle_count += 1
                cycle_start = datetime.now()
                logger.info(f"\n🚀 INTELLIGENCE CYCLE #{cycle_count} STARTING at {cycle_start}")
                
                try:
                    stats = self.run_advanced_intelligence_cycle(max_sources=8)
                    
                    # Update totals
                    cycle_processed = stats.get('articles_processed', 0)
                    total_articles_processed += cycle_processed
                    
                    # Calculate intelligence metrics
                    success_rate = (cycle_processed / max(stats.get('articles_scraped', 1), 1)) * 100
                    processing_time = stats.get('processing_time', 0)
                    
                    logger.info(f"📈 CYCLE #{cycle_count} SUMMARY:")
                    logger.info(f"   • Articles processed: {cycle_processed}")
                    logger.info(f"   • Success rate: {success_rate:.1f}%")
                    logger.info(f"   • Processing time: {processing_time:.1f}s")
                    logger.info(f"   • Total articles (all cycles): {total_articles_processed}")
                    
                    # Log operational status
                    if cycle_processed > 0:
                        logger.info(f"✅ Intelligence gathering operational - New intelligence added to database")
                        total_intelligence_gathered += cycle_processed
                    else:
                        logger.warning(f"⚠️ No new intelligence gathered in cycle #{cycle_count}")
                    
                except Exception as e:
                    logger.error(f"❌ Cycle #{cycle_count} failed: {e}")
                
                # Operational summary every 5 cycles
                if cycle_count % 5 == 0:
                    logger.info(f"🛡️ OPERATIONAL SUMMARY (Last 5 cycles):")
                    logger.info(f"   • Total intelligence gathered: {total_intelligence_gathered}")
                    logger.info(f"   • Average per cycle: {total_intelligence_gathered/cycle_count:.1f}")
                    logger.info(f"   • System uptime: {cycle_count * cycle_interval_minutes} minutes")
                
                # Wait for next cycle
                wait_seconds = cycle_interval_minutes * 60
                next_cycle = datetime.now() + timedelta(seconds=wait_seconds)
                logger.info(f"⏰ Next intelligence cycle at {next_cycle.strftime('%H:%M:%S')}")
                logger.info(f"💤 Standby mode for {cycle_interval_minutes} minutes...")
                time.sleep(wait_seconds)
                
        except KeyboardInterrupt:
            logger.info("🛑 Continuous intelligence monitoring stopped by operator")
            logger.info(f"📊 Final Summary: {total_intelligence_gathered} intelligence reports processed across {cycle_count} cycles")
        except Exception as e:
            logger.error(f"❌ Critical monitoring error: {e}")
            logger.info(f"🔄 Attempting to restart monitoring system...")
            time.sleep(30)  # Brief pause before potential restart

def test_advanced_integration():
    """Test the advanced intelligence integration."""
    logger.info("🧪 TESTING ADVANCED INTELLIGENCE INTEGRATION")
    logger.info("=" * 60)
    
    # Initialize advanced processor
    processor = AdvancedIntelligenceProcessor()
    
    # Run a test cycle with limited sources
    stats = processor.run_advanced_intelligence_cycle(max_sources=3)
    
    success_metrics = {
        'articles_processed': stats.get('articles_processed', 0),
        'sources_processed': stats.get('sources_processed', 0),
        'processing_time': stats.get('processing_time', 0)
    }
    
    logger.info("🧪 TEST RESULTS:")
    logger.info(f"   • Articles processed: {success_metrics['articles_processed']}")
    logger.info(f"   • Sources processed: {success_metrics['sources_processed']}")
    logger.info(f"   • Processing time: {success_metrics['processing_time']:.2f}s")
    
    if success_metrics['articles_processed'] > 0:
        logger.info("✅ ADVANCED INTEGRATION TEST PASSED!")
        logger.info("🛡️ Project Sentinel intelligence pipeline operational")
        return True
    else:
        logger.error("❌ ADVANCED INTEGRATION TEST FAILED - No intelligence processed")
        logger.error("🔧 Check service availability and news source connectivity")
        return False

if __name__ == "__main__":
    import sys
    
    print("🛡️ PROJECT SENTINEL - INTELLIGENCE COLLECTION SYSTEM")
    print("=" * 60)
    print("CAMEROON DEFENSE FORCE - OSINT ANALYSIS PLATFORM")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run advanced integration test
        test_advanced_integration()
        
    elif len(sys.argv) > 1 and sys.argv[1] == "continuous":
        # Run continuous intelligence monitoring
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        print(f"🚀 Starting continuous intelligence monitoring (every {interval} minutes)")
        print("🛑 Press Ctrl+C to stop monitoring")
        print()
        
        processor = AdvancedIntelligenceProcessor()
        processor.run_continuous_intelligence_monitoring(interval)
        
    elif len(sys.argv) > 1 and sys.argv[1] == "single":
        # Run single enhanced cycle
        max_sources = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        print(f"🎯 Running single intelligence collection cycle ({max_sources} sources)")
        print()
        
        processor = AdvancedIntelligenceProcessor()
        processor.run_advanced_intelligence_cycle(max_sources=max_sources)
        
    else:
        # Show usage
        print("USAGE:")
        print("  python django_integration.py test           - Test intelligence pipeline")
        print("  python django_integration.py single [N]     - Run single cycle (N sources)")
        print("  python django_integration.py continuous [M] - Run continuous monitoring (every M minutes)")
        print()
        print("EXAMPLES:")
        print("  python django_integration.py test")
        print("  python django_integration.py single 8") 
        print("  python django_integration.py continuous 30")
        print()
        print("DEFAULT: Running single intelligence cycle with 5 sources...")
        print()
        
        processor = AdvancedIntelligenceProcessor()
        processor.run_advanced_intelligence_cycle(max_sources=5)


