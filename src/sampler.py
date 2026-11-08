"""Index-derived z,y,x coordinates avoid allocating a full GPU coordinate grid."""
import torch


def coords_from_indices(indices, shape):
    d, h, w = shape
    z = indices // (h * w)
    y = (indices // w) % h
    x = indices % w
    return torch.stack([z.float() / max(d - 1, 1), y.float() / max(h - 1, 1),
                        x.float() / max(w - 1, 1)], dim=-1) * 2. - 1.


def sample_voxels(volume, points):
    batch = volume.shape[0]
    flat = volume.reshape(batch, -1)
    indices = torch.randint(flat.shape[1], (batch, points), device=volume.device)
    return coords_from_indices(indices, volume.shape[-3:]), flat.gather(1, indices).unsqueeze(-1)
