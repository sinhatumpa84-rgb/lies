# TruthLens AI - Production Deployment Guide

## 🚀 Deployment Checklist

### Pre-Deployment ✅

- [ ] Code review completed
- [ ] All tests passing (>80% coverage)
- [ ] Security audit completed
- [ ] Performance tests passed
- [ ] Documentation updated
- [ ] Infrastructure provisioned
- [ ] Monitoring configured
- [ ] Backups configured
- [ ] Incident response plan ready
- [ ] Team trained on runbooks

---

## 1. AWS Infrastructure Setup

### 1.1 VPC & Network

```bash
# Create VPC with public/private subnets
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=truthlens-vpc}]'

# Create Public Subnet
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24 --availability-zone us-east-1a

# Create Private Subnet
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.2.0/24 --availability-zone us-east-1b

# Create Internet Gateway
aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=truthlens-igw}]'

# Create NAT Gateway (for private subnet internet access)
aws ec2 allocate-address --domain vpc
aws ec2 create-nat-gateway --subnet-id subnet-xxx --allocation-id eipalloc-xxx
```

### 1.2 RDS PostgreSQL

```bash
# Create RDS cluster
aws rds create-db-cluster \
  --db-cluster-identifier truthlens-cluster \
  --engine aurora-postgresql \
  --engine-version 15.2 \
  --master-username postgres \
  --master-user-password $(openssl rand -base64 32) \
  --database-name truthlens \
  --vpc-security-group-ids sg-xxx \
  --db-subnet-group-name truthlens-db-subnet

# Create read replica
aws rds create-db-instance \
  --db-instance-identifier truthlens-replica \
  --db-instance-class db.r6g.xlarge \
  --engine aurora-postgresql \
  --db-cluster-identifier truthlens-cluster

# Create automated backups
aws rds modify-db-cluster \
  --db-cluster-identifier truthlens-cluster \
  --backup-retention-period 30 \
  --preferred-backup-window "03:00-04:00" \
  --preferred-maintenance-window "mon:04:00-mon:05:00"
```

### 1.3 ElastiCache Redis

```bash
# Create Redis cluster
aws elasticache create-replication-group \
  --replication-group-description truthlens-cache \
  --replication-group-id truthlens-redis \
  --engine redis \
  --engine-version 7.0 \
  --cache-node-type cache.r6g.xlarge \
  --num-cache-clusters 3 \
  --automatic-failover-enabled \
  --multi-az-enabled \
  --security-group-ids sg-xxx \
  --cache-subnet-group-name truthlens-cache-subnet
```

### 1.4 ECS Cluster

```bash
# Create ECS cluster
aws ecs create-cluster \
  --cluster-name truthlens-cluster \
  --cluster-settings name=containerInsights,value=enabled

# Create security group
aws ec2 create-security-group \
  --group-name truthlens-ecs-sg \
  --description "Security group for TruthLens ECS" \
  --vpc-id vpc-xxx

# Allow inbound on port 8000
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 8000 \
  --cidr 10.0.0.0/16
```

### 1.5 S3 Buckets

```bash
# Create S3 bucket for reports
aws s3api create-bucket \
  --bucket truthlens-reports \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket truthlens-reports \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket truthlens-reports \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Block public access
aws s3api put-public-access-block \
  --bucket truthlens-reports \
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Set lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket truthlens-reports \
  --lifecycle-configuration '{
    "Rules": [{
      "Id": "DeleteOldReports",
      "Status": "Enabled",
      "ExpirationInDays": 30
    }]
  }'
```

---

## 2. Docker Image Build & Registry

### 2.1 Build Image

```bash
# Build Docker image
docker build \
  --tag truthlens/api:v1.0 \
  --build-arg ENVIRONMENT=production \
  -f Dockerfile .

# Tag for ECR
docker tag truthlens/api:v1.0 [ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/truthlens/api:v1.0
```

### 2.2 ECR Registry

```bash
# Create ECR repository
aws ecr create-repository \
  --repository-name truthlens/api \
  --region us-east-1

# Configure lifecycle policy
aws ecr put-lifecycle-policy \
  --repository-name truthlens/api \
  --lifecycle-policy-text '{
    "rules": [{
      "rulePriority": 1,
      "description": "Keep last 10 images",
      "selection": {
        "tagStatus": "any",
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": {
        "type": "expire"
      }
    }]
  }'
```

