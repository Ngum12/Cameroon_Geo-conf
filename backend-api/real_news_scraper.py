#!/usr/bin/env python3
"""
REAL NEWS SCRAPER - Collect actual articles from working Cameroon sources
"""
import os
import django
import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime, timedelta
import time
import re
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentinel_core.minimal_settings')
django.setup()

from sentinel_core.dashboard.models import NewsArticle
from django.utils import timezone

def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    return text[:2000]  # Limit length

def calculate_regional_priority(title, content):
    """Enhanced priority calculation for all 10 Cameroon regions + geopolitical intelligence"""
    priority = 2  # Default medium priority
    
    # === CAMEROON REGIONAL PRIORITY MAPPING ===
    
    # CRITICAL PRIORITY REGIONS (Active conflict zones)
    critical_regions = {
        'extreme-nord': ['extreme-nord', 'far north', 'maroua', 'kousseri', 'mokolo', 'boko haram', 'chad border'],
        'nord-ouest': ['nord-ouest', 'northwest', 'bamenda', 'kumbo', 'ndop', 'anglophone', 'separatist'],
        'sud-ouest': ['sud-ouest', 'southwest', 'buea', 'limbe', 'kumba', 'mamfe', 'anglophone', 'ambazonia']
    }
    
    # HIGH PRIORITY REGIONS (Border security, economic importance)
    high_priority_regions = {
        'est': ['est', 'east', 'bertoua', 'batouri', 'car border', 'central african republic', 'refugee'],
        'nord': ['nord', 'north', 'garoua', 'ngaoundere', 'transhumance', 'farmer herder', 'cattle'],
        'littoral': ['littoral', 'douala', 'port', 'economic capital', 'maritime', 'gulf of guinea']
    }
    
    # MEDIUM PRIORITY REGIONS (Political center, stable regions)
    medium_priority_regions = {
        'centre': ['centre', 'center', 'yaoundé', 'yaounde', 'capital', 'government', 'political'],
        'adamaoua': ['adamaoua', 'ngaoundéré', 'meiganga', 'tibati', 'transhumance'],
        'ouest': ['ouest', 'west', 'bafoussam', 'dschang', 'mbouda', 'bamileke'],
        'sud': ['sud', 'south', 'ebolowa', 'sangmelima', 'kribi', 'forest', 'equatorial guinea']
    }
    
    # === ENHANCED SECURITY & GEOPOLITICAL KEYWORDS ===
    
    # CRITICAL SECURITY THREATS
    critical_keywords = [
        'terrorism', 'terrorist', 'boko haram', 'suicide bomb', 'kidnapping', 'hostage',
        'separatist', 'secession', 'ambazonia', 'independence', 'armed group'
    ]
    
    # HIGH SECURITY CONCERNS
    high_security_keywords = [
        'military operation', 'security forces', 'defense', 'conflict', 'violence', 'attack',
        'crisis', 'emergency', 'displacement', 'refugee', 'humanitarian', 'peacekeeping'
    ]
    
    # GEOPOLITICAL INTELLIGENCE
    geopolitical_keywords = [
        'border security', 'cross-border', 'regional stability', 'ecowas', 'cemac', 'african union',
        'france relations', 'china investment', 'usa policy', 'eu cooperation', 'un mission',
        'oil pipeline', 'gas exploration', 'mining', 'infrastructure', 'trade route'
    ]
    
    # POLITICAL & GOVERNANCE
    political_keywords = [
        'election', 'democracy', 'governance', 'corruption', 'transparency', 'human rights',
        'press freedom', 'civil society', 'opposition', 'ruling party', 'constitutional'
    ]
    
    text_combined = f"{title} {content}".lower()
    
    # === REGIONAL PRIORITY CALCULATION ===
    
    # Check CRITICAL regions
    for region, keywords in critical_regions.items():
        if any(keyword in text_combined for keyword in keywords):
            priority = max(priority, 5)  # Critical priority
            break
    
    # Check HIGH PRIORITY regions
    for region, keywords in high_priority_regions.items():
        if any(keyword in text_combined for keyword in keywords):
            priority = max(priority, 4)  # High priority
            break
    
    # Check MEDIUM PRIORITY regions
    for region, keywords in medium_priority_regions.items():
        if any(keyword in text_combined for keyword in keywords):
            priority = max(priority, 3)  # Medium-high priority
            break
    
    # === KEYWORD-BASED PRIORITY BOOSTING ===
    
    # Critical security threats
    critical_matches = sum(1 for keyword in critical_keywords if keyword in text_combined)
    if critical_matches >= 1:
        priority = 5  # Immediate critical priority
    
    # High security concerns
    high_security_matches = sum(1 for keyword in high_security_keywords if keyword in text_combined)
    if high_security_matches >= 2:
        priority = min(5, priority + 1)  # Boost priority
    elif high_security_matches >= 1:
        priority = min(5, priority + 0.5)  # Small boost
    
    # Geopolitical intelligence value
    geopolitical_matches = sum(1 for keyword in geopolitical_keywords if keyword in text_combined)
    if geopolitical_matches >= 2:
        priority = min(5, priority + 1)  # Strategic importance
    elif geopolitical_matches >= 1:
        priority = min(4, priority + 0.5)  # Moderate importance
    
    # Political significance
    political_matches = sum(1 for keyword in political_keywords if keyword in text_combined)
    if political_matches >= 2:
        priority = min(4, priority + 0.5)  # Political relevance
    
    # === INTERNATIONAL RELEVANCE BOOST ===
    international_indicators = ['cameroon', 'cameroun', 'paul biya', 'yaoundé', 'douala']
    if any(indicator in text_combined for indicator in international_indicators):
        priority = min(5, priority + 0.5)  # Cameroon-specific content
    
    return int(priority)

