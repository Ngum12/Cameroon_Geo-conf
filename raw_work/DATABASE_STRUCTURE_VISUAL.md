# 📊 HARMONY FLOW PLATFORM - DATABASE STRUCTURE & SAMPLE DATA

## 🗄️ **COMPLETE DATABASE SCHEMA WITH REAL EXAMPLES**

---

## **DATABASE LAYER 1: RAW DATA INGESTION**

### **📰 `raw_articles` Table**
```sql
CREATE TABLE raw_articles (
    id              UUID PRIMARY KEY,
    url             TEXT NOT NULL,
    source_name     VARCHAR(100),
    raw_content     TEXT,
    scraped_at      TIMESTAMP,
    content_hash    VARCHAR(64),
    language        VARCHAR(10),
    metadata        JSONB
);
```

### **📋 Sample Data:**
```
┌─────────────────────────────────┬──────────────────────────┬────────────┬─────────────────┬─────────────────────┐
│ id                              │ url                      │ source     │ language       │ scraped_at          │
├─────────────────────────────────┼──────────────────────────┼────────────┼─────────────────┼─────────────────────┤
│ 550e8400-e29b-41d4-a716-446655 │ bbc.com/africa/cameroon  │ BBC Africa │ en             │ 2024-01-15 14:30:00 │
│ 6ba7b810-9dad-11d1-80b4-006094 │ rfi.fr/cameroun/violence │ RFI        │ fr             │ 2024-01-15 14:35:00 │
│ 6ba7b811-9dad-11d1-80b4-006094 │ journalducameroun.com    │ Local News │ fr             │ 2024-01-15 14:40:00 │
└─────────────────────────────────┴──────────────────────────┴────────────┴─────────────────┴─────────────────────┘

Raw Content Sample:
"Tensions mounting in Bamenda as separatist groups clash with security forces. 
Local residents report gunfire in commercial districts. Government spokesperson 
confirms deployment of additional troops to Northwest region..."
```

---

## **DATABASE LAYER 2: CLEANED & PROCESSED DATA**

### **📄 `articles` Table (Main Data)**
```sql
CREATE TABLE articles (
    id                  UUID PRIMARY KEY,
    raw_article_id      UUID REFERENCES raw_articles(id),
    title              VARCHAR(500),
    content            TEXT,
    url                TEXT,
    source_id          UUID REFERENCES sources(id),
    published_date     TIMESTAMP,
    scraped_at         TIMESTAMP,
    language           VARCHAR(10),
    region             VARCHAR(50),
    processing_status  VARCHAR(20),
    relevance_score    FLOAT,
    created_at         TIMESTAMP DEFAULT NOW()
);
```

### **📋 Sample Data:**
```
┌─────────────────┬────────────────────────────────────────┬────────────────┬────────────────┬─────────────────────┐
│ id              │ title                                  │ region         │ language       │ processing_status   │
├─────────────────┼────────────────────────────────────────┼────────────────┼────────────────┼─────────────────────┤
│ art_001         │ Security Forces Deploy to Bamenda     │ Northwest      │ en             │ completed           │
│ art_002         │ Manifestations à Douala Centre-Ville  │ Littoral       │ fr             │ completed           │
│ art_003         │ Farmer-Herder Conflict in Adamaoua    │ Adamaoua       │ en             │ completed           │
│ art_004         │ Political Rally Turns Violent in Yaounde │ Centre      │ en             │ processing          │
└─────────────────┴────────────────────────────────────────┴────────────────┴────────────────┴─────────────────────┘
```

### **🏢 `sources` Table**
```sql
CREATE TABLE sources (
    id                 UUID PRIMARY KEY,
    name              VARCHAR(100) NOT NULL,
    base_url          VARCHAR(200),
    source_type       VARCHAR(50),
    language          VARCHAR(10),
    reliability_score FLOAT DEFAULT 0.5,
    is_active         BOOLEAN DEFAULT true,
    last_scraped      TIMESTAMP,
    created_at        TIMESTAMP DEFAULT NOW()
);
```

