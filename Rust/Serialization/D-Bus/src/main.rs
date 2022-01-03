use std::collections::HashMap;

#[derive(serde::Serialize, serde::Deserialize, zvariant::Type, Debug )]
struct Prot{
    stx: u16,
    len: u32,
    crc: u32,
    body:[u8;16],
}

fn main() {
    // All serialization and deserialization API, needs a context.
    let ctxt = zvariant::EncodingContext::<byteorder::LE>::new_dbus(0);
    // You can also use the more efficient GVariant format:
    // let ctxt = zvariant::EncodingContext::::<LE>::new_gvariant(0);

    // i16
    let encoded = zvariant::to_bytes(ctxt, &42i16).unwrap();
    let decoded: i16 = zvariant::from_slice(&encoded, ctxt).unwrap();
    assert_eq!(decoded, 42);
    println!("{:?} {:02x?}", decoded, encoded);

    // strings
    let encoded = zvariant::to_bytes(ctxt, &"hello").unwrap();
    let decoded: &str = zvariant::from_slice(&encoded, ctxt).unwrap();
    assert_eq!(decoded, "hello");
    println!("{:?} {:02x?}", decoded, encoded);

    // tuples
    let t = ("hello", 42i32, true);
    let encoded = zvariant::to_bytes(ctxt, &t).unwrap();
    let decoded: (&str, i32, bool) = zvariant::from_slice(&encoded, ctxt).unwrap();
    assert_eq!(decoded, t);
    println!("{:?} {:02x?}", decoded, encoded);

    // Vec
    let v = vec!["hello", "world!"];
    let encoded = zvariant::to_bytes(ctxt, &v).unwrap();
    let decoded: Vec<&str> = zvariant::from_slice(&encoded, ctxt).unwrap();
    assert_eq!(decoded, v);
    println!("{:?} {:02x?}", decoded, encoded);

    // Dictionary
    let mut map: HashMap<i64, &str> = HashMap::new();
    map.insert(1, "123");
    map.insert(2, "456");
    let encoded = zvariant::to_bytes(ctxt, &map).unwrap();
    let decoded: HashMap<i64, &str> = zvariant::from_slice(&encoded, ctxt).unwrap();
    assert_eq!(decoded[&1], "123");
    assert_eq!(decoded[&2], "456");
    println!("{:?} {:02x?}", decoded, encoded);

    //structs
    let mystrut = Prot {
        stx :0x55A5,
        len :8,
        crc : 0xba5603a9,
        body: [0x5F;16]
    };
    let encoded = zvariant::to_bytes(ctxt, &mystrut).unwrap();
    let decoded: Prot = zvariant::from_slice(&encoded, ctxt).unwrap();    
    println!("{:02X?} {:02X?}", decoded, encoded);
}
