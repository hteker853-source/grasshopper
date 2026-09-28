# Vision service image. The process listens on 0.0.0.0 so a container platform can reach it.
# Local runs of this app should still bind 127.0.0.1.
FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir fastapi==0.141.1 uvicorn==0.54.0 \
    opencv-python-headless==5.0.0.93 numpy==2.4.6 pillow==12.3.0 python-multipart==0.0.32
COPY grasshopper /app/grasshopper
COPY vision_service /app/vision_service
ENV PYTHONPATH=/app
EXPOSE 8081
CMD ["uvicorn", "vision_service.app:app", "--host", "0.0.0.0", "--port", "8081"]
