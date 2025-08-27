/**
 * Map utilities for Project Sentinel Dashboard
 * Contains helper functions for map operations, styling, and data processing
 */

import { EventType, PriorityConfig, PRIORITY_CONFIGS, ArticleProperties } from '../types';

// Cameroon coordinates and bounds
export const CAMEROON_CENTER = {
  latitude: 7.3697,
  longitude: 12.3547,
};

export const CAMEROON_BOUNDS = {
  north: 13.0833,
  south: 1.6667,
  east: 16.1833,
  west: 8.4833,
};

// Default map view state centered on Cameroon
export const DEFAULT_VIEW_STATE = {
  longitude: CAMEROON_CENTER.longitude,
  latitude: CAMEROON_CENTER.latitude,
  zoom: 6.5,
  bearing: 0,
  pitch: 0,
};

// Mapbox style URL for dark theme optimized for command centers
export const MAPBOX_STYLE = 'mapbox://styles/mapbox/dark-v11';

// Alternative styles for different use cases
export const MAP_STYLES = {
  dark: 'mapbox://styles/mapbox/dark-v11',
  satellite: 'mapbox://styles/mapbox/satellite-streets-v12',
  streets: 'mapbox://styles/mapbox/streets-v12',
  navigation: 'mapbox://styles/mapbox/navigation-night-v1',
};

/**
 * Classify event type based on article content and entities
 */
export const classifyEventType = (article: ArticleProperties): EventType => {
  const { title, entities, text_preview } = article;
  
  // Combine text sources for analysis
  const textToAnalyze = `${title} ${text_preview || ''}`.toLowerCase();
  
  // Extract entity words for analysis
  const entityWords = entities ? [
    ...entities.persons,
    ...entities.locations,
    ...entities.organizations
  ].map(word => word.toLowerCase()) : [];
  
  const allText = `${textToAnalyze} ${entityWords.join(' ')}`;
  
  // Keywords for event classification
  const eventKeywords = {
    Armed_Clash: [
      'attack', 'clash', 'fighting', 'combat', 'battle', 'conflict',
      'armed', 'violence', 'shoot', 'bomb', 'explosion', 'terrorist',
      'boko haram', 'ambush', 'raid', 'assault', 'militant'
    ],
    Security_Operation: [
      'operation', 'security', 'military', 'army', 'police', 'patrol',
      'deployment', 'mission', 'peacekeeping', 'enforcement',
      'rapid intervention battalion', 'gendarmerie'
    ],
    Political_Event: [
      'president', 'government', 'ministry', 'minister', 'election',
      'political', 'parliament', 'policy', 'diplomacy', 'summit',
      'paul biya', 'prime minister', 'cabinet'
    ],
    Economic_News: [
      'economy', 'economic', 'business', 'trade', 'investment', 'bank',
      'financial', 'market', 'commerce', 'industry', 'development',
      'gdp', 'inflation', 'employment'
    ],
    Social_Unrest: [
      'protest', 'demonstration', 'strike', 'unrest', 'riot',
      'civil disobedience', 'march', 'rally', 'uprising', 'revolt'
    ],
    Diplomatic_Event: [
      'diplomatic', 'embassy', 'ambassador', 'international',
      'bilateral', 'treaty', 'agreement', 'cooperation',
      'african union', 'united nations', 'un'
    ]
  };
  
  // Score each event type
  const scores: Record<EventType, number> = {
    Armed_Clash: 0,
    Security_Operation: 0,
    Political_Event: 0,
    Economic_News: 0,
    Social_Unrest: 0,
    Diplomatic_Event: 0,
    Other: 0
  };
  
  // Calculate scores based on keyword matches
  Object.entries(eventKeywords).forEach(([eventType, keywords]) => {
    keywords.forEach(keyword => {
      if (allText.includes(keyword)) {
        scores[eventType as EventType] += 1;
        
        // Give extra weight to title matches
        if (title.toLowerCase().includes(keyword)) {
          scores[eventType as EventType] += 2;
        }
      }
    });
  });
  
  // Find the event type with highest score
  const maxScore = Math.max(...Object.values(scores));
  
  if (maxScore === 0) {
    return 'Other';
  }
  
  const topEventType = Object.entries(scores).find(([_, score]) => score === maxScore);
  return topEventType ? topEventType[0] as EventType : 'Other';
};

/**
 * Get marker color based on priority and event type
 */
