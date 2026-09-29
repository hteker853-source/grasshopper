# Grasshopper — Public AWS Deployment Guide (App Runner & ECS Fargate)

This document details the deployment steps to expose Grasshopper's MCP server and web dashboard publicly over HTTPS.

> [!IMPORTANT]
> No AWS accounts were opened or live cloud deployments executed in this session. This guide provides official operating instructions for Halil. Secret credentials must never be committed to git.

---

## 1. Architectural Options

| Option | Suitability | Cost Model | HTTPS / SSL | Setup Time |
| --- | --- | --- | --- | --- |
| **AWS App Runner (Recommended)** | MCP Streamable HTTP & Web UI | Pay-per-use (minute-level vCPU/RAM) | Automatic free AWS SSL | ~5 minutes |
| **AWS ECS Fargate** | Large-scale background Chromium workers | Persistent running container | Via ALB / ACM | ~15 minutes |

---

## 2. AWS App Runner Single-Command Deployment

### A. Prerequisites (Operational Steps for Halil)
1. Log in to AWS Management Console (`us-east-1` or `eu-west-1` region).
2. Create an IAM user named `grasshopper-deployer` with `AppRunnerFullAccess` and `AmazonEC2ContainerRegistryFullAccess`.
3. Configure AWS CLI locally:
   ```bash
   aws configure
   ```

### B. Building and Pushing Docker Image to ECR
```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name grasshopper --region us-east-1

# 2. Authenticate Docker with ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# 3. Build and tag image
docker build -t grasshopper:latest .
docker tag grasshopper:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/grasshopper:latest

# 4. Push image to ECR
docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/grasshopper:latest
```

### C. Launching App Runner Service
```bash
aws apprunner create-service \
  --service-name grasshopper-live \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$(aws sts get-caller-identity --query Account --output text)'.dkr.ecr.us-east-1.amazonaws.com/grasshopper:latest",
      "ImageConfiguration": {
        "Port": "8080",
        "RuntimeEnvironmentVariables": {
          "MODE": "mock",
          "API_TOKEN": "halil-strong-secret-token",
          "MCP_BEARER_TOKEN": "alexa-secret-bearer-token",
          "MCP_ALLOWED_ORIGINS": "https://alexa.amazon.com,https://developer.amazon.com",
          "ALLOW_BEDROCK": "0",
          "BUDGET_USD_DAILY": "0.50",
          "BUDGET_USD_PER_RUN": "0.05"
        }
      },
      "ImageRepositoryType": "ECR"
    },
    "AutoDeploymentsEnabled": false
  }' \
  --instance-configuration '{"Cpu": "1024", "Memory": "2048"}' \
  --region us-east-1
```

---

## 3. Health Check and Verification

Upon completion, App Runner provisions a domain: `https://<service-id>.us-east-1.awsapprunner.com`.

1. **Health Endpoint**:
   ```bash
   curl -I https://<service-id>.us-east-1.awsapprunner.com/health
   # HTTP/1.1 200 OK
   ```

2. **MCP Tool Discovery Verification**:
   ```bash
   curl -X POST https://<service-id>.us-east-1.awsapprunner.com/mcp/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer alexa-secret-bearer-token" \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
   ```

---

## 4. Automated CI/CD via GitHub Actions (Optional)

Add repository secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (`us-east-1`)
- `APP_RUNNER_SERVICE_ARN`

Commits pushed to `main` trigger `.github/workflows/deploy.yml` to build, tag, and redeploy App Runner instances.
