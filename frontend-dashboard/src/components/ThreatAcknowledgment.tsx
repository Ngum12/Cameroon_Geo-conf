/**
 * 🎯 THREAT ACKNOWLEDGMENT PAGE - Defense Threat Response System
 * Dedicated page for acknowledging threats and logging operator response
 */

import React, { useState } from 'react';
import {
  Box, Card, Typography, Button, TextField, Grid, Chip,
  Alert, LinearProgress, List, ListItem, ListItemIcon, ListItemText,
  Divider, Stepper, Step, StepLabel
} from '@mui/material';
import {
  Check as CheckIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  LocationOn as LocationIcon,
  Security as SecurityIcon,
  Assignment as AssignmentIcon,
  Send as SendIcon,
  ArrowBack as BackIcon
} from '@mui/icons-material';
import { IntelligenceNotification } from '../services/notificationService';

interface ThreatAcknowledgmentProps {
  threat: IntelligenceNotification | null;
  onComplete: () => void;
  onBack: () => void;
}

const ThreatAcknowledgment: React.FC<ThreatAcknowledgmentProps> = ({
  threat,
  onComplete,
  onBack
}) => {
  const [step, setStep] = useState(0);
  const [acknowledgmentNotes, setAcknowledgmentNotes] = useState('');
  const [operatorId, setOperatorId] = useState('DEF-OPR-001');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleAcknowledge = async () => {
    if (!threat) return;
    
    setIsProcessing(true);
    
    // Simulate acknowledgment processing
    for (let i = 0; i <= 3; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setStep(i);
    }
    
    console.log(`✅ Threat acknowledged: ${threat.title}`);
    console.log(`👤 Operator: ${operatorId}`);
    console.log(`📝 Notes: ${acknowledgmentNotes}`);
    
    setTimeout(() => {
      onComplete();
    }, 2000);
  };

  if (!threat) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="error">
          No threat data available
        </Typography>
        <Button onClick={onBack} startIcon={<BackIcon />} sx={{ mt: 2 }}>
          Go Back
        </Button>
      </Box>
    );
  }

  const steps = [
    'Threat Review',
    'Operator Verification', 
    'Documentation',
    'Acknowledgment Complete'
  ];

  return (
    <Box sx={{ p: 3, maxWidth: 1200, margin: '0 auto' }}>
      
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ color: '#4caf50', fontWeight: 'bold' }}>
          ✅ THREAT ACKNOWLEDGMENT SYSTEM
        </Typography>
        <Button 
          variant="outlined" 
          startIcon={<BackIcon />} 
          onClick={onBack}
          sx={{ borderColor: '#666', color: '#666' }}
        >
          Back to Dashboard
        </Button>
      </Box>

      {/* Progress Stepper */}
      <Card sx={{ p: 3, mb: 3, bgcolor: 'rgba(76, 175, 80, 0.1)', border: '1px solid #4caf50' }}>
        <Stepper activeStep={step} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        {isProcessing && <LinearProgress sx={{ mt: 2 }} />}
      </Card>

      <Grid container spacing={3}>
        
        {/* Left Column - Threat Details */}
        <Grid item xs={12} lg={6}>
          <Card sx={{ p: 3, height: '100%', border: '1px solid #ff9800' }}>
            <Typography variant="h6" sx={{ mb: 3, color: '#ff9800', fontWeight: 'bold' }}>
              🎯 THREAT DETAILS
            </Typography>
            
            <List>
              <ListItem>
                <ListItemIcon><SecurityIcon sx={{ color: '#ff1744' }} /></ListItemIcon>
                <ListItemText 
                  primary="Threat Title"
                  secondary={threat.title}
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon><LocationIcon sx={{ color: '#2196f3' }} /></ListItemIcon>
                <ListItemText 
                  primary="Region"
                  secondary={threat.region || 'Unknown'}
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon><ScheduleIcon sx={{ color: '#9c27b0' }} /></ListItemIcon>
                <ListItemText 
                  primary="Timestamp"
                  secondary={threat.timestamp.toLocaleString()}
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon><AssignmentIcon sx={{ color: '#607d8b' }} /></ListItemIcon>
                <ListItemText 
                  primary="Source"
                  secondary={threat.source}
                />
              </ListItem>
            </List>
            
            <Divider sx={{ my: 2 }} />
            
            <Box sx={{ p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ color: '#fff', fontWeight: 'bold', mb: 1 }}>
                Threat Description:
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                {threat.message}
              </Typography>
            </Box>
            
            <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip 
                label={threat.priority.toUpperCase()} 
                color={threat.priority === 'critical' ? 'error' : 'warning'}
                size="small"
              />
              <Chip 
                label={threat.category.toUpperCase()} 
                variant="outlined"
                size="small"
              />
              {threat.threatLevel && (
                <Chip 
                  label={`${threat.threatLevel}% THREAT LEVEL`}
                  sx={{ bgcolor: '#ff1744', color: '#fff' }}
                  size="small"
                />
              )}
            </Box>
          </Card>
        </Grid>

        {/* Right Column - Acknowledgment Form */}
        <Grid item xs={12} lg={6}>
          <Card sx={{ p: 3, height: '100%', border: '1px solid #4caf50' }}>
            <Typography variant="h6" sx={{ mb: 3, color: '#4caf50', fontWeight: 'bold' }}>
              📝 ACKNOWLEDGMENT FORM
            </Typography>
            
            <Alert severity="info" sx={{ mb: 3 }}>
              By acknowledging this threat, you confirm that you have reviewed the intelligence and 
              that appropriate measures will be taken according to defense protocols.
            </Alert>
            
            <Box sx={{ mb: 3 }}>
              <TextField
                fullWidth
                label="Operator ID"
                value={operatorId}
                onChange={(e) => setOperatorId(e.target.value)}
                required
                sx={{
                  '& .MuiOutlinedInput-root': { color: '#fff' },
                  '& .MuiInputLabel-root': { color: '#aaa' },
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#666' }
                }}
              />
            </Box>
            
            <Box sx={{ mb: 3 }}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Acknowledgment Notes"
                value={acknowledgmentNotes}
                onChange={(e) => setAcknowledgmentNotes(e.target.value)}
                placeholder="Enter your assessment, actions taken, or additional notes..."
                sx={{
                  '& .MuiOutlinedInput-root': { color: '#fff' },
                  '& .MuiInputLabel-root': { color: '#aaa' },
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#666' }
                }}
              />
            </Box>
            
            {step < 3 ? (
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={<CheckIcon />}
                onClick={handleAcknowledge}
                disabled={isProcessing || !operatorId.trim()}
                sx={{
                  py: 2,
                  bgcolor: '#4caf50',
                  '&:hover': { bgcolor: '#388e3c' },
                  fontWeight: 'bold'
                }}
              >
                {isProcessing ? 'PROCESSING ACKNOWLEDGMENT...' : 'ACKNOWLEDGE THREAT'}
              </Button>
            ) : (
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6" sx={{ color: '#4caf50', mb: 2 }}>
                  ✅ THREAT ACKNOWLEDGED SUCCESSFULLY
                </Typography>
                <Typography variant="body2" sx={{ color: '#aaa', mb: 3 }}>
                  The threat has been logged and escalation protocols have been stopped.
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={onComplete}
                  sx={{ fontWeight: 'bold' }}
                >
                  RETURN TO DASHBOARD
                </Button>
              </Box>
            )}
          </Card>
        </Grid>
      </Grid>
      
      {/* Action Log */}
      <Card sx={{ mt: 3, p: 3, border: '1px solid #607d8b' }}>
        <Typography variant="h6" sx={{ mb: 2, color: '#607d8b', fontWeight: 'bold' }}>
          📋 ACTION LOG
        </Typography>
        <List dense>
          <ListItem>
            <ListItemIcon><PersonIcon sx={{ color: '#4caf50' }} /></ListItemIcon>
            <ListItemText 
              primary="Operator Access"
              secondary={`${operatorId} accessed threat acknowledgment system`}
            />
          </ListItem>
          <ListItem>
            <ListItemIcon><SecurityIcon sx={{ color: '#ff9800' }} /></ListItemIcon>
            <ListItemText 
              primary="Threat Analysis"
              secondary={`Reviewing ${threat.priority} priority threat in ${threat.region}`}
            />
          </ListItem>
          {step >= 2 && (
            <ListItem>
              <ListItemIcon><AssignmentIcon sx={{ color: '#2196f3' }} /></ListItemIcon>
              <ListItemText 
                primary="Documentation"
                secondary="Operator notes and assessment recorded"
              />
            </ListItem>
          )}
          {step >= 3 && (
            <ListItem>
              <ListItemIcon><CheckIcon sx={{ color: '#4caf50' }} /></ListItemIcon>
              <ListItemText 
                primary="Acknowledgment Complete"
                secondary={`Threat acknowledged at ${new Date().toLocaleString()}`}
              />
            </ListItem>
          )}
        </List>
      </Card>
    </Box>
  );
};

export default ThreatAcknowledgment;
