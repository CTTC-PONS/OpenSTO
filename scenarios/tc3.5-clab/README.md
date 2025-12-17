# Test Case 3.5 - Dynamic ACL rule configuration through Security Pipeline


gnmic -a clab-tc3.5-emu-ceos14_ACL:6030 -u admin -p admin --insecure capabilities
gnmic -a clab-tc3.5-emu-ceos14_ACL:6030 -u admin -p admin --insecure set \
  --update-path "/acl/acl-sets/acl-set[name=DENY_TRAFFIC][type=ACL_IPV4]/config/name" --update-value "DENY_TRAFFIC" \
  --update-path "/acl/acl-sets/acl-set[name=DENY_TRAFFIC][type=ACL_IPV4]/acl-entries/acl-entry[sequence-id=10]/config/sequence-id" --update-value "10" \
  --update-path "/acl/acl-sets/acl-set[name=DENY_TRAFFIC][type=ACL_IPV4]/acl-entries/acl-entry[sequence-id=10]/ipv4/config/source-address" --update-value "13.0.1.1/32" \
  --update-path "/acl/acl-sets/acl-set[name=DENY_TRAFFIC][type=ACL_IPV4]/acl-entries/acl-entry[sequence-id=10]/ipv4/config/destination-address" --update-value "0.0.0.0/0" \
  --update-path "/acl/acl-sets/acl-set[name=DENY_TRAFFIC][type=ACL_IPV4]/acl-entries/acl-entry[sequence-id=10]/actions/config/forwarding-action" --update-value "DROP" \
  --update-path "/acl/acl-sets/acl-set[name=DENY_TRAFFIC][type=ACL_IPV4]/acl-entries/acl-entry[sequence-id=20]/config/sequence-id" --update-value "20" \
  --update-path "/acl/acl-sets/acl-set[name=DENY_TRAFFIC][type=ACL_IPV4]/acl-entries/acl-entry[sequence-id=20]/ipv4/config/source-address" --update-value "0.0.0.0/0" \
  --update-path "/acl/acl-sets/acl-set[name=DENY_TRAFFIC][type=ACL_IPV4]/acl-entries/acl-entry[sequence-id=20]/ipv4/config/destination-address" --update-value "0.0.0.0/0" \
  --update-path "/acl/acl-sets/acl-set[name=DENY_TRAFFIC][type=ACL_IPV4]/acl-entries/acl-entry[sequence-id=20]/actions/config/forwarding-action" --update-value "ACCEPT" \
  --update-path "/acl/interfaces/interface[id=Ethernet1]/ingress-acl-sets/ingress-acl-set[set-name=DENY_TRAFFIC][type=ACL_IPV4]/config/set-name" --update-value "DENY_TRAFFIC"
