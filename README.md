# PullStats
Example AWS SAM code-defined deployment for Lambda and SQS-based ingestion of statistics collected from MLB.com APIs

Pre-reqs:
- AWS account
- AWS SAM setup for deployment (including AWS CLI with appropriately permissioned credentials)

Post-install:
- Connect to Aurora Postgres instance and run 'prep_db.pgsql' to establish required schema

Notes:
- While this could probably be deployed on a free tier account, it will likely incur minor costs when executing the Lambda functions
- Defaults setup resources in 'us-east-1' AWS zone