"""
PROJECT SENTINEL - SIMPLIFIED CONFLICT PREDICTION MODEL
Cameroon Defense Force Advanced AI System (CPU-Optimized Version)

Enhanced ML model for predicting geopolitical conflicts in Cameroon
using historical ACLED data - CPU optimized with scikit-learn only.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# ML Libraries (CPU-optimized)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score
from sklearn.feature_selection import SelectKBest, f_classif

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CameroonConflictPredictor:
    """
    CPU-optimized ML system for Cameroon conflict prediction.
    """
    
    def __init__(self, acled_data_path: str = "cameroon_events_ml_ready.json"):
        self.data_path = acled_data_path
        self.raw_data = None
        self.processed_features = None
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_importance = {}
        
        # Prediction horizons
        self.prediction_horizons = [7, 30, 90]  # days
        
        # Cameroon regions for spatial analysis
        self.cameroon_regions = [
            'Centre', 'Littoral', 'Sud-Ouest', 'Nord-Ouest', 'Extrême-Nord',
            'Nord', 'Adamaoua', 'Est', 'Sud', 'Ouest', 'Extreme-Nord'
        ]
    
    def load_acled_data(self) -> bool:
        """Load processed ACLED data."""
        try:
            logger.info(f"📊 Loading ACLED data from: {self.data_path}")
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.raw_data = json.load(f)
            
            events = self.raw_data.get('events', [])
            logger.info(f"✅ Loaded {len(events)} historical conflict events")
            
            if not events:
                logger.error("❌ No events found in ACLED data")
                return False
            
            # Convert to DataFrame
            self.df = pd.DataFrame(events)
            
            # Parse dates - handle DD/MM/YYYY format
            self.df['date'] = pd.to_datetime(self.df['date'], format='mixed', dayfirst=True, errors='coerce')
            self.df = self.df.sort_values('date').reset_index(drop=True)
            
            # Remove events with invalid dates
            invalid_dates = self.df['date'].isna().sum()
            if invalid_dates > 0:
                logger.warning(f"⚠️ Removed {invalid_dates} events with invalid dates")
                self.df = self.df.dropna(subset=['date']).reset_index(drop=True)
            
            # Basic temporal features
            self.df['year'] = self.df['date'].dt.year
            self.df['month'] = self.df['date'].dt.month
            self.df['day_of_year'] = self.df['date'].dt.dayofyear
            self.df['quarter'] = self.df['date'].dt.quarter
            
            logger.info(f"📅 Date range: {self.df['date'].min()} to {self.df['date'].max()}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading ACLED data: {e}")
            return False
    
    def engineer_features(self) -> pd.DataFrame:
        """Feature engineering for conflict prediction."""
        logger.info("🔧 Engineering features for ML models...")
        
        if self.df is None:
            logger.error("❌ No data loaded")
            return None
        
        features_df = self.df.copy()
        
        # 1. TEMPORAL FEATURES
        features_df['is_weekend'] = (features_df['date'].dt.dayofweek >= 5).astype(int)
        features_df['days_since_start'] = (features_df['date'] - features_df['date'].min()).dt.days
        
        # Seasonal features (Cameroon climate)
        features_df['is_dry_season'] = features_df['month'].isin([11, 12, 1, 2, 3, 4]).astype(int)
        features_df['is_rainy_season'] = features_df['month'].isin([5, 6, 7, 8, 9, 10]).astype(int)
        
        # 2. SPATIAL FEATURES
        # Extract coordinates safely
        def extract_lat(coords):
            try:
                return float(coords[0]) if isinstance(coords, list) and len(coords) >= 2 else 0.0
            except:
                return 0.0
        
        def extract_lon(coords):
            try:
                return float(coords[1]) if isinstance(coords, list) and len(coords) >= 2 else 0.0
            except:
                return 0.0
        
        features_df['latitude'] = features_df['coordinates'].apply(extract_lat)
        features_df['longitude'] = features_df['coordinates'].apply(extract_lon)
        
        # Region encoding
        region_encoder = LabelEncoder()
        features_df['region_encoded'] = region_encoder.fit_transform(features_df['admin1'].astype(str))
        self.label_encoders['region'] = region_encoder
        
        # Distance to capital (Yaoundé: 3.8667°N, 11.5167°E)
        capital_lat, capital_lon = 3.8667, 11.5167
        features_df['distance_to_capital'] = np.sqrt(
            (features_df['latitude'] - capital_lat)**2 +
            (features_df['longitude'] - capital_lon)**2
        )
        
        # 3. ACTOR FEATURES  
        # Actor encoding
        actor_encoder = LabelEncoder()
        features_df['actor1_encoded'] = actor_encoder.fit_transform(features_df['actor1'].astype(str))
        self.label_encoders['actor'] = actor_encoder
        
        # Government involvement
        features_df['government_involved'] = features_df['actor1'].astype(str).str.contains(
            'Military Forces of Cameroon|Police Forces of Cameroon|Government', 
            na=False, case=False
        ).astype(int)
        
        # Boko Haram involvement
        features_df['boko_haram_involved'] = features_df['actor1'].astype(str).str.contains(
            'Boko Haram', na=False, case=False
        ).astype(int)
        
        # Foreign involvement
        features_df['foreign_involved'] = features_df['actor1'].astype(str).str.contains(
            'Nigeria|Chad|International', na=False, case=False
        ).astype(int)
        
        # 4. CONFLICT CHARACTERISTICS
        # Conflict type encoding
        conflict_encoder = LabelEncoder()
        features_df['conflict_type_encoded'] = conflict_encoder.fit_transform(
            features_df['conflict_category'].astype(str)
        )
        self.label_encoders['conflict_type'] = conflict_encoder
        
        # Fatality indicators
        features_df['has_fatalities'] = (features_df['fatalities'] > 0).astype(int)
        features_df['high_fatalities'] = (features_df['fatalities'] >= 5).astype(int)
        features_df['mass_casualty'] = (features_df['fatalities'] >= 20).astype(int)
        
        # 5. REGIONAL PATTERNS
        # Region conflict density
        region_counts = features_df.groupby('admin1').size()
        features_df['region_conflict_density'] = features_df['admin1'].map(region_counts)
        
        # Border region indicator
        border_regions = ['Extrême-Nord', 'Extreme-Nord', 'Nord', 'Sud-Ouest', 'Nord-Ouest', 'Est']
        features_df['is_border_region'] = features_df['admin1'].isin(border_regions).astype(int)
        
        # 6. TARGET VARIABLES - Future conflict prediction
        # Sort by date for temporal analysis
        features_df = features_df.sort_values('date').reset_index(drop=True)
        
        for horizon in self.prediction_horizons:
            future_conflicts = []
            
            for idx, row in features_df.iterrows():
                current_date = row['date']
                current_region = row['admin1']
                future_date = current_date + timedelta(days=horizon)
                
                # Look for conflicts in same region within time horizon
                future_events = features_df[
                    (features_df['date'] > current_date) &
                    (features_df['date'] <= future_date) &
                    (features_df['admin1'] == current_region)
                ]
                
                # Binary: will there be any conflict?
                has_future_conflict = int(len(future_events) > 0)
                future_conflicts.append(has_future_conflict)
            
            features_df[f'future_conflict_{horizon}d'] = future_conflicts
        
        # 7. FEATURE SELECTION
        # Select final feature columns for ML
        feature_columns = [
            'year', 'month', 'day_of_year', 'quarter', 'is_weekend', 'days_since_start',
            'is_dry_season', 'is_rainy_season', 'latitude', 'longitude', 
            'region_encoded', 'distance_to_capital', 'actor1_encoded',
            'government_involved', 'boko_haram_involved', 'foreign_involved',
            'conflict_type_encoded', 'fatalities', 'severity_score',
            'has_fatalities', 'high_fatalities', 'mass_casualty',
            'region_conflict_density', 'is_border_region'
        ]
        
        # Handle missing values
        for col in feature_columns:
            if col in features_df.columns:
                features_df[col] = features_df[col].fillna(0)
            else:
                logger.warning(f"⚠️ Feature {col} not found, creating with zeros")
                features_df[col] = 0
        
        self.processed_features = features_df
        logger.info(f"✅ Feature engineering complete: {len(feature_columns)} features")
        
        return features_df
    
    def train_prediction_models(self) -> Dict[str, Any]:
        """Train ML models for conflict prediction."""
        if self.processed_features is None:
            logger.error("❌ No processed features available")
            return {}
        
        logger.info("🚀 Training conflict prediction models...")
        
        # Feature columns
        feature_columns = [
            'year', 'month', 'day_of_year', 'quarter', 'is_weekend', 'days_since_start',
            'is_dry_season', 'is_rainy_season', 'latitude', 'longitude',
            'region_encoded', 'distance_to_capital', 'actor1_encoded',
            'government_involved', 'boko_haram_involved', 'foreign_involved',
            'conflict_type_encoded', 'fatalities', 'severity_score',
            'has_fatalities', 'high_fatalities', 'mass_casualty',
            'region_conflict_density', 'is_border_region'
        ]
        
        X = self.processed_features[feature_columns]
        results = {}
        
        # Train models for each prediction horizon
        for horizon in self.prediction_horizons:
            target_col = f'future_conflict_{horizon}d'
            if target_col not in self.processed_features.columns:
                logger.warning(f"⚠️ Target column {target_col} not found")
                continue
            
            y = self.processed_features[target_col]
            
            # Remove samples where we can't make future predictions
            valid_indices = y.notna()
            X_valid = X[valid_indices]
            y_valid = y[valid_indices]
            
            if len(X_valid) < 50:
                logger.warning(f"⚠️ Insufficient data for {horizon}-day prediction: {len(X_valid)} samples")
                continue
            
            logger.info(f"📊 Training models for {horizon}-day prediction ({len(X_valid)} samples)...")
            
            # Time-based train/test split
            split_point = int(0.75 * len(X_valid))
            X_train, X_test = X_valid.iloc[:split_point], X_valid.iloc[split_point:]
            y_train, y_test = y_valid.iloc[:split_point], y_valid.iloc[split_point:]
            
            # Check class balance
            positive_rate = y_train.mean()
            logger.info(f"   Positive class rate: {positive_rate:.1%}")
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            self.scalers[f'{horizon}d'] = scaler
            
            # Train models
            models = {
                'RandomForest': RandomForestClassifier(
                    n_estimators=50, 
                    max_depth=8, 
                    min_samples_split=5,
                    class_weight='balanced',
                    random_state=42
                ),
                'GradientBoosting': GradientBoostingClassifier(
                    n_estimators=50,
                    max_depth=4,
                    learning_rate=0.1,
                    random_state=42
                )
            }
            
            horizon_results = {}
            
            for model_name, model in models.items():
                try:
                    # Train model
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred
                    
                    # Evaluate
                    accuracy = accuracy_score(y_test, y_pred)
                    precision = precision_score(y_test, y_pred, zero_division=0)
                    recall = recall_score(y_test, y_pred, zero_division=0)
                    
                    # Feature importance
                    if hasattr(model, 'feature_importances_'):
                        importance = dict(zip(feature_columns, model.feature_importances_))
                        top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]
                        self.feature_importance[f'{model_name}_{horizon}d'] = importance
                    else:
                        top_features = []
                    
                    horizon_results[model_name] = {
                        'accuracy': accuracy,
                        'precision': precision,
                        'recall': recall,
                        'predictions': len(y_pred),
                        'top_features': top_features
                    }
                    
                    logger.info(f"✅ {model_name} ({horizon}d): Acc={accuracy:.3f}, Prec={precision:.3f}, Rec={recall:.3f}")
                    
                    # Store model
                    self.models[f'{model_name}_{horizon}d'] = model
                    
                except Exception as e:
                    logger.error(f"❌ Error training {model_name} for {horizon}d: {e}")
                    continue
            
            results[f'{horizon}d'] = horizon_results
        
        logger.info("✅ Model training complete!")
        return results
    
    def predict_future_conflicts(self, region: str = None, days_ahead: int = 7) -> Dict[str, Any]:
        """Make predictions for future conflicts."""
        if not self.models:
            logger.error("❌ No trained models available")
            return {}
        
        # Use most recent data for prediction
        if region:
            region_data = self.processed_features[self.processed_features['admin1'] == region]
            if region_data.empty:
                logger.warning(f"⚠️ No data found for region: {region}")
                latest_data = self.processed_features.iloc[-1:].copy()
            else:
                latest_data = region_data.iloc[-1:].copy()  # Use most recent event
        else:
            latest_data = self.processed_features.iloc[-1:].copy()
        
        # Feature columns
        feature_columns = [
            'year', 'month', 'day_of_year', 'quarter', 'is_weekend', 'days_since_start',
            'is_dry_season', 'is_rainy_season', 'latitude', 'longitude',
            'region_encoded', 'distance_to_capital', 'actor1_encoded',
            'government_involved', 'boko_haram_involved', 'foreign_involved',
            'conflict_type_encoded', 'fatalities', 'severity_score',
            'has_fatalities', 'high_fatalities', 'mass_casualty',
            'region_conflict_density', 'is_border_region'
        ]
        
        X_pred = latest_data[feature_columns]
        
        # Find best matching horizon
        best_horizon = min(self.prediction_horizons, key=lambda x: abs(x - days_ahead))
        model_key = f'RandomForest_{best_horizon}d'
        
        if model_key not in self.models:
            logger.error(f"❌ Model {model_key} not available")
            return {}
        
        try:
            model = self.models[model_key]
            scaler = self.scalers[f'{best_horizon}d']
            
            # Make prediction
            X_scaled = scaler.transform(X_pred)
            prediction = model.predict(X_scaled)[0]
            
            if hasattr(model, 'predict_proba'):
                probability = model.predict_proba(X_scaled)[0]
                conflict_prob = probability[1] if len(probability) > 1 else 0.5
            else:
                conflict_prob = float(prediction)
            
            # Get top risk factors
            if hasattr(model, 'feature_importances_'):
                feature_impacts = []
                feature_values = X_pred.iloc[0]
                
                for feature, importance in zip(feature_columns, model.feature_importances_):
                    if importance > 0.05:  # Only significant features
                        feature_impacts.append({
                            'factor': feature,
                            'importance': float(importance),
                            'current_value': float(feature_values[feature])
                        })
                
                feature_impacts.sort(key=lambda x: x['importance'], reverse=True)
            else:
                feature_impacts = []
            
            # Determine confidence level
            if conflict_prob > 0.8:
                confidence = 'High'
            elif conflict_prob > 0.6:
                confidence = 'Medium'
            else:
                confidence = 'Low'
            
            result = {
                'region': region or 'All regions',
                'prediction_horizon': f'{days_ahead} days',
                'conflict_predicted': bool(prediction),
                'conflict_probability': conflict_prob,
                'confidence_level': confidence,
                'risk_level': 'Critical' if conflict_prob > 0.8 else 'High' if conflict_prob > 0.6 else 'Medium' if conflict_prob > 0.4 else 'Low',
                'key_risk_factors': feature_impacts[:5],
                'model_used': model_key,
                'prediction_timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            return {}
    
    def generate_intelligence_report(self) -> str:
        """Generate comprehensive intelligence report."""
        report = f"""
