#!/bin/bash

sudo yum -y update
sudo amazon-linux-extras disable docker
sudo amazon-linux-extras install -y ecs
cat <<'EOF' >> /etc/ecs/ecs.config
ECS_CLUSTER=${CLUSTER_NAME}
ECS_AVAILABLE_LOGGING_DRIVERS=["json-file","syslog","awslogs","fluentd"]
ECS_LOGLEVEL=debug
EOF
systemctl enable --now --no-block ecs.service
