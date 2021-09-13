terraform {
  backend "remote" {
    organization = "" # Enter the Terraform Cloud Organization here

    workspaces {
      name = "ecr-aws-circleci"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_ecrpublic_repository" "aws_circleci_repo" {
  repository_name = var.ecr_name
}

output "ECR_REPO_ARN" {
  value = aws_ecrpublic_repository.aws_circleci_repo.arn
}

output "ECR_REG_ID" {
  value = aws_ecrpublic_repository.aws_circleci_repo.registry_id
}

output "ECR_NAME" {
  value = aws_ecrpublic_repository.aws_circleci_repo.repository_name
}

output "ECR_URI" {
  value = aws_ecrpublic_repository.aws_circleci_repo.repository_uri
}
