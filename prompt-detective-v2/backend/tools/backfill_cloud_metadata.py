"""Utility script to backfill cloud metadata for analysis jobs.

This script synchronises historical analysis records with the new cloud
thumbnail pipeline by inferring missing Cloudinary public IDs and generating
thumbnail URLs when possible.

Usage
-----
Activate the backend environment and run:

    python tools/backfill_cloud_metadata.py

The script respects the database configuration defined in your environment
variables (DATABASE_URL). Ensure your Cloudinary credentials are also set so
that thumbnail URLs can be generated.
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from app.database import SessionLocal
from app.models.user import AnalysisJob
from app.services.analysis import _derive_cloudinary_public_id, _is_http_url
from app.services.cloud_storage import generate_thumbnail_url


def _backfill_job(job: AnalysisJob) -> bool:
    """Update a single job in-place, returning True when modifications occur."""

    if not job.result_data:
        return False

    data = dict(job.result_data)
    changed = False

    cloud_id: Optional[str] = data.get("cloud_id")
    if not cloud_id:
        candidate_urls = [
            data.get("cloud_file_url"),
            data.get("file_url"),
            job.file_path,
        ]
        for candidate in candidate_urls:
            cloud_id = _derive_cloudinary_public_id(candidate)
            if cloud_id:
                data["cloud_id"] = cloud_id
                changed = True
                break

    if cloud_id and not _is_http_url(data.get("thumbnail_url")):
        try:
            thumbnail_url = generate_thumbnail_url(cloud_id, job.content_type)
            if thumbnail_url:
                data["thumbnail_url"] = thumbnail_url
                changed = True
        except Exception as exc:  # pragma: no cover - operational logging only
            print(f"⚠️  Failed to generate thumbnail for job {job.id}: {exc}")

    if changed:
        job.result_data = data

    return changed


def run(limit: Optional[int] = None) -> None:
    """Execute the backfill process."""

    session = SessionLocal()
    updated = 0

    try:
        query = session.query(AnalysisJob).filter(AnalysisJob.result_data != None)  # noqa: E711
        if limit is not None:
            query = query.limit(limit)

        for job in query.yield_per(50):
            if _backfill_job(job):
                updated += 1

        if updated:
            session.commit()
        else:
            session.rollback()
    finally:
        session.close()

    print(f"✅ Backfill complete. Jobs updated: {updated}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill cloud metadata for analysis jobs")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit on jobs to process")
    args = parser.parse_args()

    run(limit=args.limit)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
