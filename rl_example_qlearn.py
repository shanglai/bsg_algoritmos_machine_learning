import gymnasium as gym
import numpy as np
from collections import defaultdict

# Parámetros de Q-learning
alpha = 0.1         # tasa de aprendizaje
gamma = 0.99        # factor de descuento
epsilon = 0.1       # probabilidad de explorar
episodes = 5000
max_steps = 500

# Discretización del espacio continuo
n_bins = 6
bins = [np.linspace(-1, 1, n_bins) for _ in range(8)]  # 8 dimensiones del estado

def discretize(obs):
    return tuple(np.digitize(o, b) for o, b in zip(obs, bins))

# Q-table
Q = defaultdict(lambda: np.zeros(4))  # 4 acciones

# Crear entorno
env = gym.make("LunarLander-v3", render_mode="human")  # usa "rgb_array" si no deseas visualizar

for ep in range(episodes):
    obs, _ = env.reset(seed=None)
    state = discretize(obs)
    total_reward = 0

    for step in range(max_steps):
        # Elegir acción ε-greedy
        if np.random.rand() < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(Q[state])

        next_obs, reward, terminated, truncated, _ = env.step(action)
        next_state = discretize(next_obs)

        # Actualización Q
        best_next = np.max(Q[next_state])
        Q[state][action] += alpha * (reward + gamma * best_next - Q[state][action])

        state = next_state
        total_reward += reward

        if terminated or truncated:
            break

    #print(f"Episode {ep+1}, Total reward: {total_reward:.2f}")
    print(f"Episode {ep+1}, Total reward: {total_reward:.2f}, epsilon: {epsilon}, alpha: {alpha}")


env.close()
