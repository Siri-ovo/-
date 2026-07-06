#!/usr/bin/env bash
set -u
cd /root/my_project/career_app || exit 1
export PYTHONPATH=.
while true; do
  printf '[%s] starting streamlit\n' "$(date '+%F %T')"
  /root/my_project/career_app/.venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
  code=$?
  printf '[%s] streamlit exited with code %s; restarting in 5s\n' "$(date '+%F %T')" "$code"
  sleep 5
done
