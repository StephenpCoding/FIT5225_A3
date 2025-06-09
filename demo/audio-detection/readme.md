aws ecr create-repository \
  --repository-name audio \
  --region us-east-1 \
  --image-scanning-configuration scanOnPush=true \
  --image-tag-mutability MUTABLE



docker build -t 668427974616.dkr.ecr.us-east-1.amazonaws.com/audio:latest .


docker push 668427974616.dkr.ecr.us-east-1.amazonaws.com/audio:latest
