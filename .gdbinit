
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

define wat
  stepi
  x/i $rip
end

define unext
  print "STEPPING"
  stepi
  print "DATASTACK-INDEX"
  uddi
  set $showds = ($r14-(unsigned long long)datastack)/8
  if $showds > 0
    print "DATASTACK"
    udds
  end
  if $showds == 0
    print "DATASTACK-EMPTY"
  end
  if $showds < 0
    print "DATASTACK-UNDERFLOWING"
  end
  print "CALLSTACK-INDEX"
  udci
  set $showcs = ($r15-(unsigned long long)callstack)/8
  if $showcs > 0
    print "CALLSTACK"
    udcs
  end
  if $showcs == 0
    print "CALLSTACK-EMPTY"
  end
  if $showcs < 0
    print "CALLSTACK-UNDERFLOW"
  end
  print "PENDING-INSTRUCTION"
  x/i $rip
end
