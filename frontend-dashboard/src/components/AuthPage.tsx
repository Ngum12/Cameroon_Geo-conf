/**
 * 🛡️ PROJECT SENTINEL - DEFENSE AUTHENTICATION SYSTEM
 * Military-grade login/signup page with stunning video background
 * Cameroon Defense Force - Secure Access Portal
 */

import React, { useState, useEffect } from 'react';
import {
  Box, Card, Typography, TextField, Button, Tab, Tabs,
  InputAdornment, IconButton, Alert, CircularProgress,
  Checkbox, FormControlLabel, Divider, Fade, Slide, Chip
} from '@mui/material';
import {
  Visibility, VisibilityOff, Person, Lock, Email,
  Security as SecurityIcon, Shield as ShieldIcon,
  Flag as FlagIcon, Login as LoginIcon, PersonAdd as SignupIcon
} from '@mui/icons-material';
import { styled, keyframes } from '@mui/material/styles';

// 🎬 STUNNING ANIMATIONS
const MilitaryGlow = keyframes`
  0% { 
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
    border-color: rgba(0, 255, 136, 0.5);
  }
  50% { 
    box-shadow: 0 0 40px rgba(0, 255, 136, 0.6);
    border-color: rgba(0, 255, 136, 0.8);
  }
  100% { 
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
    border-color: rgba(0, 255, 136, 0.5);
  }
`;

const DefenseSlide = keyframes`
  0% { 
    transform: translateY(50px);
    opacity: 0;
  }
  100% { 
    transform: translateY(0);
    opacity: 1;
  }
`;

const PatriotPulse = keyframes`
  0% { 
    transform: scale(1);
    opacity: 0.8;
  }
  50% { 
    transform: scale(1.05);
    opacity: 1;
  }
  100% { 
    transform: scale(1);
    opacity: 0.8;
  }
`;

// 🎨 STYLED COMPONENTS
const VideoBackground = styled('video')({
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100%',
  height: '100%',
  objectFit: 'cover',
  zIndex: -2,
  filter: 'brightness(0.9) contrast(1.3) saturate(1.1)', // Much brighter and more professional
});

const VideoOverlay = styled(Box)({
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100%',
  height: '100%',
  background: 'linear-gradient(135deg, rgba(0, 0, 0, 0.2) 0%, rgba(0, 0, 0, 0.3) 50%, rgba(0, 0, 0, 0.5) 100%)',
  zIndex: -1,
});

const AuthCard = styled(Card)(({ theme }) => ({
  background: 'rgba(0, 0, 0, 0.85)',
  backdropFilter: 'blur(15px)',
  border: '2px solid rgba(0, 255, 136, 0.3)',
  borderRadius: '20px',
  padding: theme.spacing(4),
  minWidth: '450px',
  maxWidth: '500px',
  animation: `${DefenseSlide} 1s ease-out, ${MilitaryGlow} 3s ease-in-out infinite`,
  boxShadow: '0 20px 60px rgba(0, 0, 0, 0.8)',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: '-100%',
    width: '100%',
    height: '100%',
    background: 'linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.1), transparent)',
    animation: 'sweep 3s ease-in-out infinite',
  },
  '@keyframes sweep': {
    '0%': { left: '-100%' },
    '50%': { left: '100%' },
    '100%': { left: '100%' },
  }
}));

const MilitaryButton = styled(Button)(({ theme }) => ({
  background: 'linear-gradient(45deg, #00ff88 0%, #00cc6a 100%)',
  color: '#000',
  fontWeight: 'bold',
  fontSize: '1.1rem',
  padding: '12px 30px',
  borderRadius: '10px',
  textTransform: 'uppercase',
  letterSpacing: '1px',
  transition: 'all 0.3s ease',
  border: '2px solid transparent',
  '&:hover': {
    background: 'linear-gradient(45deg, #00cc6a 0%, #00ff88 100%)',
    transform: 'translateY(-2px)',
    boxShadow: '0 10px 30px rgba(0, 255, 136, 0.4)',
    border: '2px solid #00ff88',
  },
  '&:active': {
    transform: 'translateY(0)',
  }
}));

const DefenseTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    borderRadius: '10px',
    '& fieldset': {
      borderColor: 'rgba(0, 255, 136, 0.3)',
      borderWidth: '2px',
    },
    '&:hover fieldset': {
      borderColor: 'rgba(0, 255, 136, 0.6)',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#00ff88',
      boxShadow: '0 0 15px rgba(0, 255, 136, 0.3)',
    },
    '& input': {
      color: '#fff',
      fontSize: '1.1rem',
    }
  },
  '& .MuiInputLabel-root': {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: '1rem',
    '&.Mui-focused': {
      color: '#00ff88',
    }
  }
}));

interface AuthPageProps {
  onLogin: (credentials: { email: string; password: string }) => void;
  onSignup: (userData: { name: string; email: string; password: string; rank?: string }) => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({ onLogin, onSignup }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loginFormVisible, setLoginFormVisible] = useState(true);
  const [currentTextIndex, setCurrentTextIndex] = useState(0);

  // Login form state
  const [loginData, setLoginData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });

  // Signup form state
  const [signupData, setSignupData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    rank: '',
    agreeToTerms: false
  });

  // 🎬 VIDEO SOURCES - Military/Defense themed videos
  const militaryVideos = [
    '/videos/spy-military-pixabay.mp4', // Your Pixabay military video
    '/videos/military-background-1.mp4', // Additional military videos if available
    '/videos/defense-operations.mp4'
  ];

  const [currentVideo, setCurrentVideo] = useState(0);

  // 🎯 PROFESSIONAL INTELLIGENCE MESSAGES
  const professionalMessages = [
    {
      title: "🛡️ CAMEROON DEFENSE FORCE",
      subtitle: "ADVANCED INTELLIGENCE PLATFORM",
      description: "Real-time threat analysis • AI-powered predictions • National security"
    },
    {
      title: "🔒 CLASSIFIED ACCESS PORTAL",
      subtitle: "AUTHORIZED PERSONNEL ONLY",
      description: "Multi-layer authentication • Biometric verification • Secure protocols"
    },
    {
      title: "📡 SENTINET CAMEROON",
      subtitle: "GEOPOLITICAL INTELLIGENCE SYSTEM",
      description: "45+ Intelligence sources • 10 Regional commands • 24/7 monitoring"
    },
    {
      title: "🎯 DEFENSE ANALYTICS",
      subtitle: "PREDICTIVE THREAT ASSESSMENT",
      description: "Machine learning models • Pattern recognition • Risk mitigation"
    },
    {
      title: "🌍 NATIONAL SECURITY",
      subtitle: "PROTECTING CAMEROON",
      description: "Border surveillance • Counter-terrorism • Strategic intelligence"
    }
  ];

  useEffect(() => {
    // Cycle through videos every 30 seconds
    const videoInterval = setInterval(() => {
      setCurrentVideo(prev => (prev + 1) % militaryVideos.length);
    }, 30000);

    return () => clearInterval(videoInterval);
  }, [militaryVideos.length]);

  useEffect(() => {
    // Cycle through professional messages every 4 seconds
    const textInterval = setInterval(() => {
      setCurrentTextIndex(prev => (prev + 1) % professionalMessages.length);
    }, 4000);

    return () => clearInterval(textInterval);
  }, [professionalMessages.length]);

  const handleLogin = async () => {
    if (!loginData.email || !loginData.password) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setSuccess('🛡️ Access Granted - Welcome to Project Sentinel');
      setTimeout(() => {
        onLogin({
          email: loginData.email,
          password: loginData.password
        });
      }, 1500);
    } catch (err) {
      setError('Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async () => {
    if (!signupData.name || !signupData.email || !signupData.password || !signupData.confirmPassword) {
      setError('Please fill in all required fields');
      return;
    }

    if (signupData.password !== signupData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!signupData.agreeToTerms) {
      setError('Please agree to the terms and conditions');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setSuccess('🎖️ Registration Successful - Welcome to the Defense Force');
      setTimeout(() => {
        onSignup({
          name: signupData.name,
          email: signupData.email,
          password: signupData.password,
          rank: signupData.rank
        });
      }, 1500);
    } catch (err) {
      setError('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between',
      position: 'relative',
      overflow: 'hidden',
      padding: '20px'
    }}>
      {/* 🎬 MILITARY BACKGROUND VIDEO */}
      <VideoBackground
        autoPlay
        muted
        loop
        playsInline
        key={currentVideo}
        onError={(e) => {
          console.log('Video failed to load, trying next video...');
          // Try next video on error
          setCurrentVideo(prev => (prev + 1) % militaryVideos.length);
        }}
        onLoadStart={() => console.log('🎬 Loading military background video...')}
        onCanPlay={() => console.log('✅ Military video ready to play')}
      >
        <source src={militaryVideos[currentVideo]} type="video/mp4" />
        {/* Your military video will play here */}
      </VideoBackground>

      {/* 🌫️ VIDEO OVERLAY */}
      <VideoOverlay />

      {/* 🎯 PROFESSIONAL TEXT OVERLAY - LEFT SIDE */}
      <Box sx={{ 
        position: 'absolute',
        left: '5%',
        top: '50%',
        transform: 'translateY(-50%)',
        zIndex: 1,
        maxWidth: '500px'
      }}>
        <Fade in timeout={1000} key={currentTextIndex}>
          <Box>
            <Typography variant="h2" sx={{ 
              fontWeight: 'bold', 
              color: '#fff',
              textShadow: '3px 3px 6px rgba(0, 0, 0, 0.8)',
              mb: 2,
              fontSize: { xs: '2rem', md: '3rem' }
            }}>
              {professionalMessages[currentTextIndex].title}
            </Typography>
            
            <Typography variant="h5" sx={{ 
              color: '#00ff88',
              fontWeight: 'bold',
              letterSpacing: '2px',
              textShadow: '2px 2px 4px rgba(0, 0, 0, 0.8)',
              mb: 2
            }}>
              {professionalMessages[currentTextIndex].subtitle}
            </Typography>
            
            <Typography variant="h6" sx={{ 
              color: 'rgba(255, 255, 255, 0.9)',
              textShadow: '2px 2px 4px rgba(0, 0, 0, 0.8)',
              lineHeight: 1.6,
              fontSize: { xs: '1rem', md: '1.2rem' }
            }}>
              {professionalMessages[currentTextIndex].description}
            </Typography>

            {/* 🎖️ PROFESSIONAL BADGES */}
            <Box sx={{ display: 'flex', gap: 2, mt: 3, flexWrap: 'wrap' }}>
              <Chip 
                label="🔒 CLASSIFIED"
                sx={{ 
                  bgcolor: '#ff1744', 
                  color: '#fff', 
                  fontWeight: 'bold',
                  fontSize: '0.9rem',
                  padding: '8px 16px'
                }}
              />
              <Chip 
                label="🛡️ DEFENSE GRADE"
                sx={{ 
                  bgcolor: '#00ff88', 
                  color: '#000', 
                  fontWeight: 'bold',
                  fontSize: '0.9rem',
                  padding: '8px 16px'
                }}
              />
              <Chip 
                label="🇨🇲 CAMEROON"
                sx={{ 
                  bgcolor: '#ffaa00', 
                  color: '#000', 
                  fontWeight: 'bold',
                  fontSize: '0.9rem',
                  padding: '8px 16px'
                }}
              />
            </Box>
          </Box>
        </Fade>
      </Box>

      {/* 🛡️ COLLAPSIBLE AUTHENTICATION CARD - RIGHT SIDE */}
      <Box sx={{ 
        position: 'absolute',
        right: loginFormVisible ? '5%' : '-400px',
        top: '50%',
        transform: 'translateY(-50%)',
        transition: 'right 0.5s ease-in-out',
        zIndex: 2
      }}>
        {/* 🔄 TOGGLE BUTTON */}
        <IconButton
          onClick={() => setLoginFormVisible(!loginFormVisible)}
          sx={{
            position: 'absolute',
            left: '-60px',
            top: '50%',
            transform: 'translateY(-50%)',
            bgcolor: 'rgba(0, 255, 136, 0.9)',
            color: '#000',
            width: 50,
            height: 50,
            border: '2px solid #00ff88',
            '&:hover': {
              bgcolor: '#00ff88',
              transform: 'translateY(-50%) scale(1.1)'
            }
          }}
        >
          {loginFormVisible ? '→' : '←'}
        </IconButton>

        <Fade in={loginFormVisible} timeout={500}>
          <AuthCard>
          {/* 🇨🇲 HEADER SECTION */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              gap: 2, 
              mb: 2,
              animation: `${PatriotPulse} 2s ease-in-out infinite`
            }}>
              <ShieldIcon sx={{ fontSize: 48, color: '#00ff88' }} />
              <FlagIcon sx={{ fontSize: 48, color: '#ff1744' }} />
              <SecurityIcon sx={{ fontSize: 48, color: '#ffaa00' }} />
            </Box>
            
            <Typography variant="h4" sx={{ 
              fontWeight: 'bold', 
              color: '#fff',
              textShadow: '2px 2px 4px rgba(0, 0, 0, 0.8)',
              mb: 1
            }}>
              SENTINET CAMEROON
            </Typography>
            
            <Typography variant="h6" sx={{ 
              color: '#00ff88',
              fontWeight: 'bold',
              letterSpacing: '2px'
            }}>
              CAMEROON DEFENSE FORCE
            </Typography>
            
            <Typography variant="body2" sx={{ 
              color: 'rgba(255, 255, 255, 0.7)',
              mt: 1,
              fontStyle: 'italic'
            }}>
              Secure Access Portal • Defense Intelligence System
            </Typography>
          </Box>

          {/* 🎯 TABS */}
          <Tabs 
            value={activeTab} 
            onChange={(_, newValue) => setActiveTab(newValue)}
            centered
            sx={{
              mb: 3,
              '& .MuiTab-root': { 
                color: 'rgba(255, 255, 255, 0.7)',
                fontWeight: 'bold',
                fontSize: '1rem',
                textTransform: 'uppercase',
                letterSpacing: '1px'
              },
              '& .Mui-selected': { 
                color: '#00ff88' 
              },
              '& .MuiTabs-indicator': { 
                backgroundColor: '#00ff88',
                height: '3px'
              }
            }}
          >
            <Tab icon={<LoginIcon />} label="SECURE LOGIN" />
            <Tab icon={<SignupIcon />} label="ENLIST NOW" />
          </Tabs>

          {/* ⚠️ ERROR/SUCCESS ALERTS */}
          {error && (
            <Slide direction="down" in={!!error}>
              <Alert severity="error" sx={{ mb: 2, backgroundColor: 'rgba(255, 23, 68, 0.1)' }}>
                {error}
              </Alert>
            </Slide>
          )}

          {success && (
            <Slide direction="down" in={!!success}>
              <Alert severity="success" sx={{ mb: 2, backgroundColor: 'rgba(0, 255, 136, 0.1)' }}>
                {success}
              </Alert>
            </Slide>
          )}

          {/* 🔐 LOGIN FORM */}
          {activeTab === 0 && (
            <Fade in timeout={500}>
              <Box>
                <DefenseTextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={loginData.email}
                  onChange={(e) => setLoginData(prev => ({ ...prev, email: e.target.value }))}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Email sx={{ color: '#00ff88' }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={{ mb: 3 }}
                />

                <DefenseTextField
                  fullWidth
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  value={loginData.password}
                  onChange={(e) => setLoginData(prev => ({ ...prev, password: e.target.value }))}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock sx={{ color: '#00ff88' }} />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          sx={{ color: '#00ff88' }}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{ mb: 3 }}
                />

                <FormControlLabel
                  control={
                    <Checkbox 
                      checked={loginData.rememberMe}
                      onChange={(e) => setLoginData(prev => ({ ...prev, rememberMe: e.target.checked }))}
                      sx={{ color: '#00ff88' }}
                    />
                  }
                  label="Remember me on this device"
                  sx={{ color: '#fff', mb: 3 }}
                />

                <MilitaryButton
                  fullWidth
                  onClick={handleLogin}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <SecurityIcon />}
                  sx={{ mb: 2 }}
                >
                  {loading ? 'AUTHENTICATING...' : 'SECURE ACCESS'}
                </MilitaryButton>
              </Box>
            </Fade>
          )}

          {/* 📝 SIGNUP FORM */}
          {activeTab === 1 && (
            <Fade in timeout={500}>
              <Box>
                <DefenseTextField
                  fullWidth
                  label="Full Name"
                  value={signupData.name}
                  onChange={(e) => setSignupData(prev => ({ ...prev, name: e.target.value }))}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Person sx={{ color: '#00ff88' }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={{ mb: 2 }}
                />

                <DefenseTextField
                  fullWidth
                  label="Military Rank (Optional)"
                  value={signupData.rank}
                  onChange={(e) => setSignupData(prev => ({ ...prev, rank: e.target.value }))}
                  placeholder="e.g., Lieutenant, Captain, Major"
                  sx={{ mb: 2 }}
                />

                <DefenseTextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={signupData.email}
                  onChange={(e) => setSignupData(prev => ({ ...prev, email: e.target.value }))}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Email sx={{ color: '#00ff88' }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={{ mb: 2 }}
                />

                <DefenseTextField
                  fullWidth
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  value={signupData.password}
                  onChange={(e) => setSignupData(prev => ({ ...prev, password: e.target.value }))}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock sx={{ color: '#00ff88' }} />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          sx={{ color: '#00ff88' }}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{ mb: 2 }}
                />

                <DefenseTextField
                  fullWidth
                  label="Confirm Password"
                  type="password"
                  value={signupData.confirmPassword}
                  onChange={(e) => setSignupData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock sx={{ color: '#00ff88' }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={{ mb: 3 }}
                />

                <FormControlLabel
                  control={
                    <Checkbox 
                      checked={signupData.agreeToTerms}
                      onChange={(e) => setSignupData(prev => ({ ...prev, agreeToTerms: e.target.checked }))}
                      sx={{ color: '#00ff88' }}
                    />
                  }
                  label="I agree to the Defense Force Terms of Service and Privacy Policy"
                  sx={{ color: '#fff', mb: 3 }}
                />

                <MilitaryButton
                  fullWidth
                  onClick={handleSignup}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <ShieldIcon />}
                  sx={{ mb: 2 }}
                >
                  {loading ? 'ENLISTING...' : 'JOIN THE DEFENSE FORCE'}
                </MilitaryButton>
              </Box>
            </Fade>
          )}

          {/* 🔒 FOOTER */}
          <Divider sx={{ my: 3, borderColor: 'rgba(0, 255, 136, 0.3)' }} />
          
          <Typography variant="caption" sx={{ 
            textAlign: 'center', 
            color: 'rgba(255, 255, 255, 0.5)',
            display: 'block'
          }}>
            🛡️ Classified System • Authorized Personnel Only
          </Typography>
          
          <Typography variant="caption" sx={{ 
            textAlign: 'center', 
            color: 'rgba(255, 255, 255, 0.5)',
            display: 'block',
            mt: 1
          }}>
            🇨🇲 Republic of Cameroon • Ministry of Defense
          </Typography>
          </AuthCard>
        </Fade>
      </Box>

      {/* 🎖️ PROFESSIONAL STATUS BAR - BOTTOM */}
      <Box sx={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: '60px',
        background: 'linear-gradient(90deg, rgba(0, 0, 0, 0.8) 0%, rgba(0, 255, 136, 0.2) 50%, rgba(0, 0, 0, 0.8) 100%)',
        borderTop: '2px solid rgba(0, 255, 136, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 30px',
        zIndex: 3
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
          <Typography variant="body2" sx={{ color: '#00ff88', fontWeight: 'bold' }}>
            🟢 SYSTEM ONLINE
          </Typography>
          <Typography variant="body2" sx={{ color: '#fff' }}>
            🔒 SECURE CONNECTION
          </Typography>
          <Typography variant="body2" sx={{ color: '#fff' }}>
            🛡️ DEFENSE PROTOCOLS ACTIVE
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
          <Typography variant="body2" sx={{ color: '#aaa' }}>
            {new Date().toLocaleString()}
          </Typography>
          <Typography variant="body2" sx={{ color: '#00ff88', fontWeight: 'bold' }}>
            🇨🇲 YAOUNDÉ COMMAND CENTER
          </Typography>
        </Box>
      </Box>

      {/* 🎯 FLOATING SECURITY INDICATORS */}
      <Box sx={{
        position: 'absolute',
        top: '20px',
        right: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
        zIndex: 3
      }}>
        <Chip 
          label="🔐 ENCRYPTION: AES-256"
          size="small"
          sx={{ 
            bgcolor: 'rgba(0, 255, 136, 0.2)', 
            color: '#00ff88', 
            border: '1px solid rgba(0, 255, 136, 0.5)',
            fontFamily: 'monospace'
          }}
        />
        <Chip 
          label="🛡️ SECURITY: LEVEL 5"
          size="small"
          sx={{ 
            bgcolor: 'rgba(255, 23, 68, 0.2)', 
            color: '#ff1744', 
            border: '1px solid rgba(255, 23, 68, 0.5)',
            fontFamily: 'monospace'
          }}
        />
        <Chip 
          label="📡 UPLINK: ACTIVE"
          size="small"
          sx={{ 
            bgcolor: 'rgba(33, 150, 243, 0.2)', 
            color: '#2196f3', 
            border: '1px solid rgba(33, 150, 243, 0.5)',
            fontFamily: 'monospace'
          }}
        />
      </Box>
    </Box>
  );
};

export default AuthPage;