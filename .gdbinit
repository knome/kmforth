
# user dump datastack
define udds
  print ((void **)datastack)[0]@(($r14-(unsigned long long)datastack)/8)
end

# user dump datastack index
define uddi
  print ($r14-(unsigned long long)datastack)/8
end

# user dump callstack
define udcs
  print ((void **)callstack)[0]@(($r15-(unsigned long long)callstack)/8)
end

# user callstack index
define udci
  print ($r15-(unsigned long long)callstack)/8
end

define unext
  print ""
  stepi
  udds
  uddi
  udcs
  udci
end
