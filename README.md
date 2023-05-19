
# Why

fun.

# What

It's forth, but not forth forth.

The syntax is lightly different.

Not a REPL. Compiled only.

No runtime name additions or changes.

There's a stack. Functions pop and push to it.

The stack value is a union of anything that fits in a 64 bit slot.

There is no type checking.

Good luck.

# How

``` bash
./tools/compile src/Example.code
```

this will create `a.out`

you will need `python3`, `nasm` and `ld` to compile code.
