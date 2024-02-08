provider "aws" {
  access_key = var.terraform-cloud-aws-access-key-id
  secret_key = var.terraform-cloud-aws-secret-access-key
  region = "us-east-2"
}