### **📋 Sample Data:**
```
┌─────────┬─────────────────┬─────────────────────────┬─────────────────┬─────────────────────┐
│ id      │ name            │ base_url                │ reliability     │ source_type         │
├─────────┼─────────────────┼─────────────────────────┼─────────────────┼─────────────────────┤
│ src_001 │ BBC Africa      │ bbc.com/africa          │ 0.95            │ international_media │
│ src_002 │ RFI Afrique     │ rfi.fr/afrique         │ 0.92            │ international_media │
│ src_003 │ Cameroun Tribune│ cameroun-tribune.cm     │ 0.78            │ national_media      │
│ src_004 │ Journal du Cameroun │ journalducameroun.com │ 0.71         │ local_media         │
└─────────┴─────────────────┴─────────────────────────┴─────────────────┴─────────────────────┘
```

---

## **DATABASE LAYER 3: NLP ANALYSIS RESULTS**

### **🧠 `entities` Table**
```sql
CREATE TABLE entities (
    id                UUID PRIMARY KEY,
    article_id        UUID REFERENCES articles(id),
    entity_text       VARCHAR(200),
    entity_type       VARCHAR(50),
    start_position    INTEGER,
    end_position      INTEGER,
    confidence_score  FLOAT,
    metadata          JSONB,
    created_at        TIMESTAMP DEFAULT NOW()
);
```

### **📋 Sample Data:**
```
┌─────────┬─────────────┬─────────────────────────┬─────────────────┬─────────────────┬─────────────────────┐
│ id      │ article_id  │ entity_text             │ entity_type     │ confidence      │ metadata            │
├─────────┼─────────────┼─────────────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│ ent_001 │ art_001     │ Bamenda                 │ LOCATION        │ 0.96            │ {"region": "NW"}    │
│ ent_002 │ art_001     │ Northwest Region        │ LOCATION        │ 0.98            │ {"admin_level": 1}  │
│ ent_003 │ art_001     │ Security Forces         │ ORGANIZATION    │ 0.89            │ {"type": "military"}│
│ ent_004 │ art_002     │ Douala                  │ LOCATION        │ 0.94            │ {"region": "LT"}    │
│ ent_005 │ art_002     │ Centre-Ville            │ LOCATION        │ 0.82            │ {"type": "district"}│
└─────────┴─────────────┴─────────────────────────┴─────────────────┴─────────────────┴─────────────────────┘
```

### **💭 `sentiment_analysis` Table**
```sql
CREATE TABLE sentiment_analysis (
    id               UUID PRIMARY KEY,
    article_id       UUID REFERENCES articles(id),
    sentiment_score  FLOAT,
    polarity        VARCHAR(20),
    confidence      FLOAT,
    emotional_tone  VARCHAR(50),
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### **📋 Sample Data:**
```
┌─────────┬─────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────────┐
│ id      │ article_id  │ sentiment_score │ polarity        │ confidence      │ emotional_tone      │
├─────────┼─────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│ sen_001 │ art_001     │ -0.73           │ NEGATIVE        │ 0.87            │ fear,anger          │
│ sen_002 │ art_002     │ -0.65           │ NEGATIVE        │ 0.82            │ tension,concern     │
│ sen_003 │ art_003     │ -0.45           │ NEGATIVE        │ 0.76            │ conflict,worry      │
│ sen_004 │ art_004     │ -0.81           │ NEGATIVE        │ 0.91            │ violence,chaos      │
└─────────┴─────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
```

### **📍 `geospatial_data` Table**
```sql
CREATE TABLE geospatial_data (
    id               UUID PRIMARY KEY,
    article_id       UUID REFERENCES articles(id),
    latitude         DECIMAL(10,8),
    longitude        DECIMAL(11,8),
    region           VARCHAR(50),
    admin_level      INTEGER,
    place_name       VARCHAR(100),
    confidence_score FLOAT,
    geometry         GEOGRAPHY(POINT, 4326),
    created_at       TIMESTAMP DEFAULT NOW()
);
```

### **📋 Sample Data:**
```
┌─────────┬─────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────────┐
│ id      │ article_id  │ latitude        │ longitude       │ region          │ place_name      │ confidence          │
├─────────┼─────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│ geo_001 │ art_001     │ 5.9597         │ 10.1419         │ Northwest       │ Bamenda         │ 0.96                │
│ geo_002 │ art_002     │ 4.0511         │ 9.7679          │ Littoral        │ Douala          │ 0.94                │
│ geo_003 │ art_003     │ 7.3167         │ 12.3833         │ Adamaoua        │ Ngaoundéré      │ 0.78                │
│ geo_004 │ art_004     │ 3.8480         │ 11.5021         │ Centre          │ Yaoundé         │ 0.99                │
└─────────┴─────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
```

---

## **DATABASE LAYER 4: MACHINE LEARNING INTELLIGENCE**

### **🎯 `threat_assessments` Table**
```sql
CREATE TABLE threat_assessments (
    id                  UUID PRIMARY KEY,
    article_id          UUID REFERENCES articles(id),
    threat_level        VARCHAR(20),
    threat_category     VARCHAR(50),
    confidence_score    FLOAT,
    feature_vector      JSONB,
    model_version       VARCHAR(20),
    assessment_date     TIMESTAMP,
    reasoning           TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);
