data "aws_availability_zones" "availableAZ" {}

# VPC in us-east-2
module "vpc-us-east-2" {
	source = "./vpc"
	region = "us-east-2"
	namespace = "vpc-us-east-2"
	cidr_block = var.vpc_us_east_2_cidr
	public_subnet_cidr = var.public_subnet_cidr
	private_subnet_cidr = var.private_subnet_cidr
}

# ALB in us-

