# Test Case 4.6b - Static ACL rule configuration

This section enumerates the steps to reproduce the demo in an isolated environment for testing.
The target scenario is described in file `scenario.txt`.

## 0. Download and install ContainerLab
```bash
sudo bash -c "$(curl -sL https://get.containerlab.dev)" -- -v 0.71.0
```

## 1. Download 64-bit image for Arista cEOS v4.33.5M and create Docker image
__NOTE__: Image to be downloaded for free from [Arista](https://www.arista.com/en/login) website.
```bash
docker import cEOS64-lab-4.33.5M.tar ceos:4.33.5M
```

## 2. Cleanup the environment
```bash
kubectl delete namespace tfs

cd ~/opensto
./undeploy.sh
./scenarios/tc4.6b/containerlab/emulated/destroy.sh
```

## 3. Deploy ContainerLab Scenario
```bash
cd ~/opensto
./scenarios/tc4.6b/containerlab/emulated/deploy.sh
```

# 4. Deploy OpenSTO
```bash
cd ~/opensto
./deploy.sh
```

# 5. Deploy TeraFlowSDN
__NOTE__: Typically, after deploying Docker resources, network is updated.
This makes MicroK8s to rediscover IP addresses and trigger a redeploy of workloads.
```bash
# Wait for MicroK8s to stabilize...
watch -n 1 kubectl get pods -A

# ... then deploy TeraFlowSDN
cd ~/opensto
./scenarios/tc4.6b/tfs-ctrl/redeploy.sh
```

# 6. Onboard topology on TeraFlowSDN
```bash
cd ~/opensto
source ~/tfs-ctrl/tfs_runtime_env_vars.sh
python -m tests.tools.load_scenario ./scenarios/tc4.6b/tfs-ctrl/tfs-topology.json
```

# 7. Register TFS Controller and Secure SLA Policy
```bash
cd ~/opensto
./scenarios/tc4.6b/actions/register-tfs-ctrl.sh
./scenarios/tc4.6b/actions/register-sslap.sh
```

# 8. Test connectivity from Internet/Corporate to Server
- Both should work.
```bash
docker exec -t clab-tc46b-emu-internet bash -c 'ping -c3 -n 192.168.0.10'
docker exec -t clab-tc46b-emu-internet bash -c 'wget -q -O- 192.168.0.10'

docker exec -t clab-tc46b-emu-corporate bash -c 'ping -c3 -n 192.168.0.10'
docker exec -t clab-tc46b-emu-corporate bash -c 'wget -q -O- 192.168.0.10'
```

# 9. Apply Secure SLA Policy
The SSLA Policy applied includes the following rules:
- `deny-http-from-internet-to-server`
- `deny-http-from-server-to-internet`
- `deny-icmp-from-internet-to-server`
- `deny-icmp-from-server-to-internet`
- `permit-http-from-corporate-to-server`
- `permit-http-from-server-to-corporate`
- `permit-icmp-from-corporate-to-server`
- `permit-icmp-from-server-to-corporate`

```bash
cd ~/opensto
./scenarios/tc4.6b/actions/apply-sslap.sh
```

# 10. Test connectivity from Internet/Corporate to Server
- From Corporate should work, from Internet should be dropped.
```bash
docker exec -t clab-tc46b-emu-internet bash -c 'ping -c3 -n 192.168.0.10'
docker exec -t clab-tc46b-emu-internet bash -c 'wget -q -O- 192.168.0.10'

docker exec -t clab-tc46b-emu-corporate bash -c 'ping -c3 -n 192.168.0.10'
docker exec -t clab-tc46b-emu-corporate bash -c 'wget -q -O- 192.168.0.10'
```

# 11. Terminate the Secure SLA Policy
```bash
cd ~/opensto
./scenarios/tc4.6b/actions/terminate-sslap.sh
```

# 12. Test connectivity from Internet/Corporate to Server
- Both should work again.
```bash
docker exec -t clab-tc46b-emu-internet bash -c 'ping -c3 -n 192.168.0.10'
docker exec -t clab-tc46b-emu-internet bash -c 'wget -q -O- 192.168.0.10'

docker exec -t clab-tc46b-emu-corporate bash -c 'ping -c3 -n 192.168.0.10'
docker exec -t clab-tc46b-emu-corporate bash -c 'wget -q -O- 192.168.0.10'
```
