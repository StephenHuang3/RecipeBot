provider "aws" {
  region = "us-east-1"
}

locals {
  app_name = "bakingbot"
}

resource "aws_security_group" "allow_http" {
  name        = "${local.app_name}-allow_http"
  description = "Allow inbound HTTP traffic"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "allow_app" {
  name        = "${local.app_name}-allow_app"
  description = "Allow inbound traffic to the application server"

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_security_group" "allow_ssh" {
  name        = "${local.app_name}-allow_ssh"
  description = "Allow inbound SSH traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_launch_configuration" "app" {
  name          = "${local.app_name}-launch_config"
  image_id      = "ami-0c94855ba95b798c7"
  instance_type = "t2.micro"

  security_groups = [
    aws_security_group.allow_http.id,
    aws_security_group.allow_ssh.id
  ]

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y httpd
              systemctl start httpd
              systemctl enable httpd
              echo "Hello, World!" > /var/www/html/index.html
              EOF

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "app" {
  name                 = "${local.app_name}-asg"
  launch_configuration = aws_launch_configuration.app.id
  min_size             = 1
  max_size             = 1
  desired_capacity     = 1

  vpc_zone_identifier = ["subnet-0ae7b4ed8b2939b1e", "subnet-07fb629516dfb0214"]

  tag {
    key                 = "Name"
    value               = "${local.app_name}-instance"
    propagate_at_launch = true
  }
}

resource "aws_elb" "app" {
  name               = "${local.app_name}-elb"
  subnets            = ["subnet-0ae7b4ed8b2939b1e", "subnet-07fb629516dfb0214"]
  security_groups    = [aws_security_group.allow_http.id]
  cross_zone_load_balancing   = true
  idle_timeout               = 400

  listener {
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTP:80/"
    interval            = 30
  }
}

resource "aws_autoscaling_attachment" "app" {
  autoscaling_group_name = aws_autoscaling_group.app.id
  elb                    = aws_elb.app.id
}

output "elb_dns_name" {
  description = "The DNS name of the ELB"
  value       = aws_elb.app.dns_name
}
