# MIT License
#
# Copyright (C) 2021. Huawei Technologies Co., Ltd. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# Inspired by https://github.com/fxia22/pointnet.pytorch/blob/master/pointnet/model.py

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable


class STNkd(nn.Module):
    def __init__(self, k: int, nc: int, bias: bool):
        super(STNkd, self).__init__()
        self.conv1 = torch.nn.Conv1d(k, nc, 1, bias=bias)
        self.conv2 = torch.nn.Conv1d(nc, nc * 4, 1, bias=bias)
        self.conv3 = torch.nn.Conv1d(nc * 4, nc * 16, 1, bias=bias)
        self.fc1 = nn.Linear(nc * 16, nc * 4, bias=bias)
        self.fc2 = nn.Linear(nc * 4, nc, bias=bias)
        self.fc3 = nn.Linear(nc, k * k, bias=bias)
        self.relu = nn.ReLU()

        # self.bn1 = nn.BatchNorm1d(nc)
        # self.bn2 = nn.BatchNorm1d(nc * 4)
        # self.bn3 = nn.BatchNorm1d(nc * 16)
        # self.bn4 = nn.BatchNorm1d(nc * 4)
        # self.bn5 = nn.BatchNorm1d(nc)
        identity = lambda x: x
        self.bn1, self.bn2, self.bn3, self.bn4, self.bn5 = [identity] * 5

        self.k = k
        self.nc = nc

    def forward(self, x):
        batchsize = x.size()[0]
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        x = torch.max(x, 2, keepdim=True)[0]
        x = x.view(-1, self.nc * 16)

        x = F.relu(self.bn4(self.fc1(x)))
        x = F.relu(self.bn5(self.fc2(x)))
        x = self.fc3(x)

        iden = (
            Variable(torch.from_numpy(np.eye(self.k).flatten().astype(np.float32)))
            .view(1, self.k * self.k)
            .repeat(batchsize, 1)
        )
        if x.is_cuda:
            iden = iden.cuda()
        x = x + iden
        x = x.view(-1, self.k, self.k)
        return x


class PNEncoder(nn.Module):
    def __init__(
        self,
        input_dim=3,
        global_features=True,
        feature_transform=True,
        nc=16,
        transform_loss_weight=0.1,
        bias=True,
    ):
        assert global_features
        super(PNEncoder, self).__init__()
        self.input_dim = input_dim
        self.nc = nc
        self.global_features = global_features
        self.feature_transform = feature_transform
        self.transform_loss_weight = transform_loss_weight

        self.transformD = STNkd(k=input_dim, nc=nc, bias=bias)
        self.conv1 = nn.Conv1d(self.input_dim, nc, 1, bias=bias)
        # self.bn1 = nn.BatchNorm1d(nc)
        self.conv2 = nn.Conv1d(nc, nc * 4, 1, bias=bias)
        # self.bn2 = nn.BatchNorm1d(nc * 4)
        self.conv3 = nn.Conv1d(nc * 4, nc * 16, 1, bias=bias)
        # self.bn3 = nn.BatchNorm1d(nc * 16)
        identity = lambda x: x
        self.bn1, self.bn2, self.bn3 = [identity] * 3
        # self.bn1, self.bn2, self.bn3 = nn.LayerNorm(nc), nn.LayerNorm(nc * 4), nn.LayerNorm(nc * 16)

        self.output_dim = nc * 16

        if self.feature_transform:
            self.transformF = STNkd(k=self.nc, nc=nc, bias=bias)

    def transform_loss(self, transD, transF):
        transform_loss_raw_number = [
            [
                feature_transform_regularizer(e.cpu()).to(e.device)
                if e is not None
                else 0.0
                for e in transD
            ],
            [
                feature_transform_regularizer(e.cpu()).to(e.device)
                if e is not None
                else 0.0
                for e in transF
            ],
        ]
        transform_loss = [
            sum(transform_loss_raw_number[0]) / len(transform_loss_raw_number[0]),
            sum(transform_loss_raw_number[1]) / len(transform_loss_raw_number[1]),
        ]
        mean_transform_loss = sum(transform_loss) / len(transform_loss)
        aux_losses = {
            "transform": {
                "value": mean_transform_loss,
                "weight": self.transform_loss_weight,
            }
        }
        return aux_losses

    def forward(self, social_vehicles_state, training=False):

        social_features, transD, transF = zip(
            *[self._forward(e) for e in social_vehicles_state]
        )

        if training:
            aux_losses = self.transform_loss(transD, transF)
            return social_features, aux_losses
        else:
            return social_features, {}

    def _forward(self, points):
        points = points.unsqueeze(-3)
        points = points.transpose(-1, -2)
        if points.numel() == 0:
            x = torch.zeros([1] + list(points.shape[2:-1]) + [self.output_dim]).to(
                points.device
            )
            transD, transF = None, None
            return x, transD, transF
        else:
            transD = self.transformD(points)
            x = points.transpose(2, 1)
            x = torch.bmm(x, transD)
            x = x.transpose(2, 1)
            x = F.relu(self.bn1(self.conv1(x)))

            if self.feature_transform:
                transF = self.transformF(x)
                x = x.transpose(2, 1)
                x = torch.bmm(x, transF)
                x = x.transpose(2, 1)
            else:
                transF = None

            point_features = x
            x = F.relu(self.bn2(self.conv2(x)))
            x = self.bn3(self.conv3(x))
            x = torch.max(x, 2, keepdim=True)[0]
            x = x.view(-1, self.output_dim)

            if self.global_features:
                return x, transD, transF
            else:
                N = points.size()[2]
                x = x.view(-1, self.nc, 1).repeat(1, 1, N)
                return torch.cat([x, point_features], 1), transD, transF


def feature_transform_regularizer(trans):
    d = trans.size()[1]
    batchsize = trans.size()[0]
    I = torch.eye(d)[None, :, :]
    if trans.is_cuda:
        I = I.cuda()
    loss = torch.mean(
        torch.norm(torch.bmm(trans, trans.transpose(2, 1)) - I, dim=(1, 2))
    )
    if torch.isnan(loss):
        loss = 0.0
    return loss
