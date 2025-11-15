/**
 * 📝 PROJECT SENTINEL - REGISTRATION COMPONENT
 * Advanced registration form for defense personnel
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
  Alert,
  CircularProgress,
  Divider,
  Link,
  Avatar,
  Stack,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Security,
  Person,
  Lock,
  Email,
  Phone,
  Badge,
  LocationOn,
  PersonAdd,
  Shield,
  ArrowBack,
  ArrowForward,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { RegisterData } from '../services/authService';

interface RegisterFormProps {
  onSwitchToLogin?: () => void;
  onRegistrationSuccess?: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({
  onSwitchToLogin,
  onRegistrationSuccess
}) => {
  const { register, loading, error, clearError } = useAuth();
  
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<RegisterData>({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    employee_id: '',
    rank: '',
    unit: '',
    clearance_level: 'RESTRICTED',
    role: 'ANALYST',
    phone_number: '',
    location: '',
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [validationErrors, setValidationErrors] = useState<{[key: string]: string}>({});

  const steps = [
    'Personal Information',
    'Account Credentials', 
    'Military Details',
    'Contact & Location'
  ];

  // Clear error when component unmounts or form data changes
  useEffect(() => {
    if (error) {
      const timer = setTimeout(clearError, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, clearError]);

  const handleInputChange = (field: keyof RegisterData) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | { target: { value: any } }
  ) => {
    const value = event.target.value;
    setFormData(prev => ({
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

  const validateStep = (step: number): boolean => {
    const errors: {[key: string]: string} = {};
    
    switch (step) {
      case 0: // Personal Information
        if (!formData.first_name.trim()) errors.first_name = 'First name is required';
        if (!formData.last_name.trim()) errors.last_name = 'Last name is required';
        break;
        
      case 1: // Account Credentials
        if (!formData.username.trim()) errors.username = 'Username is required';
        if (formData.username.length < 3) errors.username = 'Username must be at least 3 characters';
        if (!formData.email.trim()) errors.email = 'Email is required';
        if (!/\S+@\S+\.\S+/.test(formData.email)) errors.email = 'Invalid email format';
        if (!formData.password) errors.password = 'Password is required';
        if (formData.password.length < 8) errors.password = 'Password must be at least 8 characters';
        if (!formData.password_confirm) errors.password_confirm = 'Confirm password is required';
        if (formData.password !== formData.password_confirm) errors.password_confirm = 'Passwords do not match';
        break;
        
      case 2: // Military Details
        if (!formData.employee_id?.trim()) errors.employee_id = 'Employee ID is required';
        if (!formData.rank?.trim()) errors.rank = 'Rank is required';
        if (!formData.unit?.trim()) errors.unit = 'Unit is required';
        break;
        
      case 3: // Contact & Location
        if (!formData.phone_number?.trim()) errors.phone_number = 'Phone number is required';
        if (!formData.location?.trim()) errors.location = 'Location is required';
        break;
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!validateStep(3)) return;
    
    try {
      await register(formData);
      onRegistrationSuccess?.();
    } catch (error) {
      console.error('🚨 Registration failed:', error);
    }
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Stack spacing={3}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="First Name"
                  variant="outlined"
                  value={formData.first_name}
                  onChange={handleInputChange('first_name')}
                  error={!!validationErrors.first_name}
                  helperText={validationErrors.first_name}
                  disabled={loading}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Person sx={{ color: 'primary.main' }} />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Last Name"
                  variant="outlined"
                  value={formData.last_name}
                  onChange={handleInputChange('last_name')}
                  error={!!validationErrors.last_name}
                  helperText={validationErrors.last_name}
                  disabled={loading}
                />
              </Grid>
            </Grid>
          </Stack>
        );

      case 1:
        return (
          <Stack spacing={3}>
            <TextField
              fullWidth
              label="Username"
              variant="outlined"
              value={formData.username}
              onChange={handleInputChange('username')}
              error={!!validationErrors.username}
              helperText={validationErrors.username || "Choose a unique username"}
              disabled={loading}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Person sx={{ color: 'primary.main' }} />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Email Address"
              type="email"
              variant="outlined"
              value={formData.email}
              onChange={handleInputChange('email')}
              error={!!validationErrors.email}
              helperText={validationErrors.email || "Use official government/military email"}
              disabled={loading}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Email sx={{ color: 'primary.main' }} />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Password"
              type={showPassword ? 'text' : 'password'}
              variant="outlined"
              value={formData.password}
              onChange={handleInputChange('password')}
              error={!!validationErrors.password}
              helperText={validationErrors.password || "Minimum 8 characters"}
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
            />

            <TextField
              fullWidth
              label="Confirm Password"
              type={showConfirmPassword ? 'text' : 'password'}
              variant="outlined"
              value={formData.password_confirm}
              onChange={handleInputChange('password_confirm')}
              error={!!validationErrors.password_confirm}
              helperText={validationErrors.password_confirm}
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
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      edge="end"
                      disabled={loading}
                    >
                      {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Stack>
        );

      case 2:
        return (
          <Stack spacing={3}>
            <TextField
              fullWidth
              label="Employee ID"
              variant="outlined"
              placeholder="e.g., CDF001234"
              value={formData.employee_id}
              onChange={handleInputChange('employee_id')}
              error={!!validationErrors.employee_id}
              helperText={validationErrors.employee_id || "Format: 2-4 letters + 4-6 numbers"}
              disabled={loading}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Badge sx={{ color: 'primary.main' }} />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Military Rank"
              variant="outlined"
              placeholder="e.g., Captain, Major, Colonel"
              value={formData.rank}
              onChange={handleInputChange('rank')}
              error={!!validationErrors.rank}
              helperText={validationErrors.rank}
              disabled={loading}
            />

            <TextField
              fullWidth
              label="Unit/Division"
              variant="outlined"
              placeholder="e.g., 1st Battalion, Intelligence Division"
              value={formData.unit}
              onChange={handleInputChange('unit')}
              error={!!validationErrors.unit}
              helperText={validationErrors.unit}
              disabled={loading}
            />

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Security Clearance</InputLabel>
                  <Select
                    value={formData.clearance_level}
                    onChange={handleInputChange('clearance_level')}
                    disabled={loading}
                    label="Security Clearance"
                  >
                    <MenuItem value="PUBLIC">🟢 Public</MenuItem>
                    <MenuItem value="RESTRICTED">🟡 Restricted</MenuItem>
                    <MenuItem value="CONFIDENTIAL">🟠 Confidential</MenuItem>
                    <MenuItem value="SECRET">🔴 Secret</MenuItem>
                    <MenuItem value="TOP_SECRET">⚫ Top Secret</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>System Role</InputLabel>
                  <Select
                    value={formData.role}
                    onChange={handleInputChange('role')}
                    disabled={loading}
                    label="System Role"
                  >
                    <MenuItem value="ANALYST">🔍 Intelligence Analyst</MenuItem>
                    <MenuItem value="OFFICER">👮 Field Officer</MenuItem>
                    <MenuItem value="COMMANDER">⭐ Operations Commander</MenuItem>
                    <MenuItem value="VIEWER">👁️ Read-Only Viewer</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Stack>
        );

      case 3:
        return (
          <Stack spacing={3}>
            <TextField
              fullWidth
              label="Phone Number"
              variant="outlined"
              placeholder="+237 XXX XXX XXX"
              value={formData.phone_number}
              onChange={handleInputChange('phone_number')}
              error={!!validationErrors.phone_number}
              helperText={validationErrors.phone_number}
              disabled={loading}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Phone sx={{ color: 'primary.main' }} />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Base/Station Location"
              variant="outlined"
              placeholder="e.g., Yaoundé, Douala, Garoua"
              value={formData.location}
              onChange={handleInputChange('location')}
              error={!!validationErrors.location}
              helperText={validationErrors.location}
              disabled={loading}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LocationOn sx={{ color: 'primary.main' }} />
                  </InputAdornment>
                ),
              }}
            />

            <Alert
              icon={<Security />}
              severity="info"
              variant="outlined"
              sx={{
                bgcolor: 'rgba(0, 123, 255, 0.05)',
                border: '1px solid rgba(0, 123, 255, 0.2)',
              }}
            >
              Your registration will be reviewed by system administrators before account activation.
            </Alert>
          </Stack>
        );

      default:
        return null;
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
          maxWidth: 600,
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
              <PersonAdd sx={{ fontSize: 40 }} />
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
              SYSTEM ACCESS REQUEST
            </Typography>
            
            <Typography
              variant="subtitle1"
              sx={{
                color: 'text.secondary',
                fontWeight: 500,
              }}
            >
              🛡️ Defense Personnel Registration
            </Typography>
          </Box>

          {/* Error Alert */}
          {error && (
            <Alert 
              severity="error" 
              variant="filled"
              sx={{ 
                mb: 3,
                bgcolor: 'rgba(211, 47, 47, 0.1)',
                border: '1px solid rgba(211, 47, 47, 0.3)',
              }}
            >
              🚨 {error}
            </Alert>
          )}

          {/* Stepper */}
          <Stepper activeStep={activeStep} orientation="vertical" sx={{ mb: 4 }}>
            {steps.map((label, index) => (
              <Step key={label}>
                <StepLabel
                  sx={{
                    '& .MuiStepLabel-label': {
                      color: 'text.primary',
                      fontWeight: 500,
                    },
                  }}
                >
                  {label}
                </StepLabel>
                <StepContent>
                  {renderStepContent(index)}
                  
                  <Box sx={{ mt: 3 }}>
                    <Button
                      variant="contained"
                      onClick={index === steps.length - 1 ? handleSubmit : handleNext}
                      disabled={loading}
                      startIcon={loading ? <CircularProgress size={20} /> : 
                        (index === steps.length - 1 ? <PersonAdd /> : <ArrowForward />)}
                      sx={{
                        mr: 1,
                        background: 'linear-gradient(135deg, #007bff, #0056b3)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #0056b3, #004085)',
                        },
                      }}
                    >
                      {loading ? 'Processing...' : 
                        (index === steps.length - 1 ? '📝 Submit Request' : 'Next')}
                    </Button>
                    
                    <Button
                      disabled={index === 0 || loading}
                      onClick={handleBack}
                      startIcon={<ArrowBack />}
                      sx={{ color: 'text.secondary' }}
                    >
                      Back
                    </Button>
                  </Box>
                </StepContent>
              </Step>
            ))}
          </Stepper>

          {/* Login Link */}
          {onSwitchToLogin && (
            <>
              <Divider sx={{ my: 3, borderColor: 'rgba(0, 123, 255, 0.2)' }} />
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>
                  Already have access credentials?
                </Typography>
                <Link
                  component="button"
                  type="button"
                  variant="body2"
                  onClick={onSwitchToLogin}
                  disabled={loading}
                  sx={{
                    color: 'primary.main',
                    textDecoration: 'none',
                    fontWeight: 600,
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  🔐 Return to Login
                </Link>
              </Box>
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default RegisterForm;

