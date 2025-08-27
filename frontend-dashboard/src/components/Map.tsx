/**
 * Interactive Map Component for Project Sentinel Dashboard
 * Displays OSINT intelligence data on Mapbox map centered on Cameroon
 */

import React, { useState, useCallback, useEffect, useMemo } from 'react';
import Map, { 
  Marker, 
  Popup, 
  NavigationControl, 
  FullscreenControl, 
  ScaleControl,
  MapRef 
} from 'react-map-gl';
import { Box, CircularProgress, Alert, Fab, Tooltip } from '@mui/material';
import { Refresh as RefreshIcon, MyLocation as MyLocationIcon } from '@mui/icons-material';

import { EventsGeoJSON, GeoJSONFeature, ViewState, ArticleProperties } from '../types';
import { 
  DEFAULT_VIEW_STATE, 
  MAPBOX_STYLE, 
  getMarkerColor, 
  getMarkerSize, 
  classifyEventType,
  calculateBounds,
  createMapBounds 
} from '../utils/mapUtils';
import PopupContent from './PopupContent';
import MarkerCluster from './MarkerCluster';

// Mapbox access token - should be set in environment variables
const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN || 'pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjazA0a2ZkNGowNm4wM3FuZDN5NmNqNm8yIn0.dummy_token';

interface MapComponentProps {
  events: EventsGeoJSON | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
  className?: string;
}

