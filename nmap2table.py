#!/usr/bin/python
import sys
import json
from rich import box
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


def getEmptyTable():
    table = Table(show_header=True, header_style="bold green")
    table.add_column("IP", style="dim")
    table.add_column("Host")
    table.add_column("Port")
    table.add_column("Service")
    table.add_column("Version", justify="left")
    return table


def pprint_csv(hostlist):


    print("No.;Host;Port;Proto;Service")


    row_count = 0
    for host in hostlist:
        for port in host["ports"]:
            if port["state"] == "open":
                print(f"{str(row_count)};{host['ip']};{str(port['port_number'])};{port['protocol']}; {port['service'].replace('|', '/')}")
                row_count += 1





def pprint_table_dradis_services(hostlist, iponly, isAscii):

    '''
    -> Dradis output format
    No. 	Host 	Port 	Proto 	Service
    '''

    table = Table(show_header=True, header_style="bold green")
    table.add_column("No.", justify="left")
    table.add_column("Host", justify="left")
    table.add_column("Port", justify="left")
    table.add_column("Proto", justify="left")
    table.add_column("Service", justify="left")

    table.box = box.ASCII2

    row_count = 0
    for host in hostlist:
        for port in host["ports"]:
            if port["state"] == "open":
                table.add_row(
                    str(row_count),
                    host["ip"],
                    str(port["port_number"]),
                    port["protocol"],
                    port["service"].replace("|", "/")
                )

                row_count += 1

        
    #console.print(table)
    with console.capture() as capture:
        console.print(table)

    strTable = capture.get()
    strTable = strTable.replace("+", "|").split("\n")[1:-2]
    del strTable[1]
    strTable = "\n".join(strTable)

    print(strTable)
    print("\n")

def pprint_table_dradis_hosts(hostlist, iponly, isAscii):

    '''
    -> Dradis output format
    |_. No.|_. IP|_. Hostname|_. Identified via|
    |>. x.|TBD|TBD|TBD|
    '''

    table = Table(show_header=True, header_style="bold green")
    table.add_column("No.", justify="left")
    table.add_column("IP", justify="left")
    table.add_column("Hostname", justify="left")
    #table.add_column("Identified via", justify="left")

    table.box = box.ASCII2

    row_count = 0
    for host in hostlist:
        if host["status"] == "Up":
            table.add_row(
                str(row_count),
                host["ip"],
                host["hostname"],
                #"nmap scan"
            )

            row_count += 1

        
    #console.print(table)
    with console.capture() as capture:
        console.print(table)

    strTable = capture.get()
    strTable = strTable.replace("+", "|").split("\n")[1:-2]
    del strTable[1]
    strTable = "\n".join(strTable)

    print(strTable)
    print("\n")

def pprint_table_md(hostlist, iponly, isAscii):

    for host in hostlist:
        if host['hostname'] != "":
            console.print(f"# {host['ip']} ({host['hostname']})\n")
        else:
            console.print(f"# {host['ip']}\n")

        tmpTable = getEmptyTable()
        tmpTable.box = box.ASCII2

        for port in host["ports"]:
            if iponly:
                print(host["ip"])
            else:
                if port["state"] == "open":
                    tmpTable.add_row(
                        host["ip"],
                        host["hostname"],
                        str(port["port_number"]),
                        port["service"],
                        port["version"]
                    )

        #console.print(table)
        with console.capture() as capture:
            console.print(tmpTable)

        strTable = capture.get()
        strTable = "\n".join(strTable.replace("+", "|").split("\n")[1:-2])

        print(strTable)
        print("\n")




def pprint_table(hostlist, iponly, isAscii):

    table = getEmptyTable()

    if isAscii:
        table.box = box.ASCII2

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
parser.add_argument('--md', '-m', dest='md', action='store_true',
                    help='Export as Markdown Table')
parser.add_argument('--dradis-hosts', '-dh', dest='dradis_host', action='store_true',
                    help='Export as Dradis Test-Case Table')
parser.add_argument('--dradis-services', '-ds', dest='dradis_service', action='store_true',
                    help='Export as Dradis Test-Case Table')
parser.add_argument('--csv',dest='csv', action='store_true',
                    help='Export as Dradis Test-Case Table')


args = parser.parse_args()

if args.file:
    with open(args.file, "r") as inp_file:
        hosts = json.loads(inp_file.read())
else:
    hosts = json.loads(sys.stdin.read())

if args.md:
    makeAscii = True
else:
    makeAscii = False


if args.port:
    pprint_table(filter_by_port(args.port), args.ip, makeAscii)
elif args.version:
    pprint_table(filter_by_version(args.version), args.ip, makeAscii)
elif args.service:
    pprint_table(filter_by_service(args.service), args.ip, makeAscii)
elif args.md:
    pprint_table_md(hosts, args.ip, makeAscii)
elif args.dradis_host:
    pprint_table_dradis_hosts(hosts, args.ip, makeAscii)
elif args.dradis_service:
    pprint_table_dradis_services(hosts, args.ip, makeAscii)
elif args.csv:
    pprint_csv(hosts)
else:
    pprint_table(hosts, args.ip, makeAscii)

