// file containing structures
use serde_derive::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct Port {
        pub port_number: i32,
        pub state: String,
        pub protocol: String,
        pub owner: String,
        pub service: String,
        pub sun_rpc_info: String,
        pub version: String

}

#[derive(Serialize, Deserialize, Debug)]
pub struct Host {
        pub ip: String,
        pub status: String,
        pub hostname: String,
        pub ports: Vec<Port>
}

impl PartialEq for Port {
    fn eq(&self, other: &Self) -> bool {
        self.port_number == other.port_number
    }

}

impl Host {
    pub fn empty() -> Host {
        return Host {
            ip: "".to_string(),
            status: "".to_string(),
            hostname: "".to_string(),
            ports: Vec::<Port>::new()
        }
    }

    pub fn merge_ports(&mut self, host: &Host) {
        let mut port_numbers  = Vec::new();
        for p in &self.ports {
            port_numbers.push(p.port_number);
        }
        for port in &host.ports {
            if !port_numbers.contains(&port.port_number) {
                let hack: Port  = Port {
                    port_number: port.port_number,
                    state: port.state.to_string(),
                    protocol: port.protocol.to_string(),
                    owner: port.owner.to_string(),
                    service: port.service.to_string(),
                    sun_rpc_info: port.sun_rpc_info.to_string(),
                    version: port.version.to_string()
                };
                self.ports.push(hack);
            }
        }
    }
}
