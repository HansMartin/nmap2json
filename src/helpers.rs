use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;
use crate::structs::Host;

// The output is wrapped in a Result to allow matching on errors
// Returns an Iterator to the Reader of the lines of the file.
pub fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where P: AsRef<Path>, {
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}

pub fn hosts_to_json(hosts: &Vec<Host>) -> String {

    serde_json::to_string(hosts).expect("Failed to convert to json")
}
