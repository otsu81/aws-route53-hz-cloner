#!/usr/bin/env python3

import boto3
import sys
import click
import json
from dotenv import load_dotenv
from code.boto_factory import BotoFactory
from code.r53_ops import Route53Ops
from code.similarity import check_records_similarity

load_dotenv()


def __json_print(pr):
    print(json.dumps(pr, indent=4, default=str))


@click.command()
@click.option('--fqdn', help='The FQDN we wish to migrate')
@click.option('--source', help=('The source account ID where the'
                                'Route53 Hosted Zone is located'))
@click.option('--target', help=('The target account ID where the'
                                'Route53 Hosted Zone is located (must exist)'))
@click.option('--profile', help=('(Optional) The AWS CLI profile to be used,'
                                 'should have roleswitching privileges in both'
                                 'source and target accounts'))
@click.option('--verify', help=('(Optional) [true|false] flag, if a similarity'
                                'report will be generated without writing any'
                                'new records to the target account'))
def main(fqdn, source, target, profile='', verify=''):
    if (fqdn or source or target) is None:
        print("Missing parameters, use --help")
        sys.exit(1)
    if profile == '':
        profile = 'default'

    # FQDN must end with ., add if missing
    if not fqdn.endswith('.'):
        fqdn = fqdn + '.'

    # make Route53 resources
    r53ops = Route53Ops(fqdn)
    session = boto3.Session(profile_name=profile)

    r53_source = BotoFactory().get_capability(
        boto3.client, session, 'route53', account_id=source
    )
    r53_target = BotoFactory().get_capability(
        boto3.client, session, 'route53', account_id=target
    )
    try:
        source_records = r53ops.get_all_records_from_hosted_zone(r53_source)
    except AttributeError as e:
        sys.stdout.write(f"{fqdn} doesn't appear to exist in {source}")
        sys.exit(1)

    # if not verify, run put
    if verify != 'true':
        r53ops.put_records(r53_target, source_records)

    # if verify, then only run verify and skip put
    try:
        target_records = r53ops.get_all_records_from_hosted_zone(r53_target)
    except AttributeError as e:
        sys.stdout.write(f"{fqdn} doesn't appear to exist in {target}")
        sys.exit(1)


    __json_print(check_records_similarity(
        fqdn, source_records, target_records
    ))


if __name__ == '__main__':
    if sys.version_info < (3, 7):
        sys.stdout.write("Sorry, requires Python 3.7 or later")
        sys.exit(1)
    main()
