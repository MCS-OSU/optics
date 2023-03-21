
#!/bin/bash
echo 'invoke this script as  ". ./alias_ec2_machines.sh" to have the values stick in the environment'
alias ec2a='ssh -i shared-with-opics.pem ubuntu@3.208.150.109'
alias ec2b='ssh -i shared-with-opics.pem ubuntu@3.221.218.227'
export EC2A_URL=ubuntu@3.208.150.109
export EC2B_URL=ubuntu@3.221.218.227
