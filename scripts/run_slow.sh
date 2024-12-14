#!/usr/bin/env sh

cp configs/cabal.project.local.slow cabal.project.local
cabal clean
cabal run ghc-prof-alg > results/slow.log
