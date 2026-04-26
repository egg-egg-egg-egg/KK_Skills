#!/usr/bin/env python3
"""Save scraped Douyin comments to a JSON file."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta


def main():
    parser = argparse.ArgumentParser(description="Save Douyin comments to JSON")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file path (from opencli output)")
    parser.add_argument("--output", "-o", default=None, help="Output file path (auto-generated if omitted)")
    parser.add_argument("--indent", type=int, default=2, help="JSON indent (default: 2)")
    args = parser.parse_args()

    # Read input file
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Add timestamp if not present
    if isinstance(data, dict) and "scraped_at" not in data:
        tz = timezone(timedelta(hours=8))
        data["scraped_at"] = datetime.now(tz).isoformat()
    elif isinstance(data, list):
        tz = timezone(timedelta(hours=8))
        data = {
            "videos": data,
            "scraped_at": datetime.now(tz).isoformat()
        }

    # Auto-generate filename if not provided
    if args.output is None:
        # Try to extract ID from URL or first video
        note_id = "unknown"
        if isinstance(data, dict):
            url = data.get("url", "")
            if url:
                for segment in url.split("/"):
                    if segment.isdigit() or (len(segment) == 19 and segment.isdigit()):
                        note_id = segment
                        break
            # Fallback: try first video's aweme_id
            if note_id == "unknown" and "videos" in data and data["videos"]:
                note_id = data["videos"][0].get("aweme_id", "unknown")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"douyin_comments_{note_id}_{ts}.json"

    # Ensure output directory exists
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # Count comments
    comment_count = 0
    if isinstance(data, dict):
        comment_count = len(data.get("comments", []))
        if "videos" in data:
            for v in data["videos"]:
                comment_count += len(v.get("top_comments", []))

    # Write JSON file
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=args.indent)

    print(f"Saved {comment_count} comments to: {args.output}")
    return args.output


if __name__ == "__main__":
    main()
