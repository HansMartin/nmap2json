use crate::structs::Host;
use crate::structs::Port;


const DEBUG: bool = false;


// parse each line
pub fn parse_line(host_list: &mut Vec<Host>, line: &String) {

    // ignore comments
    if line.starts_with("#") {
        return
    }

    // Instanciate new Host Struct
    let mut host = Host::empty();

    // variable to track if at least on host was parsed
    let mut is_emtpy = true;

    // fields are separeted by a tab
    let fields = line.split("\t");


    // looping through the fields
    for field in fields {
        let field_parts: Vec<&str> = field.split(": ").collect();

        let field_type = field_parts[0];
        let field_value = &field_parts[1..].join("");

        if DEBUG {
            println!("[DBG] Field: {}", field);
            println!("\tField-Type: {}", field_type);
            println!("\tField-Value: {}", field_value);
        }

        // switch case for the field_type
        match field_type {
            "Host" => {
                let (ip , hostname) = parse_host_field(field_value);
                host.ip = ip;
                host.hostname = hostname;
                is_emtpy = false;
            },
            "Ports" => {
                host.ports = parse_ports_field(field_value);
            },
            "Status" => {
                    let status = field_value;
                    host.status = status.to_string();
            },
            _ => {}
        }
    }

    // merge existing hosts
    if !is_emtpy {
       let found = merge_hosts(host_list, &host);
        if !found {
            host_list.push(host);
        }
    }

}



fn parse_host_field<'a>(field: &'a String) -> (String, String) {

    let subfields: Vec<&str> = field.split(" (").collect();
    let ip: &str = subfields[0];
    let hostname  = subfields[1].replace(")", "");

    return (String::from(ip), hostname);
}


fn parse_ports_field(field: &str) -> Vec<Port> {

    let mut portlist: Vec<Port> = Vec::new();
    
    // In-case of an Empty Port Array
    if field.len() == 0 {
        return portlist;
    }
    

    for port_field in field.split("/,") {
        let port_field: Vec<&str> = port_field.trim().split("/").collect();
        let tmp_port = Port {
            port_number: port_field[0].parse().unwrap(),
            state:  port_field[1].to_owned(),
            protocol: port_field[2].to_owned(),
            owner: port_field[3].to_owned(),
            service: port_field[4].to_owned(),
            sun_rpc_info: port_field[5].to_owned(),
            version: port_field[6].to_owned(),
        };
        portlist.push(tmp_port);
    }
    return portlist;
}


fn merge_hosts(host_list: &mut Vec<Host>, host: &Host) -> bool {

    let mut found = false;
    for tmp_host in host_list {
        if tmp_host.ip == host.ip {
            tmp_host.merge_ports(&host);
            found = true;
            break;
        }
    }
    return found;
}

