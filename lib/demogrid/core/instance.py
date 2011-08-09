import shutil
import os.path
from cPickle import load
import random
from demogrid.common import DemoGridException
from demogrid.core.config import DemoGridConfig
from demogrid.core.topology import Topology
from demogrid.common.certs import CertificateGenerator
from demogrid.common.config import ConfigException

class InstanceException(Exception):
    pass

class InstanceStore(object):
    def __init__(self, instances_dir):
        self.instances_dir = instances_dir
        
    def create_new_instance(self, topology_json, config_txt):
        created = False
        while not created:
            inst_id = "xgi-" + hex(random.randint(1,2**31-1))[2:].rjust(8,"0")
            inst_dir = "%s/%s" % (self.instances_dir, inst_id)
            if not os.path.exists(inst_dir):
                os.makedirs(inst_dir)
                created = True
                
        configf = open("%s/demogrid.conf" % inst_dir, "w")
        configf.write(config_txt)
        configf.close()

        # We don't do anything with it. Just use it to raise an exception
        # if there is anything wrong with the configuration file
        DemoGridConfig("%s/demogrid.conf" % inst_dir)

        topology = Topology.from_json_string(topology_json)
        topology.set_property("id", inst_id)
        topology.set_property("state", Topology.STATE_NEW)
        topology.save("%s/topology.json" % inst_dir)
                                        
        inst = Instance(inst_id, inst_dir)
        
        return inst
    
    def get_instance(self, inst_id):
        inst_dir = "%s/%s" % (self.instances_dir, inst_id)

        if not os.path.exists(inst_dir):
            raise InstanceException("Instance %s does not exist" % inst_id)
        return Instance(inst_id, inst_dir)

    def get_instances(self):
        return [Instance(inst_id, "%s/%s" % (self.instances_dir, inst_id)) for inst_id in self.__get_instance_ids()]
    
    def __get_instance_ids(self):
        inst_ids = [i for i in os.listdir(self.instances_dir)]
        return inst_ids

class Instance(object):

    # Relative to $DEMOGRID_LOCATION
    CHEF_DIR = "/chef/"  
    
    # Relative to generated dir
    CERTS_DIR = "/certs"
    CHEF_FILES_DIR = "/chef/cookbooks/demogrid/files/default/"  
    CHEF_ATTR_DIR = "/chef/cookbooks/demogrid/attributes/"

    def __init__(self, inst_id, instance_dir):
        self.instance_dir = instance_dir
        self.id = inst_id
        self.config = DemoGridConfig("%s/demogrid.conf" % instance_dir)
        self.topology = self.__load_topology()
        
    def __load_topology(self):
        topology_file = "%s/topology.json" % self.instance_dir
        f = open (topology_file, "r")
        json_string = f.read()
        topology = Topology.from_json_string(json_string)
        topology._json_file = topology_file
        f.close()   
        return topology     

    def update_topology(self, topology_json):
        topology_file = "%s/topology.json" % self.instance_dir        
        new_topology = Topology.from_json_string(topology_json)
        new_topology._json_file = topology_file
        
        # TODO: Validate that update is allowed
        # TODO: Determine hosts to add/remove

        self.topology = new_topology
        self.topology.save()
        
        return (True, "Success", [], [])

    def gen_certificates(self, force_hosts = False, force_users = False, force_ca = False):
        certs_dir = self.instance_dir + self.CERTS_DIR
        if not os.path.exists(certs_dir):
            os.makedirs(certs_dir)  

        certg = CertificateGenerator()

        cert_files = []
        ca_cert_file = self.config.get("ca-cert")
        ca_cert_key = self.config.get("ca-key")
        
        if ca_cert_file != None:
            ca_cert, ca_key = certg.load_certificate(ca_cert_file, ca_cert_key)
        else:
            ca_cert, ca_key = certg.gen_selfsigned_ca_cert("DemoGrid CA")
        
        certg.set_ca(ca_cert, ca_key)

        h = "%x" % ca_cert.subject_name_hash()

        hash_file = open(certs_dir + "/ca_cert.hash", "w")
        hash_file.write(h)
        hash_file.close()   

        ca_cert_file = "%s/%s.0" % (certs_dir, h)
        ca_key_file = certs_dir + "/ca_key.pem"
        cert_files.append(ca_cert_file)
        cert_files.append(ca_key_file)
        certg.save_certificate(cert = ca_cert,
                              key = ca_key,
                              cert_file = ca_cert_file,
                              key_file = ca_key_file, 
                              force = force_ca)

        users = [u for u in self.topology.get_users() if u.certificate=="generated"]
        for user in users:        
            cert, key = certg.gen_user_cert(cn = user.id) 
            
            cert_file = "%s/%s_cert.pem" % (certs_dir, user.id)
            key_file = "%s/%s_key.pem" % (certs_dir, user.id)
            cert_files.append(cert_file)
            cert_files.append(key_file)    
            certg.save_certificate(cert = cert,
                                    key = key,
                                    cert_file = cert_file,
                                    key_file = key_file, 
                                    force = force_users)
        
        nodes = self.topology.get_nodes()
        for n in nodes:
            cert, key = certg.gen_host_cert(hostname = n.hostname) 
            
            filename = n.id
            
            cert_file = "%s/%s_cert.pem" % (certs_dir, filename)
            key_file = "%s/%s_key.pem" % (certs_dir, filename)
            cert_files.append(cert_file)
            cert_files.append(key_file)          
            certg.save_certificate(cert = cert,
                                   key = key,
                                   cert_file = cert_file,
                                   key_file = key_file, 
                                   force = force_hosts)        

        return cert_files  


                 
        


        
