
import argparse
import json
import subprocess
import os

import pandas as pd
#from . import xyceSimulator

class xyceSimulator:

    def __init__(self):
        pass

    def __init__(self, configFile):
        
        xyce_config = ''
        with open(configFile, 'r') as f:
            xyce_config = json.load(f)

        self.xyce_command = xyce_config["xyce_command"]

        self.xyce_libraries = []
        self.loadPlugins(xyce_config["library_files"], fromFile=False)

    def loadPlugins(self, config, fromFile=True):
        xyce_libs = None
        if fromFile:
            with open(config, 'r') as f:
                xyce_libs = json.load(f)["library_files"]
        else:
            xyce_libs = config
            
        self.xyce_libraries += xyce_libs

        pass

    def getPlugins(self):
        return self.xyce_libraries
    
    def genPluginStr(self):
        return ','.join(self.xyce_libraries) 

    def set_xyce_command(self, command):
        self.xyce_command = command

    def _hide_netlist_files(spice_dir):
        for f in os.listdir(spice_dir):
            if os.path.isfile(os.path.join(spice_dir, f)) and f[-4:]==".cir":
                os.rename(spice_dir+'/cir_files/'+f)


    def _move_results_files(spice_dir):
        for f in os.listdir(spice_dir):
            if os.path.isfile(os.path.join(spice_dir, f)) and f[-4:]==".prn":
                os.rename(spice_dir+'/results/'+f)

    def run(self, files):
        
        # generate library string
        xyce_lib_str = self.genPluginStr() 

        xyce_run = self.xyce_command+' -plugin '+xyce_lib_str+' '

        for f in files:
            xyce_run_file = (xyce_run+f)
            print('---------------------------------')
            print("run Xyce: " + xyce_run_file)
            xyce_run_file = xyce_run_file.replace('  ', ' ').split(' ')
            subprocess.run(xyce_run_file)

        # TODO test
        self._move_results_files(os.path.dirname(files[0]))

def parseFileList(ilist, wd):
    print("reading file: "+str(wd+ilist))

    listDB = pd.read_csv(wd+ilist)

    f_list = []

    for f in listDB.iterrows():
        f_name = f[1]["OutputFile"]
        f_list.append(f_name)

    return f_list

def setConfig(config):
    if args.config is None:
        config_file = "xyceConfig"
    else:
        config_file = args.config

    return config_file

def parseFiles(ifile, ilist, wd=None):
    if wd == None:
        wd = ''
    else:
        wd += '/'

    if ilist is not None and \
        ifile is not None:
        raise Exception("Pass either file or argument")
    elif ilist is not None:
        infiles = parseFileList(ilist, wd)
    elif ifile is not None:
        infiles = ifile.split(' ')
    else:
        raise Exception("No files passed")

    infiles = [wd+f for f in infiles]

    return infiles

if __name__ == "__main__":
    
    import os
    configDefault     = "/mfda_simulation/xyce_docker_server/xyceConfig"

    parser = argparse.ArgumentParser()

    parser.add_argument('--file', metavar="<files>", dest='ifile', type=str,
                        help="list of files", nargs='*')
    parser.add_argument('--list', metavar="<list_file>", dest='ilist', type=str,
                        help="list of files", nargs=1)
    parser.add_argument('--workdir', metavar='<working_dir>', dest='wd', type=str,
                        help="simulation working directory", default=None)

    parser.add_argument('--config', metavar="<config>", dest='config', type=str,
                        help="simulation configuration", nargs=1, default=configDefault)
    
    parser.add_argument('--debug', dest='debug', default=None)
    
    args = parser.parse_args()

    config_file = setConfig(args.config)
    sim = xyceSimulator(config_file)

    infiles = parseFiles(args.ifile, args.ilist[0], args.wd)

    if(args.debug == None):
        sim.run(infiles)
