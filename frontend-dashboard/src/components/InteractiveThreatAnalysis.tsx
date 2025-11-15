/**
 * 🎯 INTERACTIVE THREAT ANALYSIS - JAW-DROPPING RL VISUALIZATION
 * Real-time RL analysis with stunning visualizations when threats are selected
 */

import React, { useState, useEffect } from 'react';
import {
  Box, Card, Typography, Grid, Button, Slider, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, LinearProgress, IconButton, Tooltip, CircularProgress
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Psychology as BrainIcon,
  Security as SecurityIcon,
  AttachMoney as MoneyIcon,
  People as PeopleIcon,
  Schedule as ScheduleIcon,
  CompareArrows as CompareIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon
} from '@mui/icons-material';
import { Line, Radar, Doughnut } from 'react-chartjs-2';
import { UnifiedThreatPoint } from '../services/threatIntelligence';
import { rlService, RLAnalysisResult, InterventionRecommendation } from '../services/rlService';

interface InteractiveThreatAnalysisProps {
  selectedThreat: UnifiedThreatPoint | null;
  onThreatSelect: (threat: UnifiedThreatPoint | null) => void;
  threatData: UnifiedThreatPoint[];
}

const InteractiveThreatAnalysis: React.FC<InteractiveThreatAnalysisProps> = ({
  selectedThreat,
  onThreatSelect,
  threatData
}) => {
  const [rlAnalysis, setRlAnalysis] = useState<RLAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedIntervention, setSelectedIntervention] = useState<InterventionRecommendation | null>(null);
  const [simulationTime, setSimulationTime] = useState(30); // Days
  const [simulationRunning, setSimulationRunning] = useState(false);
  const [simulationResults, setSimulationResults] = useState<any>(null);

  // Analyze threat when selected
  useEffect(() => {
    if (selectedThreat) {
      analyzeSelectedThreat();
    }
  }, [selectedThreat]);

  const analyzeSelectedThreat = async () => {
    if (!selectedThreat) return;
    
    setLoading(true);
    try {
      const analysis = await rlService.getInterventionRecommendations(selectedThreat);
      setRlAnalysis(analysis);
      setSelectedIntervention(analysis.optimalStrategy);
    } catch (error) {
      console.error('❌ Threat analysis error:', error);
    } finally {
      setLoading(false);
    }
  };

  const runSimulation = async () => {
    if (!selectedIntervention || !selectedThreat) return;
    
    setSimulationRunning(true);
    
    // Simulate intervention over time
    const simulationData = {
      timeline: [],
      threatReduction: [],
      costAccumulation: [],
      riskLevels: [],
      successProbability: []
    };

    for (let day = 0; day <= simulationTime; day += 5) {
      const progress = day / simulationTime;
      const effectiveness = selectedIntervention.successProbability;
      
      simulationData.timeline.push(`Day ${day}`);
      simulationData.threatReduction.push(
        Math.max(0, selectedThreat.threatLevel * (1 - progress * effectiveness))
      );
      simulationData.costAccumulation.push(
        selectedIntervention.costEstimate * (progress * 0.8 + 0.2)
      );
      simulationData.riskLevels.push(
        selectedIntervention.riskLevel * 100 * (1 - progress * 0.5)
      );
      simulationData.successProbability.push(
        Math.min(100, effectiveness * 100 + progress * 20)
      );
      
      // Add small delay for animation effect
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    setSimulationResults(simulationData);
    setSimulationRunning(false);
  };

  // Chart configurations
  const simulationChartData = simulationResults ? {
    labels: simulationResults.timeline,
    datasets: [
      {
        label: 'Threat Level Reduction (%)',
        data: simulationResults.threatReduction,
        borderColor: '#ff1744',
        backgroundColor: 'rgba(255, 23, 68, 0.1)',
        tension: 0.4
      },
      {
        label: 'Success Probability (%)',
        data: simulationResults.successProbability,
        borderColor: '#00ff88',
        backgroundColor: 'rgba(0, 255, 136, 0.1)',
        tension: 0.4
      }
    ]
  } : null;

  const interventionComparisonData = rlAnalysis ? {
    labels: ['Effectiveness', 'Cost Efficiency', 'Speed', 'Risk Level', 'Sustainability'],
    datasets: rlAnalysis.recommendations.slice(0, 3).map((intervention, index) => ({
      label: intervention.interventionName,
      data: [
        intervention.successProbability * 100,
        Math.max(0, 100 - (intervention.costEstimate / 1000000) * 100),
        Math.max(0, 100 - (intervention.durationDays / 365) * 100),
        Math.max(0, 100 - intervention.riskLevel * 100),
        intervention.confidence * 100
      ],
      backgroundColor: `rgba(${index === 0 ? '0, 255, 136' : index === 1 ? '33, 150, 243' : '255, 152, 0'}, 0.2)`,
      borderColor: `rgba(${index === 0 ? '0, 255, 136' : index === 1 ? '33, 150, 243' : '255, 152, 0'}, 1)`,
      pointBackgroundColor: `rgba(${index === 0 ? '0, 255, 136' : index === 1 ? '33, 150, 243' : '255, 152, 0'}, 1)`,
    }))
  } : null;

  if (!selectedThreat) {
    // Show threat selection interface
    const criticalThreats = threatData.filter(t => t.threatLevel >= 60);
    
    return (
      <Card sx={{ p: 4, background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', border: '1px solid #00ff88' }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <BrainIcon sx={{ fontSize: 64, color: '#00ff88', mb: 2 }} />
          <Typography variant="h4" sx={{ color: '#00ff88', fontWeight: 'bold', mb: 2 }}>
            🧠 INTERACTIVE RL THREAT ANALYSIS
          </Typography>
          <Typography variant="body1" sx={{ color: '#aaa', mb: 4 }}>
            Select a high-priority threat below to see jaw-dropping AI-powered intervention analysis
          </Typography>
        </Box>

        <Grid container spacing={2}>
          {criticalThreats.length === 0 ? (
            <Grid item xs={12}>
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <SecurityIcon sx={{ fontSize: 48, color: '#666', mb: 2 }} />
                <Typography variant="h6" sx={{ color: '#666' }}>
                  No critical threats detected (≥60%)
                </Typography>
                <Typography variant="body2" sx={{ color: '#666' }}>
                  The AI system is monitoring for emerging threats...
                </Typography>
              </Box>
            </Grid>
          ) : (
            criticalThreats.map((threat, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card
                  sx={{
                    p: 2,
                    cursor: 'pointer',
                    background: threat.threatLevel >= 80 
                      ? 'linear-gradient(135deg, #5d1a1a 0%, #3a1a1a 100%)'
                      : 'linear-gradient(135deg, #5d3a1a 0%, #3a2a1a 100%)',
                    border: threat.threatLevel >= 80 ? '1px solid #ff1744' : '1px solid #ff9800',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'scale(1.05)',
                      boxShadow: '0 8px 25px rgba(255, 255, 255, 0.2)'
                    }
                  }}
                  onClick={() => onThreatSelect(threat)}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" sx={{ color: '#fff', fontWeight: 'bold' }}>
                      {threat.title}
                    </Typography>
                    <Chip
                      label={`${Math.round(threat.threatLevel)}%`}
                      sx={{
                        bgcolor: threat.threatLevel >= 80 ? '#ff1744' : '#ff9800',
                        color: '#fff',
                        fontWeight: 'bold'
                      }}
                    />
                  </Box>
                  <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
                    📍 {threat.region}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#fff' }}>
                    {threat.description}
                  </Typography>
                  <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<BrainIcon />}
                      sx={{
                        bgcolor: threat.threatLevel >= 80 ? '#ff1744' : '#ff9800',
                        '&:hover': { bgcolor: threat.threatLevel >= 80 ? '#d50000' : '#e65100' }
                      }}
                    >
                      ANALYZE WITH AI
                    </Button>
                  </Box>
                </Card>
              </Grid>
            ))
          )}
        </Grid>
      </Card>
    );
  }

  return (
    <Box>
      {/* Header with selected threat */}
      <Card sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #2e1a1a 0%, #3e2116 100%)', border: '1px solid #ff1744' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h5" sx={{ color: '#ff1744', fontWeight: 'bold', mb: 1 }}>
              🧠 AI ANALYZING: {selectedThreat.title}
            </Typography>
            <Typography variant="body1" sx={{ color: '#aaa' }}>
              📍 {selectedThreat.region} • Threat Level: {Math.round(selectedThreat.threatLevel)}%
            </Typography>
          </Box>
          <Button
            variant="outlined"
            onClick={() => onThreatSelect(null)}
            sx={{ borderColor: '#666', color: '#666' }}
          >
            ← BACK TO THREAT LIST
          </Button>
        </Box>
      </Card>

      {loading ? (
        <Card sx={{ p: 4, textAlign: 'center', background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', border: '1px solid #00ff88' }}>
          <CircularProgress sx={{ color: '#00ff88', mb: 2 }} />
          <Typography variant="h6" sx={{ color: '#00ff88' }}>
            🧠 AI PROCESSING THREAT DATA...
          </Typography>
          <Typography variant="body2" sx={{ color: '#aaa' }}>
            Running reinforcement learning analysis with 21 intervention strategies
          </Typography>
        </Card>
      ) : rlAnalysis ? (
        <Grid container spacing={3}>
          
          {/* Left Column - Intervention Strategy Comparison */}
          <Grid item xs={12} lg={8}>
            <Card sx={{ p: 3, background: 'linear-gradient(135deg, #1a2e1a 0%, #2a3e2a 100%)', border: '1px solid #4caf50' }}>
              <Typography variant="h6" sx={{ mb: 3, color: '#4caf50', fontWeight: 'bold' }}>
                ⚡ REAL-TIME STRATEGY COMPARISON
              </Typography>
              
              {interventionComparisonData && (
                <Box sx={{ height: 400, mb: 3 }}>
                  <Radar 
                    data={interventionComparisonData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: { labels: { color: '#fff' } }
                      },
                      scales: {
                        r: {
                          angleLines: { color: 'rgba(255, 255, 255, 0.2)' },
                          grid: { color: 'rgba(255, 255, 255, 0.2)' },
                          pointLabels: { color: '#fff' },
                          ticks: { color: '#aaa', display: false },
                          min: 0,
                          max: 100
                        }
                      }
                    }}
                  />
                </Box>
              )}

              {/* Intervention Selection */}
              <Typography variant="body2" sx={{ color: '#4caf50', fontWeight: 'bold', mb: 2 }}>
                🎯 SELECT INTERVENTION FOR SIMULATION:
              </Typography>
              <Grid container spacing={2}>
                {rlAnalysis.recommendations.slice(0, 3).map((intervention, index) => (
                  <Grid item xs={12} sm={4} key={intervention.id}>
                    <Card
                      sx={{
                        p: 2,
                        cursor: 'pointer',
                        border: selectedIntervention?.id === intervention.id ? '2px solid #00ff88' : '1px solid #666',
                        background: selectedIntervention?.id === intervention.id 
                          ? 'rgba(0, 255, 136, 0.1)' 
                          : 'rgba(255, 255, 255, 0.05)',
                        transition: 'all 0.3s ease'
                      }}
                      onClick={() => setSelectedIntervention(intervention)}
                    >
                      <Typography variant="body2" sx={{ color: '#fff', fontWeight: 'bold', mb: 1 }}>
                        {intervention.interventionName}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="caption" sx={{ color: '#aaa' }}>Success Rate:</Typography>
                        <Typography variant="caption" sx={{ color: '#4caf50' }}>
                          {Math.round(intervention.successProbability * 100)}%
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption" sx={{ color: '#aaa' }}>Cost:</Typography>
                        <Typography variant="caption" sx={{ color: '#ff9800' }}>
                          ${(intervention.costEstimate / 1000).toFixed(0)}K
                        </Typography>
                      </Box>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Card>
          </Grid>

          {/* Right Column - Simulation Controls */}
          <Grid item xs={12} lg={4}>
            <Card sx={{ p: 3, background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', border: '1px solid #2196f3' }}>
              <Typography variant="h6" sx={{ mb: 3, color: '#2196f3', fontWeight: 'bold' }}>
                🎮 INTERVENTION SIMULATION
              </Typography>
              
              <Typography variant="body2" sx={{ color: '#fff', mb: 2 }}>
                Simulation Timeline: {simulationTime} days
              </Typography>
              <Slider
                value={simulationTime}
                onChange={(_, value) => setSimulationTime(value as number)}
                min={7}
                max={365}
                step={7}
                marks={[
                  { value: 7, label: '1W' },
                  { value: 30, label: '1M' },
                  { value: 90, label: '3M' },
                  { value: 365, label: '1Y' }
                ]}
                sx={{
                  color: '#2196f3',
                  '& .MuiSlider-markLabel': { color: '#aaa' },
                  mb: 3
                }}
              />

              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={simulationRunning ? <PauseIcon /> : <PlayIcon />}
                onClick={runSimulation}
                disabled={!selectedIntervention || simulationRunning}
                sx={{
                  py: 2,
                  bgcolor: '#2196f3',
                  '&:hover': { bgcolor: '#1976d2' },
                  mb: 3
                }}
              >
                {simulationRunning ? 'SIMULATING...' : 'RUN AI SIMULATION'}
              </Button>

              {selectedIntervention && (
                <Box>
                  <Typography variant="body2" sx={{ color: '#2196f3', fontWeight: 'bold', mb: 2 }}>
                    📊 SELECTED STRATEGY DETAILS:
                  </Typography>
                  <Box sx={{ mb: 1 }}>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>Strategy:</Typography>
                    <Typography variant="body2" sx={{ color: '#fff', fontWeight: 'bold' }}>
                      {selectedIntervention.interventionName}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 1 }}>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>Category:</Typography>
                    <Typography variant="body2" sx={{ color: '#fff' }}>
                      {selectedIntervention.category.toUpperCase()}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 1 }}>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>Duration:</Typography>
                    <Typography variant="body2" sx={{ color: '#fff' }}>
                      {selectedIntervention.durationDays} days
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 1 }}>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>Personnel:</Typography>
                    <Typography variant="body2" sx={{ color: '#fff' }}>
                      {selectedIntervention.personnelRequired} officers
                    </Typography>
                  </Box>
                </Box>
              )}
            </Card>
          </Grid>

          {/* Full Width - Simulation Results */}
          {simulationResults && (
            <Grid item xs={12}>
              <Card sx={{ p: 3, background: 'linear-gradient(135deg, #2e1a2e 0%, #3e163e 100%)', border: '1px solid #9c27b0' }}>
                <Typography variant="h6" sx={{ mb: 3, color: '#9c27b0', fontWeight: 'bold' }}>
                  📈 AI SIMULATION RESULTS - {simulationTime} DAY PROJECTION
                </Typography>
                
                {simulationChartData && (
                  <Box sx={{ height: 400 }}>
                    <Line 
                      data={simulationChartData}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: { labels: { color: '#fff' } }
                        },
                        scales: {
                          x: { 
                            ticks: { color: '#fff' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                          },
                          y: { 
                            ticks: { color: '#fff' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                          }
                        }
                      }}
                    />
                  </Box>
                )}
              </Card>
            </Grid>
          )}

        </Grid>
      ) : null}
    </Box>
  );
};

export default InteractiveThreatAnalysis;
