module Main where

import Algebra.Graph (edges, vertexList, Graph)
import Algebra.Graph.ToGraph (postSet)
import System.CPUTime
import Data.Set (size)

completeGraph :: Int -> [(Int, Int)]
completeGraph n = [(i, j) | i <- [1..n], j <- [1..n], i > j]

completeAlgGraph :: Int -> Graph Int
completeAlgGraph = edges . completeGraph

edgeCount :: Graph Int -> Int
edgeCount g = foldr (\x r -> size (postSet x g) + r) 0 (vertexList g)

measureTime :: IO a -> IO ()
measureTime action = do
    start <- getCPUTime
    _ <- action
    end <- getCPUTime
    let diff = fromIntegral (end - start) / (1e12 :: Double)
    putStrLn $ "Elapsed: " ++ show diff ++ "s"

main :: IO ()
main =
  measureTime (print $ edgeCount (completeAlgGraph 200))
