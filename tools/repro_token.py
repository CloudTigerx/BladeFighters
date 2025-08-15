#!/usr/bin/env python3
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path


def pack(session: dict) -> str:
    raw = json.dumps(session, separators=(",", ":")).encode("utf-8")
    compressed = gzip.compress(raw, compresslevel=5)
    checksum = hashlib.sha256(compressed).digest()[:6]  # 6 bytes = 48 bits
    payload = checksum + compressed
    token = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    return token


def unpack(token: str) -> dict:
    # Pad base64
    pad = '=' * (-len(token) % 4)
    payload = base64.urlsafe_b64decode(token + pad)
    checksum = payload[:6]
    compressed = payload[6:]
    actual = hashlib.sha256(compressed).digest()[:6]
    if actual != checksum:
        raise ValueError("checksum mismatch")
    raw = gzip.decompress(compressed)
    return json.loads(raw.decode("utf-8"))


def main() -> int:
    p = argparse.ArgumentParser(description="Pack/unpack repro tokens")
    p.add_argument("--in", dest="in_path", help="Input session JSON path")
    p.add_argument("--out", dest="out_path", default="-", help="Output path or - for stdout")
    p.add_argument("--unpack", dest="token", help="Token to unpack (prints JSON)")
    args = p.parse_args()

    if args.token:
        data = unpack(args.token)
        out = json.dumps(data, indent=2)
        if args.out_path == "-":
            print(out)
        else:
            Path(args.out_path).write_text(out, encoding="utf-8")
        return 0

    if not args.in_path:
        p.error("--in required when not using --unpack")

    session = json.loads(Path(args.in_path).read_text(encoding="utf-8"))
    tok = pack(session)
    if args.out_path == "-":
        print(tok)
    else:
        Path(args.out_path).write_text(tok, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

