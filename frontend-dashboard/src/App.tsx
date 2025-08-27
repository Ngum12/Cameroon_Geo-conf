/**
 * Main App Component for Project Sentinel Dashboard
 * Cameroon Defense Force OSINT Analysis System
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  Alert,
  Snackbar,
  Backdrop,
  CircularProgress,
  Fab,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

import { EventsGeoJSON, FilterOptions, SystemStatistics } from './types';
import { fetchEvents, fetchStatistics, checkApiConnection, handleApiError } from './services/api';
import MapComponent from './components/Map';
import Sidebar from './components/Sidebar';
import StatusBar from './components/StatusBar';

// Default filter options
const defaultFilters: FilterOptions = {
  dateRange: {
    start: null,
    end: null,
  },
  sources: [],
  priorities: [],
  classifications: [],
  showOnly: {
    withLocation: true, // Only show articles with location data for map
    processed: true,    // Only show processed articles
  },
};

const App: React.FC = () => {
  // State management
  const [events, setEvents] = useState<EventsGeoJSON | null>(null);
  const [statistics, setStatistics] = useState<SystemStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [filters, setFilters] = useState<FilterOptions>(defaultFilters);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connecting');
  const [snackbarMessage, setSnackbarMessage] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  // Check API connection on startup
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const isConnected = await checkApiConnection();
        setConnectionStatus(isConnected ? 'connected' : 'disconnected');
        
        if (!isConnected) {
          setError('Unable to connect to Project Sentinel backend API. Please check that the Django server is running.');
        }
      } catch (err) {
        console.error('Connection check failed:', err);
        setConnectionStatus('disconnected');
        setError('Backend API is not accessible. Please check your network connection.');
      }
    };

    checkConnection();
  }, []);

  // Load initial data
  const loadData = useCallback(async (showLoading = true) => {
    if (connectionStatus !== 'connected') return;

    try {
      if (showLoading) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }
      
      setError(null);

      // Prepare filter options for API call
      const apiOptions: any = {
        limit: 1000, // Large limit to get comprehensive data
      };

      // Apply date filter
      if (filters.dateRange.start && filters.dateRange.end) {
        const daysDiff = Math.ceil(
          (filters.dateRange.end.getTime() - filters.dateRange.start.getTime()) / (1000 * 60 * 60 * 24)
        );
        apiOptions.days = Math.max(1, daysDiff);
      } else {
        apiOptions.days = 30; // Default to last 30 days
      }

      // Apply priority filter
      if (filters.priorities.length === 1) {
        apiOptions.priority = filters.priorities[0];
      }

      // Apply source filter
      if (filters.sources.length === 1) {
        apiOptions.source = filters.sources[0];
      }

      // Load events and statistics in parallel
      const [eventsData, statsData] = await Promise.all([
        fetchEvents(apiOptions),
        fetchStatistics(),
      ]);

      setEvents(eventsData);
      setStatistics(statsData);

      // Show success message on manual refresh
      if (!showLoading) {
        setSnackbarMessage(`Refreshed: ${eventsData.features.length} intelligence reports loaded`);
      }

    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      console.error('Failed to load data:', err);
      
      if (!showLoading) {
        setSnackbarMessage('Failed to refresh data');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [connectionStatus, filters]);

  // Load data when connection is established or filters change
  useEffect(() => {
    if (connectionStatus === 'connected') {
      loadData(true);
    }
  }, [connectionStatus, filters, loadData]);

  // Handle refresh
  const handleRefresh = useCallback(() => {
    loadData(false);
  }, [loadData]);

  // Handle filter changes
  const handleFilterChange = useCallback((newFilters: FilterOptions) => {
    setFilters(newFilters);
  }, []);

  // Handle sidebar toggle
  const toggleSidebar = useCallback(() => {
    setSidebarOpen(prev => !prev);
  }, []);

  // Handle snackbar close
  const handleSnackbarClose = useCallback(() => {
    setSnackbarMessage(null);
  }, []);

  // Connection status indicator
  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return '#28a745';
      case 'connecting': return '#ffc107';
      case 'disconnected': return '#dc3545';
      default: return '#6c757d';
    }
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      height: '100vh', 
      backgroundColor: '#0f0f0f',
      overflow: 'hidden'
    }}>
      {/* App Bar */}
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: '#1a1a1a',
          borderBottom: '1px solid #2d2d2d',
          boxShadow: '0 1px 4px rgba(0, 0, 0, 0.3)'
        }}
      >
        <Toolbar variant="dense">
          <IconButton
            edge="start"
            color="inherit"
            onClick={toggleSidebar}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            PROJECT SENTINEL
          </Typography>

          {/* Connection status indicator */}
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              backgroundColor: getConnectionStatusColor(),
              mr: 2,
              boxShadow: connectionStatus === 'connected' ? '0 0 8px rgba(40, 167, 69, 0.5)' : 'none',
            }}
          />

          <IconButton
            color="inherit"
            onClick={handleRefresh}
            disabled={loading || refreshing || connectionStatus !== 'connected'}
            sx={{ mr: 1 }}
          >
            <RefreshIcon sx={{ 
              animation: refreshing ? 'spin 1s linear infinite' : 'none',
              '@keyframes spin': {
                '0%': { transform: 'rotate(0deg)' },
                '100%': { transform: 'rotate(360deg)' },
              }
            }} />
          </IconButton>

          <IconButton color="inherit">
            <SettingsIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Drawer
        variant="temporary"
        anchor="left"
        open={sidebarOpen}
        onClose={toggleSidebar}
        sx={{
          '& .MuiDrawer-paper': {
            width: 350,
            backgroundColor: '#151515',
            borderRight: '1px solid #2d2d2d',
            boxShadow: '4px 0 8px rgba(0, 0, 0, 0.3)',
          },
        }}
      >
        <Toolbar variant="dense" /> {/* Spacer for app bar */}
        <Sidebar
          statistics={statistics}
          filters={filters}
          onFilterChange={handleFilterChange}
          onRefresh={handleRefresh}
          loading={loading || refreshing}
        />
      </Drawer>

      {/* Main content area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          height: '100vh',
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        <Toolbar variant="dense" /> {/* Spacer for app bar */}
        
        {/* Map component */}
        <MapComponent
          events={events}
          loading={loading}
          error={error}
          onRefresh={handleRefresh}
          filters={filters}
          onFilterChange={handleFilterChange}
        />

        {/* Status bar */}
        <StatusBar
          connectionStatus={connectionStatus}
          eventsCount={events?.features.length || 0}
          lastUpdate={events?.metadata.generated_at}
          loading={loading || refreshing}
        />
      </Box>

      {/* Loading backdrop for initial load */}
      <Backdrop
        sx={{
          color: '#fff',
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: 'rgba(15, 15, 15, 0.8)',
          backdropFilter: 'blur(4px)',
        }}
        open={loading && connectionStatus === 'connecting'}
      >
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress color="inherit" size={60} sx={{ mb: 2 }} />
          <Typography variant="h6" sx={{ mb: 1 }}>
            Initializing Project Sentinel
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            Connecting to intelligence systems...
          </Typography>
        </Box>
      </Backdrop>

      {/* Error/disconnection overlay */}
      {connectionStatus === 'disconnected' && (
        <Backdrop
          sx={{
            color: '#fff',
            zIndex: (theme) => theme.zIndex.drawer + 1,
            backgroundColor: 'rgba(15, 15, 15, 0.9)',
          }}
          open={true}
        >
          <Box sx={{ textAlign: 'center', maxWidth: 500, p: 3 }}>
            <Typography variant="h5" sx={{ mb: 2, color: '#dc3545' }}>
              Connection Lost
            </Typography>
            <Typography variant="body1" sx={{ mb: 3 }}>
              Unable to connect to Project Sentinel backend systems. Please ensure the Django API server is running on port 8000.
            </Typography>
            <Fab
              variant="extended"
              color="primary"
              onClick={() => window.location.reload()}
              sx={{ mr: 2 }}
            >
              <RefreshIcon sx={{ mr: 1 }} />
              Retry Connection
            </Fab>
          </Box>
        </Backdrop>
      )}

      {/* Notification snackbar */}
      <Snackbar
        open={!!snackbarMessage}
        autoHideDuration={4000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleSnackbarClose} 
          severity={snackbarMessage?.includes('Failed') ? 'error' : 'success'}
          sx={{ 
            backgroundColor: '#1a1a1a',
            color: 'white',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default App;
