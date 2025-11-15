"""
Debug script to identify RL training issues.
"""

try:
    print("🔧 DEBUGGING RL TRAINING ISSUES")
    print("=" * 50)
    
    # Test imports
    print("1. Testing imports...")
    from optimized_training import OptimizedTrainingConfig, OptimizedDQNTrainer
    from decision_support_framework import ConflictEnvironment
    print("✅ Imports successful")
    
    # Test configuration
    print("2. Testing configuration...")
    config = OptimizedTrainingConfig()
    print(f"✅ Config created: {config.num_episodes} episodes")
    
    # Test environment
    print("3. Testing environment...")
    environment = ConflictEnvironment()
    print(f"✅ Environment created: {len(environment.regions)} regions")
    print(f"   State space: {environment.state_space_size}")
    print(f"   Action space: {environment.action_space_size}")
    
    # Test trainer
    print("4. Testing trainer...")
    trainer = OptimizedDQNTrainer(config)
    print("✅ Trainer created")
    
    # Test agent creation
    print("5. Testing agent creation...")
    agent = trainer.create_optimized_agent(
        environment.state_space_size,
        environment.action_space_size
    )
    print(f"✅ Agent created on device: {agent.device}")
    
    # Test basic functionality
    print("6. Testing basic RL loop...")
    state = environment.reset()
    print(f"   Initial state shape: {state.shape}")
    
    action = agent.act(state, safe_mode=True)
    print(f"   Action selected: {action}")
    
    next_state, reward, done, info = environment.step(action)
    print(f"   Step reward: {reward:.2f}")
    print(f"   Next state shape: {next_state.shape}")
    
    # Test improved reward calculation
    print("7. Testing reward calculation...")
    improved_reward = trainer.reward_calculator.calculate_reward(
        state, action, next_state, environment
    )
    print(f"   Improved reward: {improved_reward:.2f}")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ RL system is working correctly")
    
except Exception as e:
    print(f"\n❌ ERROR FOUND: {str(e)}")
    import traceback
    traceback.print_exc()
    
    print(f"\n🔍 Error Details:")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error message: {str(e)}")

