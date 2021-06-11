terraform {
  backend "remote" {
    organization = "" # Enter the Terraform Cloud Organization here
    workspaces {
      name = "app-aws-circleci"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_apprunner_auto_scaling_configuration_version" "aws-mod-workshop" {
  auto_scaling_configuration_name = "aws-mod-workshop"
  # scale between 1-5 containers
  min_size = 1
  max_size = 5
}

resource "aws_apprunner_service" "aws-mod-workshop" {
  auto_scaling_configuration_arn = aws_apprunner_auto_scaling_configuration_version.aws-mod-workshop.arn

  service_name = "aws-mod-workshop-app-runner"

  source_configuration {
    image_repository {
      image_configuration {
        port = "5000"
      }

      image_identifier      = "${var.image_name}:${var.image_tag}"
      image_repository_type = "ECR_PUBLIC"
    }

    auto_deployments_enabled = false
  }
}

output "apprunner_service_url" {
  value = aws_apprunner_service.aws-mod-workshop.service_url
}
