"""
PROJECT SENTINEL - DEEP Q-NETWORK AGENT
Cameroon Defense Force Advanced RL System

This module implements the DQN architecture for optimal conflict intervention:
- Deep Q-Network with experience replay
- Target network for stable learning
- Exploration vs exploitation strategy
- Safe RL constraints to avoid harmful actions
- Multi-agent coordination capabilities
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque, namedtuple
import random
import logging
from typing import Dict, List, Tuple, Optional, Any
import json
from datetime import datetime

from decision_support_framework import ConflictEnvironment, InterventionType, ThreatLevel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Experience tuple for replay buffer
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])

class DQNNetwork(nn.Module):
    """Deep Q-Network for conflict prevention decision making."""
    
    def __init__(self, state_size: int, action_size: int, hidden_size: int = 512):
        super(DQNNetwork, self).__init__()
        
        self.state_size = state_size
        self.action_size = action_size
        
        # Neural network layers
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc4 = nn.Linear(hidden_size // 2, action_size)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(0.2)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize network weights using Xavier uniform."""
        for layer in [self.fc1, self.fc2, self.fc3, self.fc4]:
            nn.init.xavier_uniform_(layer.weight)
            nn.init.constant_(layer.bias, 0.01)
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network."""
        x = F.relu(self.fc1(state))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x

class ExperienceReplayBuffer:
    """Experience replay buffer for DQN training."""
    
    def __init__(self, capacity: int = 100000):
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity
    
    def push(self, state: np.ndarray, action: int, reward: float, 
             next_state: np.ndarray, done: bool):
        """Add experience to buffer."""
        experience = Experience(state, action, reward, next_state, done)
        self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """Sample a batch of experiences."""
        return random.sample(self.buffer, batch_size)
    
    def can_provide_sample(self, batch_size: int) -> bool:
        """Check if buffer has enough experiences for sampling."""
        return len(self.buffer) >= batch_size
    
    def __len__(self) -> int:
        return len(self.buffer)

class SafetyConstraints:
    """Safety constraints for conflict prevention RL."""
    
    def __init__(self):
        # Define unsafe action combinations
        self.unsafe_combinations = self._define_unsafe_combinations()
        
        # Resource limits
        self.max_military_deployments_per_week = 2
        self.max_total_resource_usage = 0.8  # 80% of total capacity
        
        # Prohibited actions in certain contexts
        self.prohibited_in_peaceful_regions = [
            InterventionType.SECURITY_DEPLOYMENT,
            InterventionType.SANCTIONS_TARGETED
        ]
    
    def _define_unsafe_combinations(self) -> List[List[InterventionType]]:
        """Define combinations of actions that should not be taken simultaneously."""
        return [
            # Don't combine military action with sanctions in same region
            [InterventionType.SECURITY_DEPLOYMENT, InterventionType.SANCTIONS_TARGETED],
            
            # Don't combine diplomatic dialogue with military deployment in same region
            [InterventionType.DIALOGUE_INITIATION, InterventionType.SECURITY_DEPLOYMENT],
        ]
    
    def is_action_safe(self, action_id: int, current_state: np.ndarray, 
                      recent_actions: List[int]) -> bool:
        """Check if an action is safe to take."""
        
        # Decode action
        intervention_type_id = action_id // 10  # 10 regions
        target_region = action_id % 10
        intervention_type = list(InterventionType)[intervention_type_id]
        
        # Extract region state (simplified - would need proper state parsing)
        region_threat_level = int(current_state[target_region * 29 + 5])  # Assuming threat level is at index 5
        
        # 1. Don't use aggressive interventions in peaceful regions
        if (region_threat_level == ThreatLevel.PEACEFUL and 
            intervention_type in self.prohibited_in_peaceful_regions):
            return False
        
        # 2. Limit military deployments per week
        recent_military_actions = sum(1 for a in recent_actions[-7:] 
                                    if list(InterventionType)[a // 10] in [
                                        InterventionType.SECURITY_DEPLOYMENT,
                                        InterventionType.PATROL_INCREASE,
                                        InterventionType.BORDER_REINFORCEMENT
                                    ])
        
        if (intervention_type in [InterventionType.SECURITY_DEPLOYMENT, 
                                InterventionType.PATROL_INCREASE, 
                                InterventionType.BORDER_REINFORCEMENT] and
            recent_military_actions >= self.max_military_deployments_per_week):
            return False
        
        # 3. Check for unsafe combinations with recent actions
        for recent_action_id in recent_actions[-3:]:  # Last 3 actions
            recent_intervention_type = list(InterventionType)[recent_action_id // 10]
            recent_target_region = recent_action_id % 10
            
            if recent_target_region == target_region:  # Same region
                for unsafe_combo in self.unsafe_combinations:
                    if (intervention_type in unsafe_combo and 
                        recent_intervention_type in unsafe_combo):
                        return False
        
        return True
    
    def get_safe_actions(self, action_values: torch.Tensor, current_state: np.ndarray,
                        recent_actions: List[int]) -> List[int]:
        """Get list of safe actions sorted by Q-value."""
        safe_actions = []
        
        # Get actions sorted by Q-value (descending)
        sorted_actions = torch.argsort(action_values, descending=True).cpu().numpy()
        
        for action_id in sorted_actions:
            if self.is_action_safe(int(action_id), current_state, recent_actions):
                safe_actions.append(int(action_id))
        
        return safe_actions

class DQNAgent:
    """Deep Q-Network Agent for conflict prevention."""
    
    def __init__(self, 
                 state_size: int,
                 action_size: int,
                 learning_rate: float = 0.001,
                 gamma: float = 0.95,
                 epsilon: float = 1.0,
                 epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01,
                 batch_size: int = 64,
                 target_update_frequency: int = 1000):
        
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.target_update_frequency = target_update_frequency
        
        # Device configuration
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"🔧 Using device: {self.device}")
        
        # Networks
        self.q_network = DQNNetwork(state_size, action_size).to(self.device)
        self.target_network = DQNNetwork(state_size, action_size).to(self.device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # Experience replay
        self.memory = ExperienceReplayBuffer(capacity=100000)
        
        # Safety constraints
        self.safety = SafetyConstraints()
        
        # Tracking
        self.steps_done = 0
        self.recent_actions = deque(maxlen=50)  # Track last 50 actions
        self.episode_rewards = []
        self.training_losses = []
        
        # Initialize target network
        self.update_target_network()
    
    def update_target_network(self):
        """Update target network with current network weights."""
        self.target_network.load_state_dict(self.q_network.state_dict())
    
    def remember(self, state: np.ndarray, action: int, reward: float,
                next_state: np.ndarray, done: bool):
        """Store experience in replay buffer."""
        self.memory.push(state, action, reward, next_state, done)
    
    def act(self, state: np.ndarray, safe_mode: bool = True) -> int:
        """Choose action using epsilon-greedy policy with safety constraints."""
        
        # Convert state to tensor
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        # Epsilon-greedy action selection
        if random.random() > self.epsilon:
            # Exploitation: choose best action
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
                
                if safe_mode:
                    # Get safe actions only
                    safe_actions = self.safety.get_safe_actions(q_values[0], state, list(self.recent_actions))
                    if safe_actions:
                        action = safe_actions[0]  # Best safe action
                    else:
                        # Fallback to monitor-only action
                        action = len(InterventionType) - 1  # MONITOR_ONLY
                else:
                    action = q_values.argmax().item()
        else:
            # Exploration: random action
            if safe_mode:
                # Random safe action
                dummy_q_values = torch.zeros(self.action_size)
                safe_actions = self.safety.get_safe_actions(dummy_q_values, state, list(self.recent_actions))
                if safe_actions:
                    action = random.choice(safe_actions)
                else:
                    action = len(InterventionType) - 1  # MONITOR_ONLY
            else:
                action = random.randint(0, self.action_size - 1)
        
        # Track action
        self.recent_actions.append(action)
        return action
    
    def replay(self) -> Optional[float]:
        """Train the model on a batch of experiences."""
        
        if not self.memory.can_provide_sample(self.batch_size):
            return None
        
        # Sample batch of experiences
        experiences = self.memory.sample(self.batch_size)
        
        # Convert to tensors
        states = torch.FloatTensor(np.array([e.state for e in experiences])).to(self.device)
        actions = torch.LongTensor([e.action for e in experiences]).to(self.device)
        rewards = torch.FloatTensor([e.reward for e in experiences]).to(self.device)
        next_states = torch.FloatTensor(np.array([e.next_state for e in experiences])).to(self.device)
        dones = torch.BoolTensor([e.done for e in experiences]).to(self.device)
        
        # Current Q values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # Next Q values from target network
        next_q_values = self.target_network(next_states).max(1)[0].detach()
        target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        # Compute loss
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), max_norm=1.0)
        
        self.optimizer.step()
        
        # Update epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        # Update target network periodically
        self.steps_done += 1
        if self.steps_done % self.target_update_frequency == 0:
            self.update_target_network()
            logger.info(f"🎯 Target network updated at step {self.steps_done}")
        
        # Track loss
        loss_value = loss.item()
        self.training_losses.append(loss_value)
        
        return loss_value
    
    def train(self, environment: ConflictEnvironment, num_episodes: int = 1000,
              max_steps_per_episode: int = 365) -> Dict[str, List[float]]:
        """Train the DQN agent on the conflict prevention environment."""
        
        logger.info(f"🚀 Starting DQN training: {num_episodes} episodes")
        
        training_stats = {
            'episode_rewards': [],
            'episode_lengths': [],
            'conflicts_prevented': [],
            'epsilon_values': []
        }
        
        for episode in range(num_episodes):
            state = environment.reset()
            total_reward = 0
            conflicts_prevented = 0
            
            for step in range(max_steps_per_episode):
                # Choose action
                action = self.act(state, safe_mode=True)
                
                # Take action in environment
                next_state, reward, done, info = environment.step(action)
                
                # Track conflicts prevented
                if reward > 10:  # Significant positive reward indicates conflict prevention
                    conflicts_prevented += 1
                
                # Store experience
                self.remember(state, action, reward, next_state, done)
                
                # Train if enough experiences
                if step % 4 == 0:  # Train every 4 steps
                    loss = self.replay()
                
                state = next_state
                total_reward += reward
                
                if done:
                    break
            
            # Record episode statistics
            training_stats['episode_rewards'].append(total_reward)
            training_stats['episode_lengths'].append(step + 1)
            training_stats['conflicts_prevented'].append(conflicts_prevented)
            training_stats['epsilon_values'].append(self.epsilon)
            
            # Logging
            if episode % 100 == 0:
                avg_reward = np.mean(training_stats['episode_rewards'][-100:])
                avg_conflicts_prevented = np.mean(training_stats['conflicts_prevented'][-100:])
                logger.info(f"Episode {episode:4d} | Avg Reward: {avg_reward:6.2f} | "
                          f"Conflicts Prevented: {avg_conflicts_prevented:.1f} | "
                          f"Epsilon: {self.epsilon:.3f} | "
                          f"Buffer Size: {len(self.memory)}")
        
        logger.info("✅ DQN training completed!")
        
        return training_stats
    
    def evaluate(self, environment: ConflictEnvironment, num_episodes: int = 10) -> Dict[str, float]:
        """Evaluate the trained agent."""
        
        logger.info(f"📊 Evaluating agent over {num_episodes} episodes...")
        
        # Temporarily disable exploration
        old_epsilon = self.epsilon
        self.epsilon = 0.0
        
        eval_stats = {
            'total_rewards': [],
            'conflicts_prevented': [],
            'high_risk_regions': [],
            'intervention_types': {}
        }
        
        for episode in range(num_episodes):
            state = environment.reset()
            total_reward = 0
            conflicts_prevented = 0
            intervention_count = {}
            
            for step in range(365):  # One year evaluation
                action = self.act(state, safe_mode=True)
                
                # Track intervention types
                intervention_type_id = action // 10
                intervention_type = list(InterventionType)[intervention_type_id]
                intervention_count[intervention_type.value] = intervention_count.get(intervention_type.value, 0) + 1
                
                next_state, reward, done, info = environment.step(action)
                
                if reward > 10:
                    conflicts_prevented += 1
                
                state = next_state
                total_reward += reward
                
                if done:
                    break
            
            # Record statistics
            eval_stats['total_rewards'].append(total_reward)
            eval_stats['conflicts_prevented'].append(conflicts_prevented)
            eval_stats['high_risk_regions'].append(info.get('total_conflicts', 0))
            
            # Aggregate intervention types
            for intervention, count in intervention_count.items():
                if intervention not in eval_stats['intervention_types']:
                    eval_stats['intervention_types'][intervention] = []
                eval_stats['intervention_types'][intervention].append(count)
        
        # Restore epsilon
        self.epsilon = old_epsilon
        
        # Calculate averages
        results = {
            'avg_reward': np.mean(eval_stats['total_rewards']),
            'avg_conflicts_prevented': np.mean(eval_stats['conflicts_prevented']),
            'avg_high_risk_regions': np.mean(eval_stats['high_risk_regions']),
            'std_reward': np.std(eval_stats['total_rewards']),
            'intervention_distribution': {k: np.mean(v) for k, v in eval_stats['intervention_types'].items()}
        }
        
        logger.info("📈 Evaluation Results:")
        logger.info(f"   Average Reward: {results['avg_reward']:.2f} ± {results['std_reward']:.2f}")
        logger.info(f"   Conflicts Prevented: {results['avg_conflicts_prevented']:.1f}")
        logger.info(f"   High-Risk Regions: {results['avg_high_risk_regions']:.1f}")
        
        return results
    
    def save_model(self, filepath: str):
        """Save the trained model."""
        torch.save({
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'steps_done': self.steps_done,
            'hyperparameters': {
                'state_size': self.state_size,
                'action_size': self.action_size,
                'learning_rate': self.learning_rate,
                'gamma': self.gamma,
                'batch_size': self.batch_size
            }
        }, filepath)
        logger.info(f"💾 Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model."""
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.q_network.load_state_dict(checkpoint['q_network_state_dict'])
        self.target_network.load_state_dict(checkpoint['target_network_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.steps_done = checkpoint['steps_done']
        
        logger.info(f"📂 Model loaded from {filepath}")

# Main demonstration and training
if __name__ == "__main__":
    logger.info("🚀 PROJECT SENTINEL - DQN AGENT TRAINING")
    logger.info("=" * 60)
    
    # Create environment
    env = ConflictEnvironment()
    
    # Create DQN agent
    agent = DQNAgent(
        state_size=env.state_space_size,
        action_size=env.action_space_size,
        learning_rate=0.001,
        gamma=0.95,
        epsilon=1.0,
        epsilon_decay=0.995,
        epsilon_min=0.05
    )
    
    logger.info(f"🧠 DQN Agent initialized:")
    logger.info(f"   State space: {env.state_space_size}")
    logger.info(f"   Action space: {env.action_space_size}")
    logger.info(f"   Device: {agent.device}")
    
    # Quick training demonstration (reduced episodes for demo)
    logger.info("\n🎯 Starting training demonstration...")
    
    training_stats = agent.train(env, num_episodes=50, max_steps_per_episode=100)
    
    # Evaluate trained agent
    logger.info("\n📊 Evaluating trained agent...")
    eval_results = agent.evaluate(env, num_episodes=5)
    
    # Save model
    model_path = "conflict_prevention_dqn_model.pth"
    agent.save_model(model_path)
    
    logger.info("\n🏆 DQN TRAINING SUMMARY:")
    logger.info(f"   Episodes completed: 50")
    logger.info(f"   Final epsilon: {agent.epsilon:.3f}")
    logger.info(f"   Buffer size: {len(agent.memory)}")
    logger.info(f"   Average reward: {eval_results['avg_reward']:.2f}")
    logger.info(f"   Conflicts prevented: {eval_results['avg_conflicts_prevented']:.1f}")
    
    logger.info("✅ DQN Agent ready for deployment!")

