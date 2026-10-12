import Lake
open Lake DSL

package iks_core where
  version := v!"2.0.0"

@[default_target]
lean_lib IksNN where
  srcDir := "."
