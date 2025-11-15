provider "aws" {
    region = var.aws_region
}

#VPC
resource "aws_vpc" "main_vpc" {
    cidr_block = "10.0.0.0/16"
}

#subnet
resource "aws_subnet" "public_subnet" {
    vpc_id = aws_vpc.main_vpc.id
    cidr_block = "10.0.1.0/24"
    map_public_ip_on_launch = true
}

#Internet gateway
resource "aws_internet_gateway" "gw" {
    vpc_id = aws_vpc.main_vpc.id
}

#route table
resource "aws_route_table" "public_rt" {
    vpc_id = aws_vpc.main_vpc.id
    
    route {
      cidr_block = "0.0.0.0/0"
      gateway_id = aws_internet_gateway.gw.id
    }
}

resource "aws_route_table_association" "public_subnet_association" {
    subnet_id = aws_subnet.public_subnet.id
    route_table_id = aws_route_table.public_rt.id
}

#Security Group
resource "aws_security_group" "web_sg" {
    name = "web_sg"
    description = "Allow SSH and HTTP"
    vpc_id = aws_vpc.main_vpc.id

    ingress{
        from_port = 22
        to_port   = 22
        protocol  = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
    
    ingress {
        from_port  = 80
        to_port    = 80
        protocol   = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
   }
    
    egress {
        from_port  = 0
        to_port    = 0
        protocol   = "-1"
        cidr_blocks = ["0.0.0.0/0"]
   }
}

#Ec2 Instance
resource "aws_instance" "web" {
       ami = "ami-016fd3af5e1c04fce"    # Ubuntu 22.04 ARM64 (latest)
       instance_type = var.instance_type
       subnet_id  = aws_subnet.public_subnet.id
       key_name   = var.key_name
       vpc_security_group_ids = [aws_security_group.web_sg.id]

       tags = {
         Name = "Terraform-Web-Instance"
       }
}
