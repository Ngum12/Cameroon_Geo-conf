/**
 * Formatting utilities for Project Sentinel Dashboard
 * Contains helper functions for data formatting, date handling, and text processing
 */

import { format, formatDistanceToNow, parseISO, isValid } from 'date-fns';

/**
 * Format date for display in various contexts
 */
export const formatDate = (
  dateString: string | null, 
  formatType: 'short' | 'long' | 'time' | 'relative' = 'short'
): string => {
  if (!dateString) return 'Unknown date';
  
  try {
    const date = parseISO(dateString);
    
    if (!isValid(date)) {
      return 'Invalid date';
    }
    
    switch (formatType) {
      case 'short':
        return format(date, 'MMM dd, yyyy');
      case 'long':
        return format(date, 'MMMM dd, yyyy \'at\' HH:mm');
      case 'time':
        return format(date, 'HH:mm');
      case 'relative':
        return formatDistanceToNow(date, { addSuffix: true });
      default:
        return format(date, 'MMM dd, yyyy');
    }
  } catch (error) {
    console.warn('Error formatting date:', dateString, error);
    return 'Invalid date';
  }
};

/**
 * Format priority level for display
 */
export const formatPriority = (priority: number): string => {
  const priorityMap: Record<number, string> = {
    1: 'Critical',
    2: 'High',
    3: 'Medium',
    4: 'Low',
  };
  
  return priorityMap[priority] || 'Unknown';
};

/**
 * Format classification level for display
 */
export const formatClassification = (classification: string): string => {
  return classification.replace(/_/g, ' ').toUpperCase();
};

/**
 * Format entity count with proper pluralization
 */
export const formatEntityCount = (count: number, entityType?: string): string => {
  if (count === 0) return `No ${entityType || 'entities'}`;
  if (count === 1) return `1 ${entityType || 'entity'}`;
  
  const pluralType = entityType ? `${entityType}s` : 'entities';
  return `${count} ${pluralType}`;
};

/**
 * Format file size in human readable format
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

/**
 * Format content length (character count)
 */
export const formatContentLength = (length: number): string => {
  if (length < 1000) return `${length} chars`;
  if (length < 1000000) return `${(length / 1000).toFixed(1)}K chars`;
  return `${(length / 1000000).toFixed(1)}M chars`;
};

/**
 * Format word count
 */
export const formatWordCount = (count: number): string => {
  if (count < 1000) return `${count} words`;
  if (count < 1000000) return `${(count / 1000).toFixed(1)}K words`;
  return `${(count / 1000000).toFixed(1)}M words`;
};

/**
 * Truncate text with ellipsis
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
};

/**
 * Extract domain from URL
 */
export const extractDomain = (url: string): string => {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname.replace('www.', '');
  } catch {
    return url;
  }
};

/**
 * Format URL for display (shortened)
 */
export const formatUrl = (url: string, maxLength: number = 50): string => {
  try {
    const urlObj = new URL(url);
    const domain = urlObj.hostname.replace('www.', '');
    const path = urlObj.pathname + urlObj.search;
    
    const fullUrl = `${domain}${path}`;
    
    if (fullUrl.length <= maxLength) return fullUrl;
    
    const availableLength = maxLength - 3; // Reserve 3 chars for "..."
    const domainLength = domain.length;
    
    if (domainLength >= availableLength) {
      return truncateText(domain, availableLength);
    }
    
    const pathLength = availableLength - domainLength;
    const truncatedPath = truncateText(path, pathLength);
    
    return `${domain}${truncatedPath}`;
  } catch {
    return truncateText(url, maxLength);
  }
};

/**
 * Format confidence score as percentage
 */
export const formatConfidence = (confidence: number): string => {
  return `${(confidence * 100).toFixed(1)}%`;
};

/**
 * Capitalize first letter of each word
 */
export const capitalizeWords = (text: string): string => {
  return text.replace(/\b\w/g, (char) => char.toUpperCase());
};

/**
 * Format processing time in human readable format
 */
export const formatProcessingTime = (seconds: number): string => {
  if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  if (minutes < 60) {
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  return `${hours}h ${remainingMinutes}m`;
};

/**
 * Format number with thousands separator
 */
export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-US').format(num);
};

/**
 * Format percentage with one decimal place
 */
export const formatPercentage = (value: number, total: number): string => {
  if (total === 0) return '0.0%';
  const percentage = (value / total) * 100;
  return `${percentage.toFixed(1)}%`;
};

/**
 * Format language code to human readable name
 */
export const formatLanguage = (langCode: string): string => {
  const languageNames: Record<string, string> = {
    'en': 'English',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'pt': 'Portuguese',
    'ar': 'Arabic',
    'auto': 'Auto-detected',
    'unknown': 'Unknown',
  };
  
  return languageNames[langCode] || langCode.toUpperCase();
};

/**
 * Clean and format article title
 */
export const cleanTitle = (title: string): string => {
  // Remove extra whitespace
  let cleaned = title.replace(/\s+/g, ' ').trim();
  
  // Remove common prefixes that might be added by scrapers
  const prefixesToRemove = [
    /^(.*?)\s*-\s*Cameroon Tribune/i,
    /^(.*?)\s*-\s*Journal du Cameroun/i,
    /^(.*?)\s*\|\s*.*$/i,
  ];
  
  prefixesToRemove.forEach(regex => {
    const match = cleaned.match(regex);
    if (match && match[1]) {
      cleaned = match[1].trim();
    }
  });
  
  return cleaned;
};

/**
 * Extract and format location from entities
 */
export const extractPrimaryLocation = (entities: { locations: string[] }): string | null => {
  if (!entities.locations || entities.locations.length === 0) return null;
  
  // Cameroon locations (prioritize these)
  const cameroonLocations = [
    'yaoundé', 'yaounde', 'douala', 'bamenda', 'bafoussam', 'garoua',
    'maroua', 'ngaoundéré', 'bertoua', 'buea', 'limbe', 'kumba'
  ];
  
  // Find Cameroonian location first
  const cameroonLocation = entities.locations.find(location =>
    cameroonLocations.some(city => 
      location.toLowerCase().includes(city) || city.includes(location.toLowerCase())
    )
  );
  
  if (cameroonLocation) return capitalizeWords(cameroonLocation);
  
  // Return first location if no Cameroonian location found
  return capitalizeWords(entities.locations[0]);
};

/**
 * Create search highlight HTML
 */
export const highlightSearchTerm = (text: string, searchTerm: string): string => {
  if (!searchTerm || !text) return text;
  
  const regex = new RegExp(`(${searchTerm})`, 'gi');
  return text.replace(regex, '<mark style="background-color: #ffc107; padding: 0 2px;">$1</mark>');
};

/**
 * Generate random color for visualization
 */
export const generateRandomColor = (seed?: string): string => {
  if (seed) {
    // Generate deterministic color based on seed
    let hash = 0;
    for (let i = 0; i < seed.length; i++) {
      hash = seed.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    const hue = hash % 360;
    return `hsl(${hue}, 70%, 50%)`;
  }
  
  // Random color
  const hue = Math.floor(Math.random() * 360);
  return `hsl(${hue}, 70%, 50%)`;
};

export default {
  formatDate,
  formatPriority,
  formatClassification,
  formatEntityCount,
  formatFileSize,
  formatContentLength,
  formatWordCount,
  truncateText,
  extractDomain,
  formatUrl,
  formatConfidence,
  capitalizeWords,
  formatProcessingTime,
  formatNumber,
  formatPercentage,
  formatLanguage,
  cleanTitle,
  extractPrimaryLocation,
  highlightSearchTerm,
  generateRandomColor,
};
