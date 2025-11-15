revision_content = """# DevOps AWS Lab with Terraform: Revision Guide

## Table of Contents
1. Prerequisites & Environment Setup
2. Creating & Managing AWS Key Pairs
3. AWS CLI Configuration
4. Project Structure & Files
5. Terraform Usage Workflow
6. Understanding Security Group Rules (Ingress/Egress)
7. Useful Commands & Troubleshooting
8. Sample Terraform Files

---

## 1. Prerequisites & Environment Setup

- AWS account with programmatic access.
- AWS CLI: Installed and configured.
- Terraform: Installed ([Download](https://www.terraform.io/downloads.html)).
- GitHub account for storing code.
- SSH key pair for connecting to EC2 instances.

---

## 2. Creating & Managing AWS Key Pairs

### A. Using AWS Console

1. Log into AWS Management Console.
2. Go to **EC2 > Key Pairs**.
3. Click **Create key pair**, name it (e.g., `devops-key`), select RSA, and download the `.pem` file.
4. Store the `.pem` file securely.

### B. Using AWS CLI

~~~sh
aws ec2 create-key-pair --key-name devops-key --query 'KeyMaterial' --output text > devops-key.pem
chmod 400 devops-key.pem
~~~
- Use the key name (`devops-key`) in your Terraform code.

---

## 3. AWS CLI Configuration

### Check if configured
~~~sh
aws configure list
~~~
- Shows current access key, secret key, region, and output format.

### Test configuration
~~~sh
aws sts get-caller-identity
~~~
- Returns your AWS user/account info if configured correctly.

### Configure if needed
~~~sh
aws configure
~~~
- Input your AWS Access Key, Secret Key, preferred region (e.g., `ap-south-1`), and output format (e.g., `json`).

---

## 4. Project Structure & Files

~~~text
devops-infra-lab/
│
├── main.tf        # Main Terraform configuration
├── variables.tf   # Input variables
├── outputs.tf     # Outputs after apply
└── README.md      # Documentation and usage
~~~

---

## 5. Terraform Usage Workflow

1. **Initialize Terraform**
    ~~~sh
    terraform init
    ~~~

2. **Set your key pair name**
    ~~~sh
    export TF_VAR_key_name=your-keypair-name
    ~~~

3. **Plan the deployment**
    ~~~sh
    terraform plan
    ~~~

4. **Apply the deployment**
    ~~~sh
    terraform apply
    ~~~

5. **SSH into your instance using the output public IP**
    ~~~sh
    ssh -i /path/to/your-key.pem ubuntu@<public-ip>
    ~~~

6. **Destroy Resources**
    ~~~sh
    terraform destroy
    ~~~

---

## 6. Understanding Security Group Rules

### Ingress Rule Example
~~~hcl
ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
}
~~~
- **Purpose:** Allows anyone to access your instance on port 80 (HTTP).

### Egress Rule Example
~~~hcl
egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
}
~~~
- **Purpose:** Allows your instance to send any traffic to any destination (default in AWS).

---

## 7. Useful Commands & Troubleshooting

- **Check AWS CLI configuration:**  
  `aws configure list`
- **Check AWS identity:**  
  `aws sts get-caller-identity`
- **Initialize Terraform:**  
  `terraform init`
- **Review plan:**  
  `terraform plan`
- **Apply changes:**  
  `terraform apply`
- **Show outputs:**  
  `terraform output`
- **Destroy resources:**  
  `terraform destroy`
- **SSH to instance:**  
  `ssh -i /path/to/devops-key.pem ubuntu@<public-ip>`

### Troubleshooting Tips

- If you see errors about missing credentials, re-run `aws configure`.
- Ensure your key pair name in Terraform matches the one in AWS.
- If you cannot SSH, check:
    - Security group allows port 22 from your IP.
    - Correct permissions on `.pem` file (`chmod 400 devops-key.pem`).
    - Correct username for AMI (`ubuntu` for Ubuntu, `ec2-user` for Amazon Linux).

---

## 8. Sample Terraform Files

### variables.tf

~~~hcl
variable "aws_region" {
  default = "ap-south-1"
}

variable "instance_type" {
  default = "t2.micro"
}

variable "key_name" {
  description = "SSH key pair name in your AWS account"
}
~~~

### main.tf

~~~hcl
provider "aws" {
  region = var.aws_region
}

resource "aws_vpc" "main_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public_subnet" {
  vpc_id     = aws_vpc.main_vpc.id
  cidr_block = "10.0.1.0/24"
  map_public_ip_on_launch = true
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main_vpc.id
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

resource "aws_route_table_association" "public_subnet_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_security_group" "web_sg" {
  name        = "web_sg"
  description = "Allow SSH and HTTP"
  vpc_id      = aws_vpc.main_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "web" {
  ami           = "ami-02eb7a4783e7e9317" # Ubuntu 22.04 LTS in ap-south-1
  instance_type = var.instance_type
  subnet_id     = aws_subnet.public_subnet.id
  key_name      = var.key_name
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  tags = {
    Name = "Terraform-Web-Instance"
  }
}
~~~

### outputs.tf

~~~hcl
output "instance_public_ip" {
  description = "Public IP of the web server"
  value       = aws_instance.web.public_ip
}
~~~

### README.md

~~~markdown
# DevOps AWS Lab with Terraform

## Prerequisites
- AWS account
- Terraform installed
- Existing AWS SSH key pair name

## Usage

1. Clone this repo and `cd` into the directory.
2. Initialize Terraform: terraform init
3. Set your key pair name: export TF_VAR_key_name=your-keypair-name
4. Plan the deployment: terraform plan
5. Apply the deployment: terraform apply
6. SSH into your instance using the output public IP: ssh -i /path/to/your-key.pem ubuntu@<public-ip>
## Destroy Resources:  terraform destroy
~~~


"""

filename = "devops-aws-lab-revision-guide.md"

with open(filename, "w", encoding="utf-8") as f:
    f.write(revision_content)

print(f"\nFile '{filename}' has been created successfully!\n")