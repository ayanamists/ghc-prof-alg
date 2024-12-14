# A small example for Issue 25573

I've succeeded in creating a smaller example with the following code:

```haskell
import Algebra.Graph (edges, vertexList, Graph)
import Algebra.Graph.ToGraph (postSet)
import System.CPUTime
import Data.Set (size)

edgeCount :: Graph Int -> Int
edgeCount g = foldr (\x r -> size (postSet x g) + r) 0 (vertexList g)
```

The `edgeCount` function is slow when profiling is off and fast when profiling
is on.

It's clear that, in the fast configuration, `toAdjacencyMap` is floated out,
whereas in the slow mode, it is not.

The fast configuration's core output:

```
-- RHS size: {terms: 142, types: 109, coercions: 10, joins: 1/6}
Main.$wedgeCount [InlPrag=[2]]
  :: Graph Int -> ghc-prim:GHC.Prim.Int#
[GblId[StrictWorker([!])],
 Arity=1,
 Str=<SL>,
 Unf=Unf{Src=<vanilla>, TopLvl=True,
         Value=True, ConLike=True, WorkFree=True, Expandable=True,
         Guidance=IF_ARGS [0] 729 0}]
Main.$wedgeCount
  = \ (g_s3lE :: Graph Int) ->
      let {
        x1_s3m4
          :: Algebra.Graph.AdjacencyMap.AdjacencyMap
               (Algebra.Graph.ToGraph.ToVertex (Graph Int))
        [LclId]
        x1_s3m4
          = scc<edgeCount>
            Algebra.Graph.ToGraph.$w$ctoAdjacencyMap
              @Int ghc-prim:GHC.Classes.$fOrdInt g_s3lE } in
      case scctick<edgeCount>
           letrec {
             $wgo_s3lz [InlPrag=[2], Occ=LoopBreaker, Dmd=SC(S,C(1,L))]
               :: ghc-prim:GHC.Prim.Int#
                  -> Data.IntSet.Internal.IntSet -> ghc-prim:GHC.Prim.Int#
                  ...
```

The `x1_s3m4` is the lifted term `toAdjacencyMap g`.

## Deeper analysis

To see what happened, I dumped the simplify process with `-ddump-simpl-trace`.
I wrote a script to capture all output with the prompt below to see the
intermediate simplified form of the `edgeCount` function.

```
==================== Simpl Trace ====================
tcww:no
  bndr: Main.edgeCount
  rhs:
```

I found that, in both the fast and slow configurations, `edgeCount` reaches the
following form. And then they diverge.

```
==================== Simpl Trace ====================
tcww:no
  bndr: Main.edgeCount
  rhs: \ (g_aSd :: Algebra.Graph.Graph GHC.Types.Int) ->
         scctick<edgeCount>
         Data.IntSet.Internal.foldrFB
           @GHC.Types.Int
           (\ (x_a13a :: GHC.Types.Int)
              (r_a13b [OS=OneShot] :: GHC.Types.Int) ->
              case case (Algebra.Graph.ToGraph.$fToGraphGraph_$cpostSet
                           @GHC.Types.Int
                           GHC.Classes.$fOrdInt
                           (GHC.Classes.$fOrdInt
                            `cast` ((GHC.Classes.Ord
                                       (Sym (Algebra.Graph.ToGraph.D:R:ToVertexGraph[0]
                                                 <GHC.Types.Int>_N)))_R
                                    :: GHC.Classes.Ord GHC.Types.Int
                                       ~R# GHC.Classes.Ord
                                             (Algebra.Graph.ToGraph.ToVertex
                                                (Algebra.Graph.Graph GHC.Types.Int))))
                           (x_a13a
                            `cast` (Sub (Sym (Algebra.Graph.ToGraph.D:R:ToVertexGraph[0]
                                                  <GHC.Types.Int>_N))
                                    :: GHC.Types.Int
                                       ~R# Algebra.Graph.ToGraph.ToVertex
                                             (Algebra.Graph.Graph GHC.Types.Int)))
                           g_aSd)
                        `cast` ((Data.Set.Internal.Set
                                   (Algebra.Graph.ToGraph.D:R:ToVertexGraph[0] <GHC.Types.Int>_N))_R
                                :: Data.Set.Internal.Set
                                     (Algebra.Graph.ToGraph.ToVertex
                                        (Algebra.Graph.Graph GHC.Types.Int))
                                   ~R# Data.Set.Internal.Set GHC.Types.Int)
                   of {
                     Data.Set.Internal.Bin bx_a1ZW ds1_a1ZX ds2_a1ZY ds3_a1ZZ ->
                       GHC.Types.I# bx_a1ZW;
                     Data.Set.Internal.Tip -> GHC.Types.I# 0#
                   }
              of
              { GHC.Types.I# x_a1ZJ ->
              case r_a13b of { GHC.Types.I# y_a1ZM ->
              GHC.Types.I# (GHC.Prim.+# x_a1ZJ y_a1ZM)
              }
              })
           (GHC.Types.I# 0#)
           (Algebra.Graph.foldg
              @Data.IntSet.Internal.IntSet
              @GHC.Types.Int
              Data.IntSet.Internal.Nil
              Data.IntSet.Internal.singleton
              Data.IntSet.Internal.union
              Data.IntSet.Internal.union
              g_aSd)
```


