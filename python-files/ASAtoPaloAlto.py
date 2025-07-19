import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ipaddress
import json
import xml.etree.ElementTree as ET
import os
import re

def mask_to_prefix(mask):
    """Convert subnet mask to CIDR prefix length."""
    try:
        return sum(bin(int(octet)).count('1') for octet in mask.split('.'))
    except ValueError:
        return 32  # Default to /32 if invalid

class ASAToPaloConverter:
    def __init__(self, config_file):
        self.config_file = config_file
        with open(config_file, 'r') as f:
            self.lines = [line.strip() for line in f.readlines() if line.strip()]
        self.address_objects = {}
        self.address_groups = {}
        self.service_objects = {}
        self.service_groups = {}
        self.acls = {}
        self.access_groups = {}
        self.snmp_settings = {'users': [], 'groups': [], 'hosts': []}
        self.routes = {}
        self.hostname = ''
        self.banner_exec = ''
        self.banner_login = ''
        self.interfaces = {}
        self.parse_config()

    def parse_config(self):
        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            
            if line.startswith('object network'):
                name = line.split()[-1]
                self.address_objects[name] = {'type': 'ip-netmask', 'value': '', 'description': ''}
                i += 1
                while i < len(self.lines) and not self.lines[i].startswith('object ') and not self.lines[i].startswith('object-group ') and not self.lines[i].startswith('!'):
                    child = self.lines[i]
                    if child.startswith('host'):
                        ip = child.split()[-1]
                        self.address_objects[name]['value'] = f"{ip}/32"
                    elif child.startswith('subnet'):
                        net, mask = child.split()[-2:]
                        prefix = mask_to_prefix(mask)
                        self.address_objects[name]['value'] = f"{net}/{prefix}"
                    elif child.startswith('description'):
                        self.address_objects[name]['description'] = ' '.join(child.split()[1:])
                    i += 1
                continue
            
            elif line.startswith('object-group network'):
                name = line.split()[-1]
                self.address_groups[name] = {'members': [], 'description': ''}
                i += 1
                while i < len(self.lines) and not self.lines[i].startswith('object ') and not self.lines[i].startswith('object-group ') and not self.lines[i].startswith('!'):
                    child = self.lines[i]
                    if child.startswith('network-object object'):
                        subname = child.split()[-1]
                        self.address_groups[name]['members'].append(subname)
                    elif child.startswith('network-object host'):
                        ip = child.split()[-1]
                        temp_name = f"TEMP_HOST_{ip.replace('.', '-')}"
                        self.address_objects[temp_name] = {'type': 'ip-netmask', 'value': f"{ip}/32", 'description': ''}
                        self.address_groups[name]['members'].append(temp_name)
                    elif child.startswith('network-object') and len(child.split()) == 3:
                        net, mask = child.split()[-2:]
                        prefix = mask_to_prefix(mask)
                        temp_name = f"TEMP_NET_{net.replace('.', '-')}_{prefix}"
                        self.address_objects[temp_name] = {'type': 'ip-netmask', 'value': f"{net}/{prefix}", 'description': ''}
                        self.address_groups[name]['members'].append(temp_name)
                    elif child.startswith('description'):
                        self.address_groups[name]['description'] = ' '.join(child.split()[1:])
                    i += 1
                continue
            
            elif line.startswith('object service'):
                name = line.split()[-1]
                self.service_objects[name] = {'protocol': '', 'port': '', 'description': ''}
                i += 1
                while i < len(self.lines) and not self.lines[i].startswith('object ') and not self.lines[i].startswith('object-group ') and not self.lines[i].startswith('!'):
                    child = self.lines[i]
                    if child.startswith('service'):
                        parts = child.split()[1:]
                        self.service_objects[name]['protocol'] = parts[0]
                        if len(parts) > 1 and parts[1] == 'eq':
                            self.service_objects[name]['port'] = parts[2]
                    elif child.startswith('description'):
                        self.service_objects[name]['description'] = ' '.join(child.split()[1:])
                    i += 1
                continue
            
            elif line.startswith('object-group service'):
                name = line.split()[-1]
                self.service_groups[name] = {'members': [], 'description': ''}
                i += 1
                while i < len(self.lines) and not self.lines[i].startswith('object ') and not self.lines[i].startswith('object-group ') and not self.lines[i].startswith('!'):
                    child = self.lines[i]
                    if child.startswith('service-object object'):
                        subname = child.split()[-1]
                        self.service_groups[name]['members'].append(subname)
                    elif child.startswith('service-object'):
                        parts = child.split()[1:]
                        proto = parts[0]
                        port = ''
                        if len(parts) > 1 and parts[1] == 'eq':
                            port = parts[2]
                        temp_name = f"TEMP_SVC_{proto}_{port}" if port else f"TEMP_SVC_{proto}"
                        self.service_objects[temp_name] = {'protocol': proto, 'port': port, 'description': ''}
                        self.service_groups[name]['members'].append(temp_name)
                    elif child.startswith('port-object eq'):
                        port = child.split()[-1]
                        temp_name = f"TEMP_PORT_{port}"
                        self.service_objects[temp_name] = {'protocol': 'tcp', 'port': port, 'description': ''}
                        self.service_groups[name]['members'].append(temp_name)
                    elif child.startswith('description'):
                        self.service_groups[name]['description'] = ' '.join(child.split()[1:])
                    i += 1
                continue
            
            elif line.startswith('access-list') and 'extended' in line:
                parts = line.split()
                acl_name = parts[1]
                if acl_name not in self.acls:
                    self.acls[acl_name] = []
                action = parts[3]
                proto = parts[4]
                
                # Parse source
                src_idx = 5
                src_advance = 1
                src = 'any'
                if len(parts) > src_idx:
                    if parts[src_idx] == 'object-group':
                        src = parts[src_idx + 1]
                        src_advance = 2
                    elif parts[src_idx] == 'object':
                        src = parts[src_idx + 1]
                        src_advance = 2
                    elif parts[src_idx] == 'any':
                        src = 'any'
                        src_advance = 1
                    elif parts[src_idx] == 'host':
                        ip = parts[src_idx + 1]
                        temp_name = f"TEMP_HOST_{ip.replace('.', '-')}"
                        self.address_objects[temp_name] = {'type': 'ip-netmask', 'value': f"{ip}/32", 'description': ''}
                        src = temp_name
                        src_advance = 2
                    elif re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', parts[src_idx]) and len(parts) > src_idx + 1 and re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', parts[src_idx + 1]):
                        net = parts[src_idx]
                        mask = parts[src_idx + 1]
                        prefix = mask_to_prefix(mask)
                        temp_name = f"TEMP_NET_{net.replace('.', '-')}_{prefix}"
                        self.address_objects[temp_name] = {'type': 'ip-netmask', 'value': f"{net}/{prefix}", 'description': ''}
                        src = temp_name
                        src_advance = 2
                    else:
                        src = parts[src_idx]
                        src_advance = 1
                
                # Parse destination
                dst_idx = src_idx + src_advance
                dst_advance = 1
                dst = 'any'
                if len(parts) > dst_idx:
                    if parts[dst_idx] == 'object-group':
                        dst = parts[dst_idx + 1]
                        dst_advance = 2
                    elif parts[dst_idx] == 'object':
                        dst = parts[dst_idx + 1]
                        dst_advance = 2
                    elif parts[dst_idx] == 'any':
                        dst = 'any'
                        dst_advance = 1
                    elif parts[dst_idx] == 'host':
                        ip = parts[dst_idx + 1]
                        temp_name = f"TEMP_HOST_{ip.replace('.', '-')}"
                        self.address_objects[temp_name] = {'type': 'ip-netmask', 'value': f"{ip}/32", 'description': ''}
                        dst = temp_name
                        dst_advance = 2
                    elif re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', parts[dst_idx]) and len(parts) > dst_idx + 1 and re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', parts[dst_idx + 1]):
                        net = parts[dst_idx]
                        mask = parts[dst_idx + 1]
                        prefix = mask_to_prefix(mask)
                        temp_name = f"TEMP_NET_{net.replace('.', '-')}_{prefix}"
                        self.address_objects[temp_name] = {'type': 'ip-netmask', 'value': f"{net}/{prefix}", 'description': ''}
                        dst = temp_name
                        dst_advance = 2
                    else:
                        dst = parts[dst_idx]
                        dst_advance = 1
                
                # Parse service
                svc_idx = dst_idx + dst_advance
                svc = 'any'
                if len(parts) > svc_idx:
                    if parts[svc_idx] == 'object-group':
                        svc = parts[svc_idx + 1]
                    elif parts[svc_idx] == 'object':
                        svc = parts[svc_idx + 1]
                    elif parts[svc_idx] == 'eq':
                        port = parts[svc_idx + 1]
                        temp_svc = f"TEMP_{proto.upper()}_{port}"
                        self.service_objects[temp_svc] = {'protocol': proto, 'port': port, 'description': ''}
                        svc = temp_svc
                    elif parts[svc_idx] in ['tcp', 'udp', 'icmp'] or re.match(r'\d+', parts[svc_idx]):
                        svc = parts[svc_idx]
                    else:
                        svc = parts[svc_idx]
                
                self.acls[acl_name].append({'action': action, 'proto': proto, 'src': src, 'dst': dst, 'svc': svc})
            
            elif line.startswith('access-group'):
                parts = line.split()
                acl_name = parts[1]
                direction = parts[3]
                interface = parts[5]
                if acl_name not in self.access_groups:
                    self.access_groups[acl_name] = []
                self.access_groups[acl_name].append({'interface': interface, 'direction': direction})
            
            elif line.startswith('snmp-server'):
                parts = line.split()
                command = parts[1]
                if command == 'group':
                    group = {'name': parts[2], 'version': parts[3]}
                    if len(parts) > 4:
                        group['context'] = parts[4]
                    self.snmp_settings['groups'].append(group)
                elif command == 'user':
                    user = {'name': parts[2], 'group': parts[3], 'version': parts[4]}
                    j = 5
                    while j < len(parts):
                        if parts[j] == 'auth':
                            user['auth_type'] = parts[j+1]
                            user['auth_pass'] = parts[j+2]
                            j += 3
                        elif parts[j] == 'priv':
                            user['priv_type'] = parts[j+1]
                            user['priv_pass'] = parts[j+2]
                            j += 3
                        else:
                            j += 1
                    self.snmp_settings['users'].append(user)
                elif command == 'host':
                    host = {'interface': parts[2], 'address': parts[3]}
                    j = 4
                    while j < len(parts):
                        if parts[j] == 'version':
                            host['version'] = parts[j+1]
                            j += 2
                        elif parts[j] == 'user':
                            host['user'] = parts[j+1]
                            j += 2
                        elif parts[j] == 'community':
                            host['community'] = parts[j+1]
                            j += 2
                        elif parts[j] in ['inform', 'trap', 'poll']:
                            host['type'] = parts[j]
                            j += 1
                        else:
                            j += 1
                    self.snmp_settings['hosts'].append(host)
            
            elif line.startswith('route'):
                parts = line.split()
                if_name = parts[1]
                net = parts[2]
                mask = parts[3]
                gw = parts[4]
                prefix = mask_to_prefix(mask)
                key = f"{net}_{prefix}"
                self.routes[key] = {'gw': gw, 'destination': f"{net}/{prefix}", 'interface': if_name}
            
            elif line.startswith('hostname'):
                self.hostname = line.split()[1]
            
            elif line.startswith('banner exec'):
                self.banner_exec += ' '.join(line.split()[2:]) + '\n'
            
            elif line.startswith('banner login'):
                self.banner_login += ' '.join(line.split()[2:]) + '\n'
            
            elif line.startswith('interface'):
                name = line.split()[-1]
                self.interfaces[name] = {'nameif': '', 'ip': '', 'mask': '', 'security_level': ''}
                i += 1
                while i < len(self.lines) and not self.lines[i].startswith('interface') and not self.lines[i].startswith('!'):
                    child = self.lines[i]
                    if child.startswith('nameif'):
                        self.interfaces[name]['nameif'] = child.split()[1]
                    elif child.startswith('security-level'):
                        self.interfaces[name]['security_level'] = child.split()[1]
                    elif child.startswith('ip address'):
                        parts = child.split()
                        self.interfaces[name]['ip'] = parts[2]
                        self.interfaces[name]['mask'] = parts[3]
                    i += 1
                continue
            
            i += 1

    def generate_set_commands(self):
        commands = []

        # Hostname
        if self.hostname:
            commands.append(f"set deviceconfig system hostname {self.hostname}")

        # Banners
        motd = (self.banner_login + self.banner_exec).strip()
        if motd:
            commands.append(f"set deviceconfig system motd-and-banner \"{motd}\"")

        # Interfaces and Zones
        intf_map = {}
        count = 1
        for asa_intf in sorted(self.interfaces.keys()):
            palo_intf = f"ethernet1/{count}"
            intf_map[asa_intf] = palo_intf
            data = self.interfaces[asa_intf]
            if data['ip'] and data['mask']:
                prefix = mask_to_prefix(data['mask'])
                ip_cidr = f"{data['ip']}/{prefix}"
                commands.append(f"set network interface ethernet {palo_intf} layer3 ip {ip_cidr}")
            if data['nameif']:
                zone = data['nameif']
                commands.append(f"set zone {zone} network layer3 {palo_intf}")
            count += 1

        # Address objects
        for name, data in self.address_objects.items():
            if data['value']:
                cmd = f"set address {name} {data['type']} {data['value']}"
                if data.get('description'):
                    cmd += f" description \"{data['description']}\""
                commands.append(cmd)

        # Address groups
        for name, data in self.address_groups.items():
            if data['members']:
                members = ' '.join(data['members'])
                cmd = f"set address-group {name} static [ {members} ]"
                if data.get('description'):
                    cmd += f" description \"{data['description']}\""
                commands.append(cmd)

        # Service objects
        for name, data in self.service_objects.items():
            if data['protocol']:
                cmd = f"set service {name} protocol {data['protocol']}"
                if data['port']:
                    cmd += f" port {data['port']}"
                if data.get('description'):
                    cmd += f" description \"{data['description']}\""
                commands.append(cmd)

        # Service groups
        for name, data in self.service_groups.items():
            if data['members']:
                members = ' '.join(data['members'])
                cmd = f"set service-group {name} members [ {members} ]"
                if data.get('description'):
                    cmd += f" description \"{data['description']}\""
                commands.append(cmd)

        # Firewall policies/rules
        rule_id = 1
        for acl_name in self.access_groups:
            for ag in self.access_groups[acl_name]:
                interface = ag['interface']
                direction = ag['direction']
                if interface in self.interfaces and self.interfaces[interface]['nameif']:
                    zone = self.interfaces[interface]['nameif']
                else:
                    zone = 'unknown'
                if direction == 'in':
                    from_zone = zone
                    to_zone = 'any'
                else:
                    from_zone = 'any'
                    to_zone = zone
                for rule in self.acls.get(acl_name, []):
                    src = rule['src'] if rule['src'] != 'any' else 'any'
                    dst = rule['dst'] if rule['dst'] != 'any' else 'any'
                    svc = rule['svc'] if rule['svc'] != 'any' else 'any'
                    action = 'allow' if rule['action'] == 'permit' else 'deny'
                    cmd = f"set rulebase security rules RULE_{rule_id} from {from_zone} to {to_zone} source [ {src} ] destination [ {dst} ] service [ {svc} ] action {action}"
                    commands.append(cmd)
                    rule_id += 1

        # SNMP
        for user in self.snmp_settings['users']:
            if 'auth_pass' in user and 'priv_pass' in user:
                commands.append(f"set deviceconfig system snmp-setting version v3 users {user['name']} authentication {user.get('auth_type', 'sha')} password PLACEHOLDER privacy {user.get('priv_type', 'aes-128')} password PLACEHOLDER")
        for host in self.snmp_settings['hosts']:
            if 'version' in host and host['version'] == '3' and 'user' in host:
                commands.append(f"set deviceconfig system snmp-setting traps snmp v3 sink {host['address']} user {host['user']}")
            elif 'community' in host:
                commands.append(f"set deviceconfig system snmp-setting snmp v2c trap server default address {host['address']} community {host['community']}")

        # Routes
        for key, data in self.routes.items():
            name = f"ROUTE_{key.replace('/', '-')}"
            commands.append(f"set network virtual-router default routing-table ip static-route {name} destination {data['destination']} nexthop ip-address {data['gw']} interface {intf_map.get(data['interface'], data['interface'])}")

        return '\n'.join(commands)

    def generate_json(self):
        data = {
            'address_objects': self.address_objects,
            'address_groups': self.address_groups,
            'service_objects': self.service_objects,
            'service_groups': self.service_groups,
            'acls': self.acls,
            'snmp_settings': self.snmp_settings,
            'routes': self.routes,
            'hostname': self.hostname,
            'banner_exec': self.banner_exec,
            'banner_login': self.banner_login,
            'interfaces': self.interfaces
        }
        return json.dumps(data, indent=4)

    def generate_xml(self):
        root = ET.Element('config')
        devices = ET.SubElement(root, 'devices')
        device_entry = ET.SubElement(devices, 'entry', {'name': 'localhost.localdomain'})
        deviceconfig = ET.SubElement(device_entry, 'deviceconfig')
        system = ET.SubElement(deviceconfig, 'system')
        if self.hostname:
            hostname = ET.SubElement(system, 'hostname')
            hostname.text = self.hostname
        motd = (self.banner_login + self.banner_exec).strip()
        if motd:
            motd_banner = ET.SubElement(system, 'motd-and-banner')
            motd_banner.text = motd

        network = ET.SubElement(device_entry, 'network')
        interfaces = ET.SubElement(network, 'interface')
        ethernet = ET.SubElement(interfaces, 'ethernet')
        count = 1
        for asa_intf in sorted(self.interfaces.keys()):
            palo_intf = f"ethernet1/{count}"
            entry = ET.SubElement(ethernet, 'entry', {'name': palo_intf})
            layer3 = ET.SubElement(entry, 'layer3')
            ip = ET.SubElement(layer3, 'ip')
            data = self.interfaces[asa_intf]
            if data['ip'] and data['mask']:
                prefix = mask_to_prefix(data['mask'])
                ip_cidr = f"{data['ip']}/{prefix}"
                ip_entry = ET.SubElement(ip, 'entry', {'name': ip_cidr})
            count += 1

        vsys = ET.SubElement(device_entry, 'vsys')
        vsys_entry = ET.SubElement(vsys, 'entry', {'name': 'vsys1'})

        # Zones
        zones = ET.SubElement(vsys_entry, 'zone')
        count = 1
        for asa_intf in sorted(self.interfaces.keys()):
            data = self.interfaces[asa_intf]
            if data['nameif']:
                zone = data['nameif']
                entry = ET.SubElement(zones, 'entry', {'name': zone})
                network = ET.SubElement(entry, 'network')
                layer3 = ET.SubElement(network, 'layer3')
                member = ET.SubElement(layer3, 'member')
                member.text = f"ethernet1/{count}"
            count += 1

        # Address objects
        addresses = ET.SubElement(vsys_entry, 'address')
        for name, data in self.address_objects.items():
            if data['value']:
                entry = ET.SubElement(addresses, 'entry', {'name': name})
                ip_netmask = ET.SubElement(entry, 'ip-netmask')
                ip_netmask.text = data['value']
                if data.get('description'):
                    desc = ET.SubElement(entry, 'description')
                    desc.text = data['description']

        # Address groups
        address_groups = ET.SubElement(vsys_entry, 'address-group')
        for name, data in self.address_groups.items():
            if data['members']:
                entry = ET.SubElement(address_groups, 'entry', {'name': name})
                static = ET.SubElement(entry, 'static')
                for member in data['members']:
                    m = ET.SubElement(static, 'member')
                    m.text = member
                if data.get('description'):
                    desc = ET.SubElement(entry, 'description')
                    desc.text = data['description']

        # Service objects
        services = ET.SubElement(vsys_entry, 'service')
        for name, data in self.service_objects.items():
            if data['protocol']:
                entry = ET.SubElement(services, 'entry', {'name': name})
                protocol = ET.SubElement(entry, 'protocol')
                sub_prot = ET.SubElement(protocol, data['protocol'])
                if data['port']:
                    port = ET.SubElement(sub_prot, 'port')
                    port.text = data['port']
                if data.get('description'):
                    desc = ET.SubElement(entry, 'description')
                    desc.text = data['description']

        # Service groups
        service_groups = ET.SubElement(vsys_entry, 'service-group')
        for name, data in self.service_groups.items():
            if data['members']:
                entry = ET.SubElement(service_groups, 'entry', {'name': name})
                members = ET.SubElement(entry, 'members')
                for member in data['members']:
                    m = ET.SubElement(members, 'member')
                    m.text = member
                if data.get('description'):
                    desc = ET.SubElement(entry, 'description')
                    desc.text = data['description']

        # Firewall policies/rules
        rulebase = ET.SubElement(vsys_entry, 'rulebase')
        security = ET.SubElement(rulebase, 'security')
        rules = ET.SubElement(security, 'rules')
        rule_id = 1
        for acl_name, rule_list in self.acls.items():
            for rule in rule_list:
                entry = ET.SubElement(rules, 'entry', {'name': f"RULE_{rule_id}"})
                from_zone = ET.SubElement(entry, 'from')
                m = ET.SubElement(from_zone, 'member')
                m.text = 'trust'  # placeholder
                to_zone = ET.SubElement(entry, 'to')
                m = ET.SubElement(to_zone, 'member')
                m.text = 'untrust'  # placeholder
                source = ET.SubElement(entry, 'source')
                m = ET.SubElement(source, 'member')
                m.text = rule['src'] if rule['src'] != 'any' else 'any'
                destination = ET.SubElement(entry, 'destination')
                m = ET.SubElement(destination, 'member')
                m.text = rule['dst'] if rule['dst'] != 'any' else 'any'
                service = ET.SubElement(entry, 'service')
                m = ET.SubElement(service, 'member')
                m.text = rule['svc'] if rule['svc'] != 'any' else 'any'
                action = ET.SubElement(entry, 'action')
                action.text = 'allow' if rule['action'] == 'permit' else 'deny'
                rule_id += 1

        # SNMP
        snmp_setting = ET.SubElement(system, 'snmp-setting')
        version = ET.SubElement(snmp_setting, 'version')
        for user in self.snmp_settings['users']:
            v3 = ET.SubElement(version, 'v3')
            users = ET.SubElement(v3, 'users')
            user_entry = ET.SubElement(users, 'entry', {'name': user['name']})
            auth = ET.SubElement(user_entry, 'authentication')
            auth_type = ET.SubElement(auth, user.get('auth_type', 'sha'))
            auth_pass = ET.SubElement(auth_type, 'password')
            auth_pass.text = 'PLACEHOLDER'
            priv = ET.SubElement(user_entry, 'privacy')
            priv_type = ET.SubElement(priv, user.get('priv_type', 'aes-128'))
            priv_pass = ET.SubElement(priv_type, 'password')
            priv_pass.text = 'PLACEHOLDER'
        traps = ET.SubElement(snmp_setting, 'traps')
        for host in self.snmp_settings['hosts']:
            if 'version' in host and host['version'] == '3':
                v3_trap = ET.SubElement(traps, 'v3')
                entry = ET.SubElement(v3_trap, 'entry', {'name': 'default'})
                ip_address = ET.SubElement(entry, 'ip-address')
                ip_address.text = host['address']
                user = ET.SubElement(entry, 'user')
                user.text = host.get('user', '')
            elif 'community' in host:
                v2c = ET.SubElement(version, 'v2c')
                community = ET.SubElement(v2c, 'community')
                community.text = host['community']

        # Routes
        virtual_router = ET.SubElement(network, 'virtual-router')
        vr_entry = ET.SubElement(virtual_router, 'entry', {'name': 'default'})
        routing_table = ET.SubElement(vr_entry, 'routing-table')
        ip = ET.SubElement(routing_table, 'ip')
        static_route = ET.SubElement(ip, 'static-route')
        for key, data in self.routes.items():
            name = f"ROUTE_{key.replace('/', '-')}"
            entry = ET.SubElement(static_route, 'entry', {'name': name})
            destination = ET.SubElement(entry, 'destination')
            destination.text = data['destination']
            nexthop = ET.SubElement(entry, 'nexthop')
            ip_address = ET.SubElement(nexthop, 'ip-address')
            ip_address.text = data['gw']
            interface = ET.SubElement(entry, 'interface')
            interface.text = data['interface']

        return ET.tostring(root, encoding='unicode', method='xml')

