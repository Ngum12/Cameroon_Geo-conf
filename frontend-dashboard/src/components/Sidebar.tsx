/**
 * Sidebar Component for Project Sentinel Dashboard
 * Contains filters, statistics, and system information
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Divider,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel,
  Button,
  Collapse,
  IconButton,
  Badge,
  Tooltip,
} from '@mui/material';
import {
  ExpandLess,
  ExpandMore,
  Article as ArticleIcon,
  Security as SecurityIcon,
  Language as LanguageIcon,
  Schedule as ScheduleIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

import { SidebarProps } from '../types';
import { formatNumber, formatDate, formatPercentage } from '../utils/formatUtils';

const Sidebar: React.FC<SidebarProps> = ({
  statistics,
  filters,
  onFilterChange,
  onRefresh,
  loading,
}) => {
  const [expandedSections, setExpandedSections] = useState({
    overview: true,
    filters: true,
    sources: false,
    processing: false,
  });

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const handleSourcesChange = (sources: string[]) => {
    onFilterChange({
      ...filters,
      sources,
    });
  };

  const handlePrioritiesChange = (priorities: number[]) => {
    onFilterChange({
      ...filters,
      priorities,
    });
  };

  const handleShowOnlyChange = (key: 'withLocation' | 'processed', value: boolean) => {
    onFilterChange({
      ...filters,
      showOnly: {
        ...filters.showOnly,
        [key]: value,
      },
    });
  };

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 2 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 1, color: '#007bff', fontWeight: 600 }}>
          INTELLIGENCE OVERVIEW
        </Typography>
        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          Cameroon Defense Force OSINT Analysis
        </Typography>
      </Box>

      {/* System Overview */}
      <Card sx={{ mb: 2, backgroundColor: '#1a1a1a', border: '1px solid #2d2d2d' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="h6" sx={{ color: 'white', fontSize: '1rem' }}>
              System Overview
            </Typography>
            <IconButton
              size="small"
              onClick={() => toggleSection('overview')}
              sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
            >
              {expandedSections.overview ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>

          <Collapse in={expandedSections.overview}>
            {statistics ? (
              <Box>
                {/* Key metrics */}
                <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 2 }}>
                  <Box sx={{ textAlign: 'center', p: 1, backgroundColor: '#0f0f0f', borderRadius: 1 }}>
                    <Typography variant="h5" sx={{ color: '#007bff', fontWeight: 600 }}>
                      {formatNumber(statistics.overview.total_articles)}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      Total Reports
                    </Typography>
                  </Box>
                  <Box sx={{ textAlign: 'center', p: 1, backgroundColor: '#0f0f0f', borderRadius: 1 }}>
                    <Typography variant="h5" sx={{ color: '#28a745', fontWeight: 600 }}>
                      {formatNumber(statistics.overview.processed_articles)}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      Processed
                    </Typography>
                  </Box>
                </Box>

                {/* Processing status */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: 'white', mb: 1 }}>
                    Processing Status
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CheckCircleIcon sx={{ color: '#28a745', fontSize: 16, mr: 1 }} />
                    <Typography variant="body2" sx={{ flex: 1, color: 'rgba(255, 255, 255, 0.8)' }}>
                      Processed: {statistics.overview.processed_articles}
                    </Typography>
                  </Box>
                  {statistics.overview.pending_articles > 0 && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <ScheduleIcon sx={{ color: '#ffc107', fontSize: 16, mr: 1 }} />
                      <Typography variant="body2" sx={{ flex: 1, color: 'rgba(255, 255, 255, 0.8)' }}>
                        Pending: {statistics.overview.pending_articles}
                      </Typography>
                    </Box>
                  )}
                  {statistics.overview.failed_articles > 0 && (
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <ErrorIcon sx={{ color: '#dc3545', fontSize: 16, mr: 1 }} />
                      <Typography variant="body2" sx={{ flex: 1, color: 'rgba(255, 255, 255, 0.8)' }}>
                        Failed: {statistics.overview.failed_articles}
                      </Typography>
                    </Box>
                  )}
                </Box>

                {/* Recent activity */}
                <Box>
                  <Typography variant="body2" sx={{ color: 'white', mb: 1 }}>
                    Recent Activity (24h)
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <TrendingUpIcon sx={{ color: '#17a2b8', fontSize: 16, mr: 1 }} />
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                      {statistics.overview.recent_articles_24h} new reports
                    </Typography>
                  </Box>
                </Box>
              </Box>
            ) : (
              <Box sx={{ textAlign: 'center', py: 2 }}>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                  Loading statistics...
                </Typography>
              </Box>
            )}
          </Collapse>
        </CardContent>
      </Card>

      {/* Filters */}
      <Card sx={{ mb: 2, backgroundColor: '#1a1a1a', border: '1px solid #2d2d2d' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="h6" sx={{ color: 'white', fontSize: '1rem' }}>
              Filters
            </Typography>
            <IconButton
              size="small"
              onClick={() => toggleSection('filters')}
              sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
            >
              {expandedSections.filters ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>

          <Collapse in={expandedSections.filters}>
            <Box>
              {/* Priority filter */}
              <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Priority</InputLabel>
                <Select
                  multiple
                  value={filters.priorities}
                  onChange={(e) => handlePrioritiesChange(e.target.value as number[])}
                  label="Priority"
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {(selected as number[]).map((priority) => {
                        const labels = { 1: 'Critical', 2: 'High', 3: 'Medium', 4: 'Low' };
                        const colors = { 1: '#dc3545', 2: '#fd7e14', 3: '#007bff', 4: '#6c757d' };
                        return (
                          <Chip
                            key={priority}
                            label={labels[priority as keyof typeof labels]}
                            size="small"
                            sx={{
                              backgroundColor: colors[priority as keyof typeof colors],
                              color: 'white',
                              height: 20,
                            }}
                          />
                        );
                      })}
                    </Box>
                  )}
                  sx={{
                    color: 'white',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255, 255, 255, 0.5)',
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: '#007bff',
                    },
                  }}
                >
                  <MenuItem value={1}>🔴 Critical</MenuItem>
                  <MenuItem value={2}>🟠 High</MenuItem>
                  <MenuItem value={3}>🔵 Medium</MenuItem>
                  <MenuItem value={4}>⚫ Low</MenuItem>
                </Select>
              </FormControl>

              {/* Source filter */}
              {statistics && statistics.by_source.length > 0 && (
                <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                  <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Sources</InputLabel>
                  <Select
                    multiple
                    value={filters.sources}
                    onChange={(e) => handleSourcesChange(e.target.value as string[])}
                    label="Sources"
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {(selected as string[]).map((source) => (
                          <Chip
                            key={source}
                            label={source}
                            size="small"
                            sx={{
                              backgroundColor: 'rgba(0, 123, 255, 0.2)',
                              color: '#007bff',
                              height: 20,
                            }}
                          />
                        ))}
                      </Box>
                    )}
                    sx={{
                      color: 'white',
                      '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'rgba(255, 255, 255, 0.3)',
                      },
                      '&:hover .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'rgba(255, 255, 255, 0.5)',
                      },
                      '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                        borderColor: '#007bff',
                      },
                    }}
                  >
                    {statistics.by_source.slice(0, 10).map((source) => (
                      <MenuItem key={source.source} value={source.source}>
                        {source.source} ({source.count})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}

              {/* Display options */}
              <Box>
                <Typography variant="body2" sx={{ color: 'white', mb: 1 }}>
                  Display Options
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={filters.showOnly.withLocation}
                      onChange={(e) => handleShowOnlyChange('withLocation', e.target.checked)}
                      size="small"
                      sx={{
                        '& .MuiSwitch-switchBase.Mui-checked': {
                          color: '#007bff',
                        },
                        '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                          backgroundColor: '#007bff',
                        },
                      }}
                    />
                  }
                  label={
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                      Show only geolocated reports
                    </Typography>
                  }
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={filters.showOnly.processed}
                      onChange={(e) => handleShowOnlyChange('processed', e.target.checked)}
                      size="small"
                      sx={{
                        '& .MuiSwitch-switchBase.Mui-checked': {
                          color: '#007bff',
                        },
                        '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                          backgroundColor: '#007bff',
                        },
                      }}
                    />
                  }
                  label={
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                      Show only processed reports
                    </Typography>
                  }
                />
              </Box>
            </Box>
          </Collapse>
        </CardContent>
      </Card>

      {/* Top Sources */}
      {statistics && statistics.by_source.length > 0 && (
        <Card sx={{ mb: 2, backgroundColor: '#1a1a1a', border: '1px solid #2d2d2d' }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="h6" sx={{ color: 'white', fontSize: '1rem' }}>
                Top Sources
              </Typography>
              <IconButton
                size="small"
                onClick={() => toggleSection('sources')}
                sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
              >
                {expandedSections.sources ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Box>

            <Collapse in={expandedSections.sources}>
              <List dense>
                {statistics.by_source.slice(0, 5).map((source, index) => {
                  const percentage = formatPercentage(source.count, statistics.overview.total_articles);
                  return (
                    <ListItem key={source.source} sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <ArticleIcon sx={{ fontSize: 16, color: 'rgba(255, 255, 255, 0.7)' }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body2" sx={{ color: 'white' }}>
                            {source.source}
                          </Typography>
                        }
                        secondary={
                          <Box>
                            <LinearProgress
                              variant="determinate"
                              value={(source.count / statistics.overview.total_articles) * 100}
                              sx={{
                                height: 4,
                                borderRadius: 2,
                                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: '#007bff',
                                },
                              }}
                            />
                            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                              {source.count} reports ({percentage})
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  );
                })}
              </List>
            </Collapse>
          </CardContent>
        </Card>
      )}

      {/* Refresh button */}
      <Box sx={{ textAlign: 'center', mt: 2 }}>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={onRefresh}
          disabled={loading}
          sx={{
            color: '#007bff',
            borderColor: '#007bff',
            '&:hover': {
              backgroundColor: 'rgba(0, 123, 255, 0.1)',
              borderColor: '#007bff',
            },
          }}
        >
          Refresh Data
        </Button>
      </Box>

      {/* Last updated */}
      {statistics && (
        <Box sx={{ textAlign: 'center', mt: 2, pt: 2, borderTop: '1px solid #2d2d2d' }}>
          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
            Last updated: {formatDate(statistics.generated_at, 'relative')}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default Sidebar;
