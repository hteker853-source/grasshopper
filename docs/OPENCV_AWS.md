# OpenCV — AWS Verification Steps

No cloud account was opened in this session. The following is the manual procedure for Halil. Commands use placeholder names. Secrets must never be committed.

1. Halil logs into the AWS console. No new accounts are created from this repo.
2. Select target region. Halil sets `AWS_REGION` in `.env`.
3. Grant IAM permissions for ECR push and running an App Runner / ECS service. Keys never enter git.
4. Build `vision_service/Dockerfile` on local host machine.
5. Create ECR repository, tag, and push image.
6. Run service on App Runner or ECS/Fargate bound to port 8081. Health endpoint `/health`.
7. Configure endpoint URL as `VISION_SERVICE_URL` in `.env`. When set, `grasshopper/browser/vision.py` dispatches frames there. When empty, processing remains local.
8. `tests/test_vision_service.py` passes against local service. Live AWS endpoint unmeasured in this session.

Responsible cloud deployment rubric requirements require completing these manual operational steps.