🎯 PROJECT SENTINEL - AI CONFLICT PREDICTION REPORT
===================================================
🇨🇲 Cameroon Defense Force Intelligence System
📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 SYSTEM STATUS:
• Historical Events Analyzed: {len(self.processed_features)} (1997-2016)
• ML Models Trained: {len(self.models)} prediction models
• Prediction Horizons: 7, 30, 90 days
• Model Type: Random Forest + Gradient Boosting (CPU-optimized)

🗺️ REGIONAL RISK ASSESSMENT (Next 7 Days):
"""
        
        # Get predictions for high-risk regions
        high_risk_regions = ['Extrême-Nord', 'Extreme-Nord', 'Sud-Ouest', 'Nord-Ouest', 'Centre', 'Littoral']
        predictions = []
        
        for region in high_risk_regions:
            try:
                prediction = self.predict_future_conflicts(region=region, days_ahead=7)
                if prediction:
                    predictions.append((region, prediction.get('conflict_probability', 0), prediction.get('risk_level', 'Unknown')))
            except:
                continue
        
        # Sort by probability
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        for region, prob, risk_level in predictions[:5]:
            emoji = '🔴' if prob > 0.7 else '🟡' if prob > 0.4 else '🟢'
            report += f"{emoji} {region}: {prob:.1%} probability ({risk_level} risk)\n"
        
        if self.feature_importance:
            report += f"\n🎯 KEY RISK INDICATORS:\n"
            # Get most important features across all models
            all_features = {}
            for model_features in self.feature_importance.values():
                for feature, importance in model_features.items():
                    if feature not in all_features:
                        all_features[feature] = []
                    all_features[feature].append(importance)
            
            avg_importance = {feature: np.mean(scores) for feature, scores in all_features.items()}
            top_indicators = sorted(avg_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for indicator, importance in top_indicators:
                report += f"• {indicator}: {importance:.3f} importance\n"
        
        report += f"""