def extract_articles_cameroon_tribune(soup):
    """Extract articles from Cameroon Tribune"""
    articles = []
    
    # Look for article containers
    article_elements = soup.find_all(['div', 'article'], class_=lambda x: x and any(
        term in x.lower() for term in ['article', 'post', 'news', 'item']
    ))
    
    for element in article_elements[:10]:  # Limit to 10 most recent
        title_elem = element.find(['h1', 'h2', 'h3', 'h4'], class_=lambda x: x and any(
            term in x.lower() for term in ['title', 'headline', 'head']
        ))
        
        if not title_elem:
            title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
        
        if title_elem:
            title = clean_text(title_elem.get_text())
            if len(title) > 10:  # Valid title
                
                # Try to find link
                link_elem = element.find('a', href=True)
                url = link_elem['href'] if link_elem else None
                if url and not url.startswith('http'):
                    url = f"https://www.cameroon-tribune.cm{url}"
                
                # Extract content preview
                content_elem = element.find(['p', 'div'], class_=lambda x: x and any(
                    term in x.lower() for term in ['excerpt', 'summary', 'content', 'text']
                ))
                
                if not content_elem:
                    # Get first paragraph
                    content_elem = element.find('p')
                
                content = clean_text(content_elem.get_text()) if content_elem else title
                
                articles.append({
                    'title': title,
                    'content': content,
                    'url': url or f"https://www.cameroon-tribune.cm/article-{hashlib.md5(title.encode()).hexdigest()[:8]}",
                    'source': 'Cameroon Tribune'
                })
    
    return articles

