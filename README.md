# Clone Route53 based hosted zone to secondary account

This is a script to copy all records from an existing hosted zone to another with an identical hosted zone name. Useful for account migrations or consolidations.

Note that the NS and SOA records for the hosted zone will not be copied as they are dynamically generated by AWS upon creation.

Example, *before*

```
Account 1:
    + Route 53
        + Hosted Zone name = example.com
            * example.com SOA
            * example.com NS
            * webserver.example.com A
            * email.example.com MX
            * dkimoaeijfoawije.aeawjlskcvihoiwoeihaowehfwaoef CNAME

Account 2:
    + Route 53
        + Hosted Zone name = example.com
            * example.com SOA
            * example.com NS
```

## Requirements
* Python 3.7 or later.
* AWS CLI
* Access roles with Route 53 READ privileges in source account, WRITE privileges in target account
* The hosted zone FQDN must already exist in the target account

## Installation

Copy `.env.example` to `.env` and modify accordingly.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

## Usage

The Hosted Zone **must** exist in both source and target accounts before execution of the script.

##### To migrate:

Necessary flags:
* `fqdn`: The FQDN used for the hosted zone in Route 53.
* `source`: The 12-digit AWS account ID where the hosted zone *to be migrated* is in.
* `target`: The 12-digit AWS account ID where the hosted zone *is migrated to* is in.
* `profile`: Optional. Can be used to specify AWS CLI profile to be used for the operation.
* `verify`: Optional. Can be used to verify/validate similarity between source and target.


Example usage to migrate:
```bash
python3 main.py --fqdn=example.com. --source=123456789012 --target=210987654321 --profile=serviceaccount
```

##### To verify:
You can validate that you have the same records in both hosted zones by using the `--verify=true` flag. This flag is optional. If the `verify` flag is used **no records will be written to the target account**.

Example usage to verify:
```bash
python3 main.py --fqdn=example.com. --source=123456789012 --target=210987654321 --profile=serviceaccount --verify=true
```

**Please note:** NS and SOA records should different for hosted zones since they are dynamically generated upon creation of the hosted zone by Route 53. If they for some reason are indeed the same, the `verify` flag will warn for this.

Example output for missing and incorrect records from `verify`:

```json
{
    "NbrOfRecords": {
        "SameNbrOfRecords": false,
        "SourceNbrOfRecords": 211,
        "TargetNbrOfRecords": 210
    },
    "Discrepancies": {
        ".dfrmzrbmikrarEXAMPLE4qkz4a5m3subdomain._domainkey.subdomain.exampledomain.com.:CNAME": {
            "Expected": {
                "Name": ".dfrmzrbmikrarEXAMPLE4qkz4a5m3subdomain._domainkey.subdomain.exampledomain.com.",
                "Type": "CNAME",
                "TTL": 1800,
                "ResourceRecords": [
                    {
                        "Value": ".dfrmzrbmikrarEXAMPLE4qkz4a5m3subdomain.dkim.amazonses.com"
                    }
                ]
            },
            "CurrentTarget": {
                "Name": ".dfrmzrbmikrarEXAMPLE4qkz4a5m3subdomain._domainkey.subdomain.exampledomain.com.",
                "Type": "CNAME",
                "TTL": 1800,
                "ResourceRecords": [
                    {
                        "Value": "dkim.amazonses.com"
                    }
                ]
            }
        },
        "_d9af41bbd4EXAMPLE371790c8c6.api.stage.acs.subdomain.exampledomain.com.:CNAME": {
            "Expected": {
                "Name": "_d9af41bbd4EXAMPLE371790c8c6.api.stage.acs.subdomain.exampledomain.com.",
                "Type": "CNAME",
                "TTL": 300,
                "ResourceRecords": [
                    {
                        "Value": "_269ba35e8EXAMPLE652bf41029ff.ltfexamplelp.acm-validations.aws."
                    }
                ]
            },
            "CurrentTarget": "Not found"
        },
        "SameNSComment": "Same NS records for both source and target parent FQDN"
    }
}
```