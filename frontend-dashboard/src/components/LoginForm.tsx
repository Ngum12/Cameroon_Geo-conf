/**
 * 🔐 PROJECT SENTINEL - LOGIN COMPONENT
 * Stunning military-grade login interface
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  IconButton,
  InputAdornment,
  Checkbox,
  FormControlLabel,
  Alert,
  CircularProgress,
  Divider,
  Link,
  Avatar,
  Stack,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Security,
  Person,
  Lock,
  LoginOutlined,
  Shield,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { LoginCredentials } from '../services/authService';

interface LoginFormProps {
  onSwitchToRegister?: () => void;
  onLoginSuccess?: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({
  onSwitchToRegister,
  onLoginSuccess
}) => {
  const { login, loading, error, clearError } = useAuth();
  
  const [credentials, setCredentials] = useState<LoginCredentials>({
    username: '',
    password: '',
    remember_me: false,
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [validationErrors, setValidationErrors] = useState<{[key: string]: string}>({});

  // Clear error when component unmounts or credentials change
  useEffect(() => {
    if (error) {
      const timer = setTimeout(clearError, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, clearError]);

  const handleInputChange = (field: keyof LoginCredentials) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = field === 'remember_me' ? event.target.checked : event.target.value;
    setCredentials(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
    
    clearError();
  };

  const validateForm = (): boolean => {
    const errors: {[key: string]: string} = {};
    
    if (!credentials.username.trim()) {
      errors.username = 'Username is required';
    }
    
    if (!credentials.password) {
      errors.password = 'Password is required';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      await login(credentials);
      onLoginSuccess?.();
    } catch (error) {
      // Error is handled by the auth context
      console.error('🚨 Login failed:', error);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !loading) {
      handleSubmit(event as any);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
      }}
    >
      <Card
        sx={{
          maxWidth: 450,
          width: '100%',
          bgcolor: 'rgba(26, 26, 46, 0.95)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(0, 123, 255, 0.2)',
          boxShadow: '0 8px 32px rgba(0, 123, 255, 0.1)',
          borderRadius: 3,
        }}
      >
        <CardContent sx={{ p: 4 }}>
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Avatar
              sx={{
                width: 80,
                height: 80,
                margin: '0 auto',
                mb: 2,
                bgcolor: 'primary.main',
                background: 'linear-gradient(135deg, #007bff, #0056b3)',
              }}
            >
              <Shield sx={{ fontSize: 40 }} />
            </Avatar>
            
            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                background: 'linear-gradient(135deg, #007bff, #4dabf7)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                color: 'transparent',
                mb: 1,
              }}
            >
              PROJECT SENTINEL
            </Typography>
            
            <Typography
              variant="subtitle1"
              sx={{
                color: 'text.secondary',
                fontWeight: 500,
              }}
            >
              🛡️ Defense Intelligence System
            </Typography>
            
            <Typography
              variant="body2"
              sx={{
                color: 'text.secondary',
                mt: 1,
              }}
            >
              Secure Access for Authorized Personnel Only
            </Typography>
          </Box>

          {/* Login Form */}
          <form onSubmit={handleSubmit}>
            <Stack spacing={3}>
              {/* Error Alert */}
              {error && (
                <Alert 
                  severity="error" 
                  variant="filled"
                  sx={{ 
                    bgcolor: 'rgba(211, 47, 47, 0.1)',
                    border: '1px solid rgba(211, 47, 47, 0.3)',
                    '& .MuiAlert-message': { color: '#ff6b6b' }
                  }}
                >
                  🚨 {error}
                </Alert>
              )}

              {/* Username Field */}
              <TextField
                fullWidth
                label="Username / Employee ID"
                variant="outlined"
                value={credentials.username}
                onChange={handleInputChange('username')}
                onKeyPress={handleKeyPress}
                error={!!validationErrors.username}
                helperText={validationErrors.username}
                disabled={loading}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Person sx={{ color: 'primary.main' }} />
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    '& fieldset': {
                      borderColor: 'rgba(0, 123, 255, 0.3)',
                    },
                    '&:hover fieldset': {
                      borderColor: 'rgba(0, 123, 255, 0.5)',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: 'primary.main',
                    },
                  },
                }}
              />

              {/* Password Field */}
              <TextField
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                variant="outlined"
                value={credentials.password}
                onChange={handleInputChange('password')}
                onKeyPress={handleKeyPress}
                error={!!validationErrors.password}
                helperText={validationErrors.password}
                disabled={loading}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock sx={{ color: 'primary.main' }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                        disabled={loading}
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    '& fieldset': {
                      borderColor: 'rgba(0, 123, 255, 0.3)',
                    },
                    '&:hover fieldset': {
                      borderColor: 'rgba(0, 123, 255, 0.5)',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: 'primary.main',
                    },
                  },
                }}
              />

              {/* Remember Me */}
              <FormControlLabel
                control={
                  <Checkbox
                    checked={credentials.remember_me}
                    onChange={handleInputChange('remember_me')}
                    disabled={loading}
                    sx={{
                      color: 'primary.main',
                      '&.Mui-checked': {
                        color: 'primary.main',
                      },
                    }}
                  />
                }
                label={
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Remember me for 7 days
                  </Typography>
                }
              />

              {/* Login Button */}
              <Button
                fullWidth
                type="submit"
                variant="contained"
                size="large"
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <LoginOutlined />}
                sx={{
                  height: 56,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #007bff, #0056b3)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #0056b3, #004085)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 6px 20px rgba(0, 123, 255, 0.4)',
                  },
                  '&:disabled': {
                    background: 'rgba(0, 123, 255, 0.3)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                {loading ? 'Authenticating...' : '🔐 SECURE LOGIN'}
              </Button>

              {/* Divider */}
              <Divider sx={{ my: 2, borderColor: 'rgba(0, 123, 255, 0.2)' }} />

              {/* Register Link */}
              {onSwitchToRegister && (
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>
                    New defense personnel?
                  </Typography>
                  <Link
                    component="button"
                    type="button"
                    variant="body2"
                    onClick={onSwitchToRegister}
                    disabled={loading}
                    sx={{
                      color: 'primary.main',
                      textDecoration: 'none',
                      fontWeight: 600,
                      '&:hover': {
                        textDecoration: 'underline',
                      },
                      '&:disabled': {
                        color: 'text.disabled',
                      },
                    }}
                  >
                    📝 Request System Access
                  </Link>
                </Box>
              )}

              {/* Security Notice */}
              <Alert
                icon={<Security />}
                severity="info"
                variant="outlined"
                sx={{
                  bgcolor: 'rgba(0, 123, 255, 0.05)',
                  border: '1px solid rgba(0, 123, 255, 0.2)',
                  '& .MuiAlert-message': { 
                    color: 'text.secondary',
                    fontSize: '0.85rem',
                  },
                }}
              >
                All access attempts are logged and monitored for security compliance.
              </Alert>
            </Stack>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
};

export default LoginForm;

