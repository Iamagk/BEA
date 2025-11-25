#!/usr/bin/env python3
"""
Simple CLI to analyze email/text files for phishing/scam risk.

Usage:
  python server/cli.py /path/to/email.eml
  python server/cli.py /path/to/folder_with_emails/ --json out.json

"""
import argparse
import json
import os
import sys
from email import policy
from email.parser import BytesParser
from typing import List

# Support running as script (`python server/cli.py`) or as module (`python -m server.cli`).
try:
    # when imported as package
    from .model import analyze_text
except Exception:
    # fallback when running the script directly
    # ensure server/ is on sys.path so `import model` finds server/model.py
    if os.path.dirname(__file__) not in sys.path:
        sys.path.insert(0, os.path.dirname(__file__))
    from model import analyze_text


def parse_file(path: str) -> str:
    """Return the textual content of an email or raw text file."""
    _, ext = os.path.splitext(path.lower())
    try:
        if ext in ('.eml',):
            with open(path, 'rb') as f:
                msg = BytesParser(policy=policy.default).parse(f)
            parts: List[str] = []
            # Prefer plain text part(s)
            if msg.is_multipart():
                for p in msg.walk():
                    ctype = p.get_content_type()
                    if ctype == 'text/plain':
                        try:
                            parts.append(p.get_content())
                        except Exception:
                            pass
            else:
                try:
                    parts.append(msg.get_content())
                except Exception:
                    pass
            if parts:
                return '\n\n'.join(parts)
            # fallback to subject + body if available
            subj = msg.get('subject', '') or ''
            body = msg.get_body(preferencelist=('plain', 'html'))
            body_text = body.get_content() if body is not None else ''
            return subj + '\n\n' + body_text
        else:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    except Exception as e:
        return f"""[Could not read file {path}: {e}]"""


def analyze_path(path: str):
    text = parse_file(path)
    return analyze_text(text, sender=None)


def find_files(paths: List[str]) -> List[str]:
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in files:
                    if f.lower().endswith(('.eml', '.txt')):
                        out.append(os.path.join(root, f))
        elif os.path.isfile(p):
            out.append(p)
    return sorted(out)


def main():
    parser = argparse.ArgumentParser(description='Analyze email/text files for phishing risk')
    parser.add_argument('paths', nargs='+', help='File or directory paths to analyze')
    parser.add_argument('--json', '-j', dest='out_json', help='Write results to JSON file')
    args = parser.parse_args()

    files = find_files(args.paths)
    if not files:
        print('No .eml or .txt files found in the provided paths.')
        return

    results = {}
    for f in files:
        print(f'Analyzing: {f}')
        res = analyze_path(f)
        level = res.get('risk_level')
        score = res.get('risk_score')
        reasons = res.get('reasons', [])
        verdict = 'SCAM' if level in ('high',) else 'POTENTIAL' if level == 'medium' else 'OK'
        print(f'  Verdict: {verdict}  Risk: {score}  Level: {level}')
        if reasons:
            print('  Reasons: ' + '; '.join(reasons))
        print('')
        results[f] = {
            'verdict': verdict,
            'risk_score': score,
            'risk_level': level,
            'reasons': reasons,
            'details': res.get('details', {}),
        }

    if args.out_json:
        with open(args.out_json, 'w', encoding='utf-8') as fh:
            json.dump(results, fh, indent=2)
        print(f'Wrote JSON results to {args.out_json}')


if __name__ == '__main__':
    main()
