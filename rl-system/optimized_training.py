"""
PROJECT SENTINEL - OPTIMIZED RL TRAINING
Advanced training script with improved hyperparameters and curriculum learning.
"""

import numpy as np
import torch
import torch.optim
import logging
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import json
from datetime import datetime
import os

from decision_support_framework import ConflictEnvironment, InterventionType, ThreatLevel
from dqn_agent import DQNAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedTrainingConfig:
    """Optimized training configuration."""
    
    def __init__(self):
        # Training parameters
        self.num_episodes = 500  # Increased from 50
        self.max_steps_per_episode = 365
        self.evaluation_frequency = 50
        self.save_frequency = 100
        
        # Agent hyperparameters (optimized)
        self.learning_rate = 0.0005  # Reduced for stability
        self.gamma = 0.99  # Higher discount for long-term planning
        self.epsilon_start = 1.0
        self.epsilon_end = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 128  # Increased batch size
        self.target_update_frequency = 500  # Less frequent updates for stability
        self.memory_size = 50000
        
        # Network architecture
        self.hidden_size = 1024  # Larger network
        
        # Reward scaling
        self.reward_scale = 10.0  # Scale up rewards
        self.success_bonus = 100.0  # Large bonus for conflict prevention
        self.stability_bonus = 50.0  # Bonus for maintaining stability

class ImprovedRewardCalculator:
    """Improved reward function for better learning."""
    
    def __init__(self, config: OptimizedTrainingConfig):
        self.config = config
        self.stability_weights = {
            ThreatLevel.PEACEFUL: 10.0,
            ThreatLevel.LOW_RISK: 5.0,
            ThreatLevel.MEDIUM_RISK: 0.0,
            ThreatLevel.HIGH_RISK: -10.0,
            ThreatLevel.CRITICAL: -25.0
        }
    
    def calculate_reward(self, initial_state: np.ndarray, action_id: int, 
                        final_state: np.ndarray, environment) -> float:
        """Calculate improved reward based on multiple factors."""
        
        # Decode action
        intervention_type_id = action_id // len(environment.regions)
        target_region_id = action_id % len(environment.regions)
        intervention_type = list(InterventionType)[intervention_type_id]
        
        reward = 0.0
        
        # 1. Regional stability assessment
        stability_reward = 0.0
        threat_reduction = 0.0
        
        for region_id, region in environment.regions.items():
            # Stability bonus based on threat level
            stability_reward += self.stability_weights.get(region.threat_level, 0.0)
            
            # Track threat reduction in target region
            if region_id == target_region_id:
                # This is simplified - in practice we'd track before/after
                if region.threat_level <= ThreatLevel.LOW_RISK:
                    threat_reduction = 20.0
                elif region.threat_level <= ThreatLevel.MEDIUM_RISK:
                    threat_reduction = 10.0
        
        reward += stability_reward * 0.5  # Weight stability
        reward += threat_reduction
        
        # 2. Intervention appropriateness
        target_region = environment.regions[target_region_id]
        
        # Reward appropriate interventions
        if target_region.threat_level >= ThreatLevel.HIGH_RISK:
            if intervention_type in [InterventionType.SECURITY_DEPLOYMENT, 
                                   InterventionType.MEDIATION_DEPLOYMENT]:
                reward += 30.0  # Good intervention for high threat
            elif intervention_type == InterventionType.MONITOR_ONLY:
                reward -= 20.0  # Don't just monitor high-risk situations
        
        elif target_region.threat_level <= ThreatLevel.LOW_RISK:
            if intervention_type in [InterventionType.DIALOGUE_INITIATION,
                                   InterventionType.DEVELOPMENT_AID,
                                   InterventionType.COMMUNITY_ENGAGEMENT]:
                reward += 20.0  # Preventive interventions are good
            elif intervention_type in [InterventionType.SECURITY_DEPLOYMENT]:
                reward -= 15.0  # Don't militarize peaceful regions
        
        # 3. Resource efficiency
        intervention_costs = {
            InterventionType.SECURITY_DEPLOYMENT: -15.0,
            InterventionType.MEDIATION_DEPLOYMENT: -8.0,
            InterventionType.DIALOGUE_INITIATION: -5.0,
            InterventionType.DEVELOPMENT_AID: -12.0,
            InterventionType.COMMUNITY_ENGAGEMENT: -6.0,
            InterventionType.MONITOR_ONLY: -1.0
        }
        
        reward += intervention_costs.get(intervention_type, -5.0)
        
        # 4. Strategic priorities (border regions, high-activity areas)
        if target_region.is_border_region and target_region.threat_level >= ThreatLevel.MEDIUM_RISK:
            reward += 25.0  # Prioritize border security
        
        if target_region.region_name == "Extreme-Nord" and target_region.threat_level >= ThreatLevel.MEDIUM_RISK:
            reward += 30.0  # Special priority for Extreme-Nord (Boko Haram)
        
        # 5. Timing bonuses
        if target_region.threat_level == ThreatLevel.MEDIUM_RISK and intervention_type in [
            InterventionType.DIALOGUE_INITIATION, InterventionType.MEDIATION_DEPLOYMENT
        ]:
            reward += 40.0  # Big bonus for early diplomatic intervention
        
        # 6. Long-term stability
        peaceful_regions = sum(1 for r in environment.regions.values() 
                             if r.threat_level <= ThreatLevel.LOW_RISK)
        if peaceful_regions >= 7:  # 70% of regions peaceful
            reward += self.config.stability_bonus
        
        # 7. Scale the reward
        reward *= self.config.reward_scale
        
        return reward

