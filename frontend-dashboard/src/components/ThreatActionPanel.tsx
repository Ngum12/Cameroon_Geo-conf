/**
 * 🎯 THREAT ACTION PANEL - Critical Defense Action Interface
 * Action buttons for threat notifications with escalation handling
 */

import React, { useState } from 'react';
import {
  Box, Card, Typography, Button, Grid, Chip,
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Alert, CircularProgress
} from '@mui/material';
import {
  PlayArrow as InvestigateIcon,
  Send as EscalateIcon,
  Check as AcknowledgeIcon,
  Close as DismissIcon,
  Warning as WarningIcon,
  Schedule as TimeIcon
} from '@mui/icons-material';
import { IntelligenceNotification } from '../services/notificationService';
// import { escalationService, ThreatActionRequest } from '../services/escalationService';

interface ThreatActionRequest {
  notificationId: string;
  actionType: 'acknowledge' | 'investigate' | 'escalate' | 'dismiss';
  operatorId: string;
  timestamp: Date;
  notes?: string;
}

interface ThreatActionPanelProps {
  notification: IntelligenceNotification;
  escalationLevel?: 'initial' | 'reminder' | 'emergency' | 'auto_escalated';
  onActionTaken?: (action: string) => void;
}

export const ThreatActionPanel: React.FC<ThreatActionPanelProps> = ({
  notification,
  escalationLevel = 'initial',
  onActionTaken
}) => {
  const [actionDialog, setActionDialog] = useState<string | null>(null);
  const [actionNotes, setActionNotes] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleAction = async (actionType: 'acknowledge' | 'investigate' | 'escalate' | 'dismiss') => {
    setIsProcessing(true);
    
    try {
      const actionRequest: ThreatActionRequest = {
        notificationId: notification.id,
        actionType,
        operatorId: 'current-operator', // This would come from auth context
        timestamp: new Date(),
        notes: actionNotes || undefined
      };

      // Submit action to escalation service
      // escalationService.handleThreatAction(actionRequest);
      console.log('🎯 Threat action taken:', actionRequest);
      
      // Navigate to appropriate page based on action type
      switch (actionType) {
        case 'acknowledge':
          window.dispatchEvent(new CustomEvent('sentinel:navigate-acknowledgment', {
            detail: { threat: notification }
          }));
          break;
        case 'investigate':
          window.dispatchEvent(new CustomEvent('sentinel:navigate-human-loop', {
            detail: { threat: notification }
          }));
          break;
        case 'escalate':
          window.dispatchEvent(new CustomEvent('sentinel:navigate-comms-hub', {
            detail: {
              notificationId: notification.id,
              title: notification.title,
              region: notification.region,
              threatLevel: notification.threatLevel || 75,
              autoFill: true
            }
          }));
          break;
        case 'dismiss':
          // For dismiss, we'll keep the dialog for confirmation
          break;
      }
      
      // Notify parent component
      onActionTaken?.(actionType);
      
      // Close dialog for all actions (they navigate to dedicated pages or stay for dismiss)
      setActionDialog(null);
      setActionNotes('');
      
      console.log(`✅ Action taken: ${actionType} for ${notification.title}`);
      
    } catch (error) {
      console.error('❌ Action failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const getEscalationInfo = () => {
    switch (escalationLevel) {
      case 'reminder':
        return {
          color: '#ff9800',
          icon: '🔔',
          message: '5 minutes elapsed - Reminder alert'
        };
      case 'emergency':
        return {
          color: '#ff1744',
          icon: '🚨',
          message: '10 minutes elapsed - Emergency escalation'
        };
      case 'auto_escalated':
        return {
          color: '#d50000',
          icon: '⚡',
          message: '15 minutes elapsed - Auto-escalated'
        };
      default:
        return {
          color: '#2196f3',
          icon: '🎯',
          message: 'Initial alert - Action required'
        };
    }
  };

  const escalationInfo = getEscalationInfo();

  return (
    <Card sx={{ 
      p: 2, 
      background: escalationLevel === 'auto_escalated' 
        ? 'linear-gradient(135deg, #5d1a1a 0%, #3a1a1a 100%)'
        : escalationLevel === 'emergency'
        ? 'linear-gradient(135deg, #5d3a1a 0%, #3a2a1a 100%)'
        : 'linear-gradient(135deg, #1a2e5d 0%, #1a2a3a 100%)',
      border: `2px solid ${escalationInfo.color}`,
      animation: escalationLevel === 'emergency' || escalationLevel === 'auto_escalated' 
        ? 'pulse 2s infinite' : 'none',
      '@keyframes pulse': {
        '0%': { borderColor: escalationInfo.color, boxShadow: '0 0 0 0 rgba(255, 0, 0, 0.4)' },
        '70%': { borderColor: escalationInfo.color, boxShadow: '0 0 0 10px rgba(255, 0, 0, 0)' },
        '100%': { borderColor: escalationInfo.color, boxShadow: '0 0 0 0 rgba(255, 0, 0, 0)' }
      }
    }}>
      
      {/* Escalation Status */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="h6" sx={{ color: escalationInfo.color }}>
            {escalationInfo.icon}
          </Typography>
          <Typography variant="body2" sx={{ color: '#fff', fontWeight: 'bold' }}>
            {escalationInfo.message}
          </Typography>
        </Box>
        
        <Chip
          label={notification.priority.toUpperCase()}
          size="small"
          sx={{
            bgcolor: notification.priority === 'critical' ? '#ff1744' : '#ff9800',
            color: '#fff',
            fontWeight: 'bold'
          }}
        />
      </Box>

      {/* Threat Information */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ color: '#fff', fontWeight: 'bold', mb: 1 }}>
          {notification.title}
        </Typography>
        <Typography variant="body2" sx={{ color: '#aaa', mb: 1 }}>
          📍 {notification.region} • 🕒 {notification.timestamp.toLocaleTimeString()}
        </Typography>
        <Typography variant="body2" sx={{ color: '#fff' }}>
          {notification.message}
        </Typography>
      </Box>

      {/* Action Buttons */}
      <Grid container spacing={2}>
        <Grid item xs={6} sm={3}>
          <Button
            fullWidth
            variant="contained"
            startIcon={<AcknowledgeIcon />}
            onClick={() => setActionDialog('acknowledge')}
            sx={{
              bgcolor: '#4caf50',
              '&:hover': { bgcolor: '#388e3c' }
            }}
          >
            ACKNOWLEDGE
          </Button>
        </Grid>
        
        <Grid item xs={6} sm={3}>
          <Button
            fullWidth
            variant="contained"
            startIcon={<InvestigateIcon />}
            onClick={() => setActionDialog('investigate')}
            sx={{
              bgcolor: '#2196f3',
              '&:hover': { bgcolor: '#1976d2' }
            }}
          >
            INVESTIGATE
          </Button>
        </Grid>
        
        <Grid item xs={6} sm={3}>
          <Button
            fullWidth
            variant="contained"
            startIcon={<EscalateIcon />}
            onClick={() => setActionDialog('escalate')}
            sx={{
              bgcolor: '#ff9800',
              '&:hover': { bgcolor: '#f57c00' }
            }}
          >
            ESCALATE
          </Button>
        </Grid>
        
        <Grid item xs={6} sm={3}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<DismissIcon />}
            onClick={() => setActionDialog('dismiss')}
            sx={{
              borderColor: '#f44336',
              color: '#f44336',
              '&:hover': { borderColor: '#d32f2f', bgcolor: 'rgba(244, 67, 54, 0.1)' }
            }}
          >
            DISMISS
          </Button>
        </Grid>
      </Grid>

      {/* Action Confirmation Dialog */}
      <Dialog open={actionDialog !== null} onClose={() => setActionDialog(null)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ bgcolor: '#1a1a1a', color: '#fff' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WarningIcon sx={{ color: '#ff9800' }} />
            Confirm Action: {actionDialog?.toUpperCase()}
          </Box>
        </DialogTitle>
        
        <DialogContent sx={{ bgcolor: '#1a1a1a', color: '#fff', pt: 2 }}>
          <Alert 
            severity={actionDialog === 'dismiss' ? 'warning' : 'info'} 
            sx={{ mb: 2, bgcolor: 'rgba(33, 150, 243, 0.1)' }}
          >
            {actionDialog === 'acknowledge' && '✅ Navigate to Threat Acknowledgment page. Escalation will be stopped.'}
            {actionDialog === 'investigate' && '🔍 Navigate to Human-in-Loop Verification system for detailed analysis.'}
            {actionDialog === 'escalate' && '📡 Navigate to Communications Hub to send emergency alerts.'}
            {actionDialog === 'dismiss' && '❌ This threat will be dismissed. Use with caution.'}
          </Alert>
          
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Action Notes (Optional)"
            value={actionNotes}
            onChange={(e) => setActionNotes(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                color: '#fff',
                '& fieldset': { borderColor: '#666' },
                '&:hover fieldset': { borderColor: '#999' },
                '&.Mui-focused fieldset': { borderColor: '#2196f3' }
              },
              '& .MuiInputLabel-root': { color: '#aaa' }
            }}
          />
        </DialogContent>
        
        <DialogActions sx={{ bgcolor: '#1a1a1a', p: 2 }}>
          <Button onClick={() => setActionDialog(null)} sx={{ color: '#999' }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={() => actionDialog && handleAction(actionDialog as any)}
            disabled={isProcessing}
            startIcon={isProcessing ? <CircularProgress size={20} /> : undefined}
            sx={{
              bgcolor: actionDialog === 'dismiss' ? '#f44336' : '#2196f3',
              '&:hover': {
                bgcolor: actionDialog === 'dismiss' ? '#d32f2f' : '#1976d2'
              }
            }}
          >
            {isProcessing ? 'PROCESSING...' : 'CONFIRM'}
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default ThreatActionPanel;
