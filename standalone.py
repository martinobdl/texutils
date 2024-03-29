import argparse
from colorama import Fore, Back, Style
import subprocess
import os
import glob
import pathlib


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


parser = argparse.ArgumentParser()

parser.add_argument('-i', metavar='in-file', type=argparse.FileType('rt'), nargs='?')
parser.add_argument('-I', metavar='in-directory', type=dir_path, nargs='?')
parser.add_argument('-o', metavar='out-dir', type=dir_path, required=True)
parser.add_argument('-f', action='store_true', help="force recompile")
parser.add_argument('-c', action='store_true', help="run pdfcrop")


args = parser.parse_args()

with open("standalone.tex", "rt") as f:
    first_part = f.readlines()[:-2]

def file_content_and_pdf(name):
    file_content = "".join(first_part) + "\\input{" + name + "}\n" + "\\end{document}"
    basename = os.path.splitext(os.path.basename(name))[0]
    outfile = os.path.join(args.o, basename+'.pdf')
    return file_content, outfile

ORIGINAL_IN_FILE = []
IN_FILES = []
FILE_CONTENTS = []
OUT_FILES_PDF = []

if args.i is not None and args.I is not None:
    raise Exception("You cannot pass both -i and -I as arguments")

if args.i is not None:
    name = args.i.name
    ORIGINAL_IN_FILE = [name]
    file, pdf_name = file_content_and_pdf(name)
    FILE_CONTENTS = [file]
    IN_FILES = ["/tmp/tmp.tex"]
    OUT_FILES_PDF = [pdf_name]
else:
    directory_in = dir_path(args.I)
    ORIGINAL_IN_FILE = glob.glob(os.path.join(args.I, "*.tex"))
    for i,tex in enumerate(ORIGINAL_IN_FILE):
        file, pdf_name = file_content_and_pdf(tex)
        FILE_CONTENTS.append(file)
        IN_FILES.append("/tmp/tmp"+str(i)+".tex")
        OUT_FILES_PDF.append(pdf_name)
    #breakpoint()

for i,tmp_file_name in enumerate(IN_FILES):
    with open(tmp_file_name, "w") as f:
        f.writelines(FILE_CONTENTS[i])


if __name__ == "__main__":
    for i,(tmp_tex_file, out_pdf, original_tex) in enumerate(zip(IN_FILES, OUT_FILES_PDF, ORIGINAL_IN_FILE)):
        if os.path.exists(out_pdf) and os.path.getmtime(original_tex) < os.path.getmtime(out_pdf) and args.f is False:
            print(Fore.YELLOW + "{} already comliled".format(out_pdf))
            print(Style.RESET_ALL)

        else:
            subprocess.run(['pdflatex', '--enable-write18', '--extra-mem-top=100000000',
                            '--synctex=1', '-output-directory=/tmp', '-jobname=foo'+str(i),
                            tmp_tex_file, ],
                           check=True, text=True)

            if not args.c:
                subprocess.run(['mv', '/tmp/foo'+str(i)+'.pdf', out_pdf],
                                check=True, text=True)
            else:
                subprocess.run(["pdfcrop", "--margins", "7", "/tmp/foo"+str(i)+".pdf"], check=True, text=True)
                subprocess.run(['mv', '/tmp/foo'+str(i)+'-crop.pdf', out_pdf],
                                check=True, text=True)
                print(Fore.RED + "{} cropped".format(out_pdf))
                print(Style.RESET_ALL)


            print(Fore.GREEN + "saved in {}".format(out_pdf))
            print(Style.RESET_ALL)

