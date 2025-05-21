## nestPython


*"what if python, with braces, one line?"*

# SETUP

Install nestPython by executing the following:
```bash
$ pip install nestpython
```
After importing;

- In order to transpile a string from nestPython to python, use `nestpython.ncompile(str)`.
- In order to execute a nestPython string, use `nestpython.nexec(str)`.
-  To transpile files and directories, use the `nestpython.files` module:
	-  `nestpython.files.ncompile(file)` transpiles the specified file to a string.
    -  `nestpython.files.ncompile_to(file)` transpiles the specified file to a new file.
	-  `nestpython.files.nexec(file)` executes the specified file.
    -  `nestpython.files.build(dir, new_dir)` transpiles a directory.
    -  arguments can be provided:
		- `indent_amount=1`: determines the indentation increment in the resulting python file.
        - `transfer_other_files=True`: determines whether non-.npy (or .npx) files should be copied into the build directory.
        - `replace_previous=False`: determines whether already built files should be replaced.
        - `erase_dir:bool=None`: determines whether the previously built directory should be completely erased. If not specified, you will be asked to specify in the console.
        - `cythonic:bool=None`: determines if code should be perceived as nestCython or nestPython.
        - `tokenlog=False`: determines if tokenization progress should be logged.
        - `new_file:str=None`: determines where to compile a source file. Reverts to the original filename with a .py(x) extension if unspecified.

Alternatively, importing nestPython files directly after importing `nestpython.imports` or the entire library into a normal python file works too.

Use `.npy` for nestPython files, `.npx` for nestCython files.

# FEATURING:
## braces

Use `{`, `;` and `}` instead of indentation - indentation and newline characters in source files will be ignored. e.g.:

```nestpython
n = input('Enter Number: ');
if (n % 2 == 0) {
	print('n is even')
} else {
	print('n is odd')
}
```

Use `~{` as a shorthand for `while True {`. 

## syntactical changes

Several keywords are altered:

|  Python  | nestPython | Python  | nestPython |
|:--------:|:----------:|:-------:|:----------:|
|  `def`   |    `:=`    |  `del`  |    `~>`    |
| `return` |    `=>`    | `yield` |    `:>`    |
|   `in`   |    `->`    |  `and`  |    `&&`    |
| `not in` |    `!>`    |  `or`   |   `\|\|`   |
|   `is`   |    `=&`    |  `:=`   |    `<-`    |
| `is not` |   `!=&`    | `case`  |    `?`     |
| `lambda` |    `;=`    |   `;`   |    `,,`    |
|   `->`   |    `>:`    |  `//`   |    `~/`    |
|  `+= 1`  |    `++`    | `-= 1`  |    `--`    |
|   `{`    |    `-{`    |   `}`   |    `}-`    |

A variable like `return` will be replaced with `return_` on transpilation. using `pass` is never required, do-nothing braces can be left empty. 
One-line functions can still be written with colons: `:= foo(): => bar`, same for if-else and for statements.

Cython keywords are also altered for `.npx`:

| Cython  | nestCython |
|:-------:|:----------:|
| `cdef`  |    `$=`    |
| `cpdef` |   `~$=`    |

Strings or ternaries do not have to be one-line; if they are not, you can use `\ ` and `#` to reserve whitespace as follows:
```
'string \
continues here'
```

is equivalent to

```
'string continues here'
```

and transpiles to a python string with the newline character ignored.
This can be used to explicitly reserve whitespace before the newline character.

Same thing can be done with the `#` character outside of a string:

```nestpython
a if b #
else c
```
is equivalent to
```nestpython
a if b else c
```

The `#` is ignored by the transpiler.


## comments

- For block comments, use `/*`, `*/`.
- For line comments, use `//`.
- Block and line comments will be ignored during transpilation.
- For comments that need to be cpiled into python ones, use `/|`, `|/`.

## macros

- Use `# (name of the macro) #!(what it stands for)!#` to define a macro.
- Macros are only accessible within the nesting they were defined in.
- Use `#~ (name of the macro) ~#` to undefine the macro.
- Use `#? (name of the macro) ?#` to get a boolean representing whether the macro is defined.
- Use `$(name of the macro)` to use the macro.
- Macros that are closer to the nesting called are prioritized.

*(to be continued)*

---
github : https://github.com/svntythsnd/nestpy 
  
pypi : https://pypi.org/project/nestpython
