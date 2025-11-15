/**
 * 🔐 AUTHENTICATION CONTEXT - DEFENSE SECURITY SYSTEM
 * Manages user authentication state for Project Sentinel
 * Cameroon Defense Force - Secure Access Management
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  rank?: string;
  role: 'admin' | 'operator' | 'analyst' | 'commander';
  permissions: string[];
  lastLogin: Date;
  avatar?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: { email: string; password: string }) => Promise<void>;
  signup: (userData: { name: string; email: string; password: string; rank?: string }) => Promise<void>;
  logout: () => void;
  updateProfile: (updates: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const savedUser = localStorage.getItem('sentinel-user');
        const savedToken = localStorage.getItem('sentinel-token');
        
        if (savedUser && savedToken) {
          const userData = JSON.parse(savedUser);
          
          // Verify token is still valid (in real app, check with backend)
          const tokenExpiry = localStorage.getItem('sentinel-token-expiry');
          if (tokenExpiry && new Date() < new Date(tokenExpiry)) {
            setUser(userData);
            console.log('🛡️ User session restored:', userData.name);
          } else {
            // Token expired, clear storage
            localStorage.removeItem('sentinel-user');
            localStorage.removeItem('sentinel-token');
            localStorage.removeItem('sentinel-token-expiry');
          }
        }
      } catch (error) {
        console.error('❌ Auth check failed:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (credentials: { email: string; password: string }) => {
    setIsLoading(true);
    
    try {
      // Simulate API call to backend authentication
      console.log('🔐 Authenticating user:', credentials.email);
      
      // In real implementation, this would be an API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock user data based on email (in real app, this comes from backend)
      const mockUser: User = {
        id: `user_${Date.now()}`,
        name: credentials.email.includes('admin') ? 'General Administrator' : 
              credentials.email.includes('commander') ? 'Field Commander' :
              credentials.email.includes('analyst') ? 'Intelligence Analyst' : 'Defense Operator',
        email: credentials.email,
        rank: credentials.email.includes('admin') ? 'General' :
              credentials.email.includes('commander') ? 'Colonel' :
              credentials.email.includes('analyst') ? 'Major' : 'Lieutenant',
        role: credentials.email.includes('admin') ? 'admin' :
              credentials.email.includes('commander') ? 'commander' :
              credentials.email.includes('analyst') ? 'analyst' : 'operator',
        permissions: credentials.email.includes('admin') ? 
          ['read', 'write', 'delete', 'admin', 'manage_users', 'system_config'] :
          credentials.email.includes('commander') ?
          ['read', 'write', 'command', 'deploy_units', 'tactical_decisions'] :
          credentials.email.includes('analyst') ?
          ['read', 'write', 'analyze', 'generate_reports', 'intelligence_access'] :
          ['read', 'acknowledge', 'basic_operations'],
        lastLogin: new Date(),
        avatar: `https://api.dicebear.com/7.x/military/svg?seed=${credentials.email}`
      };

      // Store user data and token
      const token = `sentinel_token_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const tokenExpiry = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours

      localStorage.setItem('sentinel-user', JSON.stringify(mockUser));
      localStorage.setItem('sentinel-token', token);
      localStorage.setItem('sentinel-token-expiry', tokenExpiry.toISOString());

      setUser(mockUser);
      console.log('✅ Authentication successful:', mockUser.name);
      
    } catch (error) {
      console.error('❌ Login failed:', error);
      throw new Error('Authentication failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (userData: { name: string; email: string; password: string; rank?: string }) => {
    setIsLoading(true);
    
    try {
      console.log('📝 Registering new user:', userData.email);
      
      // Simulate API call to backend registration
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Create new user
      const newUser: User = {
        id: `user_${Date.now()}`,
        name: userData.name,
        email: userData.email,
        rank: userData.rank || 'Recruit',
        role: 'operator', // Default role for new signups
        permissions: ['read', 'acknowledge', 'basic_operations'],
        lastLogin: new Date(),
        avatar: `https://api.dicebear.com/7.x/military/svg?seed=${userData.email}`
      };

      // Store user data and token
      const token = `sentinel_token_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const tokenExpiry = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours

      localStorage.setItem('sentinel-user', JSON.stringify(newUser));
      localStorage.setItem('sentinel-token', token);
      localStorage.setItem('sentinel-token-expiry', tokenExpiry.toISOString());

      setUser(newUser);
      console.log('✅ Registration successful:', newUser.name);
      
    } catch (error) {
      console.error('❌ Signup failed:', error);
      throw new Error('Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    console.log('🚪 User logging out:', user?.name);
    
    // Clear all stored data
    localStorage.removeItem('sentinel-user');
    localStorage.removeItem('sentinel-token');
    localStorage.removeItem('sentinel-token-expiry');
    
    setUser(null);
    
    // Optional: Notify backend about logout
    console.log('✅ Logout successful');
  };

  const updateProfile = (updates: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...updates };
      setUser(updatedUser);
      localStorage.setItem('sentinel-user', JSON.stringify(updatedUser));
      console.log('✅ Profile updated:', updatedUser.name);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    signup,
    logout,
    updateProfile
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Protected Route Component
interface ProtectedRouteProps {
  children: ReactNode;
  requiredPermissions?: string[];
  fallback?: ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredPermissions = [], 
  fallback 
}) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        backgroundColor: '#0a0a0a',
        color: '#00ff88'
      }}>
        <div>🛡️ Verifying Security Clearance...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return fallback || <div>Access Denied</div>;
  }

  // Check permissions if required
  if (requiredPermissions.length > 0 && user) {
    const hasPermission = requiredPermissions.some(permission => 
      user.permissions.includes(permission)
    );
    
    if (!hasPermission) {
      return (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh',
          backgroundColor: '#0a0a0a',
          color: '#ff1744'
        }}>
          <div>🚫 Insufficient Security Clearance</div>
        </div>
      );
    }
  }

  return <>{children}</>;
};

export default AuthContext;