```

### **📋 Sample Data:**
```
┌─────────┬─────────────┬─────────────────┬─────────────────────────┬─────────────────┬─────────────────┐
│ id      │ article_id  │ threat_level    │ threat_category         │ confidence      │ reasoning       │
├─────────┼─────────────┼─────────────────┼─────────────────────────┼─────────────────┼─────────────────┤
│ thr_001 │ art_001     │ HIGH            │ ARMED_CONFLICT          │ 0.87            │ Military deployment, │
│         │             │                 │                         │                 │ high violence indicators │
│ thr_002 │ art_002     │ MEDIUM          │ CIVIL_UNREST           │ 0.74            │ Protest activity,    │
│         │             │                 │                         │                 │ negative sentiment   │
│ thr_003 │ art_003     │ MEDIUM          │ COMMUNAL_TENSION        │ 0.69            │ Resource conflict,   │
│         │             │                 │                         │                 │ ethnic factors       │
│ thr_004 │ art_004     │ CRITICAL        │ POLITICAL_VIOLENCE      │ 0.93            │ Rally violence,      │
│         │             │                 │                         │                 │ capital city impact │
└─────────┴─────────────┴─────────────────┴─────────────────────────┴─────────────────┴─────────────────┘

Feature Vector Sample:
{
    "sentiment_score": -0.73,
    "entity_density": 0.45,
    "violence_keywords": 8,
    "location_specificity": 0.96,
    "temporal_urgency": 0.82,
    "source_reliability": 0.95,
    "historical_correlation": 0.78
}
```

### **🔮 `conflict_predictions` Table**
```sql
CREATE TABLE conflict_predictions (
    id                    UUID PRIMARY KEY,
    region               VARCHAR(50),
    prediction_horizon   INTEGER,
    probability          FLOAT,
    confidence_level     FLOAT,
    prediction_date      TIMESTAMP,
    contributing_factors JSONB,
    model_version        VARCHAR(20),
    created_at           TIMESTAMP DEFAULT NOW()
);
```

### **📋 Sample Data:**
```
┌─────────┬─────────────────┬─────────────────────┬─────────────────┬─────────────────┬─────────────────────┐
│ id      │ region          │ prediction_horizon  │ probability     │ confidence      │ contributing_factors│
├─────────┼─────────────────┼─────────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│ pred_001│ Northwest       │ 7                   │ 0.73            │ 0.85            │ {"separatist": 0.4, │
│         │                 │                     │                 │                 │  "military": 0.3}   │
│ pred_002│ Northwest       │ 14                  │ 0.68            │ 0.82            │ {"political": 0.5,  │
│         │                 │                     │                 │                 │  "economic": 0.2}   │
│ pred_003│ Littoral        │ 7                   │ 0.42            │ 0.71            │ {"protest": 0.6,    │
│         │                 │                     │                 │                 │  "youth": 0.4}      │
│ pred_004│ Centre          │ 7                   │ 0.39            │ 0.69            │ {"political": 0.7,  │
│         │                 │                     │                 │                 │  "urban": 0.3}      │
└─────────┴─────────────────┴─────────────────────┴─────────────────┴─────────────────┴─────────────────────┘
```

---

## **DATABASE LAYER 5: HUMAN VERIFICATION**

### **✅ `verification_results` Table**
```sql
CREATE TABLE verification_results (
    id                    UUID PRIMARY KEY,
    threat_assessment_id  UUID REFERENCES threat_assessments(id),
    analyst_id           UUID REFERENCES users(id),
    verification_status  VARCHAR(20),
    confidence_rating    INTEGER,
    analyst_notes        TEXT,
    modifications        JSONB,
    verification_date    TIMESTAMP,
    created_at           TIMESTAMP DEFAULT NOW()
);
```

### **📋 Sample Data:**
```
┌─────────┬─────────────────────┬─────────────────────┬─────────────────────┬─────────────────┬─────────────────────────┐
│ id      │ threat_assessment_id│ analyst_id          │ verification_status │ confidence      │ analyst_notes           │
├─────────┼─────────────────────┼─────────────────────┼─────────────────────┼─────────────────┼─────────────────────────┤
│ ver_001 │ thr_001            │ analyst_john        │ VERIFIED            │ 9               │ Confirmed through field │
│         │                     │                     │                     │                 │ reports. Military       │
│         │                     │                     │                     │                 │ deployment validated.   │
│ ver_002 │ thr_002            │ analyst_marie       │ MODIFIED            │ 7               │ Reduced from HIGH to    │
│         │                     │                     │                     │                 │ MEDIUM. Peaceful protest│
│         │                     │                     │                     │                 │ confirmed.              │
│ ver_003 │ thr_003            │ analyst_paul        │ VERIFIED            │ 8               │ Farmer-herder tension   │
│         │                     │                     │                     │                 │ matches historical      │
│         │                     │                     │                     │                 │ patterns.               │
│ ver_004 │ thr_004            │ analyst_john        │ ESCALATED           │ 10              │ CRITICAL confirmed.     │
│         │                     │                     │                     │                 │ Violence spreading.     │
│         │                     │                     │                     │                 │ Immediate action needed.│
└─────────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────┴─────────────────────────┘
```

---

## **DATABASE LAYER 6: DECISION SUPPORT**

### **🎯 `intervention_recommendations` Table**
```sql
CREATE TABLE intervention_recommendations (
    id                     UUID PRIMARY KEY,
    threat_assessment_id   UUID REFERENCES threat_assessments(id),
    intervention_type      VARCHAR(50),
    priority_level         VARCHAR(20),
    expected_effectiveness FLOAT,
    cost_estimate         DECIMAL(10,2),
    resource_requirements  JSONB,
    timeline_days         INTEGER,
    risk_assessment       TEXT,
    created_at            TIMESTAMP DEFAULT NOW()
);
```

### **📋 Sample Data:**
```
┌─────────┬─────────────────────┬─────────────────────────┬─────────────────┬─────────────────────┬─────────────────┐
│ id      │ threat_assessment_id│ intervention_type       │ priority        │ expected_effect     │ cost_estimate   │
├─────────┼─────────────────────┼─────────────────────────┼─────────────────┼─────────────────────┼─────────────────┤
│ int_001 │ thr_001            │ DIPLOMATIC_MEDIATION    │ HIGH            │ 0.72                │ 15000.00        │
│ int_002 │ thr_001            │ COMMUNITY_DIALOGUE      │ HIGH            │ 0.68                │ 8000.00         │
│ int_003 │ thr_002            │ YOUTH_ENGAGEMENT        │ MEDIUM          │ 0.65                │ 5000.00         │
│ int_004 │ thr_004            │ EMERGENCY_RESPONSE      │ URGENT          │ 0.85                │ 25000.00        │
└─────────┴─────────────────────┴─────────────────────────┴─────────────────┴─────────────────────┴─────────────────┘

