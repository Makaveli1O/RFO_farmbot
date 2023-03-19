# This are instruction for Windows  and Hyper-V combination

First of all make sure to have hyper-V enabled and working.

## Steps to partition GPU to VM

1. Update your NVIDIA drivers on your host PC
2. Install Windows guest machine.
3. (Optional)Turn off your **INTEGRATED** Graphics card in device manager. 
4. Run script from copyDriverFiles_v1.3 in PowerShell with admin rights(in host machine, while guest is running).
5. IN the guest machine copy files from **C:/Temp/** to **C:/Windows/**
6. Turn off guest machine.
7. Start run the second script (GPU_partiton..) in this folder with admin rights . This will boot up VM. Now Dedicated GPU should be visible in the device manager guest machine.
