# shrink_docker_for_mac_hyperkit

shrink docker for mac hyperkit

it is problem of hyperkit not docker for mac

hyperkit didn't supperly shrink

if you need shrinks please use vmware and install vmwaretool even you can share the host filesystem to docker vm client and set docker lib fites to the host share path.

I try to shrink use du but the shrinked file didn't work。

by now

i think the only way to shrink is delete the  Docker.qcow2 rebuild it and load older images and containers,like dump and load

so i write this python script

since docker export/import will lost containner's env and cann't restart containers, so commit to a new image and then start new containers depend it.

this script can restart container with current port but cann't resume the volumes


in order to avoid the unexpected i suggest do it manual


# 1 python shrink.py -t save


# 2 quit docker process and remove Docker.qcow2(rename to Docker.qcow2_back is better)


# 3 start docker process it will auto rebuild a new Docker.qcow2 file,wait it accomplish


# 4 python shrink -t load

# 5 remove the tmp file

