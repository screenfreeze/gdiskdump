DEST1=/usr/share/gdiskdump/
DESTUI=data/ui/
DESTMEDIA=data/media/
PO_FOLDER = po/
LOCAL_FOLDER = /usr/share/locale/
#include po/Makefile

all:
	make -C po/

gdiskdump:

install: gdiskdump $(CONF)
	install -d $(DESTDIR)$(DEST1)
	install -m 0755 gdiskdump.py $(DESTDIR)$(DEST1)
	install -m 0755 gdiskdumpconfig.py $(DESTDIR)$(DEST1)
	install -d $(DESTDIR)$(DEST1)$(DESTUI)
	install -d $(DESTDIR)$(DEST1)$(DESTMEDIA)
	install -m 0644 $(DESTUI)* $(DESTDIR)$(DEST1)$(DESTUI)
	install -m 0644 $(DESTMEDIA)* $(DESTDIR)$(DEST1)$(DESTMEDIA)
	install -d $(DESTDIR)/usr/share/applications/
	install -m 0755 gdiskdump.desktop.in $(DESTDIR)/usr/share/applications/gdiskdump.desktop
	install -d $(DESTDIR)/usr/bin/
	install -d $(DESTDIR)/usr/share/locale/
	install -m 0755 bin/gdiskdump $(DESTDIR)/usr/bin/
	make install -C po/

uninstall:
	rm -r $(DESTDIR)$(DEST1)
	rm /usr/bin/gdiskdump
	rm /usr/share/applications/gdiskdump.desktop
	make uninstall -D po/