def extract_articles_journal_cameroun(soup):
    """Extract articles from Journal du Cameroun"""
    articles = []
    
    # Look for article elements
    article_elements = soup.find_all(['article', 'div'], class_=lambda x: x and any(
        term in x.lower() for term in ['post', 'article', 'entry']
    ))
    
    for element in article_elements[:10]:
        title_elem = element.find(['h1', 'h2', 'h3'])
        
        if title_elem:
            title = clean_text(title_elem.get_text())
            if len(title) > 10:
                
                # Find link
                link_elem = title_elem.find('a', href=True) or element.find('a', href=True)
                url = link_elem['href'] if link_elem else None
                if url and not url.startswith('http'):
                    url = f"https://www.journalducameroun.com{url}"
                
                # Get content
                content_elem = element.find(['p', 'div'], class_=lambda x: x and 'excerpt' in x.lower() if x else False)
                if not content_elem:
                    content_elem = element.find('p')
                
                content = clean_text(content_elem.get_text()) if content_elem else title
                
                articles.append({
                    'title': title,
                    'content': content,
                    'url': url or f"https://www.journalducameroun.com/article-{hashlib.md5(title.encode()).hexdigest()[:8]}",
                    'source': 'Journal du Cameroun'
                })
    
    return articles

def extract_articles_business_cameroon(soup):
    """Extract articles from Business in Cameroon"""
    articles = []
    
    # Look for news items
    article_elements = soup.find_all(['div', 'article'], class_=lambda x: x and any(
        term in x.lower() for term in ['news', 'article', 'item', 'post']
    ))
    
    for element in article_elements[:8]:  # Limit to 8
        title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
        
        if title_elem:
            title = clean_text(title_elem.get_text())
            if len(title) > 10:
                
                link_elem = title_elem.find('a', href=True) or element.find('a', href=True)
                url = link_elem['href'] if link_elem else None
                if url and not url.startswith('http'):
                    url = f"https://www.businessincameroon.com{url}"
                
                content_elem = element.find('p')
                content = clean_text(content_elem.get_text()) if content_elem else title
                
                articles.append({
                    'title': title,
                    'content': content,
                    'url': url or f"https://www.businessincameroon.com/article-{hashlib.md5(title.encode()).hexdigest()[:8]}",
                    'source': 'Business in Cameroon'
                })
    
    return articles

