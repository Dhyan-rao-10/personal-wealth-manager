#!/usr/bin/env bash
# Starts the wealth-manager image and waits up to 30 seconds for /health to answer.
# The app takes a moment to start, so early connection errors are expected and retried.
set -u

docker run -d --name smoke -p 8000:8000 wealth-manager

for attempt in $(seq 1 30); do
  if curl --fail --silent http://localhost:8000/health; then
    echo
    echo "Container is healthy after ${attempt} attempt(s)."
    exit 0
  fi
  sleep 1
done

echo "Container did not become healthy. Its logs:"
docker logs smoke
exit 1
