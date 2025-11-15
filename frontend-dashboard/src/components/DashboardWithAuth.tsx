/**
 * 🛡️ DASHBOARD WITH AUTHENTICATION INTEGRATION
 * Enhanced dashboard with user authentication features
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  useMediaQuery,
  useTheme,
  Avatar,
  Chip,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Menu as MenuIcon,
  AccountCircle,
  Person,
  Settings as SettingsIcon,
  Logout,
  Refresh as RefreshIcon,
  Dashboard as DashboardIcon,
  Map as MapIcon,
  Psychology as AIIcon,
  Mic as VoiceIcon,
  Phone as MobileIcon,
  TrendingUp as VisualizationIcon,
  Security as SecurityIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';

import { useAuth } from '../contexts/AuthContext';
import MapComponent from './Map';
import Sidebar from './Sidebar';
import StatusBar from './StatusBar';
import ThreatVisualization from './ThreatVisualization';
import AIAnalyticsDashboard from './AIAnalyticsDashboard';
import VoiceCommandCenter from './VoiceCommandCenter';
import Enhanced3DMap from './Enhanced3DMap';
import RealTimeNotifications from './RealTimeNotifications';
import MobileCommandCenter from './MobileCommandCenter';
import MobileFieldCommander from './MobileFieldCommander';
import ReportExport from './ReportExport';
import ResponsiveWrapper, { DeviceContextProvider } from './ResponsiveWrapper';
import MultiScreenController from './MultiScreenController';
import AdaptiveScreenContent from './AdaptiveScreenContent';
import { MobileDetection } from '../utils/mobileUtils';
import { mobileService } from '../services/mobileService';

// Import services
import { threatIntelligenceService, UnifiedThreatPoint } from '../services/threatIntelligence';
import { notificationService } from '../services/notificationService';
import { api } from '../services/api';

// Check if this is a multi-screen instance
function isMultiScreen(): boolean {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.has('screen') || urlParams.has('multiscreen');
}

const DashboardWithAuth: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isSmallMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { user, logout, isCommander, canAccessClassified, getRoleDisplayName, getClearanceDisplayName } = useAuth();

  // 🖥️ CHECK FOR MULTI-SCREEN MODE
  if (isMultiScreen()) {
    return (
      <DeviceContextProvider>
        <AdaptiveScreenContent />
      </DeviceContextProvider>
    );
  }

  const [drawerOpen, setDrawerOpen] = useState(!isMobile);
  const [currentView, setCurrentView] = useState('dashboard');
  const [dashboardTab, setDashboardTab] = useState(0);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);

  // Real data state from Django backend
  const [realStatistics, setRealStatistics] = useState(null);
  const [statisticsLoading, setStatisticsLoading] = useState(true);

  // 🛡️ UNIFIED THREAT INTELLIGENCE STATE (Shared by ThreatVisualization and Map)
  const [unifiedThreats, setUnifiedThreats] = useState<UnifiedThreatPoint[]>([]);
  const [threatDataLoading, setThreatDataLoading] = useState(true);

  // Fetch real data from Django backend
  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        const stats = await api.get('/api/v1/statistics/');
        console.log('📊 Backend Statistics:', stats);
        setRealStatistics(stats);
      } catch (error) {
        console.error('❌ Failed to fetch statistics:', error);
      } finally {
        setStatisticsLoading(false);
      }
    };

    fetchStatistics();
    const interval = setInterval(fetchStatistics, 30000);
    return () => clearInterval(interval);
  }, []);

  // Initialize Threat Intelligence Service
  useEffect(() => {
    console.log('🔥 Initializing Project Sentinel Threat Intelligence...');
    
    // Subscribe to threat data updates
    threatIntelligenceService.subscribe((threats: UnifiedThreatPoint[]) => {
      console.log('📊 Received unified threat data:', threats.length, 'threats');
      setUnifiedThreats(threats);
      setThreatDataLoading(false);
      
      // 🚨 TRIGGER INTELLIGENT NOTIFICATIONS based on threat data
      notificationService.onThreatDataUpdate(threats);
    });

    // Make service globally available for notifications
    (window as any).threatIntelligenceService = threatIntelligenceService;

    // Start the intelligence engine
    threatIntelligenceService.start();

    return () => {
      console.log('🛑 Stopping Threat Intelligence Service...');
      threatIntelligenceService.stop();
      notificationService.stopIntelligenceMonitoring();
    };
  }, []);

  // User menu handlers
  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleLogout = async () => {
    handleUserMenuClose();
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Menu items with role-based access control
  const getMenuItems = () => {
    const baseItems = [
      { id: 'dashboard', label: '🏠 Command Center', icon: <DashboardIcon /> },
      { id: 'map', label: '🗺️ Intelligence Map', icon: <MapIcon /> },
      { id: 'timeline', label: '⏰ Timeline', icon: <TimelineIcon /> },
      { id: 'threats', label: '⚡ Threat Analysis', icon: <VisualizationIcon /> },
    ];

    const advancedItems = [
      { id: 'ai', label: '🤖 AI Analytics', icon: <AIIcon /> },
      { id: 'voice', label: '🎤 Voice Command', icon: <VoiceIcon /> },
      { id: 'mobile', label: '📱 Mobile Command', icon: <MobileIcon /> },
    ];

    const adminItems = [
      { id: 'reports', label: '📊 Export Reports', icon: <ReportExport /> },
      { id: 'settings', label: '⚙️ System Settings', icon: <SettingsIcon /> },
    ];

    let menuItems = [...baseItems];

    // Add advanced features for analysts and above
    if (user?.role !== 'VIEWER') {
      menuItems = [...menuItems, ...advancedItems];
    }

    // Add admin features for commanders and admins
    if (isCommander) {
      menuItems = [...menuItems, ...adminItems];
    }

    return menuItems;
  };

  const menuItems = getMenuItems();

  // Mobile interface for small screens
  if (isSmallMobile) {
    return (
      <DeviceContextProvider>
        <ResponsiveWrapper
          mobileComponent={<MobileFieldCommander />}
          tabletComponent={<MobileCommandCenter />}
          autoDetect={true}
        >
          <MobileCommandCenter />
        </ResponsiveWrapper>
      </DeviceContextProvider>
    );
  }

  return (
    <DeviceContextProvider>
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <IconButton color="inherit" onClick={() => setDrawerOpen(!drawerOpen)} sx={{ mr: 2 }}>
              <MenuIcon />
            </IconButton>
            
            <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
              🛡️ PROJECT SENTINEL - DEFENSE INTELLIGENCE
            </Typography>

            {/* User Info */}
            <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
              <Chip
                avatar={
                  <Avatar sx={{ bgcolor: 'primary.main', width: 24, height: 24 }}>
                    {user?.first_name?.[0] || user?.username?.[0] || 'U'}
                  </Avatar>
                }
                label={`${user?.rank || ''} ${user?.display_name || user?.username}`}
                variant="outlined"
                size="small"
                sx={{
                  color: 'white',
                  borderColor: 'rgba(255,255,255,0.3)',
                  '& .MuiChip-label': { color: 'white', fontSize: '0.8rem' }
                }}
              />
              <Chip
                label={getRoleDisplayName()}
                size="small"
                sx={{
                  ml: 1,
                  bgcolor: user?.clearance_level === 'TOP_SECRET' ? 'error.main' :
                           user?.clearance_level === 'SECRET' ? 'warning.main' :
                           user?.clearance_level === 'CONFIDENTIAL' ? 'orange' : 'info.main',
                  color: 'white',
                  fontSize: '0.75rem'
                }}
              />
            </Box>

            <IconButton color="inherit" sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>

            <IconButton
              color="inherit"
              onClick={handleUserMenuOpen}
              sx={{ mr: 1 }}
            >
              <AccountCircle />
            </IconButton>

            <RealTimeNotifications />

            {/* User Menu */}
            <Menu
              anchorEl={userMenuAnchor}
              open={Boolean(userMenuAnchor)}
              onClose={handleUserMenuClose}
            >
              <MenuItem disabled>
                <Box sx={{ textAlign: 'center', py: 1 }}>
                  <Typography variant="subtitle2">{user?.display_name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {getClearanceDisplayName()}
                  </Typography>
                </Box>
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleUserMenuClose}>
                <ListItemIcon><Person /></ListItemIcon>
                <ListItemText>Profile</ListItemText>
              </MenuItem>
              <MenuItem onClick={handleUserMenuClose}>
                <ListItemIcon><SettingsIcon /></ListItemIcon>
                <ListItemText>Settings</ListItemText>
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleLogout}>
                <ListItemIcon><Logout /></ListItemIcon>
                <ListItemText>Logout</ListItemText>
              </MenuItem>
            </Menu>
          </Toolbar>
        </AppBar>

        <Drawer
          variant={isMobile ? 'temporary' : 'persistent'}
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          sx={{
            width: 280,
            '& .MuiDrawer-paper': {
              width: 280,
              background: 'linear-gradient(180deg, #1a1a1a, #0a0a0a)',
              borderRight: '2px solid #00ff88',
            },
          }}
        >
          <Toolbar />
          <Box sx={{ p: 2, textAlign: 'center', borderBottom: '1px solid #333' }}>
            <Avatar sx={{ bgcolor: '#00ff88', mx: 'auto', mb: 1 }}>
              <SecurityIcon />
            </Avatar>
            <Typography variant="h6" sx={{ color: '#00ff88' }}>
              🇨🇲 PROJECT SENTINEL
            </Typography>
          </Box>

          <List sx={{ p: 1 }}>
            {menuItems.map((item) => (
              <ListItem
                button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                selected={currentView === item.id}
                sx={{
                  borderRadius: 2,
                  mb: 1,
                  '&.Mui-selected': {
                    bgcolor: 'rgba(0, 255, 136, 0.1)',
                    borderLeft: '4px solid #00ff88',
                  }
                }}
              >
                <ListItemIcon sx={{ color: currentView === item.id ? '#00ff88' : '#ccc' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItem>
            ))}
          </List>
        </Drawer>

        <Box
          component="main"
          sx={{
            flexGrow: 1,
            bgcolor: '#0a0a0a',
            marginLeft: drawerOpen && !isMobile ? 0 : `-280px`,
            transition: 'margin 0.3s ease',
          }}
        >
          <Toolbar />
          {/* Main content rendering based on current view */}
          {currentView === 'dashboard' && (
            <Box sx={{ p: 3 }}>
              <Typography variant="h4" gutterBottom>
                Welcome, {user?.display_name}! 🛡️
              </Typography>
              <Typography variant="body1" sx={{ mb: 3 }}>
                Project Sentinel Intelligence Dashboard - {getRoleDisplayName()}
              </Typography>
              {/* Add dashboard content here */}
            </Box>
          )}
          
          {/* Add other views based on currentView state */}
        </Box>

      </Box>
      <StatusBar />
    </DeviceContextProvider>
  );
};

export default DashboardWithAuth;