def scrape_real_news():
    """Enhanced scraping with regional targeting for better coverage"""
    
    print("🚀 ENHANCED REGIONAL NEWS COLLECTION FROM CAMEROON SOURCES")
    print("=" * 70)
    print("🎯 TARGETING: Nord-Ouest, Sud-Ouest, Extreme-Nord regions")
    print("📊 GOAL: Balanced regional coverage for ML training")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    sources = [
        # === TIER 1: OFFICIAL CAMEROON GOVERNMENT & DEFENSE SOURCES ===
        ('https://www.cameroon-tribune.cm/', extract_articles_cameroon_tribune),      # Official government daily
        ('https://www.journalducameroun.com/', extract_articles_journal_cameroun),    # Major independent news
        ('https://www.businessincameroon.com/', extract_articles_business_cameroon),  # Economic intelligence
        ('https://cna.cm/', extract_articles_cameroon_tribune),                       # Cameroon News Agency (Official)
        
        # === TIER 2: COMPREHENSIVE REGIONAL COVERAGE (ALL 10 REGIONS) ===
        
        # EXTREME-NORD REGION (Boko Haram, Chad border, security operations)
        ('https://237actu.com/', extract_articles_cameroon_tribune),                  # Strong Far North coverage
        ('https://www.camerounweb.com/', extract_articles_journal_cameroun),          # Regional conflicts
        ('https://actucameroun.com/', extract_articles_business_cameroon),            # Security updates
        
        # NORD-OUEST & SUD-OUEST (Anglophone Crisis, separatist activities)
        ('https://camer.be/', extract_articles_journal_cameroun),                     # Political analysis
        ('https://www.stopblablacam.com/', extract_articles_cameroon_tribune),        # Political commentary
        ('https://www.cameroon-info.net/', extract_articles_business_cameroon),       # Regional news
        ('https://bamendaonline.net/', extract_articles_journal_cameroun),            # Northwest focus
        ('https://www.camerounactuel.com/', extract_articles_cameroon_tribune),       # Southwest coverage
        
        # CENTRE, LITTORAL, OUEST (Political center, economic hub)
        ('https://www.lebledparle.com/', extract_articles_business_cameroon),         # Yaoundé politics
        ('https://www.cameroon24.net/', extract_articles_journal_cameroun),           # Douala business
        ('https://www.camerounlink.net/', extract_articles_cameroon_tribune),         # West region
        
        # EST, ADAMAOUA, NORD, SUD (CAR border, transhumance, forest conflicts)
        ('https://www.camerounactualite.com/', extract_articles_business_cameroon),   # East region (CAR border)
        ('https://www.actu-cameroun.com/', extract_articles_journal_cameroun),        # Adamaoua coverage
        ('https://www.cameroun24.com/', extract_articles_cameroon_tribune),           # North region
        ('https://www.camerounplus.com/', extract_articles_business_cameroon),        # South region
        
        # === TIER 3: PAN-AFRICAN GEOPOLITICAL INTELLIGENCE ===
        ('https://www.africanews.com/', extract_articles_cameroon_tribune),           # Pan-African perspective
        ('https://allafrica.com/cameroon/', extract_articles_journal_cameroun),       # Comprehensive Africa news
        ('https://www.theafricareport.com/', extract_articles_business_cameroon),     # Deep geopolitical analysis
        ('https://www.aa.com.tr/en/africa/', extract_articles_cameroon_tribune),      # Anadolu Agency Africa
        ('https://www.africanarguments.org/', extract_articles_journal_cameroun),     # Political analysis
        ('https://www.newafricanmagazine.com/', extract_articles_business_cameroon),  # Strategic insights
        
        # === TIER 4: INTERNATIONAL SECURITY & GEOPOLITICAL MONITORING ===
        
        # MAJOR INTERNATIONAL NEWS AGENCIES
        ('https://www.reuters.com/world/africa/', extract_articles_cameroon_tribune), # Reuters Africa Bureau
        ('https://www.bbc.com/news/world/africa', extract_articles_journal_cameroun), # BBC Africa Service
        ('https://www.france24.com/en/africa/', extract_articles_business_cameroon),  # France24 Africa
        ('https://www.dw.com/en/africa/s-12293', extract_articles_cameroon_tribune),  # Deutsche Welle Africa
        ('https://www.voanews.com/africa', extract_articles_journal_cameroun),        # Voice of America Africa
        
        # FRANCOPHONE AFRICA SPECIALISTS
        ('https://www.rfi.fr/en/africa/', extract_articles_business_cameroon),        # RFI Africa (French perspective)
        ('https://www.jeuneafrique.com/', extract_articles_cameroon_tribune),         # Jeune Afrique (French)
        ('https://www.lemonde.fr/afrique/', extract_articles_journal_cameroun),       # Le Monde Africa
        
        # SECURITY & DEFENSE INTELLIGENCE
        ('https://www.defenceweb.co.za/', extract_articles_business_cameroon),        # Defense intelligence
        ('https://www.janes.com/', extract_articles_cameroon_tribune),                # Military intelligence
        ('https://www.crisisgroup.org/', extract_articles_journal_cameroun),          # International Crisis Group
        
        # REGIONAL SECURITY ORGANIZATIONS
        ('https://www.ecowas.int/', extract_articles_business_cameroon),              # ECOWAS security updates
        ('https://au.int/', extract_articles_cameroon_tribune),                       # African Union
        ('https://www.cemac.int/', extract_articles_journal_cameroun),                # CEMAC regional bloc
        
        # === TIER 5: SPECIALIZED GEOPOLITICAL & CONFLICT ANALYSIS ===
        ('https://www.acleddata.com/', extract_articles_business_cameroon),           # Armed Conflict Location Data
        ('https://www.chathamhouse.org/', extract_articles_cameroon_tribune),         # Chatham House Africa
        ('https://www.cfr.org/regions/africa', extract_articles_journal_cameroun),    # Council on Foreign Relations
        ('https://www.brookings.edu/region/africa/', extract_articles_business_cameroon), # Brookings Africa
        ('https://www.csis.org/regions/africa', extract_articles_cameroon_tribune),   # CSIS Africa Program
        
        # HUMANITARIAN & DEVELOPMENT INTELLIGENCE
        ('https://www.unhcr.org/', extract_articles_journal_cameroun),                # UNHCR (refugee crises)
        ('https://www.unocha.org/', extract_articles_business_cameroon),              # UN OCHA (humanitarian)
        ('https://www.worldbank.org/en/region/afr', extract_articles_cameroon_tribune), # World Bank Africa
        
        # === TIER 6: ECONOMIC & RESOURCE INTELLIGENCE ===
        ('https://www.africanmining.com/', extract_articles_journal_cameroun),        # Mining intelligence
        ('https://www.energyvoice.com/africa/', extract_articles_business_cameroon),  # Energy sector
        ('https://www.commodafrica.com/', extract_articles_cameroon_tribune),         # Commodity markets
        ('https://www.africanbusinesscentral.com/', extract_articles_journal_cameroun), # Business intelligence
    ]
    
    total_collected = 0
    
    for url, extractor in sources:
        try:
            print(f"\n🔍 Scraping {url}...")
            
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = extractor(soup)
                
                print(f"   📄 Found {len(articles)} articles")
                
                saved_count = 0
                for article in articles:
                    try:
                        # Check if article exists
                        if NewsArticle.objects.filter(url=article['url']).exists():
                            continue
                        
                        # Create unique ID
                        article_id = hashlib.md5(f"{article['title']}{article['url']}".encode()).hexdigest()
                        
                        # Enhanced regional priority scoring
                        priority = calculate_regional_priority(article['title'], article['content'])
                        
                        # Create article with enhanced metadata
                        news_article = NewsArticle(
                            id=article_id,
                            title=article['title'][:500],  # Limit title length
                            raw_text=article['content'],
                            url=article['url'],
                            source=article['source'],
                            published_date=timezone.now(),
                            priority=priority,  # Calculated regional priority
                            classification='news',
                            language='fr' if 'cameroun' in article['source'].lower() else 'en',
                            processing_status='COMPLETED',
                            content_length=len(article['content']),
                            word_count=len(article['content'].split()),
                            relevance_score=75.0,
                            sentiment_score=0.0,
                            processed_json='{"status": "scraped", "timestamp": "' + timezone.now().isoformat() + '"}'
                        )
                        
                        news_article.save()
                        print(f"   ✅ Saved: {article['title'][:60]}...")
                        saved_count += 1
                        
                    except Exception as e:
                        print(f"   ❌ Error saving article: {str(e)[:100]}")
                
                print(f"   📈 Saved {saved_count} new articles from {article['source']}")
                total_collected += saved_count
                
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error scraping {url}: {str(e)[:100]}")
        
        time.sleep(3)  # Be respectful to servers
    
    print("\n" + "=" * 60)
    print("🎉 REAL NEWS COLLECTION COMPLETE!")
    print(f"📈 Total articles collected: {total_collected}")
    
    # Show updated stats
    total_db = NewsArticle.objects.count()
    recent_24h = NewsArticle.objects.filter(created_at__gte=timezone.now() - timezone.timedelta(hours=24)).count()
    
    print(f"\n📊 DATABASE STATUS:")
    print(f"   Total Articles: {total_db}")
    print(f"   Fresh (24h): {recent_24h}")
    
    if recent_24h > 0:
        print("✅ SUCCESS: Your dashboard now has REAL fresh data!")
    
    return total_collected

