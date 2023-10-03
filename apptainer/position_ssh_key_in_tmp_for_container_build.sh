#!/bin/bash

# Issue:  after rebooting my container build machine, the contianer build will fail 
# due to missing files in /tmp.  One bit of rigging to allow the build to proceed
# without asking me to authenticate every clone (since the fresh machine being configured
# has no github metadata laying about yet) is that I position my ssh keys for github to be 
# visible to the container under /tmp.  This allows my build script to copy them into place 
# prior to interacting with github.  With this arrangement, I don’t have to authenticate 
# manually with github for every interaction.

# Since the notion of ~ is not really mapping to the local machine during build time, 
# in order to get the keys into play in the container, I have to temporarily copy them from 
# my own ~/.ssh dir into /tmp, where the container gen script can access them…

#(base) jedirv@jed-office-gpu:~/main_optics/apptainer$ cat ~/.ssh/config
#Host *
#  AddKeysToAgent yes
#  IdentityFile ~/.ssh/id_ed25519_031623

cp ~/.ssh/config /tmp/config
cp ~/.ssh/id_ed25529_031623 /tmp

