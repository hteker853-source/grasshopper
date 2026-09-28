# Grasshopper — Public AWS Dağıtım Kılavuzu (App Runner & ECS Fargate)

Bu belge Grasshopper MCP sunucusunu ve web arayüzünü internete genel açık (HTTPS) olarak sunmak için izlenecek dağıtım adımlarını içerir.

> [!IMPORTANT]
> Bu oturumda AWS hesabı açılmamış ve canlı buluta deploy yapılmamıştır. Bu kılavuz Halil'in uygulayacağı resmi adımlardır. Gizli anahtarlar asla repoya yazılmaz.

---

## 1. Mimari Seçenekleri

| Yöntem | Uygunluk | Maliyet Modeli | HTTPS / SSL | Kurulum Süresi |
| --- | --- | --- | --- | --- |
| **AWS App Runner (Önerilen)** | MCP Streamable HTTP ve Web UI | Kullanım başı (dakika bazlı vCPU/RAM) | Otomatik ücretsiz AWS SSL | ~5 dakika |
| **AWS ECS Fargate** | Büyük ölçekli ve arka plan Chromium işçileri | Sürekli çalışan container | ALB / ACM üzerinden | ~15 dakika |

---

## 2. AWS App Runner İle Tek Komutla Dağıtım

### A. Ön Koşullar (Halil'in Yapacağı Kök Adımlar)
1. AWS Management Console'a giriş yapın (`us-east-1` veya `eu-west-1` bölgesi).
2. IAM Console'dan `grasshopper-deployer` adında bir kullanıcı oluşturun ve `AppRunnerFullAccess`, `AmazonEC2ContainerRegistryFullAccess` yetkilerini verin.
3. Kendi makinenizde AWS CLI'ı yapılandırın:
   ```bash
   aws configure
   ```

### B. Docker İmajını ECR'ye İtme
```bash
# 1. ECR deposu oluştur
aws ecr create-repository --repository-name grasshopper --region us-east-1

# 2. ECR'ye oturum aç
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# 3. İmajı derle ve etiketle
docker build -t grasshopper:latest .
docker tag grasshopper:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/grasshopper:latest

# 4. İmajı ECR'ye yükle
docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/grasshopper:latest
```

### C. App Runner Servisini Başlatma
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
          "API_TOKEN": "halil-guclu-gizli-token",
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

## 3. Sağlık Kontrolü ve Doğrulama

App Runner dağıtım bittiğinde size `https://<service-id>.us-east-1.awsapprunner.com` adresini tahsis eder.

1. **Sağlık Kontrolü**:
   ```bash
   curl -I https://<service-id>.us-east-1.awsapprunner.com/health
   # HTTP/1.1 200 OK
   ```

2. **MCP Araç Listesi Testi**:
   ```bash
   curl -X POST https://<service-id>.us-east-1.awsapprunner.com/mcp/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer alexa-secret-bearer-token" \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
   ```

---

## 4. GitHub Actions CI/CD İle Otomatik Dağıtım (Opsiyonel)

Repo secret'larına şunlar eklenir:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (`us-east-1`)
- `APP_RUNNER_SERVICE_ARN`

Commit `main` branch'ine düştüğünde `.github/workflows/deploy.yml` ECR derlemesini yapıp servisi günceller.
