
import os
from argparse import ArgumentParser
from libcloud.loadbalancer.base import Member, Algorithm
from libcloud.loadbalancer.types import Provider
from libcloud.loadbalancer.providers import get_driver

Driver = get_driver(Provider.RACKSPACE)

USERNAME = os.environ.get('RS_USERNAME')
APIKEY = os.environ.get('RS_APIKEY')

def get_all_lbs(region=None):
    if not region:
        regions = [
            'iad',
            'dfw',
            'ord',
            'syd',
            'hkg',
        ]
    else:
        regions = [region]

    lbs = []
    for r in regions:
        rs = Driver(USERNAME, APIKEY, region=r)
        r_lbs = rs.list_balancers()
        for lb in r_lbs:
            lbs.append({
                'id': lb.id,
                'name': lb.name,
                'region': r,
            })
    return lbs

def add_node(lbs, args):
    members = [Member(args.name, args.ip, args.port)]
    lb = {}
    for b in lbs:
        if args.lb == b['name']:
            lb = b
    if lb:
        rs = Driver(USERNAME, APIKEY, region=lb['region'])
        lb = rs.get_balancer(lb['id'])
        if check_node_exists(rs, lb, args):
            print('Node %s:%s exists in %s pool.' % (args.ip, args.port, args.lb))
        else:
          rs.ex_balancer_attach_members(lb, members)
          print('Node %s:%s attached to %s pool.' % (args.ip, args.port, args.lb))
    else:
      print('No Matching LB')

def delete_node(lbs, args):
    lb = {}
    for b in lbs:
        if args.lb == b['name']:
            lb = b
    if lb:
        rs = Driver(USERNAME, APIKEY, region=lb['region'])
        lb = rs.get_balancer(lb['id'])
        member = check_node_exists(rs, lb, args)
        if member:
            rs.ex_balancer_detach_members(lb, [member])
            print('Node %s:%s detached from %s pool.' % (args.ip, args.port, args.lb))
        else:
            print('Node %s:%s does not exist in %s pool.' % (args.ip, args.port, args.lb))
    else:
      print('No Matching LB')


def check_node_exists(rs, lb, args):
    found = False
    members = []
    for member in rs.balancer_list_members(lb):
        if args.ip == member.ip:
            if args.port == member.port:
                return member
    return found


def parse_args():
    parser = ArgumentParser(description=None)

    subparsers = parser.add_subparsers(
        title="Commands",
        description="Available Commands",
        help="Description"
    )

    # add
    add_parser = subparsers.add_parser(
        "add",
        help="Add Node"
    )
    add_parser.set_defaults(func=add_node)

    add_parser.add_argument(
        "-l", "--lb", dest="lb", default=None, metavar="LB", type=str,
        help="Load Balancer Name"
    )

    add_parser.add_argument(
        "-n", "--name", dest="name", default=None, metavar="NAME", type=str,
        help="Node Name"
    )

    add_parser.add_argument(
        "-i", "--ip", dest="ip", default=None, metavar="IP", type=str,
        help="IP Address"
    )

    add_parser.add_argument(
        "-p", "--port", dest="port", default=8080, metavar="PORT", type=int,
        help="Container Port"
    )

    # Delete
    add_parser = subparsers.add_parser(
        "delete",
        help="Delete Node"
    )
    add_parser.set_defaults(func=delete_node)

    add_parser.add_argument(
        "-l", "--lb", dest="lb", default=None, metavar="LB", type=str,
        help="Load Balancer Name"
    )

    add_parser.add_argument(
        "-n", "--name", dest="name", default=None, metavar="NAME", type=str,
        help="Node Name"
    )

    add_parser.add_argument(
        "-i", "--ip", dest="ip", default=None, metavar="IP", type=str,
        help="IP Address"
    )

    add_parser.add_argument(
        "-p", "--port", dest="port", default=8080, metavar="PORT", type=int,
        help="Container Port"
    )


    return parser.parse_args()


def main():
    args = parse_args()
    lbs = get_all_lbs()
    args.func(lbs, args)


if __name__ == "__main__":
    main()
