import sys
sys.path.insert(0, '.')
import torch
import torch.nn as nn
import numpy as np
import os

class ConstraintPredictor(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
    def forward(self, x):
        return self.network(x)

models_dir = os.path.join('models')
model_path = os.path.join(models_dir, 'constraint_predictor.pth')

model = ConstraintPredictor(input_dim=7)
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model.eval()

# Extract weights
weights = {}
for name, param in model.named_parameters():
    weights[name] = param.detach().numpy()
    print(f"Extracted {name}: {weights[name].shape}")

out_path = os.path.join(models_dir, 'constraint_predictor.npz')
np.savez(out_path, **weights)
print("Saved to", out_path)

# Test NumPy forward pass
def numpy_forward(x_np):
    # Layer 1
    w1 = weights['network.0.weight']
    b1 = weights['network.0.bias']
    x = np.dot(x_np, w1.T) + b1
    x = np.maximum(0, x) # ReLU
    
    # Layer 2 (skipping dropout during eval)
    w2 = weights['network.3.weight']
    b2 = weights['network.3.bias']
    x = np.dot(x, w2.T) + b2
    x = np.maximum(0, x) # ReLU
    
    # Layer 3
    w3 = weights['network.5.weight']
    b3 = weights['network.5.bias']
    x = np.dot(x, w3.T) + b3
    return x

# Random test
test_input = np.random.randn(5, 7).astype(np.float32)
torch_out = model(torch.tensor(test_input)).detach().numpy()
np_out = numpy_forward(test_input)

print("Torch output:\n", torch_out)
print("NumPy output:\n", np_out)
diff = np.abs(torch_out - np_out).max()
print("Max absolute difference:", diff)

