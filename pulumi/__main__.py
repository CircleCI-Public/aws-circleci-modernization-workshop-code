"""A Python Pulumi program"""

from typing import List, Mapping
import pulumi
import pulumi_aws as aws

# Provion VPC and related networking elements

aws_tags={"Name":"DevRel-Arm","Owner":"Angel Rivera","Team":"Dev Rel"}

vpc_main = aws.ec2.Vpc("dev_rel_vpc", cidr_block="10.0.0.0/16",tags=aws_tags,
    enable_dns_hostnames=True,
    enable_dns_support=True)

aws_ig = aws.ec2.InternetGateway("dev_rel_ig", vpc_id=vpc_main.id,tags=aws_tags)

aws_subnet_a = aws.ec2.Subnet("pub_subnet_a", vpc_id=vpc_main.id, cidr_block="10.0.0.0/24", availability_zone="us-east-1a", tags=aws_tags)
aws_subnet_b = aws.ec2.Subnet("pub_subnet_b", vpc_id=vpc_main.id, cidr_block="10.0.1.0/24", availability_zone="us-east-1a", tags=aws_tags)

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