### 2.3 Image Push

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin [ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com

# Push image
docker push [ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/truthlens/api:v1.0

# Verify image
aws ecr describe-images --repository-name truthlens/api
```

---

## 3. ECS Task & Service

### 3.1 Task Definition

```bash
# Create task definition
aws ecs register-task-definition \
  --family truthlens-api \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 512 \
  --memory 1024 \
  --container-definitions '[{
    "name": "api",
    "image": "[ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/truthlens/api:v1.0",
    "portMappings": [{
      "containerPort": 8000,
      "protocol": "tcp"
    }],
    "environment": [
      {"name": "ENVIRONMENT", "value": "production"},
      {"name": "LOG_LEVEL", "value": "INFO"}
    ],
    "secrets": [
      {"name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:..."},
      {"name": "REDIS_URL", "valueFrom": "arn:aws:secretsmanager:..."},
      {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/truthlens-api",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "ecs"
      }
    },
    "healthCheck": {
      "command": ["CMD-SHELL", "curl -f http://localhost:8000/api/v1/health || exit 1"],
      "interval": 30,
      "timeout": 5,
      "retries": 3,
      "startPeriod": 60
    }
  }]'
```

### 3.2 ECS Service

```bash
# Create ECS service
aws ecs create-service \
  --cluster truthlens-cluster \
  --service-name truthlens-api \
  --task-definition truthlens-api:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=DISABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:[ACCOUNT_ID]:targetgroup/truthlens-api/xxx,containerName=api,containerPort=8000 \
  --enable-ecs-managed-tags

# Configure auto-scaling
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/truthlens-cluster/truthlens-api \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 50

# CPU scaling policy
aws application-autoscaling put-scaling-policy \
  --policy-name cpu-scaling \
  --service-namespace ecs \
  --resource-id service/truthlens-cluster/truthlens-api \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    }
  }'
```

---

## 4. API Gateway & Load Balancing

### 4.1 Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name truthlens-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4

# Create target group
aws elbv2 create-target-group \
  --name truthlens-api \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxx \
  --health-check-protocol HTTP \
  --health-check-path /api/v1/health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:[ACCOUNT_ID]:loadbalancer/app/truthlens-alb/xxx \
  --protocol HTTPS \
  --port 443 \
  --certificate-arn arn:aws:acm:us-east-1:[ACCOUNT_ID]:certificate/xxx \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

### 4.2 WAF Configuration

```bash
# Create WAF ACL
aws wafv2 create-web-acl \
  --name truthlens-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules '[{
    "Name": "RateLimitRule",
    "Priority": 1,
    "Statement": {
      "RateBasedStatement": {
        "Limit": 2000,
        "AggregateKeyType": "IP"
      }
    },
    "Action": {"Block": {}},
    "VisibilityConfig": {
      "SampledRequestsEnabled": true,
      "CloudWatchMetricsEnabled": true,
      "MetricName": "RateLimitRule"
    }
  }]'

# Associate WAF with ALB
aws wafv2 associate-web-acl \
  --web-acl-arn arn:aws:wafv2:us-east-1:[ACCOUNT_ID]:regional/webacl/truthlens-waf/xxx \
  --resource-arn arn:aws:elasticloadbalancing:us-east-1:[ACCOUNT_ID]:loadbalancer/app/truthlens-alb/xxx
```

---

## 5. CloudFront CDN

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --distribution-config '{
    "CallerReference": "truthlens-'$(date +%s)'",
    "Comment": "TruthLens AI CDN",
    "Enabled": true,
    "Origins": [{
      "Id": "myAlb",
      "DomainName": "truthlens-alb-xxx.us-east-1.elb.amazonaws.com",
      "CustomOriginConfig": {
        "HTTPPort": 80,
        "OriginProtocolPolicy": "https-only",
        "OriginSSLProtocols": {"Quantity": 1, "Items": ["TLSv1.2"]}
      }
    }],
    "DefaultCacheBehavior": {
      "TargetOriginId": "myAlb",
      "ViewerProtocolPolicy": "redirect-to-https",
      "AllowedMethods": {"Quantity": 7, "Items": ["GET","HEAD","OPTIONS","PUT","POST","PATCH","DELETE"]},
      "CachePolicyId": "4135ea3d-c35d-46eb-81d7-reeSF9D331"
    },
    "ViewerCertificate": {
      "AcmCertificateArn": "arn:aws:acm:us-east-1:[ACCOUNT_ID]:certificate/xxx",
      "SslSupportMethod": "sni-only",
      "MinimumProtocolVersion": "TLSv1.2_2021"
    }
  }'
```

---

## 6. Monitoring & Observability

### 6.1 CloudWatch Setup

```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/truthlens-api

# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name truthlens-high-cpu \
  --alarm-description "Alert when CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace "AWS/ECS" \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold

# Set up dashboard
aws cloudwatch put-dashboard \
  --dashboard-name truthlens-ops \
  --dashboard-body file://dashboard.json
```

### 6.2 X-Ray Tracing

```python
# app/middleware/xray.py
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

@app.middleware("http")
async def xray_middleware(request, call_next):
    response = await call_next(request)
    return response
```

---

## 7. Database Migration & Seeding

