# Test Case 4.6b - Static ACL rule configuration

This section enumerates the steps to reproduce the demo in an isolated environment for testing.
The target scenario is described in file `scenario.txt`.


## 0. Redeploy Firewall Agent in remote system
By default Firewall Agent's RESTCONF/OpenConfig NBI is exposed on endpoint 0.0.0.0:8888
```bash
mkdir ~/tfs-ctrl && cd ~/tfs-ctrl
git clone --depth 1 --sparse --branch feat/344-implement-a-new-firewall-agent-controllable-through-restconf-openconfig https://labs.etsi.org/rep/tfs/controller.git .
git sparse-checkout set src/tests/tools/firewall_agent
cd ~/tfs-ctrl/src/tests/tools/firewall_agent/
./redeploy.sh
```

## 1. Cleanup the environment
```bash
kubectl delete namespace tfs

cd ~/opensto
./undeploy.sh
```

# 2. Deploy OpenSTO
```bash
cd ~/opensto
./deploy.sh
```

# 3. Deploy TeraFlowSDN
__NOTE__: Typically, after deploying Docker resources, network is updated.
This makes MicroK8s to rediscover IP addresses and trigger a redeploy of workloads.
```bash
# Wait for MicroK8s to stabilize...
microk8s start
watch -n 1 kubectl get pods -A

# ... then deploy TeraFlowSDN
cd ~/opensto
./scenarios/tc4.6b/tfs-ctrl/redeploy.sh
```

# 4. Onboard topology on TeraFlowSDN
```bash
cd ~/opensto
source ~/tfs-ctrl/tfs_runtime_env_vars.sh
python -m tests.tools.load_scenario ./scenarios/tc4.6b/tfs-ctrl/tfs-topology.json
```

# 5. Register TFS Controller and Secure SLA Policies (SSLAPs)
```bash
cd ~/opensto
./scenarios/tc4.6b/actions/register-tfs-ctrl.sh
./scenarios/tc4.6b/actions/register-sslap-default.sh
./scenarios/tc4.6b/actions/register-sslap-allow-client-1.sh
./scenarios/tc4.6b/actions/register-sslap-allow-client-2.sh
```

# 6. Test connectivity from Internet/Client-1/Client-2 to Server
- Traffic from 10.0.2.0/24 to 10.0.2.25:30435/tcp should be permitted
```bash
# from appropriate machines
wget -q -O- http://10.0.2.25:30435
```

# 7. Apply Default SSLAP and Test Access
```bash
cd ~/opensto
./scenarios/tc4.6b/actions/apply-sslap-default.sh
```
- Traffic from 10.0.2.0/24 to 10.0.2.25:30435/tcp should be blocked
```bash
# from appropriate machines with IP 10.0.2.0/24
wget -q -O- http://10.0.2.25:30435
```

# 8. Apply SSLAP to Allow Client-1 and Test Access
```bash
cd ~/opensto
./scenarios/tc4.6b/actions/apply-sslap-allow-client-1.sh
```
- Traffic from 10.0.2.0/24 to 10.0.2.25:30435/tcp should be blocked, except from 10.0.2.2
```bash
# from appropriate machines
wget -q -O- http://10.0.2.25:30435
```

# 9. Apply SSLAP to Allow Client-2 and Test Access
```bash
cd ~/opensto
./scenarios/tc4.6b/actions/apply-sslap-allow-client-2.sh
```
- Traffic from 10.0.2.0/24 to 10.0.2.25:30435/tcp should be blocked, except from 10.0.2.2 and 10.0.2.10
```bash
# from appropriate machines
wget -q -O- http://10.0.2.25:30435
```

# 10. Terminate SSLAP to Block Client-1 and Test Access
```bash
cd ~/opensto
./scenarios/tc4.6b/actions/terminate-sslap-allow-client-1.sh
```
- Traffic from 10.0.2.0/24 to 10.0.2.25:30435/tcp should be blocked, except from 10.0.2.10
```bash
# from appropriate machines
wget -q -O- http://10.0.2.25:30435
```

# 11. Terminate SSLAP to Block Client-2 and Test Access
```bash
cd ~/opensto
./scenarios/tc4.6b/actions/terminate-sslap-allow-client-2.sh
```
- Traffic from 10.0.2.0/24 to 10.0.2.25:30435/tcp should be blocked
```bash
# from appropriate machines
wget -q -O- http://10.0.2.25:30435
```

# 12. Terminate Default SSLAP and Test Access
```bash
cd ~/opensto
./scenarios/tc4.6b/actions/terminate-sslap-default.sh
```
- Traffic from 10.0.2.0/24 to 10.0.2.25:30435/tcp should be permitted
```bash
# from appropriate machines
wget -q -O- http://10.0.2.25:30435
```
