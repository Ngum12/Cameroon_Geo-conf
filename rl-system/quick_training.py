"""
Quick optimized RL training - shorter version for faster results.
"""

from optimized_training import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 QUICK OPTIMIZED RL TRAINING")
    logger.info("=" * 50)
    
    # Create optimized configuration (shorter for faster results)
    config = OptimizedTrainingConfig()
    config.num_episodes = 100  # Reduced for faster training
    config.max_steps_per_episode = 200  # Shorter episodes
    config.evaluation_frequency = 20   # More frequent evaluation
    
    logger.info(f"📊 Quick Training Config:")
    logger.info(f"   • Episodes: {config.num_episodes}")
    logger.info(f"   • Max steps: {config.max_steps_per_episode}")
    logger.info(f"   • Learning rate: {config.learning_rate}")
    logger.info(f"   • Hidden size: {config.hidden_size}")
    
    # Create environment
    environment = ConflictEnvironment()
    
    # Create trainer
    trainer = OptimizedDQNTrainer(config)
    
    # Create optimized agent
    agent = trainer.create_optimized_agent(
        environment.state_space_size,
        environment.action_space_size
    )
    
    logger.info(f"🧠 Agent Ready:")
    logger.info(f"   • Device: {agent.device}")
    logger.info(f"   • Memory capacity: {len(agent.memory.buffer) if hasattr(agent.memory, 'buffer') else 'Unknown'}")
    
    # Run optimized training
    logger.info("\n🎯 Starting optimized training...")
    training_history = trainer.train_optimized(environment, agent)
    
    # Final evaluation
    logger.info("\n📊 Running final evaluation...")
    final_results = trainer.evaluate_final_performance(environment, agent, num_eval_episodes=10)
    
    # Summary
    logger.info("\n🏆 TRAINING SUMMARY:")
    logger.info(f"   • Episodes completed: {config.num_episodes}")
    logger.info(f"   • Final average reward: {final_results['avg_reward']:.2f}")
    logger.info(f"   • Conflicts prevented: {final_results['avg_conflicts_prevented']:.1f}")
    logger.info(f"   • System stability: {final_results['avg_stability']:.3f}")
    logger.info(f"   • Success rate: {final_results['success_rate']:.1%}")
    
    # Performance assessment
    if final_results['avg_reward'] > 500:
        logger.info("🎉 EXCELLENT: Model performing very well!")
    elif final_results['avg_reward'] > 0:
        logger.info("✅ GOOD: Model showing positive performance")
    else:
        logger.info("⚠️ NEEDS WORK: Model needs more training")
    
    logger.info("✅ Quick training completed!")

