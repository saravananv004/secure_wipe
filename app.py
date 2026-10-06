from __future__ import annotations

import os
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, flash
from scanner import scan_devices
from wipe_algorithm import wipe_directory, is_path_allowed
from verify import verify_wipe
from certificate import generate_certificate
from logger import write_log, read_recent_logs

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.secret_key = "secure-wipe-final-year-project"

JOBS: Dict[str, Dict[str, Any]] = {}


def normalize_target_path(raw_path: str) -> str:
    return os.path.abspath(os.path.expanduser(raw_path.strip().strip('"')))


def create_job(target_path: str, passes: int) -> str:
    job_id = uuid.uuid4().hex
    JOBS[job_id] = {
        "id": job_id,
        "target_path": target_path,
        "passes": passes,
        "status": "queued",
        "message": "Job created",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "started_at": None,
        "completed_at": None,
        "progress_current": 0,
        "progress_total": 0,
        "percent": 0,
        "files_wiped": 0,
        "bytes_wiped": 0,
        "verification": False,
        "certificate_path": None,
        "errors": [],
    }
    return job_id


@app.route("/")
def index():
    devices = scan_devices()
    recent_jobs = list(JOBS.values())[-5:][::-1]
    return render_template("index.html", devices=devices, recent_jobs=recent_jobs)


@app.post("/start")
def start_job():
    raw_path = request.form.get("target_path", "")
    passes = int(request.form.get("passes", "3"))
    target_path = normalize_target_path(raw_path)

    if not raw_path:
        flash("Enter a folder path to wipe.", "danger")
        return redirect(url_for("index"))

    if not os.path.exists(target_path):
        flash("The selected path does not exist.", "danger")
        return redirect(url_for("index"))

    if not os.path.isdir(target_path):
        flash("Only folder wiping is allowed in this demo version.", "danger")
        return redirect(url_for("index"))

    allowed, reason = is_path_allowed(target_path)
    if not allowed:
        flash(reason, "danger")
        return redirect(url_for("index"))

    job_id = create_job(target_path, passes)
    thread = threading.Thread(target=run_job, args=(job_id,), daemon=True)
    thread.start()
    return redirect(url_for("job_page", job_id=job_id))


@app.route("/job/<job_id>")
def job_page(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("index"))
    return render_template("job.html", job=job)


@app.route("/api/job/<job_id>")
def job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.route("/logs")
def logs_page():
    return render_template("logs.html", logs=read_recent_logs(200))


@app.route("/certificate/<job_id>")
def download_certificate(job_id: str):
    job = JOBS.get(job_id)
    if not job or not job.get("certificate_path"):
        flash("Certificate not available yet.", "danger")
        return redirect(url_for("index"))
    return send_file(job["certificate_path"], as_attachment=True)


@app.route("/health")
def health():
    return {"status": "ok", "app": "secure-wipe-flask-premium"}


def run_job(job_id: str) -> None:
    job = JOBS[job_id]
    job["status"] = "running"
    job["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    job["message"] = "Secure wipe started"
    write_log(f"[{job_id}] Wipe started for {job['target_path']} with {job['passes']} passes")

    def progress_callback(done: int, total: int, last_file: str | None = None, bytes_wiped: int = 0):
        job["progress_current"] = done
        job["progress_total"] = total
        job["files_wiped"] = done
        job["bytes_wiped"] = bytes_wiped
        job["percent"] = int((done / total) * 100) if total else 0
        if last_file:
            job["message"] = f"Wiped: {last_file}"

    try:
        summary = wipe_directory(job["target_path"], job["passes"], progress_callback=progress_callback)
        job["files_wiped"] = summary["files_wiped"]
        job["bytes_wiped"] = summary["bytes_wiped"]
        job["progress_current"] = summary["files_wiped"]
        job["progress_total"] = summary["total_files"]
        job["percent"] = 100 if summary["total_files"] or summary["files_wiped"] == 0 else job["percent"]

        verified = verify_wipe(job["target_path"])
        job["verification"] = verified

        cert_path = generate_certificate(
            target_path=job["target_path"],
            passes=job["passes"],
            files_wiped=job["files_wiped"],
            bytes_wiped=job["bytes_wiped"],
            verification=verified,
        )
        job["certificate_path"] = cert_path
        job["status"] = "completed" if verified else "completed_with_warning"
        job["message"] = "Wipe completed successfully" if verified else "Wipe finished, but verification found remaining files"
        write_log(f"[{job_id}] Wipe finished for {job['target_path']} | verified={verified} | files={job['files_wiped']}")
    except Exception as exc:
        job["status"] = "failed"
        job["errors"].append(str(exc))
        job["message"] = f"Job failed: {exc}"
        write_log(f"[{job_id}] ERROR: {exc}")
    finally:
        job["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
