resource "aws_vpc" "vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name  = "DevRel ARM VPC",
    owner = "Angel Rivera",
    team  = "DevRel Marketing"
  }
}

resource "aws_internet_gateway" "internet_gateway" {
  vpc_id = aws_vpc.vpc.id
}

resource "aws_subnet" "pub_subnet_a" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = "10.0.0.0/24"
  availability_zone = "us-east-1a"
  tags = {
    Name  = "subnet-east1-a",
    team  = "DevRel Marketing",
    owner = "Angel Rivera",
  }
}

resource "aws_subnet" "pub_subnet_b" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name  = "subnet-east1-b",
    team  = "DevRel Marketing",
    owner = "Angel Rivera"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.internet_gateway.id
  }
  tags = {
    team  = "DevRel Marketing",
    owner = "Angel Rivera"
  }
}

# Create route table association for subnet_a
resource "aws_route_table_association" "route_table_association_subA" {
  subnet_id      = aws_subnet.pub_subnet_a.id
  route_table_id = aws_route_table.public.id
}

# Create route table association for subnet_b
resource "aws_route_table_association" "route_table_association_subB" {
  subnet_id      = aws_subnet.pub_subnet_b.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "app-arm-22" {
  description = "Port 22 Admin"
  vpc_id      = aws_vpc.vpc.id
  name_prefix = "app-arm-22-SSH-"

  ingress {
    protocol    = "tcp"
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"

    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name  = "app-arm-22-SSH",
    team  = "DevRel Marketing",
    owner = "Angel Rivera"
  }
}

resource "aws_security_group" "app-arm-ELB" {
  description = "Port 443 Elastic Load Balancer"
  name_prefix = "app-arm-443-ELB-"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"

    cidr_blocks = [
      "0.0.0.0/0",
    ]
  }
  tags = {
    Name  = "app-arm-443-ELB",
    team  = "DevRel Marketing",
    owner = "Angel Rivera"
  }
}

resource "aws_security_group" "app-arm-ELB-HTTP80" {
  description = "Port 80 Elastic Load Balancer"
  name_prefix = "app-arm-ELB-80-"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"

    cidr_blocks = [
      "0.0.0.0/0",
    ]
  }
  tags = {
    Name = "app-arm-ELB-80"
  }
}

resource "aws_security_group" "app-arm-80" {
  description = "Port 80 internal dev group "
  vpc_id      = aws_vpc.vpc.id
  name_prefix = "app-arm-80-internal-"

  ingress {
    protocol  = "tcp"
    from_port = 80
    to_port   = 80
    security_groups = [
      aws_security_group.app-arm-ELB-HTTP80.id,
    ]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"

    cidr_blocks = [
      "0.0.0.0/0",
    ]
  }
  tags = {
    Name = "app-arm-80-internal"
  }
}
