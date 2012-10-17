LOCALE_DIR = /usr/share/locale/
MSGFMT_ = @MSGFMT@
LINGUAS = $(patsubst %.po,%,$(wildcard *.po))

translations:	
	for po in $(LINGUAS); \
	do \
	msgfmt $$po.po -o $$po.mo; \
	done

install: translations $(CONF)
	for po in $(LINGUAS); \
	do \
	install -d $(DESTDIR)$(LOCALE_DIR)$$po/LC_MESSAGES/; \
	install -m 0644 $$po.mo $(DESTDIR)$(LOCALE_DIR)$$po/LC_MESSAGES/gdiskdump.mo; \
	done

uninstall:
	for po in $(LINGUAS); \
	do \
	rm $(DESTDIR)$(LOCALE_DIR)$$po/LC_MESSAGES/gdiskdump.mo; \
	done

