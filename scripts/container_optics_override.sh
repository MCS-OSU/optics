#! /bin/bash

case $1 in
    ec2[acd]) echo "$1 is valid ec2 machine name";;
    *) echo "$1 is not valid ec2 machine name - should be ec2a, ec2c, or ec2d"
        exit ;;
esac

echo "setting OPTICS_DATASTORE to $1"
export OPTICS_DATASTORE=$1

#find the run_script /
run_script="?"
for entry in /*
do
    if [[ $entry == /run_* ]]
    then
        run_script=$entry
    fi
done
if [[ $run_script == "?" ]]
then 
    echo "no run_script found - you need to shell into an optics container to run this command."
fi
echo "run_script is $run_script"

$run_script $2 $3



# #find the image file in /
# image_dir="?"
# for entry in /*
# do
#     if [[ $entry == /image__* ]]
#     then
#         image_dir=$entry
#     fi
# done
# if [[ $image_dir == "?" ]]
# then 
#     echo "no image dir found - you need to shell into an optics container to run this command."
# fi
# echo "image dir is $image_dir"
# spec_name=${image_dir/image__/}.cfg
# optics_home_runnable=${image_dir/image__/"test__"}
# echo "optics_home_runnable after init substitution is $optics_home_runnable"

# optics_home_runnable="$HOME$optics_home_runnable"
# echo "optics_home_runnable after string manip is  $optics_home_runnable"
# if [ -d $optics_home_runnable ]; then 
#     echo "optics_home_runnable $optics_home_runnable already in place"
# else
#     echo "running cp -r  $image_dir $optics_home_runnable ..."
#     cp -r $image_dir $optics_home_runnable
# fi
# echo "setting OPTICS_DATASTORE to $1"
# export OPTICS_DATASTORE=$1
# cd $optics_home_runnable

# . /miniconda3/etc/profile.d/conda.sh

# if proj == 'avoe':
#         s += f'echo "...conda activate env_{proj}"\n'
#         s += f'conda activate env_{proj}\n'
#     else:
#         s += f'echo "...conda activate env_opics_{proj}"\n'
#         s += f'conda activate env_opics_{proj}\n'

# python3 optics.py container_run specs/$spec_name
