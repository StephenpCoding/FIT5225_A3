# Deploy lambda via ECR

docker build --provenance=false -t docker-image:test .

aws ecr create-repository \
  --repository-name picture \
  --region ap-southeast-2 \
  --image-scanning-configuration scanOnPush=true \
  --image-tag-mutability MUTABLE


    "repository": {
        "repositoryArn": "arn:aws:ecr:ap-southeast-2:668427974616:repository/picture",
        "registryId": "668427974616",
        "repositoryName": "picture",
        "repositoryUri": "668427974616.dkr.ecr.ap-southeast-2.amazonaws.com/picture",
        "createdAt": "2025-06-08T01:07:26.781000+10:00",
        "imageTagMutability": "MUTABLE",
        "imageScanningConfiguration": {
            "scanOnPush": true
        },
        "encryptionConfiguration": {
            "encryptionType": "AES256"
        }
    }

docker tag docker-image:test 668427974616.dkr.ecr.ap-southeast-2.amazonaws.com/picture:latest

aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 668427974616.dkr.ecr.ap-southeast-2.amazonaws.com

docker build --provenance=false -t 668427974616.dkr.ecr.ap-southeast-2.amazonaws.com/picture:latest .

docker push 668427974616.dkr.ecr.us-east-1.amazonaws.com/picture:latest

aws lambda create-function \
  --function-name detect-picture \
  --package-type Image \
  --code ImageUri=668427974616.dkr.ecr.ap-southeast-2.amazonaws.com/picture:latest \
  --role arn:aws:iam::668427974616:role/LabRole \
  --memory-size 2048 \
  --timeout 180 \
  --region us-east-1 \
  --architectures arm64 \


  aws lambda update-function-code \
  --function-name detect-picture \
  --image-uri 668427974616.dkr.ecr.us-east-1.amazonaws.com/picture:latest \
  --region us-east-1 \
  --publish

  aws lambda get-function-configuration \
  --function-name detect-picture \
  --region us-east-1
  --qualifier 2


