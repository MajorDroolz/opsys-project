random:
	@python3 random.py > 1.txt
	@gcc random.c
	@./a.out > 2.txt
	@-diff 1.txt 2.txt > diff.txt
	@rm a.out
