
mod structs;
mod helpers;
mod parser;

use helpers::read_lines;
use helpers::hosts_to_json;
use parser::parse_line;
use crate::structs::Host;
use std::io::{self, Read, BufRead};

use std::env; // for having commandline arguments

fn open_gnmap(file: &str) -> Vec<Host> {

    // 1. Instance of the host list
    let mut host_list: Vec<Host> = Vec::new();

    if let Ok(lines) = read_lines(file) {
        for line in lines {
            if let Ok(ip) = line {
                parse_line(&mut host_list, &ip);
            }
        }
    }
    return host_list;
}

fn parse_from_buffer(buffer: String) -> Vec<Host> {
    let mut host_list: Vec<Host> = Vec::new();
    let lines = io::BufReader::new(buffer.as_bytes()).lines();
        for line in lines {
            if let Ok(ip) = line {
                parse_line(&mut host_list, &ip);
            }
        }
    return host_list;
}

fn main() {

    // arguments
    let args: Vec<String> = env::args().collect();
    let hosts: Vec<Host>;
    if args.len() == 2 {
        hosts = open_gnmap(&args[1]);
    }
    else {
        let mut buffer = String::new();
        let stdin = io::stdin();
        let mut handle = stdin.lock();
        handle.read_to_string(&mut buffer).expect("Failed to read from stdin");
        hosts = parse_from_buffer(buffer);
    }

    let json = hosts_to_json(&hosts);
    println!("{}", json);

}

