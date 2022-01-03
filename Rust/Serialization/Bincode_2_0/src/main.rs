use bincode::{config::Configuration, Decode, Encode};

#[derive(Encode, Decode, PartialEq, Debug)]
struct Entity {
    stx: u16,
    len: u32,
    crc: u32,
    body:[u8;16],
}

fn main() {
    let config = Configuration::standard().with_fixed_int_encoding();

    let world = Entity {
        stx :0x55A5,
        len :8,
        crc : 0xba5603a9,
        body: [0x5F;16]
    };

    let encoded: Vec<u8> = bincode::encode_to_vec(&world, config).unwrap();

    // The length of the vector is encoded as a varint u64, which in this case gets collapsed to a single byte
    // See the documentation on varint for more info for that.
    // The 4 floats are encoded in 4 bytes each.
    assert_eq!(encoded.len(), 2 + 4 + 4 + 16);
    
    let (decoded, len): (Entity, usize) = bincode::decode_from_slice(&encoded[..], config).unwrap();
    println!("{:02X?}\n {:02X?}", decoded, encoded);

    assert_eq!(world, decoded);
    assert_eq!(len, encoded.len()); // read all bytes
}