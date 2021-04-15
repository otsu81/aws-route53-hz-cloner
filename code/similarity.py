import json


def __jsonprint(inp):
    print(json.dumps(inp, indent=4, default=4))


def __check_NS_records(record1, record2):
    """
    NS records are stored as lists, which are unordered - this gives
    discrepancy when comparing similarity directly so we need a special
    function for this.
    Expects a records dictionary with format
    {
        'Name': (str)fqdn,
        'Type': 'NS',
        'Value': [
            'ns_.address.com',
            'ns2.address.com',
            '...'
        ]
    }
    """
    set1 = __extract_set(record1['ResourceRecords'])
    set2 = __extract_set(record2['ResourceRecords'])
    # return boolean for equal length of union and original set
    return len(set1.union(set2)) == len(set1)


def __extract_set(input_value_list):
    """takes an inputlist of value dicts and returns a set of only the
    values"""
    values = set()
    for i in input_value_list:
        values.add(i.get('Value'))
    return values


def __compare_length(source_dict, target_dict):
    source_length = len(source_dict)
    target_length = len(target_dict)
    if source_length == target_length:
        return {'SameNbrOfRecords': True}
    else:
        return {
            'SameNbrOfRecords': False,
            'SourceNbrOfRecords': source_length,
            'TargetNbrOfRecords': target_length
        }


def __compare_records(fqdn, source_dict, target_dict):
    discrepancy = list()
    discrepancies_report = dict()
    for record in source_dict:
        try:
            if source_dict[record]['Type'] == 'NS':
                if not __check_NS_records(
                                        source_dict[record],
                                        target_dict[record]):
                    discrepancy.append(record)
            elif not source_dict[record] == target_dict[record]:
                discrepancy.append(record)
        except KeyError:
            discrepancy.append(record)

    for d in discrepancy:
        try:
            discrepancies_report[d] = {
                'Expected': source_dict[d],
                'CurrentTarget': target_dict[d]
            }
        except KeyError:
            discrepancies_report[d] = {
                'Expected': source_dict[d],
                'CurrentTarget': 'Not found'
            }

    # check that NS and SOA for the FQDN is not the same - if they are the same
    # something is wrong, NS and SOA are dynamically generated when creating
    # the Hosted Zone in Route 53
    if not discrepancies_report.pop(f"{fqdn}:NS", None):
        discrepancies_report['SameNSComment'] = ('Same NS records for both'
                                                 'source and target FQDN')
    if not discrepancies_report.pop(f"{fqdn}:SOA", None):
        discrepancies_report['SameSOAComment'] = ('Same SOA for both source'
                                                  'and target FQDN')

    return discrepancies_report


def check_records_similarity(fqdn, source, target):
    source_dict = dict()
    target_dict = dict()
    for r in source:
        key = f"{r['Name']}:{r['Type']}"
        source_dict[key] = r
    for r in target:
        key = f"{r['Name']}:{r['Type']}"
        target_dict[key] = r

    discrepancies_report = dict()
    discrepancies_report['NbrOfRecords'] = __compare_length(source_dict,
                                                            target_dict)
    discrepancies_report['Discrepancies'] = __compare_records(fqdn,
                                                              source_dict,
                                                              target_dict)

    return discrepancies_report
