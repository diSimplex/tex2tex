# tex2tex

A simple tool to transliterate TeX macros.

Inspired by [de-macro](https://www.ctan.org/tex-archive/support/de-macro).

This tool loads a collection of TeX macro mappings and replaces each macro
mapping while scanning a TeX document.

We use tex2tex to allow document development using
[ConTeXt](https://wiki.contextgarden.net/Main_Page) while enabling us to
ultimately publish in journals which require documents typeset using
[LaTeX2e](https://en.wikipedia.org/wiki/LaTeX).

## Problems

- diSimplex's use of ConTeXt embeds graphics using MetaFun. We need to use
  our code like tools to export the MetaPost into individual files and
  then run ConTeXt over these files producing a single PDF page containing
  the graphic. We then need to use `pdftops` to convert the pdf to eps.

- diSimplex's use of code capture. Does the code get kept in the LaTeX
  document or do we just use LaTeX tools to show the code inline?

- How do we specify the macros to be replaced? This will differ between
  both journals and documents.



## Resources

- [ConTeXt garden manuals](https://wiki.contextgarden.net/Documentation)

- [de-macro](https://www.ctan.org/pkg/de-macro)

- [AMS author resource center](https://www.ams.org/arc/)

- **Convert PDF to EPS**

    - [StackExchange: High quality pdf to
      eps](https://stackoverflow.com/questions/44736917/high-quality-pdf-to-eps)

    - [StackExchange: How to convert PDF to
      EPS?](https://tex.stackexchange.com/questions/20883/how-to-convert-pdf-to-eps)

    - [ConTeXtGraden: Sharing
      graphics](https://wiki.contextgarden.net/Sharing_graphics)