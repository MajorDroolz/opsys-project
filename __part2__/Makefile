1:
	@python3 project.py 3 1 1024 0.001 3000 4 0.75 256 > test.out
	@diff test.out __tests__/p2-output02_3_a.out_1_1024_0.001_3000_4_0.75_256.txt > diff.out

1s:
	@python3 project.py 3 1 1024 0.001 3000 4 0.75 256 > test.out
	@diff simout.txt __tests__/simout02.txt > diff.out

1f:
	@ALL=1 python3 project.py 3 1 1024 0.001 3000 4 0.75 256 > test.out
	@diff test.out __tests__/p2output02-full.txt > diff.out

################################################################################

2:
	@python3 project.py 8 6 512 0.001 3000 6 0.9 128 > test.out
	@diff test.out __tests__/p2-output03_a.out_8_6_512_0.001_3000_6_0.9_128.txt > diff.out

2s:
	@python3 project.py 8 6 512 0.001 3000 6 0.9 128 > test.out
	@diff simout.txt __tests__/simout03.txt > diff.out

2f:
	@ALL=1 python3 project.py 8 6 512 0.001 3000 6 0.9 128 > test.out
	@diff test.out __tests__/p2output03-full.txt > diff.out

################################################################################

3:
	@python3 project.py 16 2 256 0.001 3000 4 0.5 32 > test.out
	@diff test.out __tests__/p2-output04_a.out_16_2_256_0.001_3000_4_0.5_32.txt > diff.out

3s:
	@python3 project.py 16 2 256 0.001 3000 4 0.5 32 > test.out
	@diff simout.txt __tests__/simout04.txt > diff.out

3f:
	@ALL=1 python3 project.py 16 2 256 0.001 3000 4 0.5 32 > test.out
	@diff test.out __tests__/p2output04-full.txt > diff.out

################################################################################

4:
	@python3 project.py 20 12 128 0.01 4096 4 0.96 64 > test.out
	@diff test.out __tests__/p2-output05_a.out_20_12_128_0.01_4096_4_0.96_64.txt > diff.out

4s:
	@python3 project.py 20 12 128 0.01 4096 4 0.96 64 > test.out
	@diff simout.txt __tests__/simout05.txt > diff.out

4f:
	@ALL=1 python3 project.py 20 12 128 0.01 4096 4 0.96 64 > test.out
	@diff test.out __tests__/p2output05-full.txt > diff.out