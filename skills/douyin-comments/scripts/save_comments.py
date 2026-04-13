#!/usr/bin/env python3
"""Save scraped Douyin comments to a JSON file."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta


def main():
    parser = argparse.ArgumentParser(description="Save Douyin comments to JSON")
    parser.add_argument("--data", required=True, help="JSON string of comments data")
    parser.add_argument("--output", default=None, help="Output file path (auto-generated if omitted)")
    parser.add_argument("--indent", type=int, default=2, help="JSON indent (default: 2)")
    args = parser.parse_args()

    # Parse the JSON data
    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Add timestamp if not present
    if "scraped_at" not in data:
        tz = timezone(timedelta(hours=8))
        data["scraped_at"] = datetime.now(tz).isoformat()

    # Auto-generate filename if not provided
    if args.output is None:
        # Extract note/video ID from URL
        url = data.get("url", "")
        note_id = "unknown"
        for segment in url.split("/"):
            if segment.isdigit() or (len(segment) == 19 and segment.isdigit()):
                note_id = segment
                break
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"douyin_comments_{note_id}_{ts}.json"

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)

    # Write JSON file
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=args.indent)

    print(f"Saved {len(data.get('comments', []))} comments to: {args.output}")
    return args.output


if __name__ == "__main__":
    main()
