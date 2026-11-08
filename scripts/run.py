#!/usr/bin/env python
"""CLI entry point. Core implementation lives in src/."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    parser = argparse.ArgumentParser(description='ALFA2 v1: prepare / train / evaluate / infer / smoke')
    sub = parser.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare', help='Create or verify fixed splits; no training')
    prep.add_argument('--config'); prep.add_argument('--headers', action='store_true')
    tr = sub.add_parser('train', help='Prepare/check data, select a device, then train or resume')
    tr.add_argument('--config'); tr.add_argument('--resume'); tr.add_argument('--epochs', type=int)
    tr.add_argument('--device')
    tr.add_argument('--check-only', action='store_true', help='Prepare/check data and select a device; do not train')
    ev = sub.add_parser('evaluate', help='Evaluate reconstruction or i2-only longitudinal prediction')
    ev.add_argument('--checkpoint', required=True); ev.add_argument('--device', default='auto')
    ev.add_argument('--mode', choices=['reconstruction', 'longitudinal'], default='reconstruction')
    ev.add_argument('--max-samples', type=int); ev.add_argument('--manifest'); ev.add_argument('--fit-steps', type=int)
    inf = sub.add_parser('infer', help='Fit a latent and optionally edit conditions at fixed latent')
    inf.add_argument('--checkpoint', required=True); inf.add_argument('--scan-id', required=True)
    inf.add_argument('--device', default='auto'); inf.add_argument('--manifest'); inf.add_argument('--fit-steps', type=int)
    inf.add_argument('--set', action='append', default=[], metavar='CONDITION=VALUE')
    sub.add_parser('smoke', help='Small CPU synthetic end-to-end engineering check')
    args = parser.parse_args()
    from src.config import load_config
    if args.command == 'prepare':
        from src.prepare import prepare
        result = prepare(load_config(args.config), args.headers)
    elif args.command == 'train':
        from src.train import train
        if args.resume and args.config: parser.error('--resume uses the checkpoint config; omit --config')
        result = train(load_config(args.config) if not args.resume else None, args.resume,
                       args.epochs, args.device, check_only=args.check_only)
    elif args.command == 'evaluate':
        from src.evaluator import evaluate
        result = str(evaluate(args.checkpoint, args.device, args.max_samples, args.mode, args.manifest, args.fit_steps))
    elif args.command == 'infer':
        from src.inference import infer
        try:
            edits = dict((key, float(value)) for key, value in (s.split('=', 1) for s in args.set))
        except ValueError: parser.error('--set must be CONDITION=NUMBER')
        result = str(infer(args.checkpoint, args.scan_id, args.device, edits, args.manifest, args.fit_steps))
    else:
        from src.smoke import smoke
        result = smoke()
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__':
    main()
