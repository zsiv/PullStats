# PullStats
Example AWS SAM code-defined deployment for Lambda (python 3.9) ingestion and consumption, SQS-based queuing and Aurora Postgres RDS warehousing of statistics collected from MLB.com APIs that could theoretically be extended to any API call accessible via 'requests'

Pre-reqs:
- AWS account
- AWS setup with VPC containing both public and private subnets, public subnet containing a NAT gateway and private subnet having outbound traffic routed to that NAT gateway
- Replace hardcoded security group IDs and subnet IDs in 'template.yaml' on lines 22, 24, 47 and 49 with your VPC sec group ID and the private subnet ID
- AWS SAM setup for deployment (including AWS CLI with appropriately permissioned credentials)
- Python 3.9 and pip

Install:
- git clone this repo
- run 'sam build' followed by 'sam deploy --guided' to publish cloudformation template to your account, which will create the required resources and lambda functions

Post-install:
- Connect to Aurora Postgres instance and run schema setup in 'prep_db.pgsql' to establish required schema

Notes:
- While this could probably be deployed on a free tier account, it will likely incur minor costs when executing the Lambda functions and ongoing aurora postgres rds instance expenses
- Defaults setup resources in 'us-east-1' AWS zone

To Do:
- Hard coded secrets (nothing public facing) to be replaced with generated passwords in Secrets Manager with references in CF template
- Better logic for large API calls, such as MLB.com full game data pulls, to work around 256kb limit for SQS queue records