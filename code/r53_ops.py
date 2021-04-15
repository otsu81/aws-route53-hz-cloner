import json


class Route53Ops:

    def __init__(self, fqdn):
        self.fqdn = fqdn

    def find_zone_id(self, client):
        pgntr = client.get_paginator('list_hosted_zones')
        itr = pgntr.paginate()
        for i in itr:
            for hz in i['HostedZones']:
                if hz['Name'] == self.fqdn:
                    return hz['Id']

    def get_all_records_from_hosted_zone(self, client):
        paginator = client.get_paginator('list_resource_record_sets')
        itr = paginator.paginate(
            HostedZoneId=self.find_zone_id(client)
            )
        records = list()
        for i in itr:
            for record in i.get('ResourceRecordSets'):
                records.append(record)
        return records

    def list_all_hosted_zones(self, client):
        paginator = client.get_paginator('list_hosted_zones')
        itr = paginator.paginate()
        for i in itr:
            print(i)

    def put_records(self, client, records):
        changes = list()
        for r in records:
            if r['Name'] == self.fqdn and (r['Type'] == 'NS' or r['Type'] == 'SOA'):
                pass
            else:
                change = {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': r
                }
                changes.append(change)

        change_batch = {
            'Comment': 'Migrated record',
            'Changes': changes
        }
        client.change_resource_record_sets(
            HostedZoneId=self.find_zone_id(client),
            ChangeBatch=change_batch
        )
        return True
