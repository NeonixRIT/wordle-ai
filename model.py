'''
Sourced from: Modified from https://github.com/patrickloeber/snake-ai-pytorch/
'''


import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
import numpy as np

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_layer_sizes, output_size, device: torch.device | None = None):
        super().__init__()

        self.device = device
        if device is not None and isinstance(device, torch.device):
            self.to(device)

        layer_sizes = [input_size] + hidden_layer_sizes + [output_size]
        self.layers = [nn.Linear(layer_sizes[i], layer_sizes[i + 1], device=device) for i in range(len(layer_sizes) - 1)]
        # for layer in self.layers:
        #     print(layer)
        # exit()
        for i, layer in enumerate(self.layers):
            setattr(self, f'linear{i}', layer)


    def forward(self, x):
        i = 0
        while i < len(self.layers) - 1:
            linear_layer = getattr(self, f'linear{i}')
            x = F.relu(linear_layer(x))
            i += 1

        x = getattr(self, f'linear{len(self.layers) - 1}')(x)
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

    def load(self, model_path, train=False):
        self.load_state_dict(torch.load(model_path))
        if not train:
            self.eval()


class QTrainer:
    def __init__(self, model: Linear_QNet, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        # print('shape:', state.shape, next_state.shape, action, reward, done)
        state = torch.tensor(np.array(state), dtype=torch.float, device=self.model.device)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float, device=self.model.device)
        action = torch.tensor(action, dtype=torch.int, device=self.model.device)
        reward = torch.tensor(reward, dtype=torch.float, device=self.model.device)
        # (n, x)

        if len(state.shape) == 1:
            # (1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        # 1: predicted Q values with current state
        pred: torch.Tensor = self.model(state)


        # 2: Q_new = r + y * max(next_predicted Q value) -> only do this if not done
        # pred.clone()
        # preds[argmax(action)] = Q_new
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][action[idx].item()] = Q_new
        # End 2

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()
