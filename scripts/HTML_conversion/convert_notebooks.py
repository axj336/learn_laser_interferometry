import os
import datetime
import shutil
import re
import subprocess
import fileinput
import sys
from jinja2 import Template
import toc


clean_name = lambda x: x[3:].replace("_", " ").replace(".ipynb", "")

# Walk into directories in filesystem
# Ripped from os module and slightly modified
# for alphabetical sorting
#
def sortedWalk(top, topdown=True, onerror=None):
    from os.path import join, isdir, islink
 
    names = os.listdir(top)
    names.sort()
    dirs, nondirs = [], []
 
    for name in names:
        if isdir(os.path.join(top, name)):
            dirs.append(name)
        else:
            nondirs.append(name)
 
    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        path = join(top, name)
        if not os.path.islink(path):
            for x in sortedWalk(path, topdown, onerror):
                yield x
    if not topdown:
        yield top, dirs, nondirs

def doc_path(relpath, i, chapter, j=None, section=None, k=None, notebook=None):

	chapter = chapter.replace(" ", "_")
	
	if section !=None:
		section = section.replace(" ", "_")
	if notebook !=None:
		notebook = notebook.replace(" ", "_")

	if notebook != None:
		path = os.path.join(relpath, "{i:02d}_{chapter}/{j:02d}_{section}/{k:02d}_{notebook}.php")
		return path.format(i=i, j=j, k=k, chapter=chapter, section=section, notebook=notebook)
	else:
		if section != None:
			path = os.path.join(relpath, "{i:02d}_{chapter}/{j:02d}_{section}/index.php")
			return path.format(i=i, j=j, chapter=chapter, section=section)
		else:
			path = os.path.join(relpath, "{i:02d}_{chapter}/index.php")
			return path.format(i=i, chapter=chapter)
			
def make_toc(wdir, relpath, _toc):
	
	rtn = "\n"
	rtn += "<ul>\n"
	rtn += "  <li class=\"sep\">\n"
	rtn += "    <a title='Online material to learn laser interferometry with Finesse' "
	rtn += "href='{0}/index.php'>Learn Home</a>\n".format(relpath)
	rtn += "  </li>\n"
	
	for i, chapter in enumerate(_toc):
		i += 1
		
		path = doc_path(relpath, i, chapter)
		rtn += "    <li class=\"sep\"><p>{0} {1}</p>\n".format(i, chapter, path)
		rtn += "    <ul>\n"
		rtn += "      <li class=\"sep\">\n"
		rtn += "        <a href='{2}'>{0} {1} Home</a>\n".format(i, chapter, path)
		rtn += "      </li>\n"
	
		for j, section in enumerate(_toc[chapter]):
			j += 1
			
			path = doc_path(relpath, i, chapter, j, section)
			rtn += "      <li class=\"sep\"><a href='{3}'>{0}.{1} {2}</a></li>\n".format(i, j, section, path)
			
		rtn += "    </ul>\n"		
		rtn += "    </li>\n"
	
	rtn += "</ul>\n"		
	
	return rtn
	
def make_chapter_toc(_chapter, wdir, relpath, _toc):
	rtn = ""
	
	for i, chapter in enumerate(_toc):
		i += 1

		if chapter == _chapter:
			rtn += "<h2>{0} {1}</h2>".format(i,chapter)
			rtn += "<ul style=\"list-style-type: none;\">"
			for j, section in enumerate(_toc[chapter]):
				j += 1
			
				path = doc_path(relpath, i, chapter, j, section)
				rtn += "   <li class=\"sep\"><a href='{3}'>{0}.{1} {2}</a></li>".format(i, j, section, path)
			
	
	rtn += "</ul>"		
	
	return rtn
	
	
def make_section_toc(_chapter, _section, wdir, relpath, _toc):
	rtn = ""
	
	for i, chapter in enumerate(_toc):
		i += 1
		
		if chapter == _chapter:
			rtn += "<h2>{0} {1}</h2>".format(i,chapter)
			for j, section in enumerate(_toc[chapter]):
				j += 1
				
				if section == _section:
					rtn += "<h3>{0}.{1} {2}</h3>".format(i,j,section)
					rtn += "<ul style=\"list-style-type: none;\">"
					for k, notebook in enumerate(_toc[chapter][section]):
						k += 1
						
						path = doc_path(relpath, i, chapter, j, section, k, notebook)
						rtn += "   <li class=\"sep\"><a href='{4}'>{0}.{1}.{2} {3}</a></li>".format(i,j,k, notebook, path)
	
	rtn += "</ul>"		
	
	return rtn

def html_redirect(location):
	return '''<html>
<head>
<meta http-equiv="refresh" content="5;url={0}" />
</head>
This content has moved to <a href="{0}">{0}</a>. You will be redirected to in 5 seconds.
</html>'''.format(location)


p = re.compile("^\d{2}_")

cwd = os.getcwd()

stamp = datetime.datetime.now().strftime("%Y_%M_%d_%H:%M:%S")

docwd = os.path.join(cwd, "html")
includedir = os.path.join(cwd, "include")
scriptsdir = os.path.realpath('../')
dir_prefix = '/learn'

