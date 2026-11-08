"""Real GradScaler regression tests, including invalid-gradient state protection."""
from copy import deepcopy
import io
import unittest
from unittest.mock import patch
import torch
from src.train import backward_step


class AMPTests(unittest.TestCase):
    def make_state(self, device='cpu', enabled=True):
        p = torch.nn.Parameter(torch.tensor([1., 2.], device=device))
        z = torch.nn.Parameter(torch.tensor([3.], device=device))
        opt = torch.optim.Adam([{'params': [p]}, {'params': [z]}], lr=.01)
        scaler = torch.amp.GradScaler(device, enabled=enabled, init_scale=8.)
        return p, z, opt, scaler

    def check_overflow_and_recovery(self, device, bad_value):
        p, z, opt, scaler = self.make_state(device)
        self.assertTrue(backward_step(p.square().sum() + z.square().sum(), opt, scaler, 1.))
        before = [p.detach().clone(), z.detach().clone()]
        state = deepcopy(opt.state_dict())
        opt.zero_grad(set_to_none=True)
        hook = z.register_hook(lambda grad: torch.full_like(grad, bad_value))
        with patch('torch.nn.utils.clip_grad_norm_', side_effect=AssertionError('clipped invalid gradients')):
            self.assertFalse(backward_step(p.square().sum() + z.square().sum(), opt, scaler, 1.))
        hook.remove()
        self.assertEqual(scaler.get_scale(), 4.)
        for parameter, original in zip([p, z], before):
            self.assertTrue(torch.equal(parameter, original))
        for key, values in state['state'].items():
            for name, value in values.items():
                self.assertTrue(torch.equal(value, opt.state_dict()['state'][key][name]))
        # A checkpoint taken after overflow must retain the backed-off scale and Adam.
        buffer = io.BytesIO()
        torch.save({'optimizer': opt.state_dict(), 'scaler': scaler.state_dict()}, buffer)
        buffer.seek(0)
        checkpoint = torch.load(buffer, weights_only=False)
        opt.load_state_dict(checkpoint['optimizer']); scaler.load_state_dict(checkpoint['scaler'])
        opt.zero_grad(set_to_none=True)
        self.assertTrue(backward_step(p.square().sum() + z.square().sum(), opt, scaler, 1.))
        for parameter, original in zip([p, z], before):
            self.assertTrue(torch.isfinite(parameter).all())
            self.assertFalse(torch.equal(parameter, original))
            self.assertEqual(opt.state[parameter]['step'].item(), 2)

    def test_overflow_skips_all_groups_preserves_adam_and_recovers(self):
        for bad_value in [float('inf'), float('nan')]:
            with self.subTest(bad_value=bad_value):
                self.check_overflow_and_recovery('cpu', bad_value)

    @unittest.skipUnless(torch.cuda.is_available(), 'CUDA required')
    def test_cuda_overflow_and_recovery(self):
        self.check_overflow_and_recovery('cuda', float('inf'))

    def test_full_precision_nonfinite_gradient_remains_fatal(self):
        p, z, opt, scaler = self.make_state(enabled=False)
        p.register_hook(lambda grad: torch.full_like(grad, float('nan')))
        with self.assertRaisesRegex(FloatingPointError, 'full precision'):
            backward_step(p.sum() + z.sum(), opt, scaler, 1.)
        self.assertFalse(opt.state)

    def test_nonfinite_forward_loss_remains_fatal(self):
        p, _, opt, scaler = self.make_state()
        with self.assertRaisesRegex(FloatingPointError, 'training loss'):
            backward_step(p.sum() * float('nan'), opt, scaler, 1.)
        self.assertIsNone(p.grad)
        self.assertFalse(opt.state)

    def test_finite_gradient_norm_overflow_is_not_silently_applied(self):
        p, z, opt, scaler = self.make_state()
        p.register_hook(lambda grad: torch.full_like(grad, 1e30))
        with self.assertRaisesRegex(RuntimeError, 'non-finite'):
            backward_step(p.sum() + z.sum(), opt, scaler, 1.)
        self.assertFalse(opt.state)


if __name__ == '__main__':
    unittest.main()