📈 HISTORICAL INSIGHTS:
• Most Active Region: {self.processed_features['admin1'].value_counts().index[0]}
• Peak Conflict Year: {self.processed_features.groupby('year').size().idxmax()}
• Boko Haram Events: {self.processed_features['boko_haram_involved'].sum()}
• Government Operations: {self.processed_features['government_involved'].sum()}
• Cross-border Incidents: {self.processed_features['is_border_region'].sum()}

🛡️ DEFENSE RECOMMENDATIONS:
• Prioritize monitoring of high-probability regions
• Enhance cross-border surveillance (Nigeria, Chad)
• Strengthen Extrême-Nord defensive posture
• Coordinate with international partners
• Maintain rapid response capabilities

🚀 SYSTEM READY FOR OPERATIONAL DEPLOYMENT
        """
        
        return report

# Main execution
if __name__ == "__main__":
    logger.info("🚀 PROJECT SENTINEL - CONFLICT PREDICTION SYSTEM")
    logger.info("=" * 60)
    
    # Initialize predictor
    predictor = CameroonConflictPredictor()
    
    # Load and process data
    if predictor.load_acled_data():
        # Engineer features
        features_df = predictor.engineer_features()
        
        if features_df is not None:
            # Train models
            results = predictor.train_prediction_models()
            
            if results:
                # Test predictions
                logger.info("\n🎯 SAMPLE PREDICTIONS:")
                
                test_regions = ['Extreme-Nord', 'Sud-Ouest', 'Centre']
                for region in test_regions:
                    prediction = predictor.predict_future_conflicts(region=region, days_ahead=7)
                    if prediction:
                        prob = prediction.get('conflict_probability', 0)
                        risk = prediction.get('risk_level', 'Unknown')
                        logger.info(f"   {region}: {prob:.1%} probability ({risk} risk)")
                
                # Generate and display report
                report = predictor.generate_intelligence_report()
                print(report)
                
                logger.info("🏆 CONFLICT PREDICTION SYSTEM OPERATIONAL!")
                logger.info("✅ Ready for integration with real-time intelligence pipeline")
            else:
                logger.error("❌ Model training failed")
        else:
            logger.error("❌ Feature engineering failed")  
    else:
        logger.error("❌ Data loading failed")