In the next step, the slow configuration replace `$cpostSet` with `$w$cpostSet`

```
==================== Simpl Trace ====================
tcww:no
  bndr: Main.edgeCount
  rhs: \ (g_aSa :: Algebra.Graph.Graph GHC.Types.Int) ->
         Data.IntSet.Internal.foldrFB
           @GHC.Types.Int
           (\ (x_a138 :: GHC.Types.Int)
              (r_a139 [OS=OneShot] :: GHC.Types.Int) ->
              join {
                $j_s3gN :: GHC.Prim.Int# -> GHC.Types.Int
                [LclId[JoinId(1)(Nothing)], Arity=1]
                $j_s3gN (x_a1Zz [OS=OneShot] :: GHC.Prim.Int#)
                  = case r_a139 of { GHC.Types.I# y_a1ZC ->
                    GHC.Types.I# (GHC.Prim.+# x_a1Zz y_a1ZC)
                    } } in
              case (Algebra.Graph.ToGraph.$w$cpostSet
                      @GHC.Types.Int
                      GHC.Classes.$fOrdInt
                      (x_a138
                       `cast` (Sub (Sym (Algebra.Graph.ToGraph.D:R:ToVertexGraph[0]
                                             <GHC.Types.Int>_N))
                               :: GHC.Types.Int
                                  ~R# Algebra.Graph.ToGraph.ToVertex
                                        (Algebra.Graph.Graph GHC.Types.Int)))
                      g_aSa)
                   `cast` ((Data.Set.Internal.Set
                              (Algebra.Graph.ToGraph.D:R:ToVertexGraph[0] <GHC.Types.Int>_N))_R
                           :: Data.Set.Internal.Set
                                (Algebra.Graph.ToGraph.ToVertex
                                   (Algebra.Graph.Graph GHC.Types.Int))
                              ~R# Data.Set.Internal.Set GHC.Types.Int)
              of {
                Data.Set.Internal.Bin bx_a1ZM ds1_a1ZN ds2_a1ZO ds3_a1ZP ->
                  jump $j_s3gN bx_a1ZM;
                Data.Set.Internal.Tip -> jump $j_s3gN 0#
              })
           lvl_s30v
           (Algebra.Graph.foldg
              @Data.IntSet.Internal.IntSet
              @GHC.Types.Int
              Data.IntSet.Internal.Nil
              Data.IntSet.Internal.singleton
              Data.IntSet.Internal.union
              Data.IntSet.Internal.union
              g_aSa)
```

The fast configuration, while I don't know exactly what happen, seems to inline
the definition of `$cpostSet`, and make some simplifications.

