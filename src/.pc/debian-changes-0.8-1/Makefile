DEST1=/usr/share/gdiskdump/
DESTUI=data/ui/
DESTMEDIA=data/media/

all:

gdiskdump:

install: gdiskdump $(CONF)
	install -d $(DESTDIR)$(DEST1)
	install -m 0755 gdiskdump $(DESTDIR)$(DEST1)
	install -m 0755 gdiskdumpconfig.py $(DESTDIR)$(DEST1)
	install -d $(DESTDIR)$(DEST1)$(DESTUI)
	install -d $(DESTDIR)$(DEST1)$(DESTMEDIA)
	install -m 0644 $(DESTUI)AboutGdiskdumpDialog.ui $(DESTDIR)$(DEST1)$(DESTUI)
	install -m 0644 $(DESTUI)GdiskdumpWindow.ui $(DESTDIR)$(DEST1)$(DESTUI)
	install -m 0644 $(DESTMEDIA)gdiskdump.svg $(DESTDIR)$(DEST1)$(DESTMEDIA)
	install -m 0644 $(DESTMEDIA)drive-harddisk.svg $(DESTDIR)$(DEST1)$(DESTMEDIA)
	install -d $(DESTDIR)/usr/share/applications/
	install -m 0755 gdiskdump.desktop.in $(DESTDIR)/usr/share/applications/gdiskdump.desktop
	install -d $(DESTDIR)/usr/bin/
	ln -sf $(DESTDIR)$(DEST1)gdiskdump $(DESTDIR)/usr/bin/gdiskdump

uninstall:
	rm -r $(DESTDIR)$(DEST1)
	rm /usr/bin/gdiskdump
	rm /usr/share/applications/gdiskdump.desktop