export const getMarkerColor = (priority: number, eventType?: EventType): string => {
  // Primary color based on priority
  const priorityConfig = PRIORITY_CONFIGS[priority];
  let baseColor = priorityConfig ? priorityConfig.color : '#6c757d';
  
  // Modify color intensity based on event type
  if (eventType) {
    switch (eventType) {
      case 'Armed_Clash':
        baseColor = '#dc3545'; // Always red for armed clashes
        break;
      case 'Security_Operation':
        // Keep priority color but ensure visibility
        break;
      case 'Political_Event':
        baseColor = priority <= 2 ? '#007bff' : baseColor;
        break;
      case 'Economic_News':
        baseColor = '#28a745';
        break;
      case 'Social_Unrest':
        baseColor = '#fd7e14';
        break;
      case 'Diplomatic_Event':
        baseColor = '#6f42c1';
        break;
      default:
        // Keep priority-based color
        break;
    }
  }
  
  return baseColor;
};

/**
 * Get marker size based on priority and entity count
 */
export const getMarkerSize = (priority: number, entityCount: number): number => {
  // Base size based on priority
  let baseSize = 20;
  
  switch (priority) {
    case 1: // Critical
      baseSize = 32;
      break;
    case 2: // High
      baseSize = 26;
      break;
    case 3: // Medium
      baseSize = 20;
      break;
    case 4: // Low
      baseSize = 16;
      break;
    default:
      baseSize = 20;
  }
  
  // Adjust size based on entity count (more entities = larger marker)
  const entityBonus = Math.min(entityCount * 2, 8); // Max 8px bonus
  
  return baseSize + entityBonus;
};

/**
 * Format coordinates for display
 */
export const formatCoordinates = (lng: number, lat: number): string => {
  const formatCoord = (coord: number, isLat: boolean): string => {
    const abs = Math.abs(coord);
    const degrees = Math.floor(abs);
    const minutes = Math.floor((abs - degrees) * 60);
    const seconds = Math.round(((abs - degrees) * 60 - minutes) * 60);
    
    const direction = isLat ? (coord >= 0 ? 'N' : 'S') : (coord >= 0 ? 'E' : 'W');
    
    return `${degrees}°${minutes}'${seconds}"${direction}`;
  };
  
  return `${formatCoord(lat, true)}, ${formatCoord(lng, false)}`;
};

/**
 * Calculate distance between two points in kilometers
 */
export const calculateDistance = (
  lat1: number, 
  lng1: number, 
  lat2: number, 
  lng2: number
): number => {
  const R = 6371; // Earth's radius in kilometers
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  
  return R * c;
};

const toRad = (degrees: number): number => degrees * (Math.PI / 180);

/**
 * Check if coordinates are within Cameroon bounds
 */
export const isWithinCameroon = (lat: number, lng: number): boolean => {
  return (
    lat >= CAMEROON_BOUNDS.south &&
    lat <= CAMEROON_BOUNDS.north &&
    lng >= CAMEROON_BOUNDS.west &&
    lng <= CAMEROON_BOUNDS.east
  );
};

/**
 * Generate bounds that include all features
 */
export const calculateBounds = (coordinates: Array<[number, number]>): {
  west: number;
  east: number;
  north: number;
  south: number;
} => {
  if (coordinates.length === 0) {
    return CAMEROON_BOUNDS;
  }
  
  let west = coordinates[0][0];
  let east = coordinates[0][0];
  let north = coordinates[0][1];
  let south = coordinates[0][1];
  
  coordinates.forEach(([lng, lat]) => {
    west = Math.min(west, lng);
    east = Math.max(east, lng);
    north = Math.max(north, lat);
    south = Math.min(south, lat);
  });
  
  // Add padding
  const padding = 0.1;
  return {
    west: west - padding,
    east: east + padding,
    north: north + padding,
    south: south - padding,
  };
};

/**
 * Create map bounds object for react-map-gl
 */
export const createMapBounds = (bounds: {
  west: number;
  east: number;
  north: number;
  south: number;
}): [[number, number], [number, number]] => {
  return [
    [bounds.west, bounds.south],
    [bounds.east, bounds.north]
  ];
};

/**
 * Get zoom level based on the number of features
 */
export const getOptimalZoom = (featureCount: number): number => {
  if (featureCount === 0) return DEFAULT_VIEW_STATE.zoom;
  if (featureCount === 1) return 10;
  if (featureCount <= 5) return 8;
  if (featureCount <= 20) return 7;
  return 6;
};

export default {
  CAMEROON_CENTER,
  CAMEROON_BOUNDS,
  DEFAULT_VIEW_STATE,
  MAPBOX_STYLE,
  MAP_STYLES,
  classifyEventType,
  getMarkerColor,
  getMarkerSize,
  formatCoordinates,
  calculateDistance,
  isWithinCameroon,
  calculateBounds,
  createMapBounds,
  getOptimalZoom,
};
