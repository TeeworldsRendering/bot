clean:
	$(RM) -r $(shell find . -name "__pycache__")
	$(RM) $(wildcard public/database/skin/body/*.png)
	$(RM) $(wildcard public/database/skin/eye/*.png)
	$(RM) $(wildcard public/database/skin/feet/*.png)
	$(RM) $(wildcard public/database/skin/hand/*.png)

fclean: clean
	$(RM) $(wildcard public/database/skin/full/*.png)

install:
	./install.sh