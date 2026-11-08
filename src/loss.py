"""Uniformly sampled L1 reconstruction objective, inherited from ALFAv1."""
import torch.nn.functional as F


def reconstruction_loss(prediction, target):
    return F.l1_loss(prediction, target)