```
==================== Simpl Trace ====================
tcww:no
  bndr: Main.edgeCount
  rhs: \ (g_aSd :: Algebra.Graph.Graph GHC.Types.Int) ->
         scctick<edgeCount>
         Data.IntSet.Internal.foldrFB
           @GHC.Types.Int
           (\ (x_a13a :: GHC.Types.Int)
              (r_a13b [OS=OneShot] :: GHC.Types.Int) ->
              let {
                f_a35L
                  :: Algebra.Graph.AdjacencyMap.AdjacencyMap
                       (Algebra.Graph.ToGraph.ToVertex
                          (Algebra.Graph.Graph GHC.Types.Int))
                     -> Data.Set.Internal.Set
                          (Algebra.Graph.ToGraph.ToVertex
                             (Algebra.Graph.Graph GHC.Types.Int))
                [LclId,
                 Unf=Unf{Src=<vanilla>, TopLvl=False,
                         Value=False, ConLike=False, WorkFree=False, Expandable=False,
                         Guidance=IF_ARGS [] 196 60}]
                f_a35L
                  = scctick<postSet>
                    let {
                      f1_a35M
                        :: Data.Map.Internal.Map
                             (Algebra.Graph.ToGraph.ToVertex
                                (Algebra.Graph.Graph GHC.Types.Int))
                             (Data.Set.Internal.Set
                                (Algebra.Graph.ToGraph.ToVertex
                                   (Algebra.Graph.Graph GHC.Types.Int)))
                           -> Data.Set.Internal.Set
                                (Algebra.Graph.ToGraph.ToVertex
                                   (Algebra.Graph.Graph GHC.Types.Int))
                      [LclId,
                       Unf=Unf{Src=<vanilla>, TopLvl=False,
                               Value=False, ConLike=False, WorkFree=False, Expandable=False,
                               Guidance=IF_ARGS [] 156 60}]
                      f1_a35M
                        = scctick<findWithDefault>
                          case (x_a13a
                                `cast` (Sub (Sym (Algebra.Graph.ToGraph.D:R:ToVertexGraph[0]
                                                      <GHC.Types.Int>_N))
                                        :: GHC.Types.Int
                                           ~R# Algebra.Graph.ToGraph.ToVertex
                                                 (Algebra.Graph.Graph GHC.Types.Int)))
                               `cast` (Sub (Algebra.Graph.ToGraph.D:R:ToVertexGraph[0]
                                                <GHC.Types.Int>_N)
                                       :: Algebra.Graph.ToGraph.ToVertex
                                            (Algebra.Graph.Graph GHC.Types.Int)
                                          ~R# GHC.Types.Int)
                          of nt_s3gQ
                          { __DEFAULT ->
                          letrec {
                            go8_a3gw [Occ=LoopBreaker]
                              :: Data.Map.Internal.Map
                                   (Algebra.Graph.ToGraph.ToVertex
                                      (Algebra.Graph.Graph GHC.Types.Int))
                                   (Data.Set.Internal.Set
                                      (Algebra.Graph.ToGraph.ToVertex
                                         (Algebra.Graph.Graph GHC.Types.Int)))
                                 -> Data.Set.Internal.Set
                                      (Algebra.Graph.ToGraph.ToVertex
                                         (Algebra.Graph.Graph GHC.Types.Int))
                            [LclId,
                             Arity=1,
                             Unf=Unf{Src=<vanilla>, TopLvl=False,
                                     Value=True, ConLike=True, WorkFree=True, Expandable=True,
                                     Guidance=IF_ARGS [30] 126 10}]
                            go8_a3gw
                              = \ (ds_a3gx
                                     :: Data.Map.Internal.Map
                                          (Algebra.Graph.ToGraph.ToVertex
                                             (Algebra.Graph.Graph GHC.Types.Int))
                                          (Data.Set.Internal.Set
                                             (Algebra.Graph.ToGraph.ToVertex
                                                (Algebra.Graph.Graph GHC.Types.Int)))) ->
                                  case ds_a3gx of {
                                    Data.Map.Internal.Bin bx_a3gF kx_a3gG x_a3gH l_a3gI r_a3gJ ->
                                      case nt_s3gQ of { GHC.Types.I# x#_a3gU ->
                                      case kx_a3gG
                                           `cast` (Sub (Algebra.Graph.ToGraph.D:R:ToVertexGraph[0]
                                                            <GHC.Types.Int>_N)
                                                   :: Algebra.Graph.ToGraph.ToVertex
                                                        (Algebra.Graph.Graph GHC.Types.Int)
                                                      ~R# GHC.Types.Int)
                                      of
                                      { GHC.Types.I# y#_a3gX ->
                                      join {
                                        $j_s3h3
                                          :: Data.Set.Internal.Set
                                               (Algebra.Graph.ToGraph.ToVertex
                                                  (Algebra.Graph.Graph GHC.Types.Int))
                                        [LclId[JoinId(0)(Nothing)]]
                                        $j_s3h3 = go8_a3gw l_a3gI } in
                                      join {
                                        $j_s3h4
                                          :: Data.Set.Internal.Set
                                               (Algebra.Graph.ToGraph.ToVertex
                                                  (Algebra.Graph.Graph GHC.Types.Int))
                                        [LclId[JoinId(0)(Nothing)]]
                                        $j_s3h4 = go8_a3gw r_a3gJ } in
                                      case GHC.Prim.<# x#_a3gU y#_a3gX of {
                                        __DEFAULT ->
                                          case GHC.Prim.==# x#_a3gU y#_a3gX of {
                                            __DEFAULT -> jump $j_s3h4;
                                            1# -> x_a3gH
                                          };
                                        1# -> jump $j_s3h3
                                      }
                                      }
                                      };
                                    Data.Map.Internal.Tip ->
                                      Data.Set.Internal.Tip
                                        @(Algebra.Graph.ToGraph.ToVertex
                                            (Algebra.Graph.Graph GHC.Types.Int))
                                  }; } in
                          go8_a3gw
                          } } in
                    \ (x1_a3gn
                         :: Algebra.Graph.AdjacencyMap.AdjacencyMap
                              (Algebra.Graph.ToGraph.ToVertex
                                 (Algebra.Graph.Graph GHC.Types.Int))) ->
                      f1_a35M
                        ((tick<adjacencyMap> x1_a3gn)
                         `cast` (Algebra.Graph.AdjacencyMap.N:AdjacencyMap[0]
                                     <Algebra.Graph.ToGraph.ToVertex
                                        (Algebra.Graph.Graph GHC.Types.Int)>_N
                                 :: Algebra.Graph.AdjacencyMap.AdjacencyMap
                                      (Algebra.Graph.ToGraph.ToVertex
                                         (Algebra.Graph.Graph GHC.Types.Int))
                                    ~R# Data.Map.Internal.Map
                                          (Algebra.Graph.ToGraph.ToVertex
                                             (Algebra.Graph.Graph GHC.Types.Int))
                                          (Data.Set.Internal.Set
                                             (Algebra.Graph.ToGraph.ToVertex
                                                (Algebra.Graph.Graph GHC.Types.Int))))) } in
              join {
                $j_s3hs :: GHC.Prim.Int# -> GHC.Types.Int
                [LclId[JoinId(1)(Nothing)], Arity=1]
                $j_s3hs (x_a1ZJ [OS=OneShot] :: GHC.Prim.Int#)
                  = case r_a13b of { GHC.Types.I# y_a1ZM ->
                    GHC.Types.I# (GHC.Prim.+# x_a1ZJ y_a1ZM)
                    } } in
              case (f_a35L
                      (Algebra.Graph.ToGraph.$w$ctoAdjacencyMap
                         @GHC.Types.Int GHC.Classes.$fOrdInt g_aSd))
                   `cast` ((Data.Set.Internal.Set
                              (Algebra.Graph.ToGraph.D:R:ToVertexGraph[0] <GHC.Types.Int>_N))_R
                           :: Data.Set.Internal.Set
                                (Algebra.Graph.ToGraph.ToVertex
                                   (Algebra.Graph.Graph GHC.Types.Int))
                              ~R# Data.Set.Internal.Set GHC.Types.Int)
              of {
                Data.Set.Internal.Bin bx_a1ZW ds1_a1ZX ds2_a1ZY ds3_a1ZZ ->
                  jump $j_s3hs bx_a1ZW;
                Data.Set.Internal.Tip -> jump $j_s3hs 0#
              })
           lvl_s30K
           (Algebra.Graph.foldg
              @Data.IntSet.Internal.IntSet
              @GHC.Types.Int
              Data.IntSet.Internal.Nil
              Data.IntSet.Internal.singleton
              Data.IntSet.Internal.union
              Data.IntSet.Internal.union
              g_aSd)
```

Note the term `(Algebra.Graph.ToGraph.$w$ctoAdjacencyMap @GHC.Types.Int
GHC.Classes.$fOrdInt g_aSd)` from

```
           case (f_a35L
                    (Algebra.Graph.ToGraph.$w$ctoAdjacencyMap
                        @GHC.Types.Int GHC.Classes.$fOrdInt g_aSd))
```

This term finally get float out.

## Other result

I'm not familiar with GHC, but the name `$w` seems to relate to the
"worker-wrapper" approach. So I tried to disable strictness analysis with
`-fno-strictness`. However, it behaves like the slow configuration.

I upload the simplify trace, with `*.log` is the output of `-ddump-simpl-trace`,
and `*.analysis.log` is the extracted intermediate form of `edgeCount` with
index and original line numbers.
