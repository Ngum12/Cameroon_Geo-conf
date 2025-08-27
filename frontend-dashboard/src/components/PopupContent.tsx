/**
 * Popup Content Component for Map Markers
 * Displays article information when marker is clicked
 */

import React from 'react';
import {
  Box,
  Typography,
  Chip,
  Button,
  Divider,
  IconButton,
  Link,
} from '@mui/material';
import {
  OpenInNew as OpenInNewIcon,
  Person as PersonIcon,
  LocationOn as LocationIcon,
  Business as BusinessIcon,
  Close as CloseIcon,
} from '@mui/icons-material';

import { PopupContentProps } from '../types';
import { 
  formatDate, 
  formatPriority, 
  formatClassification, 
  truncateText, 
  extractDomain,
  extractPrimaryLocation 
} from '../utils/formatUtils';
import { getMarkerColor, classifyEventType } from '../utils/mapUtils';

const PopupContent: React.FC<PopupContentProps> = ({ article, onClose }) => {
  const eventType = classifyEventType(article);
  const priorityColor = getMarkerColor(article.priority, eventType);
  const primaryLocation = extractPrimaryLocation(article.entities || { persons: [], locations: [], organizations: [] });

  const handleLinkClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    window.open(article.url, '_blank', 'noopener,noreferrer');
  };

  return (
    <Box sx={{ p: 0, maxWidth: 380, color: 'white' }}>
      {/* Header with close button */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'flex-start',
        mb: 2 
      }}>
        <Box sx={{ flex: 1, pr: 1 }}>
          <Typography 
            variant="h6" 
            sx={{ 
              fontSize: '1rem',
              fontWeight: 600,
              lineHeight: 1.3,
              mb: 1,
              color: 'white'
            }}
          >
            {truncateText(article.title, 80)}
          </Typography>
          
          {/* Priority and classification badges */}
          <Box sx={{ display: 'flex', gap: 1, mb: 1, flexWrap: 'wrap' }}>
            <Chip
              label={formatPriority(article.priority)}
              size="small"
              sx={{
                backgroundColor: priorityColor,
                color: 'white',
                fontSize: '0.75rem',
                height: 20,
                '& .MuiChip-label': { px: 1 }
              }}
            />
            <Chip
              label={formatClassification(article.classification)}
              size="small"
              sx={{
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontSize: '0.75rem',
                height: 20,
                '& .MuiChip-label': { px: 1 }
              }}
            />
            {eventType !== 'Other' && (
              <Chip
                label={eventType.replace('_', ' ')}
                size="small"
                variant="outlined"
                sx={{
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                  color: 'rgba(255, 255, 255, 0.8)',
                  fontSize: '0.75rem',
                  height: 20,
                  '& .MuiChip-label': { px: 1 }
                }}
              />
            )}
          </Box>
        </Box>
        
        <IconButton
          onClick={onClose}
          size="small"
          sx={{
            color: 'rgba(255, 255, 255, 0.7)',
            '&:hover': { color: 'white', backgroundColor: 'rgba(255, 255, 255, 0.1)' }
          }}
        >
          <CloseIcon fontSize="small" />
        </IconButton>
      </Box>

      {/* Article metadata */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 0.5 }}>
          <strong>Source:</strong> {article.source}
        </Typography>
        
        {article.published_date && (
          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 0.5 }}>
            <strong>Published:</strong> {formatDate(article.published_date, 'long')}
          </Typography>
        )}
        
        {primaryLocation && (
          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 0.5 }}>
            <strong>Location:</strong> {primaryLocation}
          </Typography>
        )}
        
        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
          <strong>Entities:</strong> {article.entity_count} identified
        </Typography>
      </Box>

      {/* Article preview */}
      {article.text_preview && (
        <Box sx={{ mb: 2 }}>
          <Typography 
            variant="body2" 
            sx={{ 
              color: 'rgba(255, 255, 255, 0.9)',
              lineHeight: 1.4,
              fontStyle: 'italic'
            }}
          >
            {truncateText(article.text_preview, 150)}
          </Typography>
        </Box>
      )}

      {/* Entities section */}
      {article.entities && (
        <Box sx={{ mb: 2 }}>
          {/* Persons */}
          {article.entities.persons && article.entities.persons.length > 0 && (
            <Box sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                <PersonIcon sx={{ fontSize: 16, mr: 0.5, color: 'rgba(255, 255, 255, 0.7)' }} />
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 500 }}>
                  PERSONS
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {article.entities.persons.slice(0, 3).map((person, idx) => (
                  <Chip
                    key={idx}
                    label={truncateText(person, 20)}
                    size="small"
                    sx={{
                      backgroundColor: 'rgba(33, 150, 243, 0.2)',
                      color: 'rgba(33, 150, 243, 1)',
                      fontSize: '0.7rem',
                      height: 18,
                      '& .MuiChip-label': { px: 0.5 }
                    }}
                  />
                ))}
                {article.entities.persons.length > 3 && (
                  <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)', alignSelf: 'center' }}>
                    +{article.entities.persons.length - 3} more
                  </Typography>
                )}
              </Box>
            </Box>
          )}

          {/* Locations */}
          {article.entities.locations && article.entities.locations.length > 0 && (
            <Box sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                <LocationIcon sx={{ fontSize: 16, mr: 0.5, color: 'rgba(255, 255, 255, 0.7)' }} />
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 500 }}>
                  LOCATIONS
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {article.entities.locations.slice(0, 3).map((location, idx) => (
                  <Chip
                    key={idx}
                    label={truncateText(location, 20)}
                    size="small"
                    sx={{
                      backgroundColor: 'rgba(76, 175, 80, 0.2)',
                      color: 'rgba(76, 175, 80, 1)',
                      fontSize: '0.7rem',
                      height: 18,
                      '& .MuiChip-label': { px: 0.5 }
                    }}
                  />
                ))}
                {article.entities.locations.length > 3 && (
                  <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)', alignSelf: 'center' }}>
                    +{article.entities.locations.length - 3} more
                  </Typography>
                )}
              </Box>
            </Box>
          )}

          {/* Organizations */}
          {article.entities.organizations && article.entities.organizations.length > 0 && (
            <Box sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                <BusinessIcon sx={{ fontSize: 16, mr: 0.5, color: 'rgba(255, 255, 255, 0.7)' }} />
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 500 }}>
                  ORGANIZATIONS
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {article.entities.organizations.slice(0, 3).map((org, idx) => (
                  <Chip
                    key={idx}
                    label={truncateText(org, 20)}
                    size="small"
                    sx={{
                      backgroundColor: 'rgba(156, 39, 176, 0.2)',
                      color: 'rgba(156, 39, 176, 1)',
                      fontSize: '0.7rem',
                      height: 18,
                      '& .MuiChip-label': { px: 0.5 }
                    }}
                  />
                ))}
                {article.entities.organizations.length > 3 && (
                  <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)', alignSelf: 'center' }}>
                    +{article.entities.organizations.length - 3} more
                  </Typography>
                )}
              </Box>
            </Box>
          )}
        </Box>
      )}

      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)', my: 1.5 }} />

      {/* Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
          {extractDomain(article.url)}
        </Typography>
        
        <Button
          onClick={handleLinkClick}
          size="small"
          endIcon={<OpenInNewIcon sx={{ fontSize: 14 }} />}
          sx={{
            color: '#007bff',
            textTransform: 'none',
            fontSize: '0.75rem',
            minWidth: 'auto',
            px: 1,
            '&:hover': {
              backgroundColor: 'rgba(0, 123, 255, 0.1)',
            }
          }}
        >
          Read Full Article
        </Button>
      </Box>
    </Box>
  );
};

export default PopupContent;
