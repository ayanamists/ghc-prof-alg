#!/usr/bin/env sh

cp configs/cabal.project.local.fast cabal.project.local
cabal clean
cabal run ghc-prof-alg > results/fast.log