Resource Requirements Sample:
{
    "personnel": 15,
    "vehicles": 3,
    "specialists": ["mediator", "translator"],
    "duration_weeks": 4,
    "equipment": ["communication", "logistics"]
}
```

---

## **DATABASE LAYER 7: ALERT SYSTEM**

### **🚨 `alerts` Table**
```sql
CREATE TABLE alerts (
    id                    UUID PRIMARY KEY,
    threat_assessment_id  UUID REFERENCES threat_assessments(id),
    alert_level          VARCHAR(20),
    title                VARCHAR(200),
    message_content      TEXT,
    recipients           JSONB,
    delivery_channels    JSONB,
    created_at           TIMESTAMP DEFAULT NOW(),
    sent_at              TIMESTAMP,
    escalation_count     INTEGER DEFAULT 0,
    acknowledgments      JSONB
);
```

### **📋 Sample Data:**
```
┌─────────┬─────────────────────┬─────────────────┬─────────────────────────────────────┬─────────────────────┐
│ id      │ threat_assessment_id│ alert_level     │ title                               │ delivery_channels   │
├─────────┼─────────────────────┼─────────────────┼─────────────────────────────────────┼─────────────────────┤
│ alt_001 │ thr_001            │ HIGH            │ Armed Conflict Risk - Northwest     │ ["email", "sms",    │
│         │                     │                 │ Region                              │  "whatsapp"]        │
│ alt_002 │ thr_002            │ MEDIUM          │ Civil Unrest Detected - Douala     │ ["email"]           │
│ alt_003 │ thr_004            │ CRITICAL        │ URGENT: Political Violence - Yaoundé│ ["email", "sms",    │
│         │                     │                 │                                     │  "whatsapp", "call"]│
└─────────┴─────────────────────┴─────────────────┴─────────────────────────────────────┴─────────────────────┘

