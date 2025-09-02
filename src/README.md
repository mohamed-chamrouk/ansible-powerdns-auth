## kpfleming.powerdns_auth.zone

This module can be used to create, remove, and manage zones. It can
also trigger some zone-related actions: NOTIFY and AXFR.

Note that if any 'metadata' attributes are specified when `state` is
set to `present`, *all* metadata attributes on the zone will be
updated or removed, depending on their defaults. As a result, you
must specify *all* metadata attributes that you wish to have set
on the zone.

Examples:
```yaml
- name: create native zone
  kpfleming.powerdns_auth.zone:
    name: d2.example.
    state: present
    api_key: 'foobar'
    properties:
      kind: 'Native'
      nameservers:
        - 'ns1.example.'
      soa:
        mname: 'localhost.'
        rname: 'hostmaster.localhost.'
    metadata:
      allow_axfr_from: ['AUTO-NS']
      axfr_source: '127.0.0.1'

- name: change native zone to master
  kpfleming.powerdns_auth.zone:
    name: d2.example.
    state: present
    api_key: 'foobar'
    properties:
      kind: 'Master'

- name: delete zone
  kpfleming.powerdns_auth.zone:
    name: d2.example.
    state: absent
    api_key: 'foobar'
```

Additionnaly, this module can also be used to create, update
and remove rrsets. The creation and deletion work the same way as the
[API](https://doc.powerdns.com/authoritative/http-api/zone.html) does.
The module also include the `keep` option on rrsets providing an
the possibility to update rrsets while keeping existing records.

Examples:
```yaml
- name: add rrset to existing zone
  pdns_auth_zone:
    name: d4.example.
    state: present
    api_key: 'foobar'
    properties:
      rrsets:
        - name: www.d4.example.
          type: A
          changetype: REPLACE
          records:
            - content: 192.168.0.1
              disabled: False
            - content: 192.168.1.1

- name: add record to existing rrset in existing zone
  pdns_auth_zone:
    name: d4.example.
    state: present
    api_key: 'foobar'
    properties:
      rrsets:
        - name: www.d4.example.
          type: A
          changetype: REPLACE
          keep: true
          records:
            - content: 192.168.2.1

- name: remove single record from rrset in existing zone
  pdns_auth_zone:
    name: d4.example.
    state: present
    api_key: 'foobar'
    properties:
      rrsets:
        - name: www.d4.example.
          type: A
          changetype: DELETE
          keep: true
          records:
            - content: 192.168.2.1

- name: remove rrset from existing zone
  pdns_auth_zone:
    name: d4.example.
    state: present
    api_key: 'foobar'
    properties:
      rrsets:
        - name: www.d4.example.
          type: A
          changetype: DELETE
```

## kpfleming.powerdns_auth.tsigkey

This module can be used to create, remove, and manage TSIG keys.

Examples:
```yaml
- name: create key with default algorithm
  kpfleming.powerdns_auth.tsigkey:
    name: key2
    state: present
    api_key: 'foobar'

- name: remove key
  kpfleming.powerdns_auth.tsigkey:
    name: key2
    state: absent
    api_key: 'foobar'

- name: create key with algorithm and content
  kpfleming.powerdns_auth.tsigkey:
    name: key3
    state: present
    api_key: 'foobar'
    algorithm: hmac-sha256
    key: '+8fQxgYhf5PVGPKclKnk8ReujIfWXOw/aEzzPPhDi6AGagpg/r954FPZdzgFfUjnmjMSA1Yu7vo6DQHVoGnRkw=='
```
