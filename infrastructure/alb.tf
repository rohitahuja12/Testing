resource "aws_security_group" "alb_sg" {
	name = "alb-security-group"
	description = "Allow https traffic"
	vpc_id = module.vpc-us-east-2.vpc_id
}

resource "aws_security_group_rule" "https_ingress_from_vpc" {
	security_group_id = aws_security_group.alb_sg.id
	type = "ingress"
	description = "TLS from VPC"
	from_port = 443
	to_port = 443
	protocol = "tcp"
	cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "http_ingress_from_vpc" {
	security_group_id = aws_security_group.alb_sg.id
	type = "ingress"
	description = "TLS from VPC"
	from_port = 80
	to_port = 80
	protocol = "tcp"
	cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "egress_within_vpc" {
	security_group_id = aws_security_group.alb_sg.id
	type = "egress"
	from_port = 0
	to_port = 0
	protocol = "-1"
	cidr_blocks = [var.vpc_us_east_2_cidr]
}

#resource "aws_acm_certificate" "cert" {
	#domain_name = "example.com"
	#validation_method = "DNS"

	#lifecycle {
		#create_before_destroy = true
	#}
#}

resource "aws_lb" "lb" {
	name = "alb-us-east-2"
	internal = false
	load_balancer_type = "application"
	subnets = module.vpc-us-east-2.public_subnet_ids
	security_groups = [aws_security_group.alb_sg.id]
}	

resource "aws_lb_listener" "http_listener" {
	load_balancer_arn = aws_lb.lb.arn
	port = 80
	protocol = "HTTP"

	default_action {
		type             = "fixed-response"

		fixed_response {
			content_type = "text/plain"
			message_body = "hello from the load balancer listener!"
			status_code = "200"
		}
	}
}

#resource "aws_lb_listener_rule" "health_listener_rule" {
	#listener_arn = aws_lb_listener.http_listener.arn
	#priority = 100

	#action {
		#type = "fixed-response"
		
		#fixed_response {
			#content_type = "text/plain"
			#message_body = "hello from the load balancer listener rule!!"
			#status_code = "200"
		#}
	#}

	#condition {
		#http_header {
			#http_header_name = "X-Forwarded-For"
			#values           = ["192.168.1.*"]
		#}
	#}
#}


resource "aws_lb_target_group" "health" {
	name = "health-target-group"
	port = 443
	protocol = "HTTPS"
	vpc_id = module.vpc-us-east-2.vpc_id
	health_check {}
}
