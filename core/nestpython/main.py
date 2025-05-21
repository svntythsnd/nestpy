def ncompile(code:str, *, indent_amount:int=1, cythonic:bool=False, tokenlog:bool=False, filename:str=None):
  import contextlib
  import re
  from collections.abc import Iterable
  from enum import Enum

  # canonicalize line breaks

  code = code.replace('\r\n', '\n').replace('\r', '\n')

  # ----------------- #
  #      TOKENS       #
  # ----------------- #

  def unpack(list):
    out = []
    for arg in list:
      match arg:
        case Iterable():
          out += unpack(arg)
        case _:
          out.append(arg)
    return out

  TokenTypes = Enum('TokenTypes', [
    'SYNTACTICAL', 'MULTILINE',
    'INDENTED', 'MAP', 'CYTHON',
    'STRING', 'APPENDSUB', 'SHORTHAND',
    'MACROS', 'ESCAPEMENT', 'NEWLINELIKE',
    'EXTRA'
  ])

  id = 0

  class Token:

    def __init__(self, symb='', *types, setID=None):
      self.symb = symb
      self.types = unpack(types)
      if TokenTypes.SHORTHAND in self.types and TokenTypes.MAP not in self.types:
        self.types.append(TokenTypes.MAP)
      if setID is None:
        nonlocal id
        id += 1
      else:
        id = setID
      self.id = id

    # TOKENIZATION ALGORITHM

  def anonToken(symb, *types):
    return Token(symb, *types, setID=-1)

  tokens_parsed = 0
  string_parsed = 0

  def tokenize(string, tokens: list[Token], buffer, tokenlog, filename):
    nonlocal string_parsed
    nonlocal tokens_parsed
    tokenized = []
    i = 0
    j = 0
    def update(token):
      nonlocal tokenized
      nonlocal string
      nonlocal tokenlog
      nonlocal string_parsed
      nonlocal tokens_parsed
      tokenized.append(token)
      string_parsed += len(token.symb)
      tokens_parsed += 1
      if tokenlog:
        print(f'tokenmatch \u2116{tokens_parsed}; {string_parsed / len(string) * 100:.2f}% of string{f" {filename}" if filename is not None else ""} parsed')
    while i + j < len(string):
      for token in tokens:
        F = (i + j - buffer >= 0)
        if match := re.match(
            fr'[\s\S]{{{buffer}}}{token.symb}' if F else token.symb,
            string[i + j - buffer:] if F else string, re.M):
          match_string = match.group()[buffer:] if F else match.group()
          if string[i:i + j] != '':
            update(anonToken(string[i:i + j]))
          update(Token(match_string, token.types, setID=token.id))
          i += j + len(match_string)
          j = -1
          break
      j += 1
    if i < len(string):
      update(anonToken(string[i:]))
    return tokenized

  # TOKEN DECLARATIONS

  def linesafe(regex):
    return r'\n*'.join(regex)

  def sclund(regex):
    return r'\b' + linesafe(regex) + r'_*\b'

  macros = {}

  class Tokens:
    escapeEscaped = Token(r'\\\\', TokenTypes.ESCAPEMENT)
    escapeNewline = Token(r'\\\n', TokenTypes.INDENTED, TokenTypes.NEWLINELIKE)
    escape = Token(r'\\', TokenTypes.ESCAPEMENT)
    multilineStringDouble = Token(r'(?<!\\)"""', TokenTypes.STRING)
    multilineStringSingle = Token(r"(?<!\\)'''", TokenTypes.STRING)
    stringDouble = Token(r'"', TokenTypes.STRING)
    stringSingle = Token(r"'", TokenTypes.STRING)
    dictIndentLeft = Token(r'-{', TokenTypes.MAP)
    dictIndentRight = Token(r'}-', TokenTypes.MAP)
    indentLeftDouble = Token(r'{\n*{')
    indentRightDouble = Token(r'}\n*}')
    indentSelfClose = Token(r'{\s*(\/\/.*\n\s*|\/\*[\s\S]\*\/\s*)*}', TokenTypes.INDENTED, TokenTypes.SYNTACTICAL)
    indentNoColonSelfClose = Token(r'~{\s*(\/\/.*\n\s*|\/\*[\s\S]\*\/\s*)*}', TokenTypes.INDENTED, TokenTypes.SYNTACTICAL)
    indentLeftNoColon = Token(r'~{', TokenTypes.INDENTED, TokenTypes.SYNTACTICAL)
    indentLeft = Token(r'{', TokenTypes.INDENTED, TokenTypes.SYNTACTICAL)
    indentRight = Token(r'}', TokenTypes.INDENTED, TokenTypes.SYNTACTICAL)
    newline = Token(r'\n', TokenTypes.INDENTED, TokenTypes.MULTILINE, TokenTypes.NEWLINELIKE)
    returnShorthand = Token(linesafe(r'=>'), TokenTypes.SHORTHAND)
    yieldShorthand = Token(linesafe(r':>'), TokenTypes.SHORTHAND)
    nativeSemicolon = Token(linesafe(r',,'), TokenTypes.MAP)
    nativeAssignment = Token(linesafe(r'<-'), TokenTypes.MAP)
    incrementOperator = Token(r'\+\n*\+', TokenTypes.MAP)
    decrementOperator = Token(linesafe(r'--'), TokenTypes.MAP)
    andShorthand = Token(linesafe(r'&&'), TokenTypes.SHORTHAND)
    orShorthand = Token(r'\|\n*\|', TokenTypes.SHORTHAND)
    isShorthand = Token(linesafe(r'=&'), TokenTypes.SHORTHAND)
    isNotShorthand = Token(linesafe(r'!=&'), TokenTypes.SHORTHAND)
    cpdefShorthand = Token(r'~\n*\$\n*=', TokenTypes.SHORTHAND, TokenTypes.CYTHON)
    cdefShorthand = Token(r'\$\n*=', TokenTypes.SHORTHAND, TokenTypes.CYTHON)
    defShorthand = Token(r':\n*=(?!\n*>)', TokenTypes.SHORTHAND)
    returntypeShorthand = Token(linesafe(r'>:'), TokenTypes.SHORTHAND)
    inShorthand = Token(linesafe(r'->'), TokenTypes.SHORTHAND)
    notInShorthand = Token(linesafe(r'!>'), TokenTypes.SHORTHAND)
    delShorthand = Token(linesafe(r'~>'), TokenTypes.SHORTHAND)
    lambdaShorthand = Token(linesafe(r';='), TokenTypes.SHORTHAND)
    indentNewline = Token(r';', TokenTypes.INDENTED, TokenTypes.SYNTACTICAL)
    notShorthand = Token(r'!(?!=)', TokenTypes.SHORTHAND)
    andDeconflict = Token(sclund('and'), TokenTypes.APPENDSUB)
    orDeconflict = Token(sclund('or'), TokenTypes.APPENDSUB)
    cpdefDeconflict = Token(sclund('cpdef'), TokenTypes.APPENDSUB, TokenTypes.CYTHON)
    cdefDeconflict = Token(sclund('cdef'), TokenTypes.APPENDSUB, TokenTypes.CYTHON)
    notDeconflict = Token(sclund('not'), TokenTypes.APPENDSUB)
    isDeconflict = Token(sclund('is'), TokenTypes.APPENDSUB)
    defDeconflict = Token(sclund('def'), TokenTypes.APPENDSUB)
    lambdaDeconflict = Token(sclund('lambda'), TokenTypes.APPENDSUB)
    inDeconflict = Token(sclund('in'), TokenTypes.APPENDSUB)
    returnDeconflict = Token(sclund('return'), TokenTypes.APPENDSUB)
    yieldDeconflict = Token(sclund('yield'), TokenTypes.APPENDSUB)
    caseDeconflict = Token(sclund('case'), TokenTypes.APPENDSUB)
    delDeconflict = Token(sclund('del'), TokenTypes.APPENDSUB)
    passDeconflict = Token(sclund('pass'), TokenTypes.APPENDSUB)
    comment = Token(r'\/\*[\s\S]*?\*\/', TokenTypes.INDENTED)
    lineComment = Token(r'\/\/.*', TokenTypes.INDENTED)
    lineStatement = Token(r'\/\|.*?\|\/', TokenTypes.INDENTED)
    intDiv = Token(linesafe(r'~/'), TokenTypes.MAP)
    caseShorthand = Token(r'\?', TokenTypes.SHORTHAND)
    macroDefine = Token(r'#\s*[\w\n]+\s*#![\s\S]*?!#', TokenTypes.MACROS)
    macroUndefine = Token(r'#~\s*[\w\n]+\s*~#', TokenTypes.MACROS)
    macroIfdef = Token(r'#\?\s*[\w\n]*\s*\?#', TokenTypes.MACROS)
    macroAccess = Token(r'\$[\w\n]*', TokenTypes.MACROS)
    macro = Token('#', TokenTypes.SYNTACTICAL)

    # CONVERSION TOKEN MAPPING

  tokenMap = {
      Tokens.dictIndentLeft.id: '{',
      Tokens.dictIndentRight.id: '}',
      Tokens.nativeSemicolon.id: ';',
      Tokens.nativeAssignment.id: ':=',
      Tokens.andShorthand.id: 'and',
      Tokens.orShorthand.id: 'or',
      Tokens.notShorthand.id: 'not',
      Tokens.isShorthand.id: 'is',
      Tokens.isNotShorthand.id: 'is not',
      Tokens.defShorthand.id: 'def',
      Tokens.inShorthand.id: 'in',
      Tokens.caseShorthand.id: 'case',
      Tokens.notInShorthand.id: 'not in',
      Tokens.returnShorthand.id: 'return',
      Tokens.lambdaShorthand.id: 'lambda',
      Tokens.delShorthand.id: 'del',
      Tokens.incrementOperator.id: '+=1',
      Tokens.decrementOperator.id: '-=1',
      Tokens.cpdefShorthand.id: 'cpdef',
      Tokens.cdefShorthand.id: 'cdef',
      Tokens.yieldShorthand.id: 'yield',
      Tokens.intDiv.id: '//',
      Tokens.returntypeShorthand.id: '->'
  }

  def isF(token, ptoken):
    with contextlib.suppress(TypeError):
      return (TokenTypes.STRING in token.types) and (ptoken.symb[-1].lower() == 'f' or
                                                     ptoken.symb[-2:].lower() == 'fr')

  def isR(token, ptoken):
    with contextlib.suppress(TypeError):
      return (TokenTypes.STRING in token.types) and (ptoken.symb[-1].lower() == 'r' or
                                                     ptoken.symb[-2:].lower() == 'rf')

  def isEscape(token):
    with contextlib.suppress(TypeError):
      return (token.id == Tokens.escape.id and not compilable())

  def isEscapedEscape(token):
    with contextlib.suppress(TypeError):
      return token.id == Tokens.escapeEscaped.id and not compilable()

  def isNRawEscape(token):
    return isEscape(token) and not in_rstring

  def isNRawEscapedEscape(token):
    return isEscapedEscape(token) and not in_rstring

  compiled_code = ''
  indent_level = 0
  string_nesting = []
  def getStringType():
    return anonToken('') if len(string_nesting) == 0 else string_nesting[-1]
  fstring_nesting = 0
  in_multilineStringSingle = lambda: getStringType().id == Tokens.multilineStringSingle.id and in_string
  in_multilineStringDouble = lambda: getStringType().id == Tokens.multilineStringDouble.id and in_string
  in_stringSingle = lambda: getStringType().id == Tokens.stringSingle.id and in_string
  in_stringDouble = lambda: getStringType().id == Tokens.stringDouble.id and in_string
  in_fstring = False
  in_rstring = False
  in_multilineString = lambda: (in_multilineStringSingle() or
                                in_multilineStringDouble())
  in_string = False
  compilable = lambda: not in_string
  tokenList = lambda included=[]: [t for t in [k for h, k in Tokens.__dict__.items() if not h.startswith('__')] if (TokenTypes.CYTHON not in t.types or cythonic) and ((TokenTypes.EXTRA in t.types) == (t.id in included))]

  def string_compilable(token):
    match token.id:
      case Tokens.multilineStringSingle.id:
        return not in_multilineStringDouble()
      case Tokens.multilineStringDouble.id:
        return not in_multilineStringSingle()
      case Tokens.stringSingle.id:
        return not (in_multilineString() or in_stringDouble())
      case Tokens.stringDouble.id:
        return not (in_multilineString() or in_stringSingle())

  indent = ' ' * indent_amount
  buffer = 1
  tokens = tokenize(code, tokenList(), buffer, tokenlog, filename)
  compiling = True
  ptoken = Token()
  class breakout(Exception):
    pass

  def string_compile(token):
    nonlocal in_string
    if getStringType().id == token.id:
      string_nesting.pop()
    else:
      string_nesting.append(token)
    in_string = not in_string

  def compile(bufferToken):
    nonlocal compiled_code
    nonlocal indent_level
    nonlocal in_multilineStringSingle
    nonlocal in_multilineStringDouble
    nonlocal in_stringSingle
    nonlocal in_stringDouble
    nonlocal in_fstring
    nonlocal in_rstring
    nonlocal fstring_nesting
    nonlocal in_multilineString
    nonlocal in_string
    nonlocal compilable
    nonlocal indent
    nonlocal tokens
    nonlocal buffer
    nonlocal compiling
    nonlocal ptoken
    nonlocal cythonic
    try:
     for n, token in enumerate(tokens):
      ptoken = tokens[n - 1] if n > 0 else bufferToken
      if compilable():
        match token.id:
          case Tokens.comment.id | Tokens.lineComment.id:
            continue
          case Tokens.lineStatement.id:
            compiled_code += '#' + token.symb[2:-2].rstrip() + '\n' + indent * indent_level
            continue
      elif token.id == Tokens.comment.id:
        tokens = tokenize(token.symb[0], tokenList(), buffer,
                            tokenlog, filename) + tokenize(token.symb[1:], tokenList(), buffer,
                            tokenlog, filename) + tokens[n + 1:]
        raise breakout
      if in_string and not in_multilineString() and token.id == Tokens.escapeNewline.id:
        continue
      if token.id == Tokens.indentLeftDouble.id:
        if in_fstring:
          compiled_code += '{{'
          continue
        else:
          tokens = [Tokens.indentLeft]*2 + tokens[n + 1:]
          raise breakout
      if token.id == Tokens.indentRightDouble.id:
        if in_fstring:
          compiled_code += '}}'
          continue
        elif in_multilineString:
          compiled_code += token.symb
          continue
        else:
          tokens = [Tokens.indentLeft]*2 + tokens[n + 1:]
          raise breakout
      if token.id == Tokens.indentSelfClose.id:
        if compilable():
          compiled_code = (compiled_code.rstrip()
                           + f':\n{indent * (indent_level+1)}\
pass\n{indent * indent_level}')
          continue
        else:
          tokens = ([Tokens.indentLeft]
          + tokenize(token.symb[1:-1], tokenList(), buffer, tokenlog=tokenlog, filename=filename)
          + [Tokens.indentRight]
          + tokens[n + 1:])
          raise breakout
      if TokenTypes.MACROS in token.types and compilable():
       match token.id:
        case Tokens.macroDefine.id:
          macro = (token.symb.split('#', 2)[1].strip().replace('\n', ''), indent_level)
          sub = token.symb.split('#', 2)[2][1:-2]

          macros.update({macro: sub})
          continue
        case Tokens.macroUndefine.id:
          macro = (token.symb.split('#')[1][1:-1].strip().replace('\n', ''), indent_level)
          macros.pop(macro)
          continue
        case Tokens.macroIfdef.id:
          macro = token.symb.split('#')[1][1:-1].strip().replace('\n', '')
          truth = False
          for N in reversed(range(indent_level+1)):
            if (macro, N) in macros:
              truth = True
              break
          if compiled_code[-1] != ' ' and compiled_code[-1] != '\n':
            compiled_code += ' '
          compiled_code += str(truth) + ' '
          continue
        case Tokens.macroAccess.id:
          if compilable():
            macro = token.symb[1:].replace('\n', '')
            for N in reversed(range(indent_level+1)):
              if (nmacro := (macro, N)) in macros:
                macro = macros[nmacro]
                tokens = tokenize(macro, tokenList(), buffer, tokenlog=tokenlog, filename=filename) + tokens[n + 1:]
                raise breakout
            continue
          else:
            compiled_code += (token.symb if in_multilineString()
                              else token.symb.replace('\n', ''))
      if TokenTypes.STRING in token.types and string_compilable(token):
        if not isNRawEscape(ptoken):
          string_compile(token)
        in_fstring = in_string and isF(token, ptoken)
        in_rstring = in_string and isR(token, ptoken)
      if compilable():
       if fstring_nesting == 0:
        match token.id:
          case Tokens.indentLeft.id | Tokens.indentLeftNoColon.id:
            indent_level += 1
            compiled_code = compiled_code.rstrip()
            compiled_code += ((':' if token.id == Tokens.indentLeft.id
                              else (
                                f'\n{indent * (indent_level-1)}while True:'
                              )) + '\n' + indent * indent_level
                             )
          case Tokens.indentRight.id:
            indent_level -= 1
            for macro in list(macros):
              if int(macro[-1]) > indent_level:
                macros.pop(macro)
            compiled_code += '\n' + indent * indent_level
          case Tokens.indentNewline.id:
            compiled_code += '\n' + indent * indent_level
       elif token.id == Tokens.indentRight.id:
        fstring_nesting -= 1
        in_fstring = True
        in_string = True

      elif in_fstring:
        match token.id:
          case Tokens.indentLeft.id:
            in_fstring = False
            in_string = False
            fstring_nesting += 1
            compiled_code += token.symb
          case Tokens.indentRight.id:
            if tokens[n+1].id == token.id:
              compiled_code += token.symb * 2
              tokens = tokens[n+2:]
              raise breakout
      if (not (TokenTypes.SYNTACTICAL in token.types and compilable())
          and not (TokenTypes.MULTILINE in token.types and not in_multilineString())):

        mtoken = tokenMap[token.id] if (TokenTypes.MAP in token.types
                                        and compilable()) else token.symb
        if compilable():
          if TokenTypes.APPENDSUB in token.types:
            mtoken = mtoken.replace('\n','')
            mtoken += '_'
          if TokenTypes.SHORTHAND in token.types:
            mtoken = mtoken.replace('\n','')
            mtoken += ' '
            if compiled_code != '':
              if compiled_code[-1] != ' ' and compiled_code[-1] != '\n':
                compiled_code += ' '
          if TokenTypes.MAP in token.types:
            mtoken = mtoken.replace('\n', '')
        compiled_code += (mtoken.lstrip() if (
                           (
                             (
                               TokenTypes.INDENTED
                               in ptoken.types
                               and compilable()
                             ) or (
                               not in_multilineString()
                               and TokenTypes.NEWLINELIKE in ptoken.types
                             )
                           ) or (
                             TokenTypes.SHORTHAND in ptoken.types
                             and compilable()
                             )
                           ) else (
                             mtoken
                           )
                         )
     compiled_code += '\n'
     compiling = False
    except breakout:
      pass
  while compiling:
    compile(ptoken)
  return compiled_code


def nexec(code:str, indent_amount:int=1, *, cythonic:bool=False, tokenlog:bool=False, filename:str=None):
  exec(ncompile(code, indent_amount=indent_amount, cythonic=cythonic, tokenlog=tokenlog, filename=filename))
