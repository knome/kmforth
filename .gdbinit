
# user dump datastack
define udds
  print ((void **)datastack)[0]@20
end

# user dump datastack index
define uddi
  print ($r14-(unsigned long long)datastack)
end

# user dump callstack
define udcs
  print ((void **)callstack)[0]@20
end

# user callstack index
define udci
  print ($r15-(unsigned long long)callstack)
end
