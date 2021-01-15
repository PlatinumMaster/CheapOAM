import os
import struct
import sys
import subprocess

def parseOAM(input, output):
	with open(input, 'rb') as rand:
		with open(output, 'w') as out:
			nCells, allegedXMax, allegedYMax, allegedXMin, allegedYMin, unknown = struct.unpack('<LHHHHB', rand.read(struct.calcsize('<LHHHHB')))
			out.write(".macro subentry x, y, size_x, size_y, cell_x, cell_y\n" + 
			".word \\x & 0xFFFFFF\n" + 
			".word \y & 0xFFFFFF\n" + 
			".word \size_x\n" + 
			".word \size_y\n" + 
			".word \cell_x\n" + 
			".word \cell_y\n" + 
			".endm\n\n")
			out.write(f'.word {hex(nCells)}\t@ nCells\n')
			out.write(f'.hword {hex(allegedXMax)}\t @ X Max?\n')
			out.write(f'.hword {hex(allegedYMax)}\t @ Y Max?\n')
			out.write(f'.hword {hex(allegedXMin)}\t @ X Min?\n')
			out.write(f'.hword {hex(allegedYMin)}\t @ Y Min?\n')
			out.write(f'.byte {hex(unknown)}\t @ Unknown?\n\n')
			out.write('@ subentry <x>, <y>, <size_x>, <size_y>, <cell_x>, <cell_y>\n')
			for cell in range(nCells):
				out.write(f'Entry{cell}:\n')
				for sub in range(2):
					x, y, size_x, size_y, cell_x, cell_y = struct.unpack('<LLLLLL', rand.read(struct.calcsize('<LLLLLL')))
					out.write(f'\tsubentry {x}, {y}, {hex(size_x)}, {hex(size_y)}, {hex(cell_x)}, {hex(cell_y)}\n')
				out.write('\n')
			while rand.tell() != os.path.getsize(input):
				out.write(f'.byte {hex(rand.read(1)[0])}\n')
		out.close()
	rand.close()

def parseASM(input, output):
	AS = ['arm-none-eabi-as', '-mthumb', '-c', input, '-o', 'temp.o']
	OBJ = ['arm-none-eabi-objcopy', '-O', 'binary', 'temp.o', output]
	subprocess.run(AS)
	subprocess.run(OBJ)

def usage():
	return f'''{sys.argv[0]} - USAGE
	Dump: python {sys.argv[0]} dump <in> <out>
	Make: python {sys.argv[0]} make <in> <out>'''

def __main__():
	if len(sys.argv) == 3:
		if sys.argv[1].lower() == 'dump':
			parseOAM(sys.argv[2], sys.argv[3])
		elif sys.argv[1].lower() == 'make':
			parseASM(sys.argv[2], sys.argv[3])
		else:
			print(usage())
	else:
		print(usage())
	return

__main__()
	