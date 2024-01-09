from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import atexit

# vCenter Server details
vc_server = 'vc.ntpro.local'
username = 'administrator@ntpro.local'
password = 'VMware1!'

# Disable SSL certificate verification (for demo purposes only, not recommended for production)
context = ssl._create_unverified_context()

# Function to connect to vCenter
def connect_to_vcenter(server, user, password):
    si = SmartConnect(host=server, user=user, pwd=password, sslContext=context)
    atexit.register(Disconnect, si)
    return si

# Function to get all VMs
def get_all_vms(si):
    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    return container.view

# Power operations for the VM
def power_on_vm(vm):
    if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOn:
        task = vm.PowerOnVM_Task()
        wait_for_task(task)
        print(f"VM '{vm.name}' is powered on.")
    else:
        print(f"VM '{vm.name}' is already powered on.")

def power_off_vm(vm):
    if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOff:
        task = vm.PowerOffVM_Task()
        wait_for_task(task)
        print(f"VM '{vm.name}' is powered off.")
    else:
        print(f"VM '{vm.name}' is already powered off.")

def suspend_vm(vm):
    if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
        task = vm.SuspendVM_Task()
        wait_for_task(task)
        print(f"VM '{vm.name}' is suspended.")
    else:
        print(f"VM '{vm.name}' cannot be suspended because it is not powered on.")

def resume_vm(vm):
    if vm.runtime.powerState == vim.VirtualMachinePowerState.suspended:
        task = vm.PowerOnVM_Task()
        wait_for_task(task)
        print(f"VM '{vm.name}' is resumed.")
    else:
        print(f"VM '{vm.name}' is not suspended.")

def create_snapshot(vm):
    task = vm.CreateSnapshot_Task(name='Snapshot', description='Created by script', memory=False, quiesce=False)
    wait_for_task(task)
    print(f"Snapshot for VM '{vm.name}' created.")

# Wait for vCenter task to complete
def wait_for_task(task):
    task_done = False
    while not task_done:
        if task.info.state == vim.TaskInfo.State.success:
            return
        if task.info.state == vim.TaskInfo.State.error:
            print(f"Task failed: {task.info.error}")
            raise Exception("Task failed")

# Main script logic
if __name__ == "__main__":
    si = connect_to_vcenter(vc_server, username, password)
    vms = get_all_vms(si)
    vms_dict = {vm.name: vm for vm in vms}
    
    print("List of VMs:")
    for vm_name in vms_dict.keys():
        print(vm_name)
    
    selected_vm_name = input("Enter the name of the VM you wish to manage: ")
    vm = vms_dict.get(selected_vm_name)
    
    if vm:
        print(f"Selected VM: {selected_vm_name}")
        action = input("Choose an action: (on) Power On, (off) Power Off, (suspend) Suspend, (resume) Resume, (snapshot) Create Snapshot: ").lower().strip()
        if action == 'on':
            power_on_vm(vm)
        elif action == 'off':
            power_off_vm(vm)
        elif action == 'suspend':
            suspend_vm(vm)
        elif action == 'resume':
            resume_vm(vm)
        elif action == 'snapshot':
            create_snapshot(vm)
        else:
            print("Invalid action selected.")
    else:
        print(f"VM '{selected_vm_name}' not found.")
