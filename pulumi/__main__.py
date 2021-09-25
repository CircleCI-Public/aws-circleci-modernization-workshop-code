"""A Python Pulumi program"""

from os import name
from typing import AsyncGenerator, List, Mapping, Protocol
import base64
import pulumi
import pulumi_aws as aws

config=pulumi.Config()
ami=config.require("ami")
ec2_type=config.require("ec2_type")
iam_profile=config.require("iam_profile")
key_pair=config.require("key_pair")
asg_min_size=int(config.require("asg_min"))
asg_max_size=int(config.require("asg_max"))
desired_capcity=int(config.require("ecs_desired_count"))
user_data = open("user_data.sh", "rb").read()
enc_user_data = base64.b64encode(user_data).decode("utf-8")


# Provion VPC and related networking elements

aws_tags={"Name":"DevRel-Arm","Owner":"Angel Rivera","Team":"Dev Rel"}

vpc_main = aws.ec2.Vpc("dev_rel_vpc", cidr_block="10.0.0.0/16",tags=aws_tags,
    enable_dns_hostnames=True,
    enable_dns_support=True
)

aws_ig = aws.ec2.InternetGateway("dev_rel_ig", vpc_id=vpc_main.id,tags=aws_tags)

aws_subnet_a = aws.ec2.Subnet("pub_subnet_a", vpc_id=vpc_main.id, cidr_block="10.0.0.0/24", availability_zone="us-east-1a", tags=aws_tags)
aws_subnet_b = aws.ec2.Subnet("pub_subnet_b", vpc_id=vpc_main.id, cidr_block="10.0.1.0/24", availability_zone="us-east-1b", tags=aws_tags)

aws_route_table = aws.ec2.RouteTable("route_table", vpc_id=vpc_main, tags=aws_tags,
    routes=[aws.ec2.RouteTableRouteArgs(
        cidr_block='0.0.0.0/0',
        gateway_id=aws_ig.id)
    ]
)

aws_rt_assoc_a = aws.ec2.RouteTableAssociation("rta_subA", route_table_id=aws_route_table.id,
    subnet_id=aws_subnet_a.id
)

aws_rt_assoc_b = aws.ec2.RouteTableAssociation("rta_subB", route_table_id=aws_route_table.id,
    subnet_id=aws_subnet_b.id
)

aws_sg_22 = aws.ec2.SecurityGroup("app-arm-22", name_prefix="app-arm-22-SSH-", vpc_id=vpc_main,
    description="Port 22 SSH", tags=aws_tags,
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )],
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        from_port=22,
        to_port=22,
        protocol="tcp",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )]
)
aws_sg_443 = aws.ec2.SecurityGroup("app-arm-443", name_prefix="app-arm-443-", vpc_id=vpc_main,
    description="Port 443 ELB", tags=aws_tags,
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )],
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        from_port=443,
        to_port=443,
        protocol="tcp",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )]
)
aws_sg_80 = aws.ec2.SecurityGroup("app-arm-80", name_prefix="app-arm-80-", vpc_id=vpc_main,
    description="Port 80 ELB", tags=aws_tags,
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )],
    ingress=[aws.ec2.SecurityGroupIngressArgs(
        from_port=80,
        to_port=80,
        protocol="tcp",
        cidr_blocks=["0.0.0.0/0"],
        ipv6_cidr_blocks=["::/0"],
    )]
)

# Provision AWS Compute Resources

iam_pol_doc = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
    actions=["sts:AssumeRole"],
    principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
        type="Service",
        identifiers=["ec2.amazonaws.com"],
    )],
)])

ecs_iam_role = aws.iam.Role("ecs_iam_role",
    path="/system/", assume_role_policy=iam_pol_doc.json
)

iam_role_attachment = aws.iam.RolePolicyAttachment("ecs_agent",
    role=ecs_iam_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
)

iam_inst_profile = aws.iam.InstanceProfile("iam_inst_profile", role=ecs_iam_role.name)



alb_target_group = aws.alb.TargetGroup("alb_tg",
    name="app-arm",
    port=80,
    protocol="HTTP",
    vpc_id=vpc_main.id,
    deregistration_delay=10,
    health_check=aws.alb.TargetGroupHealthCheckArgs(
        path="/",
        healthy_threshold=5,
        unhealthy_threshold=10,
        interval=30,
        timeout=10
    )
)

aws_alb = aws.lb.LoadBalancer("alb_main",
    name="app-arm",
    security_groups=[
        aws_sg_80.id,
    ],
    subnets=[
        aws_subnet_a.id,
        aws_subnet_b.id
    ],
    tags=aws_tags
)

aws_alb_listner = aws.lb.Listener("alb_listener",
    load_balancer_arn=aws_alb.arn,
    port=80,
    protocol="HTTP",
    default_actions=[aws.lb.ListenerDefaultActionArgs(
        type="forward",
        target_group_arn=alb_target_group.arn
    )]
)

launch_config = aws.ec2.LaunchConfiguration("asg_launch_config", 
    name_prefix="app-arm-asg-lc-",
    key_name=key_pair,
    image_id=ami,
    instance_type=ec2_type,
    iam_instance_profile=iam_inst_profile.name,
    user_data_base64=enc_user_data,
    associate_public_ip_address=True,
    root_block_device=aws.ec2.LaunchConfigurationRootBlockDeviceArgs(
        volume_size=60,
        volume_type="standard",
        delete_on_termination=True
    ),
    security_groups=[
        aws_sg_22.id,
        aws_sg_80.id,
        aws_sg_443.id
    ]
)

aws_asg = aws.autoscaling.Group("aws-asg",
    name="app-arm",
    min_size=asg_min_size,
    max_size=asg_max_size,
    desired_capacity=desired_capcity,
    launch_configuration=launch_config,
    target_group_arns=[alb_target_group.arn],
    vpc_zone_identifiers=[
        aws_subnet_a.id,
        aws_subnet_b.id
    ],
    tags=[{
        "key":"Name",
        "value":"app-arm",
        "propagate_at_launch":True
    }]
)