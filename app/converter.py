import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from torchvision import transforms, models
import torchvision.utils as vutils
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation
from IPython.display import HTML
from matplotlib.animation import PillowWriter
import time
from PIL import Image

model_name = "model.pth"


class HandClassifier(nn.Module):
    def __init__(self, output):
        super(HandClassifier, self).__init__()

        alexnet = models.alexnet()

        self.process = nn.Sequential(
            alexnet.features,
            nn.Conv2d(256, output, (7, 7)),
            nn.ReLU(),
            nn.Softmax2d()
        )

    def forward(self, inputs):
        return self.process(inputs).squeeze()


model = HandClassifier(3)
model.load_state_dict(torch.load(f"./app/resources/model/{model_name}"))

loader = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(256),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def convert(image_path):
    image = Image.open(image_path)
    image = loader(image).float()
    image = torch.tensor(image)

    possibility, idx = model(image).max(0)
    return possibility, idx