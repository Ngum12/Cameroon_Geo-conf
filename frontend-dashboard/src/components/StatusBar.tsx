/**
 * Status Bar Component for Project Sentinel Dashboard
 * Shows connection status, data counts, and last update time
 */

import React from 'react';
import { Box, Typography, Chip, LinearProgress } from '@mui/material';
import { 
  Circle as CircleIcon,
  SignalWifi4Bar as SignalIcon,
  SignalWifiOff as SignalOffIcon,
  Update as UpdateIcon,
} from '@mui/icons-material';

import { formatDate, formatNumber } from '../utils/formatUtils';

interface StatusBarProps {
  connectionStatus: 'connected' | 'connecting' | 'disconnected';
  eventsCount: number;
  lastUpdate?: string;
  loading: boolean;
}

const StatusBar: React.FC<StatusBarProps> = ({
  connectionStatus,
  eventsCount,
  lastUpdate,
  loading,
}) => {
  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return '#28a745';
      case 'connecting': return '#ffc107';
      case 'disconnected': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected': return <SignalIcon sx={{ fontSize: 16 }} />;
      case 'connecting': return <CircleIcon sx={{ fontSize: 16 }} />;
      case 'disconnected': return <SignalOffIcon sx={{ fontSize: 16 }} />;
      default: return <CircleIcon sx={{ fontSize: 16 }} />;
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting';
      case 'disconnected': return 'Disconnected';
      default: return 'Unknown';
    }
  };

  return (
    <Box
      sx={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: 40,
        backgroundColor: 'rgba(26, 26, 26, 0.95)',
        backdropFilter: 'blur(10px)',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        display: 'flex',
        alignItems: 'center',
        px: 2,
        zIndex: 1000,
      }}
    >
      {/* Loading indicator */}
      {loading && (
        <LinearProgress
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 2,
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            '& .MuiLinearProgress-bar': {
              backgroundColor: '#007bff',
            },
          }}
        />
      )}

      {/* Connection status */}
      <Chip
        icon={getStatusIcon()}
        label={getStatusText()}
        size="small"
        sx={{
          backgroundColor: `${getStatusColor()}20`,
          color: getStatusColor(),
          border: `1px solid ${getStatusColor()}`,
          mr: 2,
          fontSize: '0.75rem',
          height: 24,
          '& .MuiChip-icon': {
            color: getStatusColor(),
          },
        }}
      />

      {/* Events count */}
      <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)', mr: 0.5 }}>
          Reports:
        </Typography>
        <Typography variant="caption" sx={{ color: 'white', fontWeight: 500 }}>
          {formatNumber(eventsCount)}
        </Typography>
      </Box>

      {/* Spacer */}
      <Box sx={{ flexGrow: 1 }} />

      {/* Last update time */}
      {lastUpdate && (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <UpdateIcon sx={{ fontSize: 14, color: 'rgba(255, 255, 255, 0.7)', mr: 0.5 }} />
          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
            Updated: {formatDate(lastUpdate, 'relative')}
          </Typography>
        </Box>
      )}

      {/* System info */}
      <Typography
        variant="caption"
        sx={{
          color: 'rgba(255, 255, 255, 0.5)',
          ml: 2,
          fontSize: '0.7rem',
        }}
      >
        PROJECT SENTINEL v1.0 • CDF OSINT
      </Typography>
    </Box>
  );
};

export default StatusBar;
