
class Optimizer:
    
    def optimize( allfns, used, callgraph, startname, uniques ):
        notes = {}
        opted = {}
        
        recursive = set()
        
        callees = callgraph
        callers = {}
        for (k,vv) in callees.items():
            for v in vv:
                if v not in callers:
                    callers[v] = set()
                callers[v].add(k)
        
        pending = [(startname, NotStupidCoroutine(optimize_fn(
            notes     = notes             ,
            callees   = callees           ,
            callers   = callers           ,
            opted     = opted             ,
            allfns    = allfns            ,
            recursive = recursive         ,
            name      = startname         ,
            fn        = allfns[startname] ,
            uniques   = uniques           ,
        )))]
        
        pendingNames = { startname }
        
        while pending:
            name, optgn = pending[-1]
            needed = next( optgn, None )
            if needed == None:
                pendingNames.remove(pending[-1][0])
                pending.pop()
                if pending:
                    pending[-1][1].prepare_send(False)
            elif needed in opted:
                pending[-1][1].prepare_send(False)
            elif needed in pendingNames:
                pending[-1][1].prepare_send(True)
            else:
                pending.append( (needed,NotStupidCoroutine(optimize_fn(
                    notes     = notes          ,
                    callees   = callees        ,
                    callers   = callers        ,
                    opted     = opted          ,
                    allfns    = allfns         ,
                    recursive = recursive      ,
                    name      = needed         ,
                    fn        = allfns[needed] ,
                    uniques   = uniques        ,
                ))))
                pendingNames.add( needed )
        
        return opted
