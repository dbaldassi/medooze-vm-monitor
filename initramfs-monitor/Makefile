BUSYBOX := $(shell which busybox)

all:
	mkdir -p initramfs/bin
	mkdir -p initramfs/proc
	mkdir -p initramfs/sys
	mkdir -p initramfs/dev
	mkdir -p initramfs/mnt/root
	cp init initramfs/
	cp monitor_memory.sh initramfs/memory_monitor.sh
	chmod +x initramfs/init
	chmod +x initramfs/memory_monitor.sh
	cp $(BUSYBOX) initramfs/bin/
	cd initramfs/bin && ln -s busybox sh && cd ..
	cd initramfs/bin && ln -s busybox mount && cd ..
	cd initramfs/bin && ln -s busybox umount && cd ..
	cd initramfs/bin && ln -s busybox switch_root && cd ..
	mknod initramfs/dev/null c 1 3
	chmod 666 initramfs/dev/null
	mknod initramfs/dev/console c 5 1
	chmod 600 initramfs/dev/console
	cd initramfs && find . | cpio -o -H newc | gzip > ../initramfs.cpio.gz
clean:
	rm -rf initramfs initramfs.cpio.gz