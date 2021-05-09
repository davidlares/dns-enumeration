from typing import Dict, List
import dns.resolver
import dns.query
import argparse
import dns.zone
import json

# list of nameservers
def get_ns(tlz, soa=False):
    # servers list
    servers = []
    # SOA or Nameserver
    if not soa:
        ns = dns.resolver.query(tlz, 'NS')
        sn = [x.to_text() for x in ns]
    else:
        ns = dns.resolver.query(tlz, 'SOA')
        sn = [x.mname.to_text() for x in ns]
    for name in sn:
        ips = dns.resolver.query(name, 'A')
        for rdata in ips:
            servers.append(rdata.address)
    return servers

# perform a zone transfer for the top-level zone
def do_xfr(tlz, server):
    try:
        z = dns.zone.from_xfr(dns.query.xfr(server, tlz, timeout=3.0)) # zone transfers
        return z
    except:
        return None

# DNS enumeration based on a file
def do_enum(tlz, subdomains_file, resolver=dns.resolver):
    # domains dictionary
    domains = {}
    with open(subdomains_file, 'r') as f:
        for sub in f:
            sub = sub.strip()
            qname = '{}.{}'.format(sub, tlz)
            try:
                q = resolver.query(qname)
                a = [a.address for a in q]
                domains[qname] = a
            except Exception as e:
                print(e)
                continue
    return domains


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='A simple DNS enumeration tool.')
    parser.add_argument('-x', '--skip-xfr', help='Skip zone transfer attempt (default is to attempt before enumerating)', action='store_true')
    parser.add_argument('-s', '--server', help='Specify DNS server to query (default is to use system resolver)')
    parser.add_argument('-o', '--output', help='Output file to write to')
    parser.add_argument('-f', '--format', help='Output format (default is json)', default='json', choices=['json', 'plain'])
    parser.add_argument('-n', '--no-address', help='Print only the valid subdomains (do not print the rdata)', action='store_true')
    parser.add_argument('tlz', help='Top-level zone to enumerate (i.e. google.com)')
    parser.add_argument('subdomains_file', help='File containing a list of subdomains to enumerate')
    args = parser.parse_args()

    # arguments variable assignation
    subdomains_file = args.subdomains_file
    no_address = args.no_address
    output_format = args.format
    skip_xfr = args.skip_xfr
    server = args.server
    output = args.output
    tlz = args.tlz

    # getting nameserver values
    soa_server = get_ns(tlz, soa=True)[0] 
    resolver = dns.resolver

    # checking if DNS server is found
    if server:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [server]

    # checking skip zone transfer flag
    if not skip_xfr:
        print('Trying zone transfer.')
        results = do_xfr(tlz, soa_server)
        # TODO: if xfr succeeds, try xfr for all gathered subdomains

    # if xfr does not succeed or we chose to skip it, enumerate
    print('Enumerating subdomains.')
    domains = do_enum(tlz, subdomains_file, resolver)
    # print results
    if output:
        print('Writing output to {}.'.format(output))
        with open(output, 'w') as of:
            if output_format == 'json':
                if no_address:
                    json.dump(list(domains.keys()), of, indent=2)
                else:
                    json.dump(domains, of, indent=2)
            else:
                for k, v in domains.items():
                    if no_address:
                        of.write('{}\n'.format(k))
                    else:
                        of.write('{} : {}\n'.format(k, v))
    else:
        print('Writing output to STDOUT.')
        # printing to console
        if output_format == 'json':
            if no_address:
                print(json.dumps(list(domains.keys()), indent=2))
            else:
                print(json.dumps(domains, indent=2))
        else:
            for k, v in domains.items():
                if no_address:
                    print(k)
                else:
                    print('{} : {}'.format(k, v))
