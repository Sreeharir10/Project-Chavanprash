# Use the official Python image with uv pre-installed by Astral
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set the working directory inside the container
WORKDIR /app

# Speed up application startup by pre-compiling Python bytecode
ENV UV_COMPILE_BYTECODE=1

# Ensure uv copies files instead of using symlinks (best practice for Docker)
ENV UV_LINK_MODE=copy

# 1. Copy ONLY the dependency files first
# Docker will cache this layer so you don't re-download packages every time you change your code
COPY pyproject.toml uv.lock ./

# 2. Install dependencies (without installing the project code itself or dev dependencies)
RUN uv sync --frozen --no-install-project --no-dev

# 3. Copy the rest of your application code
COPY . .

# 4. Install the project itself
RUN uv sync --frozen --no-dev

# Make sure the virtual environment's executables are on the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Run your main application script
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]