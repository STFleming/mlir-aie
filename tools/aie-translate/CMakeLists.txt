#
# This file is licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# (c) Copyright 2021 Xilinx Inc.

set(LLVM_LINK_COMPONENTS Support)

get_property(dialect_libs GLOBAL PROPERTY MLIR_DIALECT_LIBS)
get_property(translation_libs GLOBAL PROPERTY MLIR_TRANSLATION_LIBS)

add_mlir_tool(aie-translate
  aie-translate.cpp
)
llvm_update_compile_flags(aie-translate)
target_link_libraries(aie-translate
  PRIVATE
  ${dialect_libs}
  ${translation_libs}
  AIE
  AIETransforms
  AIEX
  AIEXTransforms
  AIEXUtils
  AIETargets
  MLIRIR
  MLIRParser
  MLIRPass
  MLIRTargetAIEVecCpp
  MLIRTargetLLVMIRExport
  MLIRTargetLLVMIRImport
)