# GUI
root = tk.Tk()
root.title("ASA to Palo Alto Converter")
root.geometry("800x600")

config_file = None
converter = None
output_format = tk.StringVar(value="set")

def upload_file():
    global config_file, converter
    config_file = filedialog.askopenfilename(title="Select ASA Config File", filetypes=(("Text files", "*.txt"), ("Config files", "*.cfg"), ("All files", "*.*")))
    if config_file:
        try:
            converter = ASAToPaloConverter(config_file)
            messagebox.showinfo("Success", "Config file loaded and parsed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse config: {str(e)}")

def convert_and_display():
    if not converter:
        messagebox.showerror("Error", "Please upload a config file first!")
        return
    fmt = output_format.get()
    try:
        if fmt == "set":
            output = converter.generate_set_commands()
        elif fmt == "json":
            output = converter.generate_json()
        elif fmt == "xml":
            output = converter.generate_xml()
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, output)
    except Exception as e:
        messagebox.showerror("Error", f"Conversion failed: {str(e)}")

def save_output():
    if not text_area.get(1.0, tk.END).strip():
        messagebox.showerror("Error", "No output to save!")
        return
    ext = ".txt" if output_format.get() == "set" else f".{output_format.get()}"
    file = filedialog.asksaveasfilename(defaultextension=ext, filetypes=(("Text files", "*.txt"), ("JSON files", "*.json"), ("XML files", "*.xml"), ("All files", "*.*")))
    if file:
        with open(file, 'w') as f:
            f.write(text_area.get(1.0, tk.END))
        messagebox.showinfo("Success", "Output saved successfully!")

# Widgets
tk.Label(root, text="ASA to Palo Alto Configuration Converter", font=("Arial", 16)).pack(pady=10)

upload_btn = tk.Button(root, text="Upload ASA Config File", command=upload_file)
upload_btn.pack(pady=5)

tk.Label(root, text="Select Output Format:").pack(pady=5)
tk.Radiobutton(root, text="Set Commands", variable=output_format, value="set").pack()
tk.Radiobutton(root, text="JSON", variable=output_format, value="json").pack()
tk.Radiobutton(root, text="XML", variable=output_format, value="xml").pack()

convert_btn = tk.Button(root, text="Convert and Display", command=convert_and_display)
convert_btn.pack(pady=10)

save_btn = tk.Button(root, text="Save Output", command=save_output)
save_btn.pack(pady=5)

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=25)
text_area.pack(pady=10)

root.mainloop()