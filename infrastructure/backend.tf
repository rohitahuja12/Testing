# The block below configures Terraform to use the 'remote' backend with Terraform Cloud.
# For more information, see https://www.terraform.io/docs/backends/types/remote.html
terraform {
  required_providers {
  	aws = {
	  source = "hashicorp/aws"
	  version = "~> 4.0"
	}
  }

  backend "remote" {
    organization = "brightest-bio"

    workspaces {
      name = "Phoenix"
    }
  }

  required_version = ">= 0.14.0"
}
