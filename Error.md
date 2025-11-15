---

## 1. InvalidKeyPair.NotFound

**Error Message:**

InvalidKeyPair.NotFound: The key pair 'devops-key.pem' does not exist

**Cause:**  
Terraform or AWS could not find a key pair by that name in your AWS account.

**Solution Steps:**
- **Check your AWS Console → EC2 → Key Pairs** for the exact key name.
- **Key names in AWS do not have `.pem`**; the `.pem` is your local file.
- **Correct in Terraform:**  
  ```hcl
  key_name = "devops-key"

If needed, create a key pair:

- In AWS Console: EC2 → Key Pairs → Create key pair.
- Or with AWS CLI: 

~~~sh
aws ec2 create-key-pair --key-name devops-key --query 'KeyMaterial' --output text > devops-key.pem
chmod 400 devops-key.pem
~~~

- Set the Terraform variable:

~~~sh
export TF_VAR_key_name=devops-key
~~~


##2. Free Tier Instance Type Error 

Error Message: 

InvalidParameterCombination: The specified instance type is not eligible for Free Tier.  

Cause: 

The EC2 instance type you specified is not Free Tier eligible. 

Solution Steps: 

Use Free Tier eligible instance types: 

t2.micro in most regions (x86_64 architecture) 

t3.micro in some regions (x86_64 architecture) 

t4g.small in some regions (ARM64 architecture) 

Update your Terraform configuration: 

instance_type = "t2.micro"  

or 

instance_type = "t4g.small"  

To find Free Tier eligible types in your region: 

aws ec2 describe-instance-types --filters Name=free-tier-eligible,Values=true --region <your-region>  

 

 

##3. ARM Instance AMI Compatibility 

Issue: 

If you use an ARM instance type (like t4g.small), your AMI must be ARM64 compatible. 

Solution Steps: 

Find an ARM64 Ubuntu AMI for your region: 

aws ec2 describe-images \ --owners 099720109477 \ --filters "Name=architecture,Values=arm64" "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-arm64-server-*" \ --query 'Images[*].[ImageId,Name]' --output text --region <your-region>  

Update your Terraform EC2 resource with the correct ami ID. 

 

 

##4. AWS CLI Region Syntax Error 

Error Message: 

bash: syntax error near unexpected token `newline'  

Cause: 

You used <your-region> (with angle brackets) in your AWS CLI command. 

Solution: 

Replace <your-region> with your real region code (no brackets).--region ap-south-1 Example:aws ec2 describe-images ... --region ap-south-1  

eg for mumbai region
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=architecture,Values=arm64" "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-arm64-server-*" \
  --query 'Images[*].[ImageId,Name]' --output text --region ap-south-1

 

 

##5. Choosing the Correct Ubuntu ARM64 AMI 

What to Look For: 

Use the most recent AMI for stability and security. 

Example output:ami-016fd3af5e1c04fce ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-arm64-server-20251111  

Update your Terraform EC2 resource: 

ami = "ami-016fd3af5e1c04fce" instance_type = "t4g.small"  

 

##6. General Troubleshooting Tips 

Check your AWS key pair name: 

Must match exactly, no .pem extension. 

Confirm AMI architecture matches instance type: 

Use ARM64 AMIs for ARM instance types. 

Permissions: 

Your .pem file must be set to chmod 400. 

SSH username: 

ubuntu for Ubuntu AMIs, ec2-user for Amazon Linux. 

Security group: 

Ensure SSH (port 22) is open to your IP. 

Re-run Terraform after changes: terraform apply  

 

 

Example: Correct EC2 Resource for Ubuntu ARM Free Tier 

resource "aws_instance" "web" { ami = "ami-016fd3af5e1c04fce" # Ubuntu 22.04 ARM64 instance_type = "t4g.small" subnet_id = aws_subnet.public_subnet.id key_name = var.key_name vpc_security_group_ids = [aws_security_group.web_sg.id] tags = { Name = "Terraform-Web-Instance" } }  

 