for _dir in [docwd, includedir]:
	if os.path.exists(_dir):
		shutil.rmtree(_dir)
	os.mkdir(_dir)

ignore = [".git", ".ipynb_checkpoints", "scripts"]

print('docwd: '+str(docwd))
print('scriptsdir: '+str(scriptsdir))
	
try:
	os.chdir("../../")

	_toc = toc.get_toc()
	
	wd = os.getcwd()
	#shutil.copytree(os.path.join(wd,"images"), os.path.join(docwd,"images"))
	
	# Make TOC php file
	with open(os.path.join(includedir,"learn_toc.php"), "w") as ofile:
		ofile.write('<!--- Begin LEARN_TOC (this content is autogenerated) -->')
		ofile.write("<li>"
					+"<p>Learn</p>\n")
		ofile.write(make_toc(cwd, dir_prefix, _toc))
		ofile.write('\n<!--- End LEARN_TOC -->')

	for (path, folders, files) in os.walk("."):
		#for (path, folders, files) in sortedWalk("."):
		folders.sort()
		files.sort()
		if any(i in path for i in ignore):
			continue
		(parent, curfolder) = os.path.split(path)
		parfolder = os.path.split(parent)[1]
		print("** Current Folder : {}".format(curfolder))
		if parfolder == ".":
			cursection = None
			curchapter = clean_name(curfolder)
		else:
			cursection = clean_name(curfolder)
			curchapter = clean_name(parfolder)
			
		if not p.match(curfolder) and curfolder != ".":
			continue
		
		if not os.path.exists(os.path.join(docwd, path)):
			os.mkdir(os.path.join(docwd, path))

		os.chdir(os.path.join(docwd, path))
		
		for f in files:
			if f.startswith("."):
				continue
				
			# If basic text file render with the simple
			# jinja 2 template (which renders a php template)
			if ((f == "index.txt" and curfolder != ".")
				or (f == "main.txt" and curfolder == ".")):
				
				if cursection is None:
					if curchapter is None:
						title = " "
					else:
						title = "{0} ".format(curchapter)
				else:
					title  = "{0} ".format(cursection)

				content = ""
				with fileinput.FileInput(os.path.join(wd,path,f)) as ifile:
					for line in ifile:
						if line.strip() == "%%%%TOC_REPLACE%%%%":
							if cursection is None:
								content += make_chapter_toc(curchapter, cwd, os.path.relpath(docwd), _toc)
							else:
								content += make_section_toc(curchapter, cursection, cwd, os.path.relpath(docwd), _toc)
						else:
							content += line
				with open(os.path.join(cwd,'non_notebook.php.j2'),'r') as f:
					template = Template(f.read())
				with open("index.php", "w") as ofile:
					ofile.write(template.render(title=title,content=content))
				with open('index.html','w') as ofile:
					ofile.write(html_redirect('index.php'))
							
			elif not f.endswith(".ipynb") and curfolder != ".":
				shutil.copy(os.path.join(wd, path, f), ".")
			
			# Else convert into a jupyter notebook.
			# We can't do a simple jinja render
			# and this relies on jupyter-nbconvert
			# being installed and at least version 6.
			elif curfolder != ".":
				# convert notebook to HTML
				
				shutil.copy(os.path.join(wd, path, f), ".")
				# Don't actually need that file
				
				subprocess.call(["jupyter-nbconvert", f, "--to", "HTML",
								"--TemplateExporter.extra_template_basedirs="+str(scriptsdir),
				                 "--template", "gwoptics"])
				
				# clean up
				os.remove(f)
				shutil.move(f[:-5]+'html', f[:-5]+'php')
				with open(f[:-5]+'html','w') as ofile:
					ofile.write(html_redirect(f[:-5]+'php'))
				
		os.chdir(wd)

	print('Conversion complete.')
	
	def ensure_trailing(stringin):
		return stringin.strip().rstrip('/')+'/'

	def mymove(dir1,dir2):
		dir1 = ensure_trailing(dir1)
		dir2 = ensure_trailing(dir2)

		args = ["cp", "-r", dir1+'*', dir2]
		args_str = ' '.join([str(_) for _ in args])
		
		print('Executing: '+args_str)
		p = subprocess.call(args_str,shell=True)
		if p != 0:
			print('cp failed, trying with sudo')
			args.insert(0,'sudo')
			p = subprocess.call(args_str,shell=True)
		if p == 0:
			print('Moved.')
		else:
			print('Failed')

	phpdir = os.path.realpath(
				os.path.join('/var/www/gwoptics-web',
							dir_prefix.strip('/')))
	resp = input('Would you like to deploy to '+phpdir+' [y/n]')
	if resp.lower().strip() in ['y','yes']:
		mymove(docwd,phpdir)

	phpinclude = os.path.realpath(os.path.join(phpdir,'../include/'))
	resp = input('Would you like to deploy to '+phpinclude+' [y/n]')
	if resp.lower().strip() in ['y','yes']:
		mymove(includedir,phpinclude)

finally:
	os.chdir(cwd)
