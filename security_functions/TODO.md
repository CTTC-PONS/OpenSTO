ONGOING:
- integrated cttc-only test (clab + pipeline + TFS)

ISSUES:
- Topology should map all device names to UUIDs
- Add method that maps all device names to UUIDs
- On Topology::refresh()/load_unsafe, update the device name-uuid mappings

[2025-11-24 20:03:47,990] INFO:attack_mitigator.Processor:Processing: {"attack_uuid": "malign_heavy_hitter", "src_ip": "13.0.1.1", "interface": "eth1", "monitored_device": "ceos14_ACL", "protocol": 1, "dst_ip": "192.168.16.13", "src_port": 0, "dst_port": 0}
[2025-11-24 20:03:47,990] INFO:attack_mitigator.Processor:Attack Sample: {'attack_uuid': 'malign_heavy_hitter', 'src_ip': '13.0.1.1', 'interface': 'eth1', 'monitored_device': 'ceos14_ACL', 'protocol': 1, 'dst_ip': '192.168.16.13', 'src_port': 0, 'dst_port': 0}
[2025-11-24 20:03:48,716] INFO:attack_mitigator.AttackModels:[get_target_firewalls] source_device_uuids={'819d1db9-316c-5272-a3a1-02eaf0502920'}
[2025-11-24 20:03:48,717] INFO:attack_mitigator.AttackModels:[get_target_firewalls] destination_device_uuids={'aaeee8c3-ed07-524c-9547-9ce78d3b8845'}
[2025-11-24 20:03:48,717] INFO:attack_mitigator.AttackModels:[get_target_firewalls] involved_device_uuids={'ceos14_ACL'}
[2025-11-24 20:03:48,717] INFO:attack_mitigator.Topology:[get_target_firewalls] required={'aaeee8c3-ed07-524c-9547-9ce78d3b8845', '819d1db9-316c-5272-a3a1-02eaf0502920', 'ceos14_ACL'}
[2025-11-24 20:03:48,719] ERROR:attack_mitigator.Processor:Unhandled Exception
Traceback (most recent call last):
  File "/app/attack_mitigator/Processor.py", line 82, in run
    self.dispatch_attack(str_attack_sample, producer)
  File "/app/attack_mitigator/Processor.py", line 106, in dispatch_attack
    firewall_acl_rule_set, mitigated_sources = self.attack_models.get_mitigation_acls(
                                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/attack_mitigator/AttackModels.py", line 210, in get_mitigation_acls
    firewall_acl_rule_set, mitigated_sources = attack_model.get_mitigation_acls(topology)
                                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/attack_mitigator/AttackModels.py", line 105, in get_mitigation_acls
    target_firewalls = self.get_target_firewalls(topology)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/attack_mitigator/AttackModels.py", line 98, in get_target_firewalls
    target_firewalls = topology.get_target_firewalls(
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/attack_mitigator/Topology.py", line 44, in get_target_firewalls
    stree = steiner_tree(self._network, required, weight=WEIGHT)

...

  File "/usr/local/lib/python3.11/site-packages/networkx/algorithms/shortest_paths/weighted.py", line 754, in multi_source_dijkstra
    raise nx.NodeNotFound(f"Node {s} not found in graph")
networkx.exception.NodeNotFound: Node ceos14_ACL not found in graph
