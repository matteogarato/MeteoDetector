# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-alpine

RUN apk update && apk add python3-dev \
                        build-base

                        # gcc \
                        # libc-dev\
                        # libffi-dev
# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PROJ_DIR="/app"
ENV LOG_FILE="${PROJ_DIR}/app.log"
ENV CRON_SPEC="0 * * * *"
# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR ${PROJ_DIR}

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
# USER appuser

# Copy the source code into the container.
COPY . ${PROJ_DIR}

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
RUN echo "${CRON_SPEC} python ${PROJ_DIR}/MeteoDetector.py >> ${LOG_FILE} 2>&1" > ${PROJ_DIR}/crontab
RUN touch ${LOG_FILE} 
RUN crontab ${PROJ_DIR}/crontab
RUN crontab -l
CMD crond  && tail -f ${LOG_FILE} 