def generate_historical_data(months_back=3):
    """
    🕐 HISTORICAL DATA GENERATOR - Fill database with 3 months of realistic data
    Creates articles with dates spread over the past 3 months for ML training
    """
    print("🚀 GENERATING 3-MONTH HISTORICAL DATASET")
    print("=" * 60)
    print("📅 Timeframe: Past 3 months")
    print("🎯 Purpose: ML model training & temporal analysis")
    print("🔄 Method: Realistic article distribution")
    print("=" * 60)
    
    # Historical article templates based on Cameroon geopolitical patterns
    historical_templates = [
        # EXTREME-NORD (Boko Haram, Chad border)
        {"title": "Boko Haram attacks repelled in Far North region", "region": "Extreme-Nord", "priority": 5, "source": "Cameroon Tribune"},
        {"title": "Military operations intensify along Chad border", "region": "Extreme-Nord", "priority": 4, "source": "Journal du Cameroun"},
        {"title": "Refugees from Chad arrive in Kousseri", "region": "Extreme-Nord", "priority": 4, "source": "Africanews"},
        {"title": "Security reinforced in Maroua following threats", "region": "Extreme-Nord", "priority": 5, "source": "RFI Africa"},
        
        # NORD-OUEST & SUD-OUEST (Anglophone crisis)
        {"title": "Separatist activities reported in Northwest region", "region": "Nord-Ouest", "priority": 5, "source": "BBC Africa"},
        {"title": "Dialogue efforts continue in Anglophone regions", "region": "Sud-Ouest", "priority": 4, "source": "VOA Africa"},
        {"title": "Schools reopen in Bamenda amid security concerns", "region": "Nord-Ouest", "priority": 4, "source": "CamerounWeb"},
        {"title": "Humanitarian aid reaches Southwest communities", "region": "Sud-Ouest", "priority": 3, "source": "UNHCR Cameroon"},
        
        # CENTRE (Political activities)
        {"title": "President Paul Biya receives diplomatic delegation", "region": "Centre", "priority": 3, "source": "Presidency of Cameroon"},
        {"title": "Government announces new security measures", "region": "Centre", "priority": 4, "source": "Prime Minister Office"},
        {"title": "Parliamentary session discusses regional issues", "region": "Centre", "priority": 3, "source": "Cameroon Tribune"},
        
        # LITTORAL (Economic activities)
        {"title": "Port of Douala reports increased activity", "region": "Littoral", "priority": 2, "source": "Investir au Cameroun"},
        {"title": "Maritime security enhanced in Gulf of Guinea", "region": "Littoral", "priority": 4, "source": "Reuters Africa"},
        {"title": "Economic summit held in Douala", "region": "Littoral", "priority": 2, "source": "African Development Bank"},
        
        # EST (CAR border, refugees)
        {"title": "Central African refugees cross into East region", "region": "Est", "priority": 4, "source": "UNHCR Cameroon"},
        {"title": "Border security reinforced with CAR", "region": "Est", "priority": 4, "source": "Ministry of Defense"},
        {"title": "Humanitarian corridor established in Bertoua", "region": "Est", "priority": 3, "source": "WFP Cameroon"},
        
        # NORD (Transhumance, farmer-herder conflicts)
        {"title": "Farmer-herder conflicts mediated in North region", "region": "Nord", "priority": 3, "source": "Journal du Cameroun"},
        {"title": "Transhumance season begins with security measures", "region": "Nord", "priority": 3, "source": "Cameroon Tribune"},
        {"title": "Cattle rustling incidents reported in Garoua", "region": "Nord", "priority": 4, "source": "ActuCameroun"},
        
        # Other regions
        {"title": "Development projects launched in Adamawa", "region": "Adamaoua", "priority": 2, "source": "World Bank Cameroon"},
        {"title": "Cultural festival celebrates diversity in West", "region": "Ouest", "priority": 1, "source": "CamerPost"},
        {"title": "Infrastructure development continues in South", "region": "Sud", "priority": 2, "source": "African Development Bank"},
    ]
    
    # Generate articles for past 3 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 3 months
    
    articles_per_day = random.randint(8, 15)  # Realistic daily article count
    total_days = 90
    total_target = articles_per_day * total_days
    
    print(f"📊 Target: ~{total_target} articles over {total_days} days")
    print(f"📈 Average: {articles_per_day} articles per day")
    print()
    
    generated_count = 0
    
    for day in range(total_days):
        current_date = start_date + timedelta(days=day)
        daily_articles = random.randint(5, 20)  # Vary daily count realistically
        
        for article_num in range(daily_articles):
            # Select random template
            template = random.choice(historical_templates)
            
            # Add temporal variation to title
            time_variants = [
                f"{template['title']} - {current_date.strftime('%B %d')}",
                f"Update: {template['title']}",
                f"Breaking: {template['title']}",
                f"Analysis: {template['title']}",
                template['title']  # Keep some original
            ]
            
            title = random.choice(time_variants)
            
            # Generate realistic content
            content_templates = [
                f"Security forces in {template['region']} region report developments in ongoing operations. Local authorities coordinate with national defense to ensure civilian safety and maintain territorial integrity.",
                f"Regional analysis indicates continued monitoring required in {template['region']}. Intelligence sources confirm strategic importance of maintaining security presence in the area.",
                f"Government officials emphasize commitment to peace and stability in {template['region']} region. Coordination between military and civilian authorities continues to strengthen regional security.",
                f"International observers note progress in {template['region']} region security situation. Humanitarian access remains priority while maintaining operational security requirements."
            ]
            
            content = random.choice(content_templates)
            
            # Add regional context
            content += f" This development in {template['region']} region aligns with broader national security objectives and regional stability initiatives."
            
            try:
                # Create unique ID
                article_id = hashlib.md5(f"{title}{current_date.isoformat()}{article_num}".encode()).hexdigest()
                
                # Check if similar article exists
                if NewsArticle.objects.filter(id=article_id).exists():
                    continue
                
                # Create historical article
                news_article = NewsArticle(
                    id=article_id,
                    title=title[:500],
                    raw_text=content,
                    url=f"https://historical-data.sentinel/{article_id}",
                    source=template['source'],
                    published_date=current_date,
                    created_at=current_date,  # Important: Set historical date
                    priority=template['priority'],
                    classification='news',
                    language='en',
                    processing_status='COMPLETED',
                    content_length=len(content),
                    word_count=len(content.split()),
                    relevance_score=random.uniform(60.0, 95.0),
                    sentiment_score=random.uniform(-0.5, 0.5),
                    processed_json=f'{{"status": "historical", "region": "{template["region"]}", "generated_at": "{datetime.now().isoformat()}"}}'
                )
                
                news_article.save()
                generated_count += 1
                
                # Progress indicator
                if generated_count % 50 == 0:
                    progress = (generated_count / total_target) * 100
                    print(f"📈 Progress: {generated_count}/{total_target} articles ({progress:.1f}%)")
                
            except Exception as e:
                print(f"⚠️  Error creating article: {e}")
                continue
    
    print("\n" + "=" * 60)
    print("✅ HISTORICAL DATA GENERATION COMPLETE")
    print(f"📊 Generated: {generated_count} historical articles")
    print(f"📅 Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Final database stats
    total_db = NewsArticle.objects.count()
    recent_7d = NewsArticle.objects.filter(created_at__gte=datetime.now() - timedelta(days=7)).count()
    recent_30d = NewsArticle.objects.filter(created_at__gte=datetime.now() - timedelta(days=30)).count()
    recent_90d = NewsArticle.objects.filter(created_at__gte=datetime.now() - timedelta(days=90)).count()
    
    print(f"\n📈 DATABASE SUMMARY:")
    print(f"   Total Articles: {total_db}")
    print(f"   Last 7 days: {recent_7d}")
    print(f"   Last 30 days: {recent_30d}")
    print(f"   Last 90 days: {recent_90d}")
    print("\n🎯 System ready for comprehensive ML training!")
    
    return generated_count

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--historical':
        # Generate 3 months of historical data
        generate_historical_data(3)
    else:
        # Normal scraping
        scrape_real_news()
