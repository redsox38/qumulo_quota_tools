# qumulo_quota_tools
Tools for managing qumulo quotas

## syncing quotas from one cluster to a new one
1. Edit get_quotas.py and set_quotas.py to set cluster host name (source cluster in get_quotas.py and target in set_quotas.py), api user name and password
2. run as "./get_quotas.py | ./set_quotas.py"
