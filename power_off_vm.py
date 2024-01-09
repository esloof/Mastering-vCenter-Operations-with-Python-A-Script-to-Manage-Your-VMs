from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl

# vCenter Server details
vc_server = 'vc.ntpro.local'
username = 'administrator@ntpro.local'
password = 'VMware1!'
vm_name = 'raspberry'

# Disable SSL certificate verification (for demo purposes only, not recommended for production)
context = ssl._create_unverified_context()

# Function to connect to vCenter
def connect_to_vcenter(server, user, password):
    si = SmartConnect(host=server, user=user, pwd=password, sslContext=context)
    if not si:
        raise Exception("Could not connect to the specified host using specified username and password")
    return si

# Function to find the VM
def get_vm_by_name(si, vm_name):
    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    for vm in container.view:
        if vm.name == vm_name:
            return vm
    return None

# Function to power off the VM
def power_off_vm(vm):
    if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
        print(f"Powering off VM '{vm_name}'...")
        task = vm.PowerOffVM_Task()
        task_info = task.info
        while task_info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            task_info = task.info
        if task_info.state == vim.TaskInfo.State.success:
            print(f"VM '{vm_name}' has been powered off")
        else:
            raise Exception(f"Error powering off VM: {task_info.error}")
    else:
        print(f"VM '{vm_name}' is already powered off")

# Function to power on the VM
def power_on_vm(vm):
    if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
        print(f"Powering on VM '{vm_name}'...")
        task = vm.PowerOnVM_Task()
        task_info = task.info
        while task_info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            task_info = task.info
        if task_info.state == vim.TaskInfo.State.success:
            print(f"VM '{vm_name}' has been powered on")
        else:
            raise Exception(f"Error powering on VM: {task_info.error}")
    else:
        print(f"VM '{vm_name}' is already powered on")

# Main script logic
if __name__ == "__main__":
    service_instance = connect_to_vcenter(vc_server, username, password)
    vm = get_vm_by_name(service_instance, vm_name)
    if vm:
        user_choice = input("Do you want to (on) power on or (off) power off the VM? (on/off): ").strip().lower()
        if user_choice == 'on':
            power_on_vm(vm)
        elif user_choice == 'off':
            power_off_vm(vm)
        else:
            print("Invalid choice. No action taken.")
    else:
        print(f"No VM named '{vm_name}' found")
    Disconnect(service_instance)
