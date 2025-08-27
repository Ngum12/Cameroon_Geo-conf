/**
 * TypeScript type definitions for Project Sentinel Dashboard
 * Cameroon Defense Force OSINT Analysis System
 */

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface EntityData {
  word: string;
  entity_group: 'PERSON' | 'LOCATION' | 'ORGANIZATION' | 'MISCELLANEOUS';
  confidence: number;
  start: number;
  end: number;
}

export interface ProcessedEntities {
  persons: string[];
  locations: string[];
  organizations: string[];
}

export interface ArticleProperties {
  id: string;
  title: string;
  source: string;
  url: string;
  published_date: string | null;
  created_at: string;
  priority: 1 | 2 | 3 | 4; // 1=Critical, 2=High, 3=Medium, 4=Low
  classification: 'UNCLASSIFIED' | 'RESTRICTED' | 'CONFIDENTIAL' | 'SECRET';
  language: string;
  entity_count: number;
  content_length: number;
  word_count: number;
  entities?: ProcessedEntities;
  text_preview?: string;
}

export interface GeoJSONFeature {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number]; // [longitude, latitude]
  };
  properties: ArticleProperties;
}

export interface EventsGeoJSON {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
  metadata: {
    total_features: number;
    generated_at: string;
    query_parameters: {
      limit: number;
      days: number;
      source?: string;
      priority?: number;
    };
  };
}

export interface NewsArticle {
  id: string;
  url: string;
  title: string;
  source: string;
  raw_text: string;
  processed_json: Record<string, any>;
  published_date: string | null;
  location: {
    type: 'Point';
    coordinates: [number, number];
  } | null;
  coordinates: Coordinates | null;
  language: string;
  classification: string;
  priority: number;
  processing_status: 'pending' | 'translating' | 'extracting_entities' | 'processed' | 'failed';
  created_at: string;
  updated_at: string;
  sentiment_score: number | null;
  entity_count: number;
  relevance_score: number | null;
  content_length: number;
  word_count: number;
  translated_text: string;
  entities: EntityData[];
  person_entities: EntityData[];
  location_entities: EntityData[];
  organization_entities: EntityData[];
}

export interface SystemStatistics {
  overview: {
    total_articles: number;
    processed_articles: number;
    pending_articles: number;
    failed_articles: number;
    located_articles: number;
    recent_articles_24h: number;
  };
  by_source: Array<{
    source: string;
    count: number;
  }>;
  by_priority: Array<{
    priority: number;
    count: number;
  }>;
  by_status: Array<{
    processing_status: string;
    count: number;
  }>;
  generated_at: string;
}

export interface ProcessingResponse {
  success: boolean;
  message: string;
  article: NewsArticle;
  processing_results?: {
    translation?: {
      translated_text: string;
      detected_language: string;
      processing_time: number;
    };
    entities?: {
      entities: EntityData[];
      entity_count: number;
      processing_time: number;
    };
  };
  error?: string;
  article_id?: string;
}

// Event type classifications for marker styling
export type EventType = 
  | 'Armed_Clash' 
  | 'Security_Operation' 
  | 'Political_Event' 
  | 'Economic_News' 
  | 'Social_Unrest' 
  | 'Diplomatic_Event'
  | 'Other';

// Priority levels with colors
export interface PriorityConfig {
  level: number;
  label: string;
  color: string;
  description: string;
}

export const PRIORITY_CONFIGS: Record<number, PriorityConfig> = {
  1: {
    level: 1,
    label: 'Critical',
    color: '#dc3545',
    description: 'Requires immediate attention'
  },
  2: {
    level: 2,
    label: 'High',
    color: '#fd7e14',
    description: 'High priority for analysis'
  },
  3: {
    level: 3,
    label: 'Medium',
    color: '#007bff',
    description: 'Standard priority'
  },
  4: {
    level: 4,
    label: 'Low',
    color: '#6c757d',
    description: 'Low priority or routine'
  }
};

// Classification levels with colors
export interface ClassificationConfig {
  level: string;
  color: string;
  description: string;
}

export const CLASSIFICATION_CONFIGS: Record<string, ClassificationConfig> = {
  'UNCLASSIFIED': {
    level: 'UNCLASSIFIED',
    color: '#28a745',
    description: 'Public information'
  },
  'RESTRICTED': {
    level: 'RESTRICTED',
    color: '#007bff',
    description: 'Limited distribution'
  },
  'CONFIDENTIAL': {
    level: 'CONFIDENTIAL',
    color: '#ffc107',
    description: 'Sensitive information'
  },
  'SECRET': {
    level: 'SECRET',
    color: '#dc3545',
    description: 'Highly sensitive information'
  }
};

// Map view states
export interface ViewState {
  longitude: number;
  latitude: number;
  zoom: number;
  bearing?: number;
  pitch?: number;
}

// Filter options
export interface FilterOptions {
  dateRange: {
    start: Date | null;
    end: Date | null;
  };
  sources: string[];
  priorities: number[];
  classifications: string[];
  showOnly: {
    withLocation: boolean;
    processed: boolean;
  };
}

// API Error types
export interface APIError {
  error: string;
  details?: string;
  status: number;
}

// Component props interfaces
export interface MapComponentProps {
  events: EventsGeoJSON | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
  filters: FilterOptions;
  onFilterChange: (filters: FilterOptions) => void;
}

export interface SidebarProps {
  statistics: SystemStatistics | null;
  filters: FilterOptions;
  onFilterChange: (filters: FilterOptions) => void;
  onRefresh: () => void;
  loading: boolean;
}

export interface PopupContentProps {
  article: ArticleProperties;
  onClose: () => void;
}
