#==================================
# Security Group Stuff
#==================================

resource "aws_security_group" "ecs_sg" {
	name = "ecs-security-group"
	description = "Allow https traffic from ALB and this SG"
	vpc_id = module.vpc-us-east-2.vpc_id
}

resource "aws_security_group_rule" "ecs_sg_allow_https_from_alb" {
	security_group_id = aws_security_group.ecs_sg.id
	type = "ingress"
	from_port = 443
	to_port = 443
	protocol = "tcp"
	source_security_group_id = aws_security_group.alb_sg.id
}

resource "aws_security_group_rule" "ecs_sg_allow_https_from_self" {
	security_group_id = aws_security_group.ecs_sg.id
	type = "ingress"
	from_port = 443
	to_port = 443
	protocol = "tcp"
	source_security_group_id = aws_security_group.ecs_sg.id
}

resource "aws_security_group_rule" "ecs_sg_allow_http_from_alb" {
	security_group_id = aws_security_group.ecs_sg.id
	type = "ingress"
	from_port = 80
	to_port = 80
	protocol = "tcp"
	source_security_group_id = aws_security_group.alb_sg.id
}

resource "aws_security_group_rule" "ecs_sg_allow_http_from_self" {
	security_group_id = aws_security_group.ecs_sg.id
	type = "ingress"
	from_port = 80
	to_port = 80
	protocol = "tcp"
	source_security_group_id = aws_security_group.ecs_sg.id
}

resource "aws_security_group_rule" "ecs_sg_allow_https_outbound" {
	security_group_id = aws_security_group.ecs_sg.id
	type = "egress"
	from_port = 0
	to_port = 0
	protocol = "-1"
	cidr_blocks = ["0.0.0.0/0"]
}

#===========================================
# ECR Repos
#===========================================

resource "aws_ecr_repository" "ecr_api" {
	name = "phoenix_api"
}



#===========================================
# ECS 
#===========================================

resource "aws_ecs_cluster" "main" {
	name = "phoenix_cluster"
}

resource "aws_ecs_service" "phoenix_api" {
	name = "phoenix_api"
	cluster = aws_ecs_cluster.main.id
	task_definition = aws_ecs_task_definition.phoenix_api_task.arn
}

#data "aws_iam_policy_document" "ecs_task_execution_policy" {
  #statement {
    #effect = "Allow"

    #actions = [
		#"sts:AssumeRole", 
		#"ecr:GetAuthorizationToken",
		#"ecr:BatchCheckLayerAvailability",
		#"ecr:GetDownloadUrlForLayer",
		#"ecr:BatchGetImage",
		#"logs:CreateLogStream",
		#"logs:PutLogEvents"
	#]
	#resource = "*"
  #}
#}

resource "aws_iam_role" "task_execution" {
  name               = "task_execution_role"
  assume_role_policy = jsonencode(
	{
		Version = "2012-10-17",
		Statement = [
			{
				Action = "sts:AssumeRole",
				Principal = {
					Service = "ecs-tasks.amazonaws.com"
				},
				Effect = "Allow",
				Sid = "",
				Path = "/"
			}
		]
	})
}

resource "aws_iam_role_policy" "task_execution" {
  name = "ecs_task_execution"
  role = aws_iam_role.task_execution.name
  policy = jsonencode(
	{
		Version = "2012-10-17",
		Statement = [
			{
				Sid = "2",
				Effect = "Allow",
				Action = [
					"ecr:GetAuthorizationToken",
					"ecr:BatchCheckLayerAvailability",
					"ecr:GetDownloadUrlForLayer",
					"ecr:BatchGetImage",
					"logs:CreateLogStream",
					"logs:PutLogEvents",
					"ecr:BatchGetImage",
					"ecr:GetAuthorizationToken",
					"ecr:GetDownloadUrlForLayer"
				],
				Resource = "*"
			}
		]
	})
}


resource "aws_ecs_task_definition" "phoenix_api_task" {
	family = "phoenix_api_task"
	requires_compatibilities = ["FARGATE"]
	cpu = 1024
	memory = 2048
	network_mode = "awsvpc"
	execution_role_arn = aws_iam_role.task_execution.arn

	
	# THIS IS GARBAGE, REPLACE ONCE IMAGE IS IN ECR
	container_definitions = <<EOF
[
	{
		"name": "phoenix_api",
		"image": "${aws_ecr_repository.ecr_api.repository_url}",
		"cpu": 1024,
		"memory": 2048,
		"networkMode": "awsvpc",
		"portMappings": [
			{
				"containerPort": 5000,
				"hostPort": 5000
			}
		]
		
	}
]
EOF
}