class CurriculumLearning:
    """Curriculum learning for gradual difficulty increase."""
    
    def __init__(self):
        self.current_phase = 0
        self.phase_episodes = [100, 150, 250]  # Episodes per phase
        self.phases = [
            "simple_scenarios",
            "moderate_complexity", 
            "full_complexity"
        ]
    
    def get_current_phase(self, episode: int) -> str:
        """Get current training phase."""
        cumulative = 0
        for i, phase_length in enumerate(self.phase_episodes):
            cumulative += phase_length
            if episode < cumulative:
                return self.phases[i]
        return self.phases[-1]
    
    def modify_environment(self, environment, phase: str):
        """Modify environment based on curriculum phase."""
        if phase == "simple_scenarios":
            # Reduce complexity: fewer high-risk regions
            for region in environment.regions.values():
                if region.threat_level >= ThreatLevel.HIGH_RISK:
                    region.threat_level = ThreatLevel.MEDIUM_RISK
        
        elif phase == "moderate_complexity":
            # Standard complexity but with some constraints
            pass  # Keep normal initialization
        
        # full_complexity uses standard environment

class OptimizedDQNTrainer:
    """Optimized DQN trainer with curriculum learning."""
    
    def __init__(self, config: OptimizedTrainingConfig):
        self.config = config
        self.reward_calculator = ImprovedRewardCalculator(config)
        self.curriculum = CurriculumLearning()
        
        # Training tracking
        self.training_history = {
            'episode_rewards': [],
            'episode_lengths': [],
            'conflicts_prevented': [],
            'epsilon_values': [],
            'average_stability': [],
            'loss_values': []
        }
    
    def create_optimized_agent(self, state_size: int, action_size: int) -> DQNAgent:
        """Create agent with optimized hyperparameters."""
        
        # Get config values first
        hidden_size = self.config.hidden_size
        
        class OptimizedDQNAgent(DQNAgent):
            def __init__(self, hidden_units, *args, **kwargs):
                super().__init__(*args, **kwargs)
                
                # Override with optimized network using passed hidden_units
                from dqn_agent import DQNNetwork
                self.q_network = DQNNetwork(
                    state_size, action_size, 
                    hidden_size=hidden_units
                ).to(self.device)
                self.target_network = DQNNetwork(
                    state_size, action_size,
                    hidden_size=hidden_units
                ).to(self.device)
                
                # Update optimizer with new networks
                self.optimizer = torch.optim.Adam(
                    self.q_network.parameters(), 
                    lr=kwargs.get('learning_rate', 0.001),
                    weight_decay=1e-5  # L2 regularization
                )
                
                # Initialize target network
                self.update_target_network()
        
        agent = OptimizedDQNAgent(
            hidden_units=hidden_size,
            state_size=state_size,
            action_size=action_size,
            learning_rate=self.config.learning_rate,
            gamma=self.config.gamma,
            epsilon=self.config.epsilon_start,
            epsilon_decay=self.config.epsilon_decay,
            epsilon_min=self.config.epsilon_end,
            batch_size=self.config.batch_size,
            target_update_frequency=self.config.target_update_frequency
        )
        
        # Set the config reference
        agent.config = self.config
        
        return agent
    
    def train_optimized(self, environment: ConflictEnvironment, agent: DQNAgent) -> Dict:
        """Run optimized training with curriculum learning."""
        
        logger.info(f"🚀 Starting optimized RL training: {self.config.num_episodes} episodes")
        logger.info(f"📊 Configuration:")
        logger.info(f"   • Learning rate: {self.config.learning_rate}")
        logger.info(f"   • Batch size: {self.config.batch_size}")
        logger.info(f"   • Memory size: {self.config.memory_size}")
        logger.info(f"   • Hidden units: {self.config.hidden_size}")
        
        best_reward = float('-inf')
        
        for episode in range(self.config.num_episodes):
            # Curriculum learning
            current_phase = self.curriculum.get_current_phase(episode)
            if episode % 100 == 0:
                logger.info(f"📚 Curriculum phase: {current_phase}")
            
            # Reset environment with curriculum modifications
            state = environment.reset()
            self.curriculum.modify_environment(environment, current_phase)
            
            total_reward = 0
            conflicts_prevented = 0
            step_losses = []
            
            for step in range(self.config.max_steps_per_episode):
                # Choose action
                action = agent.act(state, safe_mode=True)
                
                # Take action
                next_state, base_reward, done, info = environment.step(action)
                
                # Calculate improved reward
                improved_reward = self.reward_calculator.calculate_reward(
                    state, action, next_state, environment
                )
                
                # Track conflict prevention
                if improved_reward > 50:  # Threshold for successful intervention
                    conflicts_prevented += 1
                
                # Store experience
                agent.remember(state, action, improved_reward, next_state, done)
                
                # Train agent
                if step % 4 == 0 and len(agent.memory) >= agent.batch_size:
                    loss = agent.replay()
                    if loss is not None:
                        step_losses.append(loss)
                
                state = next_state
                total_reward += improved_reward
                
                if done:
                    break
            
            # Calculate stability
            avg_stability = np.mean([
                4 - region.threat_level for region in environment.regions.values()
            ]) / 4.0  # Normalize to 0-1
            
            # Record episode statistics
            self.training_history['episode_rewards'].append(total_reward)
            self.training_history['episode_lengths'].append(step + 1)
            self.training_history['conflicts_prevented'].append(conflicts_prevented)
            self.training_history['epsilon_values'].append(agent.epsilon)
            self.training_history['average_stability'].append(avg_stability)
            
            if step_losses:
                self.training_history['loss_values'].append(np.mean(step_losses))
            
            # Track best performance
            if total_reward > best_reward:
                best_reward = total_reward
                # Save best model
                agent.save_model("best_conflict_prevention_model.pth")
            
            # Logging and evaluation
            if episode % self.config.evaluation_frequency == 0 and episode > 0:
                recent_rewards = self.training_history['episode_rewards'][-self.config.evaluation_frequency:]
                recent_conflicts = self.training_history['conflicts_prevented'][-self.config.evaluation_frequency:]
                recent_stability = self.training_history['average_stability'][-self.config.evaluation_frequency:]
                
                avg_reward = np.mean(recent_rewards)
                avg_conflicts = np.mean(recent_conflicts)
                avg_stability = np.mean(recent_stability)
                
                logger.info(f"Episode {episode:4d} | "
                          f"Avg Reward: {avg_reward:8.2f} | "
                          f"Conflicts Prevented: {avg_conflicts:.1f} | "
                          f"Stability: {avg_stability:.3f} | "
                          f"Epsilon: {agent.epsilon:.3f} | "
                          f"Best: {best_reward:.2f}")
            
            # Save checkpoint
            if episode % self.config.save_frequency == 0 and episode > 0:
                agent.save_model(f"checkpoint_episode_{episode}.pth")
        
        logger.info("✅ Optimized training completed!")
        
        return self.training_history
    
    def evaluate_final_performance(self, environment: ConflictEnvironment, 
                                  agent: DQNAgent, num_eval_episodes: int = 20) -> Dict:
        """Comprehensive final evaluation."""
        logger.info(f"📊 Final evaluation: {num_eval_episodes} episodes")
        
        # Load best model for evaluation
        try:
            agent.load_model("best_conflict_prevention_model.pth")
            logger.info("✅ Loaded best model for evaluation")
        except:
            logger.warning("⚠️ Could not load best model, using current")
        
        # Disable exploration for evaluation
        old_epsilon = agent.epsilon
        agent.epsilon = 0.0
        
        eval_stats = {
            'rewards': [],
            'conflicts_prevented': [],
            'stability_scores': [],
            'intervention_effectiveness': {},
            'regional_performance': {}
        }
        
        for episode in range(num_eval_episodes):
            state = environment.reset()
            total_reward = 0
            conflicts_prevented = 0
            
            for step in range(365):  # One year evaluation
                action = agent.act(state, safe_mode=True)
                next_state, _, done, info = environment.step(action)
                
                # Calculate improved reward for evaluation
                reward = self.reward_calculator.calculate_reward(
                    state, action, next_state, environment
                )
                
                if reward > 50:
                    conflicts_prevented += 1
                
                state = next_state
                total_reward += reward
                
                if done:
                    break
            
            eval_stats['rewards'].append(total_reward)
            eval_stats['conflicts_prevented'].append(conflicts_prevented)
            
            # Calculate stability
            stability = np.mean([
                4 - region.threat_level for region in environment.regions.values()
            ]) / 4.0
            eval_stats['stability_scores'].append(stability)
        
        # Restore epsilon
        agent.epsilon = old_epsilon
        
        # Calculate final metrics
        results = {
            'avg_reward': np.mean(eval_stats['rewards']),
            'std_reward': np.std(eval_stats['rewards']),
            'avg_conflicts_prevented': np.mean(eval_stats['conflicts_prevented']),
            'avg_stability': np.mean(eval_stats['stability_scores']),
            'improvement_vs_baseline': 0,  # Would compare to baseline
            'success_rate': np.mean([r > 0 for r in eval_stats['rewards']])
        }
        
        logger.info("🏆 FINAL EVALUATION RESULTS:")
        logger.info(f"   Average Reward: {results['avg_reward']:.2f} ± {results['std_reward']:.2f}")
        logger.info(f"   Conflicts Prevented: {results['avg_conflicts_prevented']:.1f}")
        logger.info(f"   System Stability: {results['avg_stability']:.3f}")
        logger.info(f"   Success Rate: {results['success_rate']:.1%}")
        
        return results
    
    def save_training_plots(self):
        """Save training progress plots."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Episode rewards
        axes[0,0].plot(self.training_history['episode_rewards'])
        axes[0,0].set_title('Episode Rewards')
        axes[0,0].set_xlabel('Episode')
        axes[0,0].set_ylabel('Total Reward')
        
        # Conflicts prevented
        axes[0,1].plot(self.training_history['conflicts_prevented'])
        axes[0,1].set_title('Conflicts Prevented per Episode')
        axes[0,1].set_xlabel('Episode')
        axes[0,1].set_ylabel('Conflicts Prevented')
        
        # Stability
        axes[1,0].plot(self.training_history['average_stability'])
        axes[1,0].set_title('System Stability')
        axes[1,0].set_xlabel('Episode')
        axes[1,0].set_ylabel('Stability Score')
        
        # Epsilon decay
        axes[1,1].plot(self.training_history['epsilon_values'])
        axes[1,1].set_title('Exploration Rate (Epsilon)')
        axes[1,1].set_xlabel('Episode')
        axes[1,1].set_ylabel('Epsilon')
        
        plt.tight_layout()
        plt.savefig('training_progress.png', dpi=300, bbox_inches='tight')
        logger.info("📊 Training plots saved to training_progress.png")

# Main optimized training execution
if __name__ == "__main__":
    logger.info("🎯 PROJECT SENTINEL - OPTIMIZED RL TRAINING")
    logger.info("=" * 60)
    
    # Create optimized configuration
    config = OptimizedTrainingConfig()
    
    # Create environment
    environment = ConflictEnvironment()
    
    # Create trainer
    trainer = OptimizedDQNTrainer(config)
    
    # Create optimized agent
    agent = trainer.create_optimized_agent(
        environment.state_space_size,
        environment.action_space_size
    )
    
    logger.info(f"🧠 Optimized Agent Created:")
    logger.info(f"   State size: {environment.state_space_size}")
    logger.info(f"   Action size: {environment.action_space_size}")
    logger.info(f"   Network size: {config.hidden_size} hidden units")
    
    # Run optimized training
    training_history = trainer.train_optimized(environment, agent)
    
    # Final evaluation
    final_results = trainer.evaluate_final_performance(environment, agent)
    
    # Save training plots
    trainer.save_training_plots()
    
    # Save training history
    with open('training_history.json', 'w') as f:
        # Convert numpy arrays to lists for JSON serialization
        history_for_json = {}
        for key, value in training_history.items():
            if isinstance(value, list):
                history_for_json[key] = value
            else:
                history_for_json[key] = str(value)
        
        json.dump({
            'training_history': history_for_json,
            'final_results': final_results,
            'config': {
                'num_episodes': config.num_episodes,
                'learning_rate': config.learning_rate,
                'hidden_size': config.hidden_size,
                'batch_size': config.batch_size
            },
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    logger.info("💾 Training history saved to training_history.json")
    logger.info("🏆 OPTIMIZED RL TRAINING COMPLETE!")
    
    # Summary
    if final_results['avg_reward'] > 0:
        logger.info("🎉 SUCCESS: Model achieved positive rewards!")
    else:
        logger.info("⚠️ Model needs further optimization")
    
    logger.info(f"✅ Best model saved as: best_conflict_prevention_model.pth")
