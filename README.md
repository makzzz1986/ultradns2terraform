# Script for translation UltraDNS tabspaced exported zone file to Terraform configuration 

## Usage:
Specify file with exported hosted zone:
```python3 main.py /tmp/my_zone.txt```

## ZONE_ID
```zone_id``` parameter is hardcoded as ```aws_route53_zone.my_zone.zone_id```, you can easily change it. 
