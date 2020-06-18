#!/usr/bin/python3

import sys

def create_tf_block(resource_name, zone_id, origin, record_name, record_ttl, record_type, record_data):
    terraform_block = (
f'resource "aws_route53_record" "{resource_name}" {{\n'
f'  count           = terraform.workspace == "production" ? 1 : 0\n'
f'  \n'
f'  allow_overwrite = true\n'
f'  name            = "{record_name}"\n'
f'  ttl             = {record_ttl}\n'
f'  type            = "{record_type}"\n'
f'  zone_id         = {zone_id}\n'
f'\n'
f'  records = [\n'
f'    "{record_data}"\n'
f'  ]\n'
f'}}\n'
    )
    return terraform_block

if len(sys.argv) > 1:
    zone_file_raw_path = sys.argv[-1]
else:
    print('Specify zone file path')
    sys.exit(1)

# CHANGE THIS!
zone_id = 'aws_route53_zone.my_zone.zone_id'

zone_records = [{'name': '', 'ttl': '', 'type': '', 'data': []}]
origin = ''
original_records_counter = 0

with open(zone_file_raw_path, 'r') as zone_file_raw:
    for line in zone_file_raw.readlines():
        new_record = {'name': '', 'ttl': '', 'type': '', 'data': []}
        # Empty line
        if len(line.strip()) == 0:
            continue
        # Get the origin
        if line.startswith('$ORIGIN'):
            origin = line.strip().split()[1]
            continue
        # Remove service lines
        elif (line.startswith(';')) or (line.startswith('\t')) or ('SOA' in line):
            continue

        line_splitted = line.strip().split()

        # Join spaced data field
        if len(line_splitted) > 5:
            line_splitted[4] = ' '.join(line_splitted[4:])
            line_splitted = line_splitted[:5]

        record_name, record_ttl, record_class, record_type, record_data = line_splitted

        # @ -> origin
        if record_name == '@':
            record_name = origin
        # Remove quotes in TXT records
        if record_type == 'TXT':
            record_data = record_data.replace('"', '')
        # Remove NS
        if (record_type == 'NS') and (record_name == origin):
            continue
        # if data is more than 255 characters, we should split it in a specific way! 
        # And we should also strip a space between lines from origin string
        if len(record_data) > 255:
            record_data = '%s\\" \\"%s' % (record_data[:254], record_data[255:])

        original_records_counter += 1
        addition = True
        for record in zone_records:
            if (record['name'] == record_name) and (record['type'] == record_type):
                if int(record['ttl']) < int(record_ttl):
                    record['ttl'] = record_ttl
                record['data'].append(record_data)
                addition = False
                break
        if addition:
            # print('Add:', record_name, record_type)
            zone_records.append({'name': record_name, 'ttl': record_ttl, 'type': record_type, 'data': [record_data]})

translated_records_counter = 0
counter = 0
for record in zone_records[1:]:
    counter += 1
    translated_records_counter += len(record['data'])
    # filter symbols from record['name'] and create a resource name 
    resource_name = "%s_%s" % (record['type'], "".join(filter(lambda x: x not in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', ',', '.'], record['name'])))
    print(create_tf_block(resource_name.lower(), zone_id, origin, record['name'], record['ttl'], record['type'], '",\n    "'.join(record['data'])))

if original_records_counter == translated_records_counter:
    #print('Looks good!')
    pass
else:
    print('-'*30)
    print('Original records counter =', original_records_counter)
    print('Translated records counter =', translated_records_counter)
    print('Ups, something wrong here! 8)')
