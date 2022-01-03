use serde::{Serialize, Deserialize};

#[derive(serde_derive::Serialize, serde_derive::Deserialize, PartialEq, Debug)]
struct Entity {
    stx: u16,
    flag: u8,
    len: u32,
    crc: u32,
    body:[u8;16],
}

fn main() {
    let world = Entity {
        stx :0x55A5,
        flag : 0x1A,
        len :8,
        crc : 0xba5603a9,
        body: [0x5F;16]
    };

    let encoded: Vec<u8> = bincode::serialize(&world).unwrap();

    assert_eq!(encoded.len(), 2 + 1 +4 + 4 + 16);
    
    let decoded: Entity = bincode::deserialize(&encoded[..]).unwrap();
    println!("{:02X?}\n {:02X?}", decoded, encoded);

    assert_eq!(world, decoded);    
}