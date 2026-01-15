FROM futureys/claude-code-python-development:20251104123000
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
