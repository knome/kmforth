
# Why

fun.

# What

It's forth, but not forth forth.

Not a REPL. Compiled only.

No runtime name additions or changes.

Includes are modular (not text inserts) but the namespace is flat.

Functions and macros can be defined in any order.

If your macros expand recursively infinitely, don't.

There's a datastack. Functions pop and push to it.

There's a callstack. Return addresses and locals get shunted on and off it.

The stack value is a union of anything that fits in eight bytes.

There is no type checking.

Good luck.

# How

everything assumes you're using `bash` on `linux`

run this from the project root

``` bash
./tools/compile src/Example.code
```

this will create `a.out`

you will need `python3`, `nasm` and `ld` to compile code.

# Language Reference

look in LANGUAGE-REFERENCE
