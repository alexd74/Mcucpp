import os
from SCons.Script import *

import os
from SCons.Script import *

def print_size(env, source, alias='size'):
	action = Action("$SIZE %s" % source[0].path, cmdstr="Used section sizes:")
	return env.AlwaysBuild(env.Alias(alias, source, action))


def setup_gnu_tools(env, prefix):
	gnu_tools = ['gcc', 'g++', 'gnulink', 'ar', 'gas']
	for tool in gnu_tools:
		env.Tool(tool)
	env['CC'] = prefix+'gcc'
	env['CXX'] = prefix+'g++'
	env['AR'] = prefix+'ar'
	env['AS'] = prefix+'gcc'
	env['OBJCOPY'] = prefix+'objcopy'
	env['OBJDUMP'] = prefix+'objdump'
	env['NM'] = prefix+"nm"
	env['RANLIB'] = prefix+"ranlib"
	env['SIZE'] = prefix+"size"
	env['PROGSUFFIX'] = '.elf'
	
	device = env['DEVICE']
	env.Append(CPPDEFINES = {})
	if 'defines' in device:
		env.Append(CPPDEFINES = device['defines'])
	if 'clock' in device:
		env.Append(CPPDEFINES = {'F_CPU' : device['clock'] })
	
	env['CFLAGS'] = ["-std=gnu99", "-Wredundant-decls","-Wnested-externs"]
	
	env['CCFLAGS'] = [
		"-mmcu=" + device['cpu'],
		"-gdwarf-2",
		"-funsigned-char",
		"-funsigned-bitfields",
		"-fshort-enums",
		"-fno-split-wide-types",
		"-ffunction-sections",
		"-fdata-sections",
		"-Wall",
		"-Wformat",
		"-Wextra",
		"-Wpointer-arith",
		"-Wunused",
		"-ffunction-sections"
		#"-fshort-wchar"
		#"-pedantic"
	]
	
	
	if 'archOptions' in device:
		for option in device['archOptions']:
			env.Append(CCFLAGS = "-%s" % option)
	
	env['CXXFLAGS'] = [
		"-fno-exceptions",
		"-nostdlib",
		"-fno-threadsafe-statics",
		"-fno-rtti",
		"-fuse-cxa-atexit",
		"-Woverloaded-virtual",
		"-std=c++03",
		#"-fshort-wchar"
	]
	
	env['ASFLAGS'] = [
		"-mcpu=" + device['cpu'],
		"-gdwarf-2",
		"-Wa,--gstabs",
		"-xassembler-with-cpp"
	]
	
	env['ASCOM'] = '$AS $ASFLAGS -o $TARGET -c $SOURCES'

	linkerscript = ""
	if 'linkerscript' in device:
		linkerscript = os.path.join(env.Dir('.').srcnode().abspath, device['linkerscript'])
		linkerscript = '"-T%s"' % linkerscript
	
	env['LINKFLAGS'] = [
		"-mmcu=" + device['cpu'],
		"-Wl,--gc-sections",
		"-nostartfiles",
		linkerscript,
		"-Wl,--gc-sections",
		"-Wl,-Map=${TARGET.base}.map,--cref"
	]
	

	sectionToExport = '--only-section .isr_vectors --only-section .text --only-section .rodata --only-section .ctors --only-section .dtors --only-section .data'
	
	hexBuilder = Builder(
		action = '$OBJCOPY -O ihex ' + sectionToExport + ' $SOURCE $TARGET', 
		src_suffix = ".elf",
		suffix = ".hex")
		
	srecBuilder = Builder(
		action = '$OBJCOPY -O srec  ' + sectionToExport + ' $SOURCE $TARGET', 
		src_suffix = ".elf",
		suffix = ".s37")
		
	binaryBuilder = Builder(
		action = '$OBJCOPY -O binary  ' + sectionToExport + ' $SOURCE $TARGET', 
		src_suffix = ".elf",
		suffix = ".bin")
		
	disasmBuilder = Builder(
		action = '$OBJDUMP -h -S $SOURCE > $TARGET', 
		src_suffix = ".elf",
		suffix = ".lss")
	
	env.Append(BUILDERS = {
		'Hex': hexBuilder,
		'Disassembly': disasmBuilder,
		'Srec' : srecBuilder,
		'Binary' : binaryBuilder})
	
	env.AddMethod(print_size, 'Size')

def generate(env, **kw):
	setup_gnu_tools(env, 'avr-')

def exists(env):
	return env.Detect('avr-gcc')