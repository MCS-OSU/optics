
#!/bin/bash
echo 'invoke this script as  ". ./alias_ec2_machines.sh" to have the values stick in the environment'
alias ec2a='ssh -i shared-with-opics.pem ubuntu@3.208.150.109'
alias ec2b='ssh -i shared-with-opics.pem ubuntu@3.20.113.119'
alias ec2c='ssh -i shared-with-opics.pem ubuntu@3.221.218.227'
alias ec2d='ssh -i shared-with-opics.pem ubuntu@18.207.99.209'
export EC2A_URL=ubuntu@3.208.150.109
export EC2B_URL=ubuntu@3.20.113.119
export EC2C_URL=ubuntu@3.221.218.227
export EC2D_URL=ubuntu@18.207.99.209

echo "ec2a has 172-31-32-89 on command line"
echo "ec2b has 172-31-12-56 on command line"
echo "ec2c has 172-31-72-254 on command line"
echo "ec2d has 172-31-10-162 on command line"
