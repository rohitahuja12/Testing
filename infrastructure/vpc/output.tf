
output "vpc_id" {
  value = "${aws_vpc.vpc.id}"
}

output "public_subnet_ids" {
  value = [
	  aws_subnet.publicsubnet[0].id, 
	  aws_subnet.publicsubnet[1].id, 
	  aws_subnet.publicsubnet[2].id
  ]
}
