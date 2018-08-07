/*
 * MITx Grading Library Javascript Helper
 * https://github.com/mitodl/mitx-grading-library
 *
 * Copyright 2017-2018 Jolyon Bloomfield and Chris Chudzicki
 *
 * Modifies MathJax AsciiMath renderer to accept a variety of new functions
 * Also defines a preprocessor for further beautification
 *
 */

// Make sure that this script only loads once
if (window.MJxPrep) {
} else {
  // Define the preprocessor
  window.MJxPrep = function() {
    /*-----------------------------------------------------
         *This is the preprocessor, used for translating inputs
         *-----------------------------------------------------
         */
    this.fn = function(eqn) {
      try {
        return preProcessEqn(eqn)
      }
      catch (err) {
        return eqn
      }
    };
  };

  function preProcessEqn(eqn) {
    // Note that /pattern/flags is shorthand for a regex parser
    // g is global - makes all changes
    // log10(x) -> log_10(x)
    eqn = eqn.replace(/log10\(/g, "log_10(");
    // log2(x) -> log_2(x)
    eqn = eqn.replace(/log2\(/g, "log_2(");

    // Note that fact(x) renders as x!, while fact(n-1) renders as n-1! (not good!)
    // To make it look right, we need to use fact((n-1))
    // This means that fact(10) renders as (10)!, but that's pretty benign
    // Same applies to factorial
    var replace_fact = function(match, substr1, substr2) {
      if (substr2.length == 1)
        return substr1 + "(" + substr2 + ")";
      else
        return substr1 + "((" + substr2 + "))";
    };
    eqn = eqn.replace(
      /(fact|factorial)\((.+?)\)/g,
      replace_fact
    );
    eqn = replaceFunctionCalls(eqn, 'trans', function(funcName, args) {
      return '{:' + groupExpr(args[0]) + '^T:}'
    } )

    return eqn;
  }

  // Try to update AsciiMath
  function updateMathJax() {
    if (MathJax.InputJax.AsciiMath) {
      // Grab the AsciiMath object
      AM = MathJax.InputJax.AsciiMath.AM;

      // All of these new symbols are based on those appearing in the AsciiMath definitions
      // See https://github.com/asciimath/asciimathml/blob/master/ASCIIMathML.js
      // Add functions, including some edX functions that don't exist in AsciiMath
      AM.newsymbol({
        input: "arcsec",
        tag: "mi",
        output: "arcsec",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        func: true
      });
      AM.newsymbol({
        input: "arccsc",
        tag: "mi",
        output: "arccsc",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        func: true
      });
      AM.newsymbol({
        input: "arccot",
        tag: "mi",
        output: "arccot",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        func: true
      });
      AM.newsymbol({
        input: "arcsinh",
        tag: "mi",
        output: "arcsinh",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        func: true
      });
      AM.newsymbol({
        input: "arccosh",
        tag: "mi",
        output: "arccosh",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        func: true
      });
      AM.newsymbol({
        input: "arctanh",
        tag: "mi",
        output: "arctanh",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        func: true
      });
      AM.newsymbol({
        input: "arcsech",
        tag: "mi",
        output: "arcsech",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        func: true
      });
      AM.newsymbol({
        input: "arccsch",
        tag: "mi",
        output: "arccsch",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        func: true
      });
      AM.newsymbol({
        input: "arccoth",
        tag: "mi",
        output: "arccoth",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        func: true
      });
      AM.newsymbol({
        input: "re",
        tag: "mi",
        output: "Re",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        func: true
      });
      AM.newsymbol({
        input: "im",
        tag: "mi",
        output: "Im",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        func: true
      });
      AM.newsymbol({
        input: "conj",
        tag: "mover",
        output: "\xAF",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        acc: true
      });
      AM.newsymbol({
        input: "trace",
        tag: "mi",
        output: "Tr",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        func: true
      });

      // Add special functions: fact and factorial
      AM.newsymbol({
        input: "fact",
        tag: "mo",
        output: "fact",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        rewriteleftright: [ "", "!" ]
      });
      AM.newsymbol({
        input: "factorial",
        tag: "mo",
        output: "factorial",
        tex: null,
        ttype: AM.TOKEN.UNARY,
        rewriteleftright: [ "", "!" ]
      });

      // Ask MathJax to reprocess all input boxes, as saved answers may have rendered
      // before these definitions went through
      MathJax.Hub.Queue([
        "Reprocess",
        MathJax.Hub,
        "div.equation"
      ]);

      // No need to update again
      clearInterval(checkExist);
      console.log(
        "MITx Grading Library: Updated AsciiMath renderer definitions"
      );
    }
  }

  // Check for the AsciiMath object every 200ms
  var checkExist = setInterval(updateMathJax, 200);

  function findClosingBrace(expr, startIdx) {
    var braces = { "[": "]", "<": ">", "(": ")", "{": "}" };

    var openingBrace = expr[startIdx];

    var closingBrace = braces[openingBrace];

    if (closingBrace === undefined) {
      throw Error(
        expr +
          " does not contain an opening brace at position " +
          startIdx +
          "."
      );
    }

    var stack = 1;

    for (var j = startIdx + 1; j < expr.length; j++) {
      if (expr[j] === openingBrace) {
        stack += +1;
      } else if (expr[j] === closingBrace) {
        stack += -1;
      }
      if (stack === 0) {
        return j;
      }
    }

    // stack !== 0
    throw Error(
      expr + " has a brace that opens at position " +
        startIdx +
        " but does not close."
    );
  }

  /**
   * TODO: for splitting delimited lists, such as arguments of a function
   *
   * @param  {string} str [description]
   * @return {string}     [description]
   */
  function splitList(str) {
    return [str]
  }

  /**
   * Recursively replace each instance of 'funcName(<args>)' that occurs after
   * startingAt in a string with the return value of action(funcName, args)
   *
   * @param  {string} expr expression we're processing
   * @param  {string} funcName name of function we're looking for
   * @param  {function} action a callback with signature
   *                           (funcName: string, args: [str]) => string
   * @param  {?number} startingAt index after which replacements occur, defaults to 0
   * @return {[type]}          [description]
   */
  function replaceFunctionCalls(expr, funcName, action, startingAt) {
    // default value for startingAt
    var startingAt = startingAt ? startingAt : 0

    // Replace the first instance of 'funcName(<args>)'
    var funcStart = expr.indexOf(funcName, startingAt)
    if (funcStart < 0) {
      return expr
    }

    var openCallParens = funcStart + funcName.length
    var closeCallParens = findClosingBrace(expr, openCallParens)
    var argsString = expr.substring(openCallParens + 1, closeCallParens)
    var args = splitList(argsString)
    var newExpr = expr.substring(0, funcStart) +
      action(funcName, args) +
      expr.substring(closeCallParens + 1)

    // Recursively replace the remaining instances of 'funcName(<args>)'
    return replaceFunctionCalls(newExpr, funcName, action, funcStart + 1)

  }

  function groupExpr(expr) {
    var atomic = ['alpha', 'beta', 'chi', 'delta', 'Delta', 'epsi', 'varepsilon', 'eta', 'gamma', 'Gamma', 'iota', 'kappa', 'lambda', 'Lambda', 'lamda', 'Lamda', 'mu', 'nu', 'omega', 'Omega', 'phi', 'varphi', 'Phi', 'pi', 'Pi', 'psi', 'Psi', 'rho', 'sigma', 'Sigma', 'tau', 'theta', 'vartheta', 'Theta', 'upsilon', 'xi', 'Xi', 'zeta']
    var temp = expr.startsWith('hat') || expr.startsWith('vec')
      ? expr.substring(3)
      : expr

    if (temp.length == 1 || atomic.includes(temp)) {
      return expr
    }

    // If expression is already wrapped in parens or brackets, don't add extra
    if (expr.startsWith("(") || expr.startsWith("[")) {
      var closedAt = findClosingBrace(expr, 0)
      if (closedAt === expr.length - 1) {
        return expr
      }
    }
    return "(" + expr + ")"

  }

  // Hacky exports for test file since we aren't transpiling
  window.MJxPrepExports = {
    findClosingBrace: findClosingBrace,
    replaceFunctionCalls: replaceFunctionCalls,
    groupExpr: groupExpr,
    splitList: splitList
  }
}
