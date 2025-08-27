/**
 * Marker Clustering Component
 * Groups nearby markers to improve performance and readability
 */

import React, { useMemo } from 'react';
import { Marker } from 'react-map-gl';
import { Box } from '@mui/material';
import { GeoJSONFeature } from '../types';

interface MarkerClusterProps {
  features: GeoJSONFeature[];
  onMarkerClick: (feature: GeoJSONFeature) => void;
}

interface ClusterPoint {
  features: GeoJSONFeature[];
  center: [number, number];
  count: number;
}

// Simple clustering algorithm based on distance
const clusterFeatures = (features: GeoJSONFeature[], zoom: number): ClusterPoint[] => {
  const clusters: ClusterPoint[] = [];
  const processed = new Set<number>();
  
  // Adjust cluster distance based on zoom level
  const clusterDistance = Math.max(0.1, 2 / Math.pow(2, zoom - 4));
  
  features.forEach((feature, index) => {
    if (processed.has(index)) return;
    
    const [lng, lat] = feature.geometry.coordinates;
    const cluster: ClusterPoint = {
      features: [feature],
      center: [lng, lat],
      count: 1
    };
    
    processed.add(index);
    
    // Find nearby features to cluster
    features.forEach((otherFeature, otherIndex) => {
      if (processed.has(otherIndex)) return;
      
      const [otherLng, otherLat] = otherFeature.geometry.coordinates;
      const distance = Math.sqrt(
        Math.pow(lng - otherLng, 2) + Math.pow(lat - otherLat, 2)
      );
      
      if (distance <= clusterDistance) {
        cluster.features.push(otherFeature);
        cluster.count++;
        processed.add(otherIndex);
        
        // Update cluster center (average position)
        const totalLng = cluster.features.reduce((sum, f) => sum + f.geometry.coordinates[0], 0);
        const totalLat = cluster.features.reduce((sum, f) => sum + f.geometry.coordinates[1], 0);
        cluster.center = [totalLng / cluster.count, totalLat / cluster.count];
      }
    });
    
    clusters.push(cluster);
  });
  
  return clusters;
};

const MarkerCluster: React.FC<MarkerClusterProps> = ({ features, onMarkerClick }) => {
  // For now, use a simple zoom level estimate
  const estimatedZoom = 6;
  
  const clusters = useMemo(() => {
    return clusterFeatures(features, estimatedZoom);
  }, [features, estimatedZoom]);
  
  return (
    <>
      {clusters.map((cluster, index) => {
        const [longitude, latitude] = cluster.center;
        
        if (cluster.count === 1) {
          // Single marker
          const feature = cluster.features[0];
          const priority = feature.properties.priority;
          const markerSize = priority === 1 ? 32 : priority === 2 ? 26 : priority === 3 ? 20 : 16;
          const markerColor = priority === 1 ? '#dc3545' : priority === 2 ? '#fd7e14' : priority === 3 ? '#007bff' : '#6c757d';
          
          return (
            <Marker
              key={`single-${feature.properties.id}`}
              longitude={longitude}
              latitude={latitude}
              onClick={() => onMarkerClick(feature)}
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
                  cursor: 'pointer',
                  '&:hover': {
                    transform: 'scale(1.1)',
                  },
                  transition: 'transform 0.2s ease-in-out',
                }}
              >
                {priority}
              </Box>
            </Marker>
          );
        }
        
        // Cluster marker
        const clusterSize = Math.min(50, 20 + cluster.count * 2);
        const highestPriority = Math.min(...cluster.features.map(f => f.properties.priority));
        const clusterColor = highestPriority === 1 ? '#dc3545' : highestPriority === 2 ? '#fd7e14' : '#007bff';
        
        return (
          <Marker
            key={`cluster-${index}`}
            longitude={longitude}
            latitude={latitude}
            onClick={() => {
              // For clusters, click on the first (highest priority) feature
              const sortedFeatures = cluster.features.sort((a, b) => a.properties.priority - b.properties.priority);
              onMarkerClick(sortedFeatures[0]);
            }}
          >
            <Box
              sx={{
                width: clusterSize,
                height: clusterSize,
                backgroundColor: clusterColor,
                borderRadius: '50%',
                border: '3px solid rgba(255, 255, 255, 0.9)',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '14px',
                fontWeight: 'bold',
                color: 'white',
                cursor: 'pointer',
                position: 'relative',
                '&:hover': {
                  transform: 'scale(1.1)',
                },
                transition: 'transform 0.2s ease-in-out',
              }}
            >
              {cluster.count}
              
              {/* Ring indicator for clusters */}
              <Box
                sx={{
                  position: 'absolute',
                  top: -2,
                  left: -2,
                  right: -2,
                  bottom: -2,
                  borderRadius: '50%',
                  border: `2px solid ${clusterColor}`,
                  opacity: 0.5,
                }}
              />
            </Box>
          </Marker>
        );
      })}
    </>
  );
};

export default MarkerCluster;
