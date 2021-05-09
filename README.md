# DNS enumeration script with DnsPython

The DNS enumeration process is a way for discovering hosts from a target, which actual hosts are attached to it.

In simple words, this is used for mapping out the IP space of a target based on a top-level zone (domain).

This script outputs the available subdomains available based on a txt list. It consists of three main functions.

1. The `get_ns` get the list of nameservers that owns the to-level zone we are going to search. This can allow attempting zone transfers too, but this is a very unusual thing. This process also gathers SOA instead of NS records is required.
2. The `do_xfr` method attempts to perform a zone-transfer
3. The `do_enum` performs the DNS enumeration itself, it loops the subdomains file and determines which one exists or not.

## Run

Simply, just run: `python dns_enumeration.py -x [your_domain] subdomains.txt`

The `-x` flag is intended to skip the zone-transfer process.

This is a fancy way of listing or mapping subdomains.

## Credits

 - [David E Lares](https://twitter.com/davidlares3)

## License

 - [MIT](https://opensource.org/licenses/MIT)
