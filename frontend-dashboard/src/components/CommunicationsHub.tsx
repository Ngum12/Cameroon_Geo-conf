/**
 * 📡 COMMUNICATIONS HUB - THREAT-CONNECTED ALERT SYSTEM
 * Send targeted alerts based on actual threats detected by the system
 */

import React, { useState, useEffect } from 'react';
import {
  Box, Card, Typography, Grid, Button, 
  Chip, Checkbox, FormControlLabel, Alert, CircularProgress,
  TextField, IconButton, Divider
} from '@mui/material';
import {
  Email as EmailIcon,
  WhatsApp as WhatsAppIcon,
  Sms as SmsIcon,
  Send as SendIcon,
  Warning as WarningIcon,
  LocationOn as LocationIcon,
  Add as AddIcon,
  Person as PersonIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { alertMessagingService, AlertMessage } from '../services/alertMessagingService';
import { UnifiedThreatPoint } from '../services/threatIntelligence';

interface CommunicationsHubProps {
  threatData?: UnifiedThreatPoint[];
}

const ThreatCard = ({ 
  threat, 
  onSendAlert 
}: { 
  threat: UnifiedThreatPoint; 
  onSendAlert: (threat: UnifiedThreatPoint) => void;
}) => (
  <Card sx={{ 
    p: 2, 
    mb: 2, 
    background: threat.threatLevel >= 80 ? 'linear-gradient(135deg, #5d1a1a 0%, #3a1a1a 100%)' :
                threat.threatLevel >= 60 ? 'linear-gradient(135deg, #5d3a1a 0%, #3a2a1a 100%)' :
                'linear-gradient(135deg, #1a3a5d 0%, #1a2a3a 100%)',
    border: threat.threatLevel >= 80 ? '1px solid #ff1744' :
            threat.threatLevel >= 60 ? '1px solid #ff9800' :
            '1px solid #2196f3'
  }}>
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <Box sx={{ flex: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <WarningIcon sx={{ 
            mr: 1, 
            color: threat.threatLevel >= 80 ? '#ff1744' :
                   threat.threatLevel >= 60 ? '#ff9800' : '#2196f3' 
          }} />
          <Typography variant="h6" sx={{ color: '#fff', fontWeight: 'bold' }}>
            {threat.title}
          </Typography>
          <Chip 
            label={`${Math.round(threat.threatLevel)}%`}
            size="small" 
            sx={{ 
              ml: 2,
              bgcolor: threat.threatLevel >= 80 ? '#ff1744' :
                       threat.threatLevel >= 60 ? '#ff9800' : '#2196f3',
              color: '#fff'
            }} 
          />
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <LocationIcon sx={{ fontSize: 16, color: '#aaa', mr: 1 }} />
          <Typography variant="body2" sx={{ color: '#aaa' }}>
            {threat.region} • {new Date().toLocaleString()}
          </Typography>
        </Box>
        
        <Typography variant="body2" sx={{ color: '#fff', mb: 2 }}>
          {threat.description}
        </Typography>
        
        <Typography variant="caption" sx={{ color: '#aaa' }}>
          Threat Level: {Math.round(threat.threatLevel)}% • Region: {threat.region}
        </Typography>
      </Box>
      
      <Button
        variant="contained"
        size="small"
        startIcon={<SendIcon />}
        onClick={() => onSendAlert(threat)}
        sx={{
          ml: 2,
          bgcolor: threat.threatLevel >= 80 ? '#ff1744' :
                   threat.threatLevel >= 60 ? '#ff9800' : '#2196f3',
          '&:hover': {
            bgcolor: threat.threatLevel >= 80 ? '#d50000' :
                     threat.threatLevel >= 60 ? '#e65100' : '#1976d2'
          }
        }}
      >
        ALERT
      </Button>
    </Box>
  </Card>
);

const CommunicationsHub: React.FC<CommunicationsHubProps> = ({ threatData = [] }) => {
  const [selectedThreat, setSelectedThreat] = useState<UnifiedThreatPoint | null>(null);
  const [selectedChannels, setSelectedChannels] = useState<string[]>(['email']);
  const [selectedRecipients, setSelectedRecipients] = useState<string[]>([]);
  const [recipients, setRecipients] = useState<any[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [lastAlertResult, setLastAlertResult] = useState<any>(null);
  const [customMessage, setCustomMessage] = useState<string>('');
  
  // Human-approved threats are now passed via props from App.tsx
  
  // Custom contact management
  const [customContacts, setCustomContacts] = useState<any[]>([]);
  const [newContactName, setNewContactName] = useState('');
  const [newContactEmail, setNewContactEmail] = useState('');
  const [newContactPhone, setNewContactPhone] = useState('');
  const [newContactRole, setNewContactRole] = useState('');

  useEffect(() => {
    setRecipients(alertMessagingService.getRecipients());
    
    // Load custom contacts from localStorage
    const savedContacts = localStorage.getItem('sentinel-custom-contacts');
    if (savedContacts) {
      setCustomContacts(JSON.parse(savedContacts));
    }
    
    // Listen for Human-in-Loop approved threats
    const handleCommsPrefill = (event: CustomEvent) => {
      const { notificationId, title, region, threatLevel, description, verificationStatus, urgency } = event.detail;
      console.log('📡 Communications Hub: RECEIVED approved threat event!', event.detail);
      console.log('📡 Communications Hub: Component is active and processing threat');
      
      // Create threat object for communications hub
      const verifiedThreat = {
        id: notificationId || `verified-${Date.now()}`,
        title: title || 'Verified Threat Alert',
        region: region || 'Unknown',
        threatLevel: threatLevel || 85,
        category: 'verified_threat',
        description: description || 'Human verified threat requiring immediate response',
        priority: urgency === 'critical' ? 'critical' : 'high',
        confidence: verificationStatus === 'human_approved' ? 0.95 : 0.85,
        timestamp: new Date()
      };
      
      setSelectedThreat(verifiedThreat);
      
      // For human-approved threats, select ALL channels for maximum reach
      setSelectedChannels(['email', 'whatsapp', 'sms']);
      
      // Auto-select emergency and regional recipients
      const emergencyRecipients = [...recipients, ...customContacts].filter(r => 
        r.role?.includes('Emergency') || 
        r.role?.includes('Command') ||
        r.region === region ||
        r.region === 'All'
      );
      setSelectedRecipients(emergencyRecipients.map(r => r.id));
      
      // Auto-populate custom message with professional format (editable)
      const autoMessage = `🚨🇨🇲 HARMONY FLOW ALERT

🎯 THREAT: ${verifiedThreat.title.replace('VERIFIED THREAT: ', '')}
📊 LEVEL: ${verifiedThreat.threatLevel >= 90 ? 'CRITICAL' : verifiedThreat.threatLevel >= 70 ? 'HIGH' : 'MEDIUM'} (${verifiedThreat.threatLevel}%)
📍 REGION: ${verifiedThreat.region}

${verifiedThreat.description.length > 200 ? verifiedThreat.description.substring(0, 200) + '...' : verifiedThreat.description}

⚠️ ${verificationStatus === 'human_approved' ? 'HUMAN VERIFIED' : 'SYSTEM ESCALATED'} - Immediate response required

👤 TO: Defense Command Center
🕒 ${new Date().toLocaleString()}

🛡️ Harmony Flow Defense System`;
      
      setCustomMessage(autoMessage);
      
      console.log('📡 Communications Hub loaded with verified threat:', verifiedThreat);
    };
    
    window.addEventListener('sentinel:navigate-comms-hub', handleCommsPrefill as EventListener);
    
    return () => {
      window.removeEventListener('sentinel:navigate-comms-hub', handleCommsPrefill as EventListener);
    };
  }, [recipients, customContacts]);

  // Save custom contacts to localStorage
  const saveCustomContacts = (contacts: any[]) => {
    localStorage.setItem('sentinel-custom-contacts', JSON.stringify(contacts));
    setCustomContacts(contacts);
  };

  // Only show threats that come from Human-in-Loop approval (passed via props)
  const criticalThreats = threatData.filter(t => t.threatLevel >= 60);

  const handleChannelChange = (channel: string) => {
    setSelectedChannels(prev => 
      prev.includes(channel) 
        ? prev.filter(c => c !== channel)
        : [...prev, channel]
    );
  };

  const handleRecipientChange = (recipientId: string) => {
    setSelectedRecipients(prev => 
      prev.includes(recipientId) 
        ? prev.filter(id => id !== recipientId)
        : [...prev, recipientId]
    );
  };

  const getRelevantRecipients = (threat: UnifiedThreatPoint) => {
    // Combine system recipients and custom contacts
    const systemRecipients = recipients.filter(recipient => {
      // Filter by region
      if (recipient.region === 'All') return true;
      if (recipient.region === threat.region) return true;
      
      // Filter by threat level vs recipient priority
      if (threat.threatLevel >= 80 && recipient.priority === 'critical') return true;
      if (threat.threatLevel >= 60 && (recipient.priority === 'critical' || recipient.priority === 'high')) return true;
      
      return false;
    });

    // Add all custom contacts (they're always relevant for manual selection)
    const allRelevantRecipients = [...systemRecipients, ...customContacts];
    return allRelevantRecipients;
  };

  const addCustomContact = () => {
    if (!newContactName.trim() || !newContactEmail.trim() || !newContactPhone.trim()) {
      alert('Please fill in all contact fields (Name, Email, Phone)');
      return;
    }

    const newContact = {
      id: `custom-${Date.now()}`,
      name: newContactName.trim(),
      email: newContactEmail.trim(),
      phone: newContactPhone.trim(),
      role: newContactRole.trim() || 'Custom Contact',
      region: 'Custom',
      priority: 'high',
      isCustom: true
    };

    const updatedContacts = [...customContacts, newContact];
    saveCustomContacts(updatedContacts);

    // Clear form
    setNewContactName('');
    setNewContactEmail('');
    setNewContactPhone('');
    setNewContactRole('');
  };

  const removeCustomContact = (contactId: string) => {
    const updatedContacts = customContacts.filter(c => c.id !== contactId);
    saveCustomContacts(updatedContacts);
    
    // Remove from selected recipients if it was selected
    setSelectedRecipients(prev => prev.filter(id => id !== contactId));
  };

  const handleSendAlert = async (threat: UnifiedThreatPoint) => {
    setSelectedThreat(threat);
    
    // Auto-select relevant recipients
    const relevantRecipients = getRelevantRecipients(threat);
    setSelectedRecipients(relevantRecipients.map(r => r.id));
    
    // Auto-select all channels for critical threats
    if (threat.threatLevel >= 80) {
      setSelectedChannels(['email', 'whatsapp', 'sms']);
    }
    
    // Generate professional message template (editable)
    const defaultMessage = `🚨🇨🇲 HARMONY FLOW ALERT

🎯 THREAT: ${threat.title}
📊 LEVEL: ${threat.threatLevel >= 90 ? 'CRITICAL' : threat.threatLevel >= 70 ? 'HIGH' : 'MEDIUM'} (${threat.threatLevel}%)
📍 REGION: ${threat.region}

${threat.description ? (threat.description.length > 200 ? threat.description.substring(0, 200) + '...' : threat.description) : 'Intelligence monitoring has detected elevated threat activity requiring immediate attention.'}

⚠️ SYSTEM ALERT - Immediate response required

👤 TO: Defense Command Center
🕒 ${new Date().toLocaleString()}

🛡️ Harmony Flow Defense System`;
    
    setCustomMessage(defaultMessage);
  };

  const handleSendConfirmed = async () => {
    console.log('📡 Communications Hub: Attempting to send alert...');
    console.log('   Selected Threat:', selectedThreat);
    console.log('   Selected Channels:', selectedChannels);
    console.log('   Selected Recipients:', selectedRecipients);
    console.log('   Custom Message Length:', customMessage?.length);
    
    if (!selectedThreat || selectedChannels.length === 0 || selectedRecipients.length === 0 || !customMessage.trim()) {
      console.log('❌ Communications Hub: Missing required fields for sending alert');
      console.log('   Has Threat:', !!selectedThreat);
      console.log('   Has Channels:', selectedChannels.length > 0);
      console.log('   Has Recipients:', selectedRecipients.length > 0);
      console.log('   Has Message:', !!customMessage?.trim());
      return;
    }

    console.log('✅ Communications Hub: All requirements met, sending alert...');
    setIsSending(true);
    try {
      const alertMessage: AlertMessage = {
        id: `threat-${Date.now()}`,
        title: `🚨 THREAT ALERT: ${selectedThreat.title}`,
        message: customMessage, // Use the custom/edited message
        urgency: selectedThreat.threatLevel >= 80 ? 'critical' : 
                 selectedThreat.threatLevel >= 60 ? 'high' : 'medium',
        category: 'security_threat',
        timestamp: new Date(),
        region: selectedThreat.region,
        coordinates: { lat: 0, lng: 0 }
      };

      // Send to selected recipients via selected channels
      console.log('📡 Communications Hub: Calling alertMessagingService.sendCriticalAlert...');
      console.log('   Alert Message:', alertMessage);
      console.log('   Target Recipients:', selectedRecipients);
      
      const results = await alertMessagingService.sendCriticalAlert(alertMessage, selectedRecipients);
      
      console.log('📡 Communications Hub: Alert service results:', results);
      
      setLastAlertResult({
        threat: selectedThreat.title,
        channels: selectedChannels,
        recipients: selectedRecipients.length,
        results
      });

      // Reset selection
      setSelectedThreat(null);
      setSelectedChannels(['email']);
      setSelectedRecipients([]);
      setCustomMessage(''); // Clear custom message
      
    } finally {
      setIsSending(false);
    }
  };

  return (
    <Box sx={{ p: 3, background: '#0a0a0a', minHeight: '100vh' }}>
      <Typography variant="h4" sx={{ mb: 4, color: '#00ff88', fontWeight: 'bold', textAlign: 'center' }}>
        📡 THREAT-CONNECTED ALERT SYSTEM
      </Typography>

      <Grid container spacing={3}>
        
        {/* LEFT COLUMN - Active Threats */}
        <Grid item xs={12} md={8}>
          <Card sx={{ 
            p: 3, 
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            border: '1px solid #00ff88'
          }}>
            <Typography variant="h6" sx={{ mb: 3, color: '#00ff88', fontWeight: 'bold' }}>
              🚨 HUMAN-APPROVED THREATS READY FOR ALERTS
            </Typography>
            
            {criticalThreats.length === 0 ? (
              <Alert severity="info" sx={{ bgcolor: 'rgba(33, 150, 243, 0.1)' }}>
                Waiting for Human-in-Loop approval. No threats ready for alert dispatch.
              </Alert>
            ) : (
              <Box sx={{ maxHeight: '60vh', overflow: 'auto' }}>
                {criticalThreats.map((threat, index) => (
                  <ThreatCard 
                    key={index} 
                    threat={threat} 
                    onSendAlert={handleSendAlert}
                  />
                ))}
              </Box>
            )}
          </Card>

          {/* Alert Result */}
          {lastAlertResult && (
            <Card sx={{ 
              p: 3, 
              mt: 3,
              background: 'linear-gradient(135deg, #1a2e1a 0%, #163e21 100%)',
              border: '1px solid #4caf50'
            }}>
              <Typography variant="h6" sx={{ mb: 2, color: '#4caf50', fontWeight: 'bold' }}>
                ✅ ALERT SENT SUCCESSFULLY
              </Typography>
              <Typography variant="body2" sx={{ color: '#fff', mb: 1 }}>
                <strong>Threat:</strong> {lastAlertResult.threat}
              </Typography>
              <Typography variant="body2" sx={{ color: '#fff', mb: 1 }}>
                <strong>Channels Used:</strong> {lastAlertResult.channels.join(', ').toUpperCase()}
              </Typography>
              <Typography variant="body2" sx={{ color: '#fff' }}>
                <strong>Recipients:</strong> {lastAlertResult.recipients} personnel notified
              </Typography>
            </Card>
          )}
        </Grid>

        {/* RIGHT COLUMN - Alert Configuration */}
        <Grid item xs={12} md={4}>
          
          {selectedThreat && (
            <Card sx={{ 
              p: 3, 
              mb: 3,
              background: 'linear-gradient(135deg, #2e1a1a 0%, #3e2116 100%)',
              border: '1px solid #ff9800'
            }}>
              <Typography variant="h6" sx={{ mb: 3, color: '#ff9800', fontWeight: 'bold' }}>
                ⚙️ CONFIGURE ALERT
              </Typography>
              
              <Typography variant="body2" sx={{ color: '#fff', mb: 2, fontWeight: 'bold' }}>
                Selected Threat:
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa', mb: 3 }}>
                {selectedThreat.title} ({Math.round(selectedThreat.threatLevel)}%)
              </Typography>

              {/* Channel Selection */}
              <Typography variant="body2" sx={{ color: '#fff', mb: 2, fontWeight: 'bold' }}>
                📡 Select Channels:
              </Typography>
              <Box sx={{ mb: 3 }}>
                {[
                  { id: 'email', label: 'EMAIL', icon: EmailIcon, color: '#2196f3' },
                  { id: 'whatsapp', label: 'WHATSAPP', icon: WhatsAppIcon, color: '#4caf50' },
                  { id: 'sms', label: 'SMS', icon: SmsIcon, color: '#ff9800' }
                ].map(channel => (
                  <FormControlLabel
                    key={channel.id}
                    control={
                      <Checkbox
                        checked={selectedChannels.includes(channel.id)}
                        onChange={() => handleChannelChange(channel.id)}
                        sx={{ color: channel.color }}
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <channel.icon sx={{ mr: 1, color: channel.color }} />
                        {channel.label}
                      </Box>
                    }
                    sx={{ display: 'block', mb: 1, color: '#fff' }}
                  />
                ))}
              </Box>

              {/* Recipient Selection */}
              <Typography variant="body2" sx={{ color: '#fff', mb: 2, fontWeight: 'bold' }}>
                👥 Select Recipients:
              </Typography>
              <Box sx={{ maxHeight: 200, overflow: 'auto', mb: 3 }}>
                {getRelevantRecipients(selectedThreat).map(recipient => (
                  <FormControlLabel
                    key={recipient.id}
                    control={
                      <Checkbox
                        checked={selectedRecipients.includes(recipient.id)}
                        onChange={() => handleRecipientChange(recipient.id)}
                        sx={{ color: '#00ff88' }}
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {recipient.isCustom && <PersonIcon sx={{ color: '#4caf50', fontSize: 16 }} />}
                        <Box>
                          <Typography variant="body2" sx={{ color: '#fff' }}>
                            {recipient.name} {recipient.isCustom && '(Custom)'}
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#aaa' }}>
                            {recipient.role} - {recipient.region}
                          </Typography>
                        </Box>
                      </Box>
                    }
                    sx={{ display: 'block', mb: 1 }}
                  />
                ))}
              </Box>

              {/* Message Editor */}
              <Typography variant="body2" sx={{ color: '#fff', mb: 2, fontWeight: 'bold' }}>
                ✏️ Edit Alert Message:
              </Typography>
              <TextField
                multiline
                rows={8}
                fullWidth
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                placeholder="Enter your custom alert message..."
                sx={{ 
                  mb: 3,
                  '& .MuiOutlinedInput-root': { 
                    color: '#fff',
                    fontSize: '0.9rem',
                    '& fieldset': { borderColor: '#666' },
                    '&:hover fieldset': { borderColor: '#ff9800' },
                    '&.Mui-focused fieldset': { borderColor: '#ff9800' }
                  },
                  '& .MuiInputBase-input': {
                    fontFamily: 'monospace',
                    lineHeight: '1.4'
                  }
                }}
              />

              {/* Send Button */}
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={isSending ? <CircularProgress size={20} /> : <SendIcon />}
                onClick={handleSendConfirmed}
                disabled={isSending || selectedChannels.length === 0 || selectedRecipients.length === 0 || !customMessage.trim()}
                sx={{
                  py: 2,
                  bgcolor: '#ff1744',
                  '&:hover': { bgcolor: '#d50000' },
                  fontSize: '1.1rem',
                  fontWeight: 'bold'
                }}
              >
                {isSending ? 'SENDING ALERT...' : `SEND VIA ${selectedChannels.length} CHANNEL${selectedChannels.length !== 1 ? 'S' : ''}`}
              </Button>

              <Button
                fullWidth
                variant="outlined"
                size="small"
                onClick={() => {
                  setSelectedThreat(null);
                  setCustomMessage('');
                }}
                sx={{ mt: 1, borderColor: '#666', color: '#666' }}
              >
                CANCEL
              </Button>
            </Card>
          )}

          {/* Custom Contacts Management */}
          <Card sx={{ 
            p: 3, 
            mb: 3,
            background: 'linear-gradient(135deg, #1a2e1a 0%, #2a3e2a 100%)',
            border: '1px solid #4caf50'
          }}>
            <Typography variant="h6" sx={{ mb: 2, color: '#4caf50', fontWeight: 'bold' }}>
              ➕ ADD CUSTOM CONTACT
            </Typography>
            <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
              Add additional personnel not in the system directory
            </Typography>
            
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  size="small"
                  label="Full Name"
                  value={newContactName}
                  onChange={(e) => setNewContactName(e.target.value)}
                  sx={{ 
                    '& .MuiOutlinedInput-root': { 
                      color: '#fff',
                      '& fieldset': { borderColor: '#666' },
                      '&:hover fieldset': { borderColor: '#4caf50' },
                      '&.Mui-focused fieldset': { borderColor: '#4caf50' }
                    },
                    '& .MuiInputLabel-root': { color: '#aaa' }
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  size="small"
                  label="Role/Position"
                  value={newContactRole}
                  onChange={(e) => setNewContactRole(e.target.value)}
                  sx={{ 
                    '& .MuiOutlinedInput-root': { 
                      color: '#fff',
                      '& fieldset': { borderColor: '#666' },
                      '&:hover fieldset': { borderColor: '#4caf50' },
                      '&.Mui-focused fieldset': { borderColor: '#4caf50' }
                    },
                    '& .MuiInputLabel-root': { color: '#aaa' }
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  size="small"
                  label="Email Address"
                  type="email"
                  value={newContactEmail}
                  onChange={(e) => setNewContactEmail(e.target.value)}
                  sx={{ 
                    '& .MuiOutlinedInput-root': { 
                      color: '#fff',
                      '& fieldset': { borderColor: '#666' },
                      '&:hover fieldset': { borderColor: '#4caf50' },
                      '&.Mui-focused fieldset': { borderColor: '#4caf50' }
                    },
                    '& .MuiInputLabel-root': { color: '#aaa' }
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  size="small"
                  label="Phone Number"
                  value={newContactPhone}
                  onChange={(e) => setNewContactPhone(e.target.value)}
                  sx={{ 
                    '& .MuiOutlinedInput-root': { 
                      color: '#fff',
                      '& fieldset': { borderColor: '#666' },
                      '&:hover fieldset': { borderColor: '#4caf50' },
                      '&.Mui-focused fieldset': { borderColor: '#4caf50' }
                    },
                    '& .MuiInputLabel-root': { color: '#aaa' }
                  }}
                />
              </Grid>
            </Grid>
            
            <Button
              fullWidth
              variant="contained"
              startIcon={<AddIcon />}
              onClick={addCustomContact}
              sx={{
                bgcolor: '#4caf50',
                '&:hover': { bgcolor: '#388e3c' }
              }}
            >
              ADD CONTACT
            </Button>

            {/* Custom Contacts List */}
            {customContacts.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Divider sx={{ mb: 2, borderColor: '#666' }} />
                <Typography variant="body2" sx={{ color: '#4caf50', fontWeight: 'bold', mb: 2 }}>
                  CUSTOM CONTACTS ({customContacts.length})
                </Typography>
                {customContacts.map((contact) => (
                  <Box key={contact.id} sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    p: 1,
                    mb: 1,
                    bgcolor: 'rgba(76, 175, 80, 0.1)',
                    borderRadius: 1
                  }}>
                    <Box>
                      <Typography variant="body2" sx={{ color: '#fff', fontWeight: 'bold' }}>
                        {contact.name}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#aaa' }}>
                        {contact.role} • {contact.email} • {contact.phone}
                      </Typography>
                    </Box>
                    <IconButton
                      size="small"
                      onClick={() => removeCustomContact(contact.id)}
                      sx={{ color: '#f44336' }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                ))}
              </Box>
            )}
          </Card>

          {/* Instructions */}
          <Card sx={{ 
            p: 3, 
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            border: '1px solid #666'
          }}>
            <Typography variant="h6" sx={{ mb: 2, color: '#666', fontWeight: 'bold' }}>
              📋 INSTRUCTIONS
            </Typography>
            <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
              1. Human-in-Loop approves critical threats
            </Typography>
            <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
              2. Approved threats appear here automatically
            </Typography>
            <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
              3. Click "ALERT" to configure and send
            </Typography>
            <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
              4. Add custom contacts for broader reach
            </Typography>
            <Typography variant="body2" sx={{ color: '#aaa' }}>
              5. Select WhatsApp/SMS channels and send alerts
            </Typography>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CommunicationsHub;