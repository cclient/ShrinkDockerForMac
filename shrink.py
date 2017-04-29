#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Cui Dapeng'
__version__ = '0.1.0'
__description__ = 'MongoDB backup and restore utility'
__license__ = 'MIT'

import os
import argparse
import subprocess
import re

__author__ = 'Cui Dapeng'
__version__ = '0.1.0'
__description__ = 'shrink docker for mac hyperkit vm harddisk(commit docker container,save docker images,then reload、restart)'
__license__ = 'MIT'

parser = argparse.ArgumentParser(description='shrink docker,by default it only retain running container,other container will be lost')

parser.add_argument('-t', '--task',
                    type=str,
                    required=False,
                    default='save',
                    help='save,commint container and save image;load,load image and restar container')

parser.add_argument('-p', '--path',
                    type=str,
                    required=False,
                    default='./',
                    help='temp directory')

parser.add_argument('-a', '--all',
                    type=bool,
                    required=False,
                    default=False,
                    help='if want commit and restart all container set True')


class Image:
    def __init__(self):
        self.repository = ""
        self.tag = ""
        self.image_id = ""

    def save(self, path):
        print self
        dockerarg = ["docker", "save", "-o", path + self.repository + "_" + self.tag + "_" + self.image_id + ".dockerimg", self.image_id]
        print "img_save", str.join(" ", dockerarg)
        stat = subprocess.check_output(dockerarg)

    def load(self, path, filename):
        dockerarg = ["docker", "load", "-i", path + filename]
        print "img_load", str.join(" ", dockerarg)
        stat = subprocess.check_output(dockerarg)
        dockerarg = ["docker", "tag", self.image_id, self.repository.replace("=", "/") + ":" + self.tag]
        print "img_tag", str.join(" ", dockerarg)
        stat = subprocess.check_output(dockerarg)
        print "img_resutl", stat

    @staticmethod
    def build_image_by_file(filename):
        tmp_arr = filename.split("_")
        img = Image()
        img.repository = tmp_arr[0].replace('|', '/')
        img.tag = tmp_arr[1]
        img.image_id = tmp_arr[2].split(".")[0]
        return img

    @staticmethod
    def build_image_by_info(infostr):
        tmp_arr = infostr.split("   ")
        tapp = []
        for column in tmp_arr:
            column_str = column.strip()
            if len(column_str) > 0:
                tapp.append(column_str)
        if len(tapp) > 0:
            img = Image()
            if tapp[0] == "<none>":
                img.repository = "none"
            else:
                img.repository = tapp[0].replace('/', '|').replace('.', '@')
            img.tag = tapp[1]
            if img.tag == "<none>":
                img.tag = "none"
            img.image_id = tapp[2]
            return img
        return None


class Container:
    def __init__(self):
        self.container_id = ""
        self.image = ""
        self.names = ""
        self.ports = ""
        self.command = ""

    @staticmethod
    def trans_port_map(ports):
        portmaparr = []
        portsstr = ""
        if "->" in ports:
            portmapstrs = ports.split(",")
            for portmapstr in portmapstrs:
                if "->" not in portmapstr:
                    continue
                tarr = portmapstr.split("->")
                hostportstr = tarr[0]
                clientportstr = tarr[1]
                # print hostportstr,clientportstr
                if "-" in hostportstr:
                    htsplit = hostportstr.split("-")
                    hostportstart = htsplit[0].split(":")[-1]
                    hostportend = htsplit[-1]
                    # print clientportstr,hostportend
                    ctsplit = clientportstr.split("-")
                    clientportstart = ctsplit[0]
                    clientportend = ctsplit[-1].split("/")[0]
                    hostportint = int(hostportstart)
                    clientportint = int(clientportstart)
                    for i in range(int(hostportend) - int(hostportstart) + 1):
                        # print hostportint+i,clientportint+i
                        portmaparr.append(str(hostportint + i) + ":" + str(clientportint + i))
                else:
                    hostport = hostportstr.split(":")[-1]
                    clientport = clientportstr.split("/")[0]
                    portmaparr.append(hostport + ":" + clientport)
        return portmaparr

    def export(self, path):
        dockerarg = ["docker", "export", "-o",
                     path + self.names + "_" + self.image + "_" + self.container_id + "_" + str.join("+", Container.trans_port_map(self.ports)) + "_" + self.command + ".dockercontainer",
                     self.container_id]
        print self
        print "container_export", str.join(" ", dockerarg)
        stat = subprocess.check_output(dockerarg)

    def commit(self, path):
        dockerarg = ["touch", path + self.names + "_" + self.image.replace('/', '|') + "_" + self.container_id + "_" + str.join("+", Container.trans_port_map(self.ports)) + "_" + self.command + ".dockercommit"]
        print "container_touch", str.join(" ", dockerarg)
        stat = subprocess.check_output(dockerarg)
        dockerarg = ["docker", "commit", self.container_id, "c/" + self.image]
        print "container_commit", str.join(" ", dockerarg)
        stat = subprocess.check_output(dockerarg)

    def restart(self, path, filename):
        print "sefl.image", self.image
        # if self.image[0:1]!="c=":
        #     return
        dockerarg = ["docker", "run", "--name", self.names, "-d"]
        portarr = self.ports.split("+")
        # "6379:6379+6381:6381+6385:6385"
        for portmapstr in portarr:
            if len(portmapstr) > 0:
                dockerarg.extend(["-p", portmapstr])
        dockerarg.append("c/" + self.image)
        print "container_restat", str.join(" ", dockerarg)
        stat = subprocess.check_output(dockerarg)
        print "container_restat", stat

    def c_import(self, path, filename):
        def get_new_img_id(stat):
            return stat.strip().split(":")[-1]

        dockerarg = ["docker", "import", path + filename]
        print "container_import", str.join(" ", dockerarg)
        stat = subprocess.check_output(dockerarg)
        image_id = get_new_img_id(stat)
        dockerarg = ["docker", "tag", image_id, "c=" + self.image]
        print "container_tag", str.join(" ", dockerarg)
        stat = subprocess.check_output(dockerarg)
        print "container_tag", stat
        # dockerarg=["docker", "run", "--name", "mysql","-d","c="+self.image]
        dockerarg = ["docker", "run", "--name", self.names, "-d"]
        portarr = self.ports.split("+")
        # "6379:6379+6381:6381+6385:6385"
        for portmapstr in portarr:
            dockerarg.extend(["-p", portmapstr])
        dockerarg.extend(["-d", "c=" + self.image])
        dockerarg.append(self.command)
        print "container_run", str.join(" ", dockerarg)
        stat = subprocess.check_output(dockerarg)
        print "container_run", stat

    @staticmethod
    def build_container_by_file(filename):
        tmp_arr = filename.split("_")
        print tmp_arr
        container = Container()
        container.names = tmp_arr[0]
        container.image = tmp_arr[1].replace('|', '/')
        container.container_id = tmp_arr[2]
        container.ports = tmp_arr[3]
        # docker-entrypoint#sh
        container.command = tmp_arr[4].split(".")[0]
        container.command = container.command.replace("/", "^").replace("#", ".")
        # print "container.command",container.command
        return container

    @staticmethod
    def build_container_by_info(infostr):
        tmp_arr = infostr.split("  ")
        tapp = []
        for column in tmp_arr:
            column_str = column.strip()
            if len(column_str) > 0:
                tapp.append(column_str)
        if len(tapp) > 0:
            container = Container()
            container.container_id = tapp[0]
            container.image = tapp[1]
            container.command = tapp[2]
            if "docker-entrypoint" in container.command:
                container.command = "docker-entrypoint.sh"
            container.command = container.command.replace("/", "^").replace('"', '').replace('.', '#')
            container.ports = tapp[5]
            container.names = tapp[6]
            return container
        return None


def save_images(args):
    # backup_path = os.path.join(os.path.expanduser("~"), 'images')
    # if args.path is not None:
    backup_path = args.path
    stat = subprocess.check_output(["docker", "images"])
    statarr = stat.split("\n")
    statarr = statarr[1:]
    for dinfo in statarr:
        img = Image.build_image_by_info(dinfo)
        if not img:
            continue
        img.save(backup_path)
        break


def load_images(args):
    # backup_path = os.path.join(os.path.expanduser("~"), 'images')
    # backup_path = os.path.join(os.path.expanduser("~"))
    # if args.path is not None:
    backup_path = args.path
    print backup_path
    tmp_files = os.listdir(backup_path)
    try:
        for filepath in tmp_files:
            if re.findall('.*\.dockerimg$', filepath):
                print "image_file", filepath
                img = Image.build_image_by_file(filepath)
                print img
                img.load(backup_path, filepath)
    except Exception, ex:
        print ex
        print "current directory has no docker image file"


def exporter_containers(args):
    backup_path = args.path
    stat = subprocess.check_output(["docker", "ps"])
    statarr = stat.split("\n")
    statarr = statarr[1:]
    for dinfo in statarr:
        container = Container.build_container_by_info(dinfo)
        if not container:
            continue
        container.export(backup_path)
        # break


def commit_containers(args):
    backup_path = args.path
    stat = subprocess.check_output(["docker", "ps"])
    statarr = stat.split("\n")
    statarr = statarr[1:]
    for dinfo in statarr:
        container = Container.build_container_by_info(dinfo)
        if not container:
            continue
        container.commit(backup_path)
        # break


def importer_containers(args):
    backup_path = args.path
    # print backup_path
    tmp_files = os.listdir(backup_path)
    try:
        for filepath in tmp_files:
            if re.findall('.*\.dockercontainer$', filepath):
                print "container_file", filepath
                container = Container.build_container_by_file(filepath)
                print "names", container.names, "image", container.image

                # print container
                container.c_import(backup_path, filepath)
    except Exception, ex:
        print ex
        print "current directory has no docker image file"


def restart_containers(args):
    backup_path = args.path
    # print backup_path
    tmp_files = os.listdir(backup_path)
    try:
        for filepath in tmp_files:
            if re.findall('.*\.dockercommit$', filepath):
                print "container_file", filepath
                container = Container.build_container_by_file(filepath)
                # print "names",container.names,"image",container.image
                # print container
                container.restart(backup_path, filepath)
    except Exception, ex:
        print ex
        print "current directory has no docker image file"


def save(args):
    # 1 commit container
    commit_containers(args)
    # 2 save images
    save_images(args)


def load(args):
    # 1 load images
    load_images(args)
    # 2 restart container
    restart_containers(args)


if __name__ == '__main__':
    args = parser.parse_args()
    # print args
    task = args.task
    print task
    if task == 'save':
        save(args)
    else:
        load(args)
