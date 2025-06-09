FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

RUN dnf install -y \
  mesa-libGL \
  mesa-libGLU \
  glib2 \
  && dnf clean all

# Copy function code
COPY lambda.py ${LAMBDA_TASK_ROOT}
COPY model ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda.handler" ]