Message Content Sample:
"🚨 HIGH ALERT - Northwest Region
THREAT: Armed Conflict Risk
LOCATION: Bamenda and surrounding areas
CONFIDENCE: 87%
RECOMMENDED ACTION: Diplomatic mediation with community leaders
TIMELINE: Immediate response required
ANALYST: Verified by Intelligence Team
REFERENCE: TH-2024-001"

Recipients Sample:
{
    "analysts": ["john.doe@security.gov.cm", "marie.paul@defense.cm"],
    "field_ops": ["+237123456789", "+237987654321"],
    "decision_makers": ["minister@defense.cm", "governor@northwest.cm"]
}
```

### **📞 `communication_log` Table**
```sql
CREATE TABLE communication_log (
    id              UUID PRIMARY KEY,
    alert_id        UUID REFERENCES alerts(id),
    channel_type    VARCHAR(20),
    recipient       VARCHAR(100),
    status          VARCHAR(20),
    sent_at         TIMESTAMP,
    delivered_at    TIMESTAMP,
    acknowledged_at TIMESTAMP,
    error_message   TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### **📋 Sample Data:**
```
┌─────────┬─────────┬─────────────────┬─────────────────────────┬─────────────────┬─────────────────────┐
│ id      │ alert_id│ channel_type    │ recipient               │ status          │ acknowledged_at     │
├─────────┼─────────┼─────────────────┼─────────────────────────┼─────────────────┼─────────────────────┤
│ log_001 │ alt_001 │ EMAIL          │ john.doe@security.gov.cm │ ACKNOWLEDGED    │ 2024-01-15 15:05:00 │
│ log_002 │ alt_001 │ SMS            │ +237123456789           │ DELIVERED       │ NULL                │
│ log_003 │ alt_001 │ WHATSAPP       │ +237987654321           │ ACKNOWLEDGED    │ 2024-01-15 15:12:00 │
│ log_004 │ alt_003 │ EMAIL          │ minister@defense.cm     │ ACKNOWLEDGED    │ 2024-01-15 15:01:00 │
│ log_005 │ alt_003 │ SMS            │ +237111222333           │ FAILED          │ NULL                │
└─────────┴─────────┴─────────────────┴─────────────────────────┴─────────────────┴─────────────────────┘
```

---

## **DATABASE LAYER 8: USER MANAGEMENT**

### **👥 `users` Table**
```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    password_hash   VARCHAR(255),
    role            VARCHAR(30),
    full_name       VARCHAR(100),
    department      VARCHAR(50),
    region_access   JSONB,
    is_active       BOOLEAN DEFAULT true,
    last_login      TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### **📋 Sample Data:**
```
┌─────────────────┬─────────────────┬─────────────────────────┬─────────────────┬─────────────────┬─────────────────────┐
│ id              │ username        │ email                   │ role            │ full_name       │ department          │
├─────────────────┼─────────────────┼─────────────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│ analyst_john    │ john.analyst    │ john.doe@security.gov.cm│ ANALYST         │ John Doe        │ Intelligence Unit   │
│ analyst_marie   │ marie.analyst   │ marie.paul@defense.cm  │ ANALYST         │ Marie Paul      │ Regional Analysis   │
│ field_op_001    │ field.nw.001   │ field1@northwest.cm     │ FIELD_OPERATOR  │ Paul Kamdem     │ Northwest Command   │
│ decision_001    │ minister.def    │ minister@defense.cm     │ DECISION_MAKER  │ Hon. Minister   │ Defense Ministry    │
│ admin_001       │ sys.admin       │ admin@harmony.cm        │ SYSTEM_ADMIN    │ Tech Admin      │ IT Department       │
└─────────────────┴─────────────────┴─────────────────────────┴─────────────────┴─────────────────┴─────────────────────┘

Region Access Sample:
{
    "regions": ["Northwest", "Southwest"],
    "clearance_level": "HIGH",
    "special_permissions": ["view_classified", "approve_interventions"]
}
```

---

## **🗺️ DATABASE RELATIONSHIPS VISUALIZATION**

```
RAW ARTICLES ──────────────────────┐
    │                              │
    │ (1:1)                        │
    ▼                              │
ARTICLES ──────┐                   │
    │          │                   │
    │ (1:N)    │ (1:1)             │
    ▼          ▼                   │
ENTITIES   SENTIMENT               │
    │      ANALYSIS                │
    │          │                   │
    │ (1:1)    │ (1:1)             │
    ▼          ▼                   │
GEOSPATIAL ── THREAT_ASSESSMENTS ──┤
DATA           │                   │
               │ (1:N)             │
               ▼                   │
        VERIFICATION_RESULTS       │
               │                   │
               │ (1:N)             │
               ▼                   │
    INTERVENTION_RECOMMENDATIONS   │
               │                   │
               │ (1:N)             │
               ▼                   │
           ALERTS ─────────────────┤
               │                   │
               │ (1:N)             │
               ▼                   │
       COMMUNICATION_LOG           │
                                   │
SOURCES ───────────────────────────┘
    │
    │ (1:N)
    ▼
 USERS ←──── (verification, decisions, administration)
```

---

## **💾 STORAGE STATISTICS (Typical Daily Volume)**

```
┌─────────────────────────────┬──────────────┬─────────────────┬─────────────────────┐
│ Table                       │ Daily Inserts│ Storage/Day     │ Retention Period    │
├─────────────────────────────┼──────────────┼─────────────────┼─────────────────────┤
│ raw_articles                │ 1,200        │ 50 MB           │ 30 days             │
│ articles                    │ 1,000        │ 25 MB           │ 5 years             │
│ entities                    │ 3,500        │ 2 MB            │ 5 years             │
│ sentiment_analysis          │ 1,000        │ 1 MB            │ 5 years             │
│ geospatial_data            │ 800          │ 3 MB            │ 5 years             │
│ threat_assessments         │ 150          │ 5 MB            │ 10 years            │
│ conflict_predictions       │ 30           │ 1 MB            │ 10 years            │
│ verification_results       │ 50           │ 2 MB            │ 10 years            │
│ intervention_recommendations│ 20           │ 1 MB            │ 10 years            │
│ alerts                     │ 15           │ 2 MB            │ 5 years             │
│ communication_log          │ 200          │ 1 MB            │ 2 years             │
├─────────────────────────────┼──────────────┼─────────────────┼─────────────────────┤
│ TOTAL DAILY                │ 6,965 rows   │ 91 MB           │ Multi-tier archive  │
└─────────────────────────────┴──────────────┴─────────────────┴─────────────────────┘
```

---

## **🔍 KEY INSIGHTS FOR DEFENSE:**

### **Why This Database Design?**

1. **LAYERED STORAGE**: Raw → Processed → Analyzed → Verified → Actionable
2. **AUDIT TRAIL**: Complete traceability from source to decision
3. **SCALABILITY**: Partitioned tables, indexed for fast queries
4. **RELIABILITY**: Foreign key constraints ensure data integrity
5. **FLEXIBILITY**: JSONB fields for evolving requirements

### **Performance Optimizations:**
- **Indexes** on frequently queried columns (region, date, threat_level)
- **Partitioning** by date for time-series data  
- **Caching** of recent predictions in Redis
- **Archiving** of old raw data to reduce active dataset size

**Now you can see exactly where every piece of data lives and how it flows through your system! This gives you complete mastery for your defense! 🎯**
