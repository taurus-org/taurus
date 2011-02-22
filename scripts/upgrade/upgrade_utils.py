import sys, os, imp
import PyTango

class Upgrade:
    
    def upgrade(self, db, serv, old, new):
        raise RuntimeError("Invalid Upgrade class. Must define a upgrade method")
    
    @classmethod
    def fromTo(cls):
        raise RuntimeError("Invalid Upgrade class. Must define a fromTo method")

    @classmethod
    def supports(cls, old, new):
        raise RuntimeError("Invalid Upgrade class. Must define a supports method")
    
    @classmethod
    def supports_old(cls, old):
        raise RuntimeError("Invalid Upgrade class. Must define a supports_old method")

    @classmethod
    def supports_new(cls, new):
        raise RuntimeError("Invalid Upgrade class. Must define a supports_new method")

def print_list(l):
    for i in l: print i

def get_db(host = None, port = None):
    if host is None or port is None:
        return PyTango.Database()
    return PyTango.Database(host, port)

def get_server_list(type = "Pool", host = None, port = None, db = None):
    type += '/'
    db = db or get_db(host, port)
    return [ s[s.index('/')+1:] for s in db.get_server_list() if s.startswith(type) ]

def print_server_list():
    for s in get_server_list():
        print s

def get_pool_device_from_server(serv, host = None, port = None, db = None):
    db = db or get_db(host, port)
    return db.get_device_name("Pool/%s" % serv, "Pool")[0]

def get_pool_server_version(serv, host = None, port = None, db = None):
    db = db or get_db(host, port)
    pool_dev_name = get_pool_device_from_server(serv, db=db)
    if not len(db.get_device_property_list(pool_dev_name,"Version")):
        # if not in database it means it is version 0.1.0
        return "0.1.0"
    else:
        return db.get_device_property(pool_dev_name, ["Version"])["Version"][0]

def to_version_nb(v_str):
    m,n,r = v_str.split('.')
    return int(m)*10000 + int(n)*100 + int(r)

def strip_old_versions(v_list, thresold):
    thresold = to_version_nb(thresold)
    return [ v for v in v_list if to_version_nb(v) > thresold ]

def get_suitable_upgrade(old_vers, new_vers):
    upgrades = get_supported_upgrades()
    for u_kcls in upgrades:
        if u_kcls.supports(old_vers, new_vers):
            return u_kcls
    return None

def get_supported_upgrades():
    upgrade_classes = []
    curr_dir = os.path.abspath(os.path.dirname(__file__))
    for mod_name in os.listdir(curr_dir):
        if not mod_name.endswith(".py"): continue
        mod_name = mod_name[:mod_name.rindex(".py")]
        if mod_name == __name__: continue
        if mod_name.startswith("upgrade_"): continue
        m = imp.load_module(mod_name, *imp.find_module(mod_name))
        for s in m.__dict__.values():
            if type(s) == type(Upgrade):
                if s == Upgrade: continue
                if issubclass(s, Upgrade):
                    upgrade_classes.append(s)
                    
    return upgrade_classes

def get_possible_upgrades(serv, host = None, port = None, db = None):
    curr_vers = get_pool_server_version(serv, host = host, port = port, db = db)
    upgrades = get_supported_upgrades()
    possible_upgrades = []
    for u_kcls in upgrades:
        if u_kcls.supports_old(curr_vers):
            possible_upgrades.append(u_kcls.fromTo()[1])
    return possible_upgrades