```bash
# Create RDS
# (Use steps above)

# Connect to database
PGPASSWORD=$DB_PASSWORD psql \
  -h truthlens-cluster.xxxxx.us-east-1.rds.amazonaws.com \
  -U postgres \
  truthlens

# Run migrations
alembic upgrade head

# Seed initial data
python -c "from app.database.seed import seed_data; seed_data()"
```

---

## 8. SSL/TLS Certificates

```bash
# Request SSL certificate
aws acm request-certificate \
  --domain-name truthlens.ai \
  --subject-alternative-names '*.truthlens.ai' \
  --validation-method DNS \
  --region us-east-1

# Verify certificate
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:[ACCOUNT_ID]:certificate/xxx

# Auto-renewal
# AWS ACM automatically renews certificates within 120 days
```

---

## 9. Secrets Management

```bash
# Store database password
aws secretsmanager create-secret \
  --name truthlens/database/password \
  --secret-string $(openssl rand -base64 32)

# Store API keys
aws secretsmanager create-secret \
  --name truthlens/openai/key \
  --secret-string "sk-..."

# Rotate secrets
aws secretsmanager rotate-secret \
  --secret-id truthlens/database/password \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:[ACCOUNT_ID]:function:rotate-secret \
  --rotation-rules AutomaticallyAfterDays=30
```

---

## 10. Continuous Deployment

### 10.1 GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t truthlens/api:${{ github.sha }} .
      
      - name: Push to ECR
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin ${{ secrets.ECR_REGISTRY }}
          docker tag truthlens/api:${{ github.sha }} ${{ secrets.ECR_REGISTRY }}/truthlens/api:latest
          docker push ${{ secrets.ECR_REGISTRY }}/truthlens/api:latest
      
      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster truthlens-cluster \
            --service truthlens-api \
            --force-new-deployment
```

---

## 11. Health Checks & Monitoring

### 11.1 Synthetic Monitoring

```python
# monitoring/health_check.py
import httpx
import asyncio

async def check_api():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.truthlens.ai/api/v1/health",
                timeout=5
            )
            assert response.status_code == 200
            print("✓ API is healthy")
        except Exception as e:
            print(f"✗ API health check failed: {e}")
            # Alert team

asyncio.run(check_api())
```

---

## 12. Rollback Procedure

```bash
# If deployment fails, rollback to previous task definition
aws ecs update-service \
  --cluster truthlens-cluster \
  --service truthlens-api \
  --task-definition truthlens-api:PREVIOUS_VERSION

# Verify rollback
aws ecs describe-services \
  --cluster truthlens-cluster \
  --services truthlens-api
```

---

## 13. Post-Deployment Verification

```bash
# Test API
curl -X POST https://api.truthlens.ai/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "text": "Person A: Hi! How are you? Person B: Good thanks!",
    "analysis_type": "balanced"
  }'

# Check logs
aws logs tail /ecs/truthlens-api --follow

# Monitor metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=truthlens-api Name=ClusterName,Value=truthlens-cluster \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

---

## 14. Maintenance & Updates

### 14.1 Weekly Tasks
- [ ] Review CloudWatch logs for errors
- [ ] Check database replication lag
- [ ] Verify backup completion
- [ ] Monitor API response times

### 14.2 Monthly Tasks
- [ ] Database maintenance window
- [ ] Security patches
- [ ] Model retraining evaluation
- [ ] Cost analysis

### 14.3 Quarterly Tasks
- [ ] Disaster recovery drill
- [ ] Security audit
- [ ] Performance optimization review
- [ ] Capacity planning

---

## Troubleshooting

### High CPU Usage
```bash
# Check ECS task metrics
aws ecs list-tasks --cluster truthlens-cluster --service-name truthlens-api
aws ecs describe-tasks --cluster truthlens-cluster --tasks <TASK_ARN>

# Scale up temporarily
aws ecs update-service --cluster truthlens-cluster --service truthlens-api --desired-count 5
```

### Database Connection Issues
```bash
# Test connection
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U postgres -d truthlens -c "SELECT 1"

# Check RDS status
aws rds describe-db-clusters --db-cluster-identifier truthlens-cluster
```

### OOM (Out of Memory) Errors
```bash
# Increase task memory
aws ecs register-task-definition --family truthlens-api --memory 2048 ...
aws ecs update-service --cluster truthlens-cluster --service truthlens-api --task-definition truthlens-api:NEW_VERSION
```

---

## Disaster Recovery

### Backup & Recovery Strategy
- **RTO**: 1 hour
- **RPO**: 15 minutes
- Automated daily backups to S3
- Cross-region replication enabled

### Recovery Procedure
1. Verify backup integrity
2. Restore database to new RDS instance
3. Update ECS task environment
4. Run health checks
5. Perform data validation

---

**Deployment Completed Successfully!**

For questions or issues, contact: ops@truthlens.ai
