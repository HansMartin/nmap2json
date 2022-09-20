#!/usr/bin/python
import sys
import json
from rich.console import Console
from rich.table import Table
import argparse
import re


translateSvc = {
    "smb":"microsoft-ds?|netbios-ssn",
    "rdp":"ms-wbt-server",
    "dns":"domain",
}



# Setup Table
console = Console()

table = Table(show_header=True, header_style="bold green")
table.add_column("IP", style="dim")
table.add_column("Host")
table.add_column("Port")
table.add_column("Service")
table.add_column("Version", justify="left")

def pprint_table(hostlist, iponly):
    global table

    for host in hostlist:
        for port in host["ports"]:
            if iponly:
                print(host["ip"])
            else:
                if port["state"] == "open":
                    table.add_row(
                        host["ip"],
                        host["hostname"],
                        str(port["port_number"]),
                        port["service"],
                        port["version"]
                    )

    if not iponly and table.row_count > 0:
        console.print(table)

def filter_by_port(port):
    global hosts
    out = []
    ports = []
    for host in hosts:
        for p in host["ports"]:
            if port == str(p["port_number"]) and p["state"] == "open":
                ports.append(p)
        host["ports"] = ports
        ports = []
        out.append(host)
    return out


def filter_by_service(service):
    global hosts

    if service in translateSvc:
        service = translateSvc[service]

    recomp = re.compile(service, re.IGNORECASE)
    out = []
    ports = []
    for host in hosts:
        for p in host["ports"]:
            if len(recomp.findall(p["service"])) > 0:
                ports.append(p)
        host["ports"] = ports
        ports = []
        out.append(host)
    return out


def filter_by_version(version):
    global hosts
    # Support regular expressions for version matching
    recomp = re.compile(version, re.IGNORECASE)
    out = []
    ports = []
    for host in hosts:
        for p in host["ports"]:
            if len(recomp.findall(p["version"])) > 0:
                ports.append(p)
        host["ports"] = ports
        ports = []
        out.append(host)
    return out


# Setup Argument Parser
parser = argparse.ArgumentParser(description='Filtering nmap')
parser.add_argument('file', action='store', nargs='?',
                    help='Input File')
parser.add_argument('--port', dest='port', action='store',
                    help='Filter by port number')
parser.add_argument('--version', dest='version', action='store',
                    help='Filter by version string')
parser.add_argument('--service', dest='service', action='store',
                    help='Filter by service')
parser.add_argument('--ip-only', '-i', dest='ip', action='store_true',
                    help='Only print the ips')


args = parser.parse_args()

if args.file:
    with open(args.file, "r") as inp_file:
        hosts = json.loads(inp_file.read())
else:
    hosts = json.loads(sys.stdin.read())


if args.port:
    pprint_table(filter_by_port(args.port), args.ip)
elif args.version:
    pprint_table(filter_by_version(args.version), args.ip)
elif args.service:
    pprint_table(filter_by_service(args.service), args.ip)
else:
    pprint_table(hosts, args.ip)