const MapComponent: React.FC<MapComponentProps> = ({
  events,
  loading,
  error,
  onRefresh,
  className = '',
}) => {
  // Map state
  const [viewState, setViewState] = useState<ViewState>(DEFAULT_VIEW_STATE);
  const [selectedMarker, setSelectedMarker] = useState<GeoJSONFeature | null>(null);
  const [mapRef, setMapRef] = useState<MapRef | null>(null);
  const [showClustering, setShowClustering] = useState(true);

  // Memoized features for performance
  const features = useMemo(() => {
    return events?.features || [];
  }, [events]);

  // Calculate optimal view state when features change
  useEffect(() => {
    if (features.length > 0 && mapRef) {
      const coordinates = features.map(feature => feature.geometry.coordinates as [number, number]);
      const bounds = calculateBounds(coordinates);
      const mapBounds = createMapBounds(bounds);
      
      // Fit bounds with padding
      mapRef.fitBounds(mapBounds, {
        padding: { top: 50, bottom: 50, left: 50, right: 50 },
        duration: 1000
      });
    }
  }, [features, mapRef]);

  // Handle map click to close popup
  const handleMapClick = useCallback(() => {
    setSelectedMarker(null);
  }, []);

  // Handle marker click
  const handleMarkerClick = useCallback((feature: GeoJSONFeature) => {
    setSelectedMarker(feature);
  }, []);

  // Handle popup close
  const handlePopupClose = useCallback(() => {
    setSelectedMarker(null);
  }, []);

  // Recenter map to Cameroon
  const handleRecenter = useCallback(() => {
    setViewState(DEFAULT_VIEW_STATE);
  }, []);

  // Toggle clustering
  const handleToggleClustering = useCallback(() => {
    setShowClustering(prev => !prev);
  }, []);

  // Render individual marker
  const renderMarker = useCallback((feature: GeoJSONFeature) => {
    const { geometry, properties } = feature;
    const [longitude, latitude] = geometry.coordinates;
    
    const eventType = classifyEventType(properties);
    const markerColor = getMarkerColor(properties.priority, eventType);
    const markerSize = getMarkerSize(properties.priority, properties.entity_count);
    
    return (
      <Marker
        key={properties.id}
        longitude={longitude}
        latitude={latitude}
        onClick={(e) => {
          e.originalEvent.stopPropagation();
          handleMarkerClick(feature);
        }}
        style={{ cursor: 'pointer' }}
      >
        <Box
          sx={{
            width: markerSize,
            height: markerSize,
            backgroundColor: markerColor,
            borderRadius: '50%',
            border: '2px solid rgba(255, 255, 255, 0.8)',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: markerSize > 24 ? '12px' : '10px',
            fontWeight: 'bold',
            color: 'white',
            position: 'relative',
            '&:hover': {
              transform: 'scale(1.1)',
              boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)',
            },
            transition: 'all 0.2s ease-in-out',
          }}
        >
          {properties.priority}
          
          {/* Pulse animation for critical events */}
          {properties.priority === 1 && (
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                borderRadius: '50%',
                backgroundColor: markerColor,
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%': {
                    transform: 'scale(1)',
                    opacity: 1,
                  },
                  '100%': {
                    transform: 'scale(2)',
                    opacity: 0,
                  },
                },
              }}
            />
          )}
        </Box>
      </Marker>
    );
  }, [handleMarkerClick]);

  // Render all markers
  const markers = useMemo(() => {
    if (!features.length) return null;
    
    if (showClustering && features.length > 50) {
      return <MarkerCluster features={features} onMarkerClick={handleMarkerClick} />;
    }
    
    return features.map(renderMarker);
  }, [features, showClustering, renderMarker, handleMarkerClick]);

  // Error state
  if (error) {
    return (
      <Box 
        className={className}
        sx={{ 
          width: '100%', 
          height: '100%', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          backgroundColor: '#0f0f0f'
        }}
      >
        <Alert 
          severity="error" 
          sx={{ maxWidth: 400 }}
          action={
            <Fab
              size="small"
              color="primary"
              onClick={onRefresh}
              sx={{ ml: 2 }}
            >
              <RefreshIcon />
            </Fab>
          }
        >
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box 
      className={className}
      sx={{ 
        width: '100%', 
        height: '100%', 
        position: 'relative',
        '& .mapboxgl-canvas': {
          outline: 'none',
        },
        '& .mapboxgl-control-container': {
          '& .mapboxgl-ctrl': {
            backgroundColor: 'rgba(26, 26, 26, 0.8)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          },
          '& button': {
            backgroundColor: 'transparent',
            color: 'white',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
            },
          },
        },
      }}
    >
      {/* Loading overlay */}
      {loading && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
        >
          <Box sx={{ textAlign: 'center', color: 'white' }}>
            <CircularProgress size={48} sx={{ mb: 2 }} />
            <Box sx={{ typography: 'body1' }}>Loading intelligence data...</Box>
          </Box>
        </Box>
      )}

      {/* Map */}
      <Map
        ref={setMapRef}
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        onClick={handleMapClick}
        mapStyle={MAPBOX_STYLE}
        mapboxAccessToken={MAPBOX_TOKEN}
        style={{ width: '100%', height: '100%' }}
        attributionControl={false}
        logoPosition="bottom-left"
        maxZoom={18}
        minZoom={4}
        maxBounds={[
          [8.0, 1.5], // Southwest coordinates of Cameroon
          [16.5, 13.5] // Northeast coordinates of Cameroon
        ]}
      >
        {/* Map controls */}
        <NavigationControl position="top-right" showCompass showZoom />
        <FullscreenControl position="top-right" />
        <ScaleControl position="bottom-right" maxWidth={100} unit="metric" />

        {/* Markers */}
        {markers}

        {/* Selected marker popup */}
        {selectedMarker && (
          <Popup
            longitude={selectedMarker.geometry.coordinates[0]}
            latitude={selectedMarker.geometry.coordinates[1]}
            onClose={handlePopupClose}
            closeButton={true}
            closeOnClick={false}
            anchor="bottom"
            maxWidth="400px"
            className="sentinel-popup"
            style={{
              zIndex: 1001,
            }}
          >
            <PopupContent 
              article={selectedMarker.properties} 
              onClose={handlePopupClose}
            />
          </Popup>
        )}
      </Map>

      {/* Action buttons */}
      <Box
        sx={{
          position: 'absolute',
          bottom: 80,
          right: 16,
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
          zIndex: 1000,
        }}
      >
        {/* Refresh data button */}
        <Tooltip title="Refresh data" placement="left">
          <Fab
            size="small"
            color="primary"
            onClick={onRefresh}
            disabled={loading}
            sx={{
              backgroundColor: 'rgba(26, 26, 26, 0.9)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              '&:hover': {
                backgroundColor: 'rgba(0, 123, 255, 0.8)',
              },
            }}
          >
            <RefreshIcon />
          </Fab>
        </Tooltip>

        {/* Recenter button */}
        <Tooltip title="Center on Cameroon" placement="left">
          <Fab
            size="small"
            onClick={handleRecenter}
            sx={{
              backgroundColor: 'rgba(26, 26, 26, 0.9)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            <MyLocationIcon />
          </Fab>
        </Tooltip>
      </Box>

      {/* Data summary */}
      <Box
        sx={{
          position: 'absolute',
          top: 16,
          left: 16,
          backgroundColor: 'rgba(26, 26, 26, 0.9)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 2,
          padding: 2,
          color: 'white',
          minWidth: 200,
          zIndex: 1000,
        }}
      >
        <Box sx={{ typography: 'h6', mb: 1 }}>PROJECT SENTINEL</Box>
        <Box sx={{ typography: 'body2', opacity: 0.8 }}>
          {features.length} intelligence reports
        </Box>
        {events?.metadata && (
          <Box sx={{ typography: 'caption', opacity: 0.6 }}>
            Updated: {new Date(events.metadata.generated_at).toLocaleTimeString()}
          </Box>
        )}
      </Box>

      {/* Custom CSS for popup styling */}
      <style>
        {`
          .sentinel-popup .mapboxgl-popup-content {
            background-color: #1a1a1a !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important;
            backdrop-filter: blur(10px) !important;
            max-width: 400px !important;
            max-height: 300px !important;
            overflow-y: auto !important;
          }
          
          .sentinel-popup .mapboxgl-popup-close-button {
            color: white !important;
            font-size: 20px !important;
            padding: 4px 8px !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
            border-radius: 50% !important;
            width: 28px !important;
            height: 28px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
          }
          
          .sentinel-popup .mapboxgl-popup-close-button:hover {
            background-color: rgba(255, 255, 255, 0.2) !important;
          }
          
          .sentinel-popup .mapboxgl-popup-tip {
            border-top-color: #1a1a1a !important;
          }
        `}
      </style>
    </Box>
  );
};

export default MapComponent;
