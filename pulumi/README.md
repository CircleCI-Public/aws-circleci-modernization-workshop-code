# Pulumi command Notes

pulumi config set aws:region "us-east-1a"
pulumi config set aws:ami "ami-0c3dda3deab25a563"
pulumi config set aws:key_pair "devrel-angel-rivera"
pulumi config set aws:ec2_type "t4g.medium"
pulumi config set aws:iam_profile "ec2ECSRole"
pulumi config set aws:asg_min 3
pulumi config set aws:asg_max 5
pulumi config set aws:asg_desired 3
pulumi config set aws:ecs_desired_count 3
pulumi config set docker:image_name "ariv3ra/aws-circleci-modernization-workshop-code"
pulumi config set docker:image_tag "latest"
