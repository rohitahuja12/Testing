variable "vpc_us_east_2_cidr" {
  default = "192.0.0.0/20"
  description = "the primary CIDR block for the VPC in us-east-2"
  nullable = false
}

variable "public_subnet_cidr" {
  default = [ "192.0.1.0/24", "192.0.2.0/24", "192.0.3.0/24" ]
  description = "The list of CIDR blocks for public subnet"
  type = list(string)
  nullable = false
}

variable "private_subnet_cidr" {
  default = [ "192.0.4.0/24", "192.0.5.0/24", "192.0.6.0/24" ]
  description = "The list of CIDR blocks for private subnet"
  type = list(string)
  nullable = false
}

variable "namespace" {
  default = "tf-generated"
  nullable = false
}


