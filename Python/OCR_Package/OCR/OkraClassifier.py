from torch.nn import Conv2d
from torchvision.models.resnet import ResNet, BasicBlock


class OkraClassifier(ResNet):

    def __init__(self):

        # Init a ResNet-18 classifier
        super(OkraClassifier, self).__init__(BasicBlock, [2, 2, 2, 2], num_classes=10)
        self.conv1 = Conv2d(1, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
