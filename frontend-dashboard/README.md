# Project Sentinel Frontend Dashboard

**Classification:** RESTRICTED  
**Authority:** Cameroon Defense Force  
**Component:** React TypeScript Frontend for OSINT Analysis System

## Overview

This is the interactive map dashboard for Project Sentinel, built with React, TypeScript, and Material-UI. It provides real-time visualization of intelligence data on an interactive Mapbox map centered on Cameroon, with comprehensive filtering and analysis capabilities.

## Features

### 🗺️ Interactive Mapping
- **Mapbox GL Integration**: High-performance interactive maps optimized for intelligence operations
- **Cameroon-Centered**: Default view focused on Cameroon with appropriate zoom levels and bounds
- **Dark Theme**: Professional command center aesthetic suitable for 24/7 operations
- **Real-time Markers**: Dynamic markers showing intelligence reports with priority-based styling
- **Clustering**: Automatic marker clustering for improved performance with large datasets

### 📊 Intelligence Visualization
- **Priority-Based Styling**: Markers styled by priority (Critical=Red, High=Orange, Medium=Blue, Low=Gray)
- **Event Classification**: Automatic classification of events (Armed Clash, Security Operation, Political Event, etc.)
- **Entity Visualization**: Display of extracted named entities (Persons, Locations, Organizations)
- **Interactive Popups**: Detailed article information on marker click
- **Source Attribution**: Clear indication of news sources and publication dates

### 🔍 Advanced Filtering
- **Priority Filters**: Filter by intelligence priority levels (Critical, High, Medium, Low)
- **Source Filters**: Filter by specific news sources
- **Date Range**: Configurable date range filtering
- **Processing Status**: Show only processed or geolocated reports
- **Real-time Updates**: Automatic data refresh capabilities

### 📈 Analytics Dashboard
- **System Statistics**: Overview of total reports, processing status, recent activity
- **Source Analytics**: Top news sources by article count
- **Performance Metrics**: Processing success rates and system health indicators
- **Real-time Monitoring**: Connection status and data freshness indicators

## Technology Stack

- **React 18** with TypeScript for type-safe component development
- **Material-UI (MUI) 5** for professional dark-themed UI components
- **Mapbox GL JS** with react-map-gl for high-performance mapping
- **Axios** for API communication with Django backend
- **Vite** for fast development and optimized builds
- **date-fns** for advanced date/time formatting

## Prerequisites

1. **Node.js 18+** (LTS version recommended)
2. **Mapbox Account** with access token
3. **Project Sentinel Backend API** running on port 8000
4. **Modern Web Browser** with WebGL support

## Installation & Setup

### 1. Install Dependencies

```bash
cd frontend-dashboard
npm install
```

### 2. Environment Configuration

Create a `.env.local` file with:

```bash
# Backend API
VITE_API_BASE_URL=http://localhost:8000

# Mapbox (get token from https://account.mapbox.com/)
VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here

# Optional: Feature flags
VITE_ENABLE_DEBUG=false
VITE_AUTO_REFRESH_INTERVAL=300000
```

### 3. Development Server

```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### 4. Production Build

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend-dashboard/
├── src/
│   ├── components/          # React components
│   │   ├── Map.tsx         # Main map component
│   │   ├── PopupContent.tsx # Marker popup content
│   │   ├── Sidebar.tsx     # Filters and statistics
│   │   ├── StatusBar.tsx   # System status bar
│   │   └── MarkerCluster.tsx # Marker clustering
│   ├── services/           # API communication
│   │   └── api.ts          # Django backend integration
│   ├── types/              # TypeScript definitions
│   │   └── index.ts        # Application types
│   ├── utils/              # Utility functions
│   │   ├── mapUtils.ts     # Map-related utilities
│   │   └── formatUtils.ts  # Data formatting utilities
│   ├── App.tsx             # Main application component
│   └── main.tsx            # Application entry point
├── index.html              # HTML template
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite configuration
└── tsconfig.json           # TypeScript configuration
```

## Configuration

### Mapbox Setup

1. Create a Mapbox account at https://account.mapbox.com/
2. Generate an access token with appropriate permissions
3. Add the token to your `.env.local` file
4. Ensure the token has access to:
   - Maps API
   - Navigation API (for routing features)

### Backend Integration

The dashboard connects to the Django backend API endpoints:

- **GET `/api/v1/events/`** - Fetch GeoJSON intelligence data
- **GET `/api/v1/statistics/`** - System analytics and statistics
- **GET `/api/v1/articles/`** - Article listings with pagination
- **GET `/health/`** - Backend health check

### Map Customization

#### Map Styles
Available map styles can be configured in `src/utils/mapUtils.ts`:

```typescript
export const MAP_STYLES = {
  dark: 'mapbox://styles/mapbox/dark-v11',
  satellite: 'mapbox://styles/mapbox/satellite-streets-v12',
  streets: 'mapbox://styles/mapbox/streets-v12',
  navigation: 'mapbox://styles/mapbox/navigation-night-v1',
};
```

#### Cameroon Bounds
The map is constrained to Cameroon's geographic bounds:

```typescript
export const CAMEROON_BOUNDS = {
  north: 13.0833,
  south: 1.6667,
  east: 16.1833,
  west: 8.4833,
};
```

## Development

### Adding New Components

1. Create component in `src/components/`
2. Add type definitions to `src/types/index.ts`
3. Export from component folder if needed
4. Add to main App.tsx or appropriate parent

### API Integration

All API calls should go through the service layer in `src/services/api.ts`. The service includes:

- Automatic error handling
- Request/response interceptors
- Authentication token management
- Consistent error formatting

### Styling Guidelines

- Use Material-UI's `sx` prop for component styling
- Follow the dark theme color scheme
- Maintain consistency with command center aesthetics
- Use proper spacing and typography scales

## Performance Optimization

### Map Performance
- **Marker Clustering**: Automatically enabled for >50 markers
- **Viewport Culling**: Only render visible markers
- **Lazy Loading**: Components loaded as needed
- **Memoization**: React.memo and useMemo for expensive operations

### Bundle Optimization
- **Code Splitting**: Automatic route-based splitting
- **Tree Shaking**: Unused code elimination
- **Asset Optimization**: Images and fonts optimized
- **Vendor Chunking**: Separate vendor and app bundles

## Security Considerations

- **No Sensitive Data**: No classified information in frontend code
- **Environment Variables**: Sensitive configs in environment files
- **CORS Protection**: Backend CORS configuration required
- **HTTPS Only**: Production deployment should use HTTPS
- **CSP Headers**: Content Security Policy implementation recommended

## Deployment

### Docker Deployment

```bash
# Build production image
docker build -t project-sentinel/frontend .

# Run container
docker run -p 3000:80 project-sentinel/frontend
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-dashboard
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend-dashboard
  template:
    metadata:
      labels:
        app: frontend-dashboard
    spec:
      containers:
      - name: frontend
        image: project-sentinel/frontend:latest
        ports:
        - containerPort: 80
        env:
        - name: VITE_API_BASE_URL
          value: "http://backend-api:8000"
```

### Static Hosting

The built application can be deployed to any static hosting service:

```bash
npm run build
# Deploy the 'dist' folder to your hosting provider
```

## Troubleshooting

### Common Issues

1. **Map Not Loading**
   - Check Mapbox access token
   - Verify token permissions
   - Check browser console for WebGL errors

2. **API Connection Failed**
   - Verify backend is running on port 8000
   - Check CORS configuration
   - Verify API base URL in environment

3. **Performance Issues**
   - Enable marker clustering
   - Check for memory leaks in browser dev tools
   - Optimize large dataset handling

### Browser Compatibility

- **Chrome/Edge 88+** ✅
- **Firefox 85+** ✅
- **Safari 14+** ✅
- **Mobile browsers** ⚠️ (limited touch support)

## Contributing

1. Follow TypeScript strict mode
2. Use ESLint and Prettier for code formatting
3. Write comprehensive prop types
4. Add JSDoc comments for complex functions
5. Test on multiple screen sizes

## Monitoring

### Performance Metrics
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Time to Interactive (TTI)
- Map Load Time

### Error Tracking
- API error rates
- Map rendering failures
- Component crash boundaries
- Network connectivity issues

## License

**RESTRICTED** - Cameroon Defense Force Internal Use Only

---

*This system is classified RESTRICTED and is intended for authorized personnel only.*

## Support

For technical support and system issues, contact the Project Sentinel development team through official CDF channels.

**Version**: 1.0.0  
**Last Updated**: 2024  
**Classification**: RESTRICTED
