# paxmaker
Write PAX Files for PDFs created by wkhtmltopdf for insertion into LaTeX, using the pax package

This project solves a specific problem: When you need to include a PDF into a LaTeX document,
and the inserted PDF has internal links, and the inserted PDF was created by wkhtmltopdf.

Who would need to do that? Anyone who has HTML+CSS content they want to use inside a LaTeX workflow.

This is a Python project and it requires the PyPDF2 package. 
The steps to use it are as follows:

1. Convert your html file to pdf with wkhtmltopdf
2. Run paxmaker.py on the pdf (the program takes a single argument, the name of the pdf file)
3. In the LaTeX file in which you want this pdf inserted: load the 'pdfpages' and 'pax' packages,
and use a command like this where you want the inserted pdf to appear:

    \includepdf[pages=-]{pdfname}
    

The paxmaker.py file does for the wkhtmltopdf-generated pdfs 
what the pax java program does for normal pdfs.

links for more information:

----------------   ------------------------------------
wkhtmltopdf      : http://wkhtmltopdf.org/

pdfpages package : https://www.ctan.org/pkg/pdfpages

pax package      : https://www.ctan.org/pkg/pax

pypdf2           : https://pypi.python.org/pypi/PyPDF2

----------------   ------------------------